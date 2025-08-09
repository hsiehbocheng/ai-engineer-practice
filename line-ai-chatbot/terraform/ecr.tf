# general lifecycle policy
locals {
    ecr_lifecycle_policy = jsonencode({
        rules = [
            {
            "rulePriority": 1,
            "description": "Keep latest tag",
            "selection": {
                "tagStatus": "tagged",
                "tagPrefixList": ["latest"],
                "countType": "imageCountMoreThan",
                "countNumber": 999
            },
            "action": {
                "type": "expire"
            }
        },
        {
            "rulePriority": 2,
            "description": "Keep last 10 versioned images",
            "selection": {
                "tagStatus": "tagged",
                "countType": "imageCountMoreThan",
                "countNumber": 10
            },
            "action": {
                "type": "expire"
            }
        }
        ]
    })
}

# ECR Repository for Agent Service
resource "aws_ecr_repository" "agent" {
    name = "${var.project_name}-agent"
    image_tag_mutability = "MUTABLE"

    image_scanning_configuration {
    scan_on_push = true
  }
}

# ECR Repository for MCP Service
resource "aws_ecr_repository" "weather_mcp" {
  name                 = "${var.project_name}-weather-mcp"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_ecr_lifecycle_policy" "agent_policy" {
  repository = aws_ecr_repository.agent.name
  policy     = local.ecr_lifecycle_policy
}

resource "aws_ecr_lifecycle_policy" "weather_mcp_policy" {
  repository = aws_ecr_repository.weather_mcp.name
  policy     = local.ecr_lifecycle_policy
}