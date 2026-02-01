# Terraform Outputs

# VPC Outputs
output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.vpc_id
}

output "public_subnet_ids" {
  description = "Public subnet IDs"
  value       = module.vpc.public_subnet_ids
}

output "private_subnet_ids" {
  description = "Private subnet IDs"
  value       = module.vpc.private_subnet_ids
}

# RDS Outputs
output "db_endpoint" {
  description = "RDS endpoint"
  value       = module.rds.db_instance_address
}

output "db_port" {
  description = "RDS port"
  value       = module.rds.db_instance_port
}

output "db_credentials_secret_name" {
  description = "Name of the secret containing DB credentials"
  value       = module.rds.db_credentials_secret_name
}

output "db_master_password_secret_arn" {
  description = "ARN of the secret containing DB master password"
  value       = module.rds.db_master_user_secret_arn
}

# Elastic Beanstalk Outputs
output "eb_application_name" {
  description = "Elastic Beanstalk application name"
  value       = module.elastic_beanstalk.application_name
}

output "eb_environment_name" {
  description = "Elastic Beanstalk environment name"
  value       = module.elastic_beanstalk.environment_name
}

output "application_url" {
  description = "Application URL"
  value       = module.elastic_beanstalk.load_balancer_url
}

output "eb_cname" {
  description = "Elastic Beanstalk CNAME"
  value       = module.elastic_beanstalk.cname
}
