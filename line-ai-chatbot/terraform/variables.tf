variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
  default     = "line-parking-agent"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "ap-northeast-1"
}

# ECS Task settings
variable "agent_cpu" {
  description = "CPU units for agent task"
  type        = number
  default     = 256
}

variable "agent_memory" {
  description = "Memory for agent task"
  type        = number
  default     = 512
}

variable "weather_mcp_cpu" {
  description = "CPU units for weather MCP task"
  type        = number
  default     = 256
}

variable "weather_mcp_memory" {
  description = "Memory for weather MCP task"
  type        = number
  default     = 512
}