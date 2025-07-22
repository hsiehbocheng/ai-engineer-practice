#!/bin/bash
set -e

echo "🚀 開始部署 Lambda FastAPI..."

# 設定變數
PROJECT_NAME="lambda-deploy-fastapi"
AWS_PROFILE="berg2"
AWS_REGION="ap-northeast-1"

# 取得 AWS 帳號 ID
echo "📋 取得 AWS 帳號資訊..."
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --profile $AWS_PROFILE --query Account --output text)
ECR_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${PROJECT_NAME}"

echo "AWS Account: $AWS_ACCOUNT_ID"
echo "ECR URI: $ECR_URI"

# 1. 先建立 ECR Repository
echo "📦 建立 ECR Repository..."
cd terraform
terraform init -upgrade
terraform apply -target=aws_ecr_repository.this -auto-approve
cd ..

# 2. 登入 ECR
echo "🔐 登入 ECR..."
aws ecr get-login-password --region $AWS_REGION --profile $AWS_PROFILE | \
    docker login --username AWS --password-stdin $ECR_URI

# 3. 建置並推送映像
# 確認 buildx 設定
BUILDER="lambda-builder"
CACHE_LIMIT_GB=5          # 觸發清理的門檻
if ! docker buildx inspect "$BUILDER" >/dev/null 2>&1; then
  echo "🛠  建立 buildx builder $BUILDER ..."
  docker buildx create --name "$BUILDER" --driver docker-container --use
else
  docker buildx use "$BUILDER"
fi

echo "🔨 建置 ARM64 映像..."
docker buildx build --builder lambda-builder --platform linux/arm64 --load \
  -t "${ECR_URI}:latest" .

docker push $ECR_URI:latest

# 4. 部署完整基礎設施
echo "🏗️ 部署 Lambda 資源..."
cd terraform
terraform apply -auto-approve

# 5. 取得結果
FUNCTION_URL=$(terraform output -raw function_url)
echo "✅ 部署完成！"
echo "🌐 Function URL: $FUNCTION_URL"
echo "🧪 測試: curl $FUNCTION_URL"
cd .. 