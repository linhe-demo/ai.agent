# AI智能体中间件

## 🛠️ 技术栈

- **Web 框架**：FastAPI
- **OCR 引擎**：PaddleOCR
- **AI 模型**：DeepSeek API
- **语言**：Python 3.10+
- **文档**：Swagger UI / ReDoc
   
    

## 环境安装
    # Windows
    python -m venv .venv
    .venv\Scripts\activate

    # Linux/Mac
    python3 -m venv .venv
    source .venv/bin/activate

## 服务启动后
    API 文档：http://localhost:8000/docs

    ReDoc 文档：http://localhost:8000/redoc

    健康检查：http://localhost:8000/api/health

## 项目功能说明
- **发票识别**：可识别单张或多张发票（速度快，准确率高）实现原理：通过PaddleOCR识别出图片文字，调用deepseek
- 模型（编辑提示词分析出发票信息）返回json数据