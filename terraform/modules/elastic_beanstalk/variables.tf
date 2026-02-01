variable "project_name" {
  description = "Project name for resource naming"
  type        = string
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "aws_region" {
  description = "AWS region"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "public_subnet_ids" {
  description = "List of public subnet IDs for ALB"
  type        = list(string)
}

variable "private_subnet_ids" {
  description = "List of private subnet IDs for instances"
  type        = list(string)
}

variable "alb_security_group_id" {
  description = "Security group ID for ALB"
  type        = string
}

variable "instance_security_group_id" {
  description = "Security group ID for instances"
  type        = string
}

variable "service_role_arn" {
  description = "ARN of the EB service role"
  type        = string
}

variable "instance_profile_name" {
  description = "Name of the EC2 instance profile"
  type        = string
}

variable "solution_stack_name" {
  description = "EB solution stack name"
  type        = string
  default     = "64bit Amazon Linux 2023 v4.9.2 running Docker"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.small"
}

variable "min_instances" {
  description = "Minimum number of instances"
  type        = number
  default     = 1
}

variable "max_instances" {
  description = "Maximum number of instances"
  type        = number
  default     = 4
}

variable "db_host" {
  description = "Database host"
  type        = string
}

variable "db_port" {
  description = "Database port"
  type        = number
  default     = 5432
}

variable "db_name" {
  description = "Database name"
  type        = string
}

variable "db_username" {
  description = "Database username"
  type        = string
}

variable "db_secret_name" {
  description = "Name of the secret containing DB credentials"
  type        = string
}

variable "admin_username" {
  description = "Default admin username"
  type        = string
  default     = "admin"
}

variable "admin_password" {
  description = "Default admin password"
  type        = string
  sensitive   = true
}

variable "admin_email" {
  description = "Default admin email"
  type        = string
  default     = "admin@example.com"
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}
