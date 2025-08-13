output "agent_ecr_url" { value = aws_ecr_repository.agent.repository_url }
output "weather_mcp_ecr_url" { value = aws_ecr_repository.weather_mcp.repository_url }
output "alb_dns_name" { value = aws_lb.app.dns_name }
output "project_name" { value = var.project_name }
output "aws_region" { value = var.aws_region }