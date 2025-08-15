# handler.py
import serverless_wsgi
from main import app  # 假設你的檔名就是 app.py；若不同，改成相對應名稱

def handler(event, context):
    return serverless_wsgi.handle_request(app, event, context)