# 使用 AWS 官方 Lambda Python 基礎映像
FROM public.ecr.aws/lambda/python:3.12

# 複製依賴檔案
COPY requirements.txt ${LAMBDA_TASK_ROOT}/

# 安裝 Python 依賴
RUN pip install -r requirements.txt --no-cache-dir

# 複製應用程式碼
COPY src/ ${LAMBDA_TASK_ROOT}/

# 設定 Lambda 處理函數
CMD ["main.handler"]