#!/bin/bash
# Deploy script for Gradio Chatbot

set -e

# Configuration
ENVIRONMENT="${1:-dev}"
PROJECT_NAME="gradio-chatbot"
AWS_REGION="us-east-1"
ECR_REPO_NAME="chatbot"

echo "=== Deploying to environment: $ENVIRONMENT ==="

# Get AWS Account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REPO_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO_NAME}"

echo "AWS Account ID: $AWS_ACCOUNT_ID"
echo "ECR Repository: $ECR_REPO_URI"

# Step 1: Create ECR repository if it doesn't exist
echo "=== Step 1: Setting up ECR repository ==="
if aws ecr describe-repositories --repository-names "${ECR_REPO_NAME}" --region "${AWS_REGION}" >/dev/null 2>&1; then
    echo "ECR repository '${ECR_REPO_NAME}' already exists"
else
    echo "Creating ECR repository '${ECR_REPO_NAME}'..."
    aws ecr create-repository --repository-name "${ECR_REPO_NAME}" --region "${AWS_REGION}"
fi

# Step 2: Build Docker image (for x86_64/amd64 architecture)
echo "=== Step 2: Building Docker image ==="
# Use buildx to ensure correct platform build (required for M1/M2 Macs)
docker buildx create --use --name amd64builder 2>/dev/null || docker buildx use amd64builder 2>/dev/null || true
docker buildx build --platform linux/amd64 --load -t "${ECR_REPO_NAME}:latest" -f docker/Dockerfile .

# Verify architecture
ARCH=$(docker inspect "${ECR_REPO_NAME}:latest" --format '{{.Architecture}}')
echo "Built image architecture: ${ARCH}"
if [ "$ARCH" != "amd64" ]; then
    echo "ERROR: Image architecture is ${ARCH}, expected amd64"
    exit 1
fi

# Step 3: Login to ECR
echo "=== Step 3: Logging in to ECR ==="
aws ecr get-login-password --region "${AWS_REGION}" | \
    docker login --username AWS --password-stdin "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

# Step 4: Tag and push image
echo "=== Step 4: Pushing Docker image to ECR ==="
docker tag "${ECR_REPO_NAME}:latest" "${ECR_REPO_URI}:latest"
docker push "${ECR_REPO_URI}:latest"

# Step 5: Deploy Terraform infrastructure
echo "=== Step 5: Deploying Terraform infrastructure ==="
cd terraform

# Initialize Terraform
terraform init

# Plan and apply
terraform plan -var="environment=${ENVIRONMENT}" -out=tfplan
terraform apply tfplan

# Get outputs
APPLICATION_URL=$(terraform output -raw application_url)
DB_SECRET_NAME=$(terraform output -raw db_credentials_secret_name)

cd ..

# Step 6: Update Dockerrun.aws.json with correct ECR URI
echo "=== Step 6: Updating Dockerrun.aws.json ==="
sed -i.bak "s|<AWS_ACCOUNT_ID>|${AWS_ACCOUNT_ID}|g" Dockerrun.aws.json 2>/dev/null || \
    sed -i '' "s|<AWS_ACCOUNT_ID>|${AWS_ACCOUNT_ID}|g" Dockerrun.aws.json
rm -f Dockerrun.aws.json.bak

# Step 7: Deploy application to Elastic Beanstalk
echo "=== Step 7: Deploying application to Elastic Beanstalk ==="
VERSION_LABEL="v-$(date +%Y%m%d-%H%M%S)"
S3_BUCKET="elasticbeanstalk-${AWS_REGION}-${AWS_ACCOUNT_ID}"
S3_KEY="${PROJECT_NAME}/${VERSION_LABEL}.zip"

# Create deployment package
zip -j deployment.zip Dockerrun.aws.json

# Create S3 bucket if it doesn't exist
aws s3 mb "s3://${S3_BUCKET}" --region "${AWS_REGION}" 2>/dev/null || true

# Upload to S3
aws s3 cp deployment.zip "s3://${S3_BUCKET}/${S3_KEY}"

# Create application version
aws elasticbeanstalk create-application-version \
    --application-name "${PROJECT_NAME}" \
    --version-label "${VERSION_LABEL}" \
    --source-bundle S3Bucket="${S3_BUCKET}",S3Key="${S3_KEY}" \
    --region "${AWS_REGION}"

# Deploy to environment
aws elasticbeanstalk update-environment \
    --application-name "${PROJECT_NAME}" \
    --environment-name "${PROJECT_NAME}-${ENVIRONMENT}" \
    --version-label "${VERSION_LABEL}" \
    --region "${AWS_REGION}"

# Cleanup
rm -f deployment.zip

echo "=== Waiting for deployment to complete ==="
aws elasticbeanstalk wait environment-updated \
    --application-name "${PROJECT_NAME}" \
    --environment-names "${PROJECT_NAME}-${ENVIRONMENT}" \
    --region "${AWS_REGION}"

# Get final URL
APPLICATION_URL=$(aws elasticbeanstalk describe-environments \
    --environment-names "${PROJECT_NAME}-${ENVIRONMENT}" \
    --region "${AWS_REGION}" \
    --query 'Environments[0].CNAME' --output text)

echo ""
echo "=== Deployment Complete ==="
echo "Application URL: http://${APPLICATION_URL}"
echo "DB Secret Name: ${DB_SECRET_NAME}"
echo ""
echo "Next steps:"
echo "1. Access the application at http://${APPLICATION_URL}"
echo "2. Login with default credentials: admin / admin123"
echo "3. Change the admin password immediately"
