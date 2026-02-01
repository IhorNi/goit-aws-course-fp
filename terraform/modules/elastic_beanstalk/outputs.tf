output "application_name" {
  description = "EB application name"
  value       = aws_elastic_beanstalk_application.main.name
}

output "environment_name" {
  description = "EB environment name"
  value       = aws_elastic_beanstalk_environment.main.name
}

output "environment_id" {
  description = "EB environment ID"
  value       = aws_elastic_beanstalk_environment.main.id
}

output "endpoint_url" {
  description = "EB environment endpoint URL"
  value       = aws_elastic_beanstalk_environment.main.endpoint_url
}

output "cname" {
  description = "EB environment CNAME"
  value       = aws_elastic_beanstalk_environment.main.cname
}

output "load_balancer_url" {
  description = "Load balancer URL"
  value       = "http://${aws_elastic_beanstalk_environment.main.cname}"
}
