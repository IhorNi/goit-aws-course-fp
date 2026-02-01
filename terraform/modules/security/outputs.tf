output "alb_security_group_id" {
  description = "Security group ID for ALB"
  value       = aws_security_group.alb.id
}

output "eb_instances_security_group_id" {
  description = "Security group ID for EB instances"
  value       = aws_security_group.eb_instances.id
}

output "rds_security_group_id" {
  description = "Security group ID for RDS"
  value       = aws_security_group.rds.id
}
