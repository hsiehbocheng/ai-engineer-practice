terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region  = var.aws_region
  profile = var.aws_profile
}

###############################################################################
# 1. 共用變數與命名
###############################################################################
locals {
  repo_name   = var.project_name                        # lambda-deploy-fastapi
  lambda_name = "${var.project_name}-${var.environment}"# lambda-deploy-fastapi-dev
  image_tag   = "latest"
}

###############################################################################
# 2. ECR Repository：存放 container image
###############################################################################
resource "aws_ecr_repository" "this" {
  name                 = local.repo_name
  image_tag_mutability = "MUTABLE"  # 允許覆寫 :latest
  force_delete         = true       # destroy 時強制刪除
}

###############################################################################
# 3. IAM Role：讓 Lambda 有基本權限（寫 CloudWatch Log）
###############################################################################
data "aws_iam_policy" "lambda_basic" {
  arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role" "lambda_exec" {
  name = "${local.lambda_name}-exec"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = data.aws_iam_policy.lambda_basic.arn
}

###############################################################################
# 4. Lambda Function（使用 ECR 容器映像）
###############################################################################
resource "aws_lambda_function" "this" {
    function_name = local.lambda_name
    package_type = "Image"
    # ECR repository URL
    image_uri = "${aws_ecr_repository.this.repository_url}:${local.image_tag}"

    role = aws_iam_role.lambda_exec.arn
    architectures = ["arm64"]
    memory_size = 1024
    timeout = 30

    environment {
        variables = {
            ENVIRONMENT = var.environment,
            LOG_LEVEL = "INFO"
        }
    }
}

###############################################################################
# 5. Function URL：給 FastAPI 最快的 HTTPS 入口
###############################################################################
resource "aws_lambda_function_url" "this" {
  function_name      = aws_lambda_function.this.function_name
  authorization_type = "NONE"   # Demo 階段先開放匿名；正式環境建議 IAM/JWT
  cors {
    allow_methods = ["*"]
    allow_origins = ["*"]
  }
}

###############################################################################
# 6. 輸出
###############################################################################
output "function_url" {
  value = aws_lambda_function_url.this.function_url
}