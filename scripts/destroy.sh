#!/bin/bash
# Destroy script for Gradio Chatbot

set -e

ENVIRONMENT="${1:-dev}"
PROJECT_NAME="gradio-chatbot"
AWS_REGION="us-east-1"
ECR_REPO_NAME="chatbot"

echo "=== Destroying environment: $ENVIRONMENT ==="
echo "WARNING: This will destroy all resources!"
read -p "Are you sure you want to continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Aborted."
    exit 0
fi

# Step 1: Destroy Terraform infrastructure
echo "=== Step 1: Destroying Terraform infrastructure ==="
cd terraform

terraform init
terraform destroy -var="environment=${ENVIRONMENT}" -auto-approve

cd ..

# Step 2: Clean up ECR images (optional)
read -p "Do you want to delete ECR repository and images? (yes/no): " DELETE_ECR

if [ "$DELETE_ECR" == "yes" ]; then
    echo "=== Step 2: Deleting ECR repository ==="
    aws ecr delete-repository \
        --repository-name "${ECR_REPO_NAME}" \
        --region "${AWS_REGION}" \
        --force 2>/dev/null || echo "ECR repository not found or already deleted"
fi

echo ""
echo "=== Destruction Complete ==="
echo "All resources have been destroyed."
