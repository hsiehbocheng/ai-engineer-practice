# Lambda Deploy FastAPI

使用 AWS Lambda + Container Image 部署 FastAPI 應用的 Example。

## 🚀 功能特色

- ✅ **FastAPI CRUD API** -  Todo 管理系統
- ✅ **AWS Lambda Container** - 使用容器映像部署
- ✅ **Lambda Function URL** - 直接 HTTPS 存取，無需 API Gateway
- ✅ **Terraform IaC** - 基礎設施即程式碼
- ✅ **ARM64 架構** - 成本優化和效能提升
- ✅ **自動化部署** - 一鍵部署腳本

## 🛠 技術棧

| 類別 | 技術 |
|------|------|
| **後端框架** | FastAPI + Mangum |
| **部署平台** | AWS Lambda (Container Image) |
| **基礎設施** | Terraform |
| **容器技術** | Docker (ARM64) |
| **套件管理** | uv |
| **語言版本** | Python 3.12 |

## 📋 前置需求

確保環境已安裝以下工具：

```bash
# 檢查 Python 版本
python3 --version  # >= 3.12

# 檢查 Docker 和 buildx
docker --version
docker buildx version

# 檢查 AWS CLI
aws --version

# 檢查 Terraform
terraform version

# 安裝 uv (如果還沒有)
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## 🚀 快速開始

### 1. 複製專案
```bash
git clone this repo
cd lambda-deploy-fastapi
```

### 2. 設定 AWS 認證
```bash
# 設定 AWS CLI (如果還沒設定)
aws configure --profile your-profile

# 驗證 AWS 連線
aws sts get-caller-identity --profile your-profile
```

### 3. 設定專案配置
```bash
# 複製範本檔案
cp terraform/terraform.tfvars.example terraform/terraform.tfvars

# 編輯配置檔案 (填入你的 AWS profile 和偏好設定)
nano terraform/terraform.tfvars
```

### 4. 安裝 Python 依賴
```bash
# 使用 uv 建立虛擬環境並安裝依賴
uv sync
```

### 5. 本地開發測試
```bash
# 啟動本地開發伺服器
uv run python src/main.py

# 瀏覽器開啟 API 文檔
open http://localhost:8000/docs
```

### 6. 部署到 AWS
```bash
# 使用自動化腳本部署
chmod +x scripts/deploy.sh
./scripts/deploy.sh

# 或手動分步驟部署
cd terraform
terraform init
terraform apply
```

## 📡 API 端點

部署完成後，你可以使用以下端點：

| 方法 | 端點 | 描述 |
|------|------|------|
| `GET` | `/` | 根路徑 - API 歡迎訊息 |
| `GET` | `/docs` | Swagger UI - 互動式 API 文檔 |
| `GET` | `/health` | 健康檢查 |
| `GET` | `/todos` | 取得所有 todos |
| `POST` | `/todos` | 建立新 todo |
| `GET` | `/todos/{id}` | 取得特定 todo |
| `PUT` | `/todos/{id}` | 更新 todo |
| `DELETE` | `/todos/{id}` | 刪除 todo |

### 使用範例

```bash
# 取得 Function URL (部署後顯示)
FUNCTION_URL="https://your-unique-id.lambda-url.ap-northeast-1.on.aws"

# 建立新 todo
curl -X POST "$FUNCTION_URL/todos" \
  -H "Content-Type: application/json" \
  -d '{"title": "學習 AWS Lambda", "description": "完成 FastAPI 部署練習"}'

# 查看所有 todos
curl "$FUNCTION_URL/todos"
```

## 📁 專案結構
