# Main Terraform Configuration
# This file wires all modules together

locals {
  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

# VPC Module
module "vpc" {
  source = "./modules/vpc"

  project_name = var.project_name
  vpc_cidr     = var.vpc_cidr
  tags         = local.tags
}

# Security Groups Module
module "security" {
  source = "./modules/security"

  project_name = var.project_name
  vpc_id       = module.vpc.vpc_id
  tags         = local.tags
}

# IAM Module
module "iam" {
  source = "./modules/iam"

  project_name = var.project_name
  aws_region   = var.aws_region
  tags         = local.tags
}

# RDS Module
module "rds" {
  source = "./modules/rds"

  project_name       = var.project_name
  private_subnet_ids = module.vpc.private_subnet_ids
  security_group_id  = module.security.rds_security_group_id

  instance_class    = var.db_instance_class
  allocated_storage = var.db_allocated_storage
  multi_az          = var.db_multi_az

  tags = local.tags
}

# Elastic Beanstalk Module
module "elastic_beanstalk" {
  source = "./modules/elastic_beanstalk"

  project_name = var.project_name
  environment  = var.environment
  aws_region   = var.aws_region

  vpc_id             = module.vpc.vpc_id
  public_subnet_ids  = module.vpc.public_subnet_ids
  private_subnet_ids = module.vpc.private_subnet_ids

  alb_security_group_id      = module.security.alb_security_group_id
  instance_security_group_id = module.security.eb_instances_security_group_id

  service_role_arn      = module.iam.eb_service_role_arn
  instance_profile_name = module.iam.ec2_instance_profile_name

  solution_stack_name = var.eb_solution_stack
  instance_type       = var.eb_instance_type
  min_instances       = var.eb_min_instances
  max_instances       = var.eb_max_instances

  db_host       = module.rds.db_instance_address
  db_port       = module.rds.db_instance_port
  db_name       = module.rds.db_instance_name
  db_username   = module.rds.db_instance_username
  db_secret_name = module.rds.db_credentials_secret_name

  admin_username = var.admin_username
  admin_password = var.admin_password
  admin_email    = var.admin_email

  tags = local.tags

  depends_on = [module.rds]
}
