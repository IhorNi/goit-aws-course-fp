variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "gradio-chatbot"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

# RDS Configuration
variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "db_allocated_storage" {
  description = "RDS allocated storage in GB"
  type        = number
  default     = 20
}

variable "db_multi_az" {
  description = "Enable Multi-AZ for RDS"
  type        = bool
  default     = false
}

# Elastic Beanstalk Configuration
variable "eb_instance_type" {
  description = "EC2 instance type for EB"
  type        = string
  default     = "t3.small"
}

variable "eb_min_instances" {
  description = "Minimum number of EB instances"
  type        = number
  default     = 1
}

variable "eb_max_instances" {
  description = "Maximum number of EB instances"
  type        = number
  default     = 4
}

variable "eb_solution_stack" {
  description = "EB solution stack name"
  type        = string
  default     = "64bit Amazon Linux 2023 v4.9.2 running Docker"
}

# Admin credentials
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
