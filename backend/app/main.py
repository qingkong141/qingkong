from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.api.v1 import auth as auth_router

app = FastAPI(
    title="QingKong API",
    version="0.1.0",
    debug=settings.DEBUG,
)


# 错误类型 → 中文提示映射
VALIDATION_MESSAGES = {
    "missing":                    "该字段为必填项",
    "string_too_short":           "输入内容太短",
    "string_too_long":            "输入内容太长",
    "value_error":                "格式不正确",
    "int_parsing":                "请输入有效的整数",
    "value_error.email":          "邮箱格式不正确",
    "string_type":                "请输入字符串",
}

# 字段名 → 中文映射
FIELD_NAMES = {
    "username": "用户名",
    "email":    "邮箱",
    "password": "密码",
}


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """统一 Pydantic 校验错误格式，翻译成中文"""
    errors = exc.errors()
    first = errors[0]

    # 取字段名并翻译
    raw_field = ".".join(str(loc) for loc in first["loc"] if loc != "body")
    field = FIELD_NAMES.get(raw_field, raw_field)

    # 取错误类型并翻译，找不到则用原始英文信息兜底
    error_type = first.get("type", "")
    msg = VALIDATION_MESSAGES.get(error_type, first["msg"])

    message = f"{field}{msg}" if field else msg
    return JSONResponse(status_code=422, content={"detail": message})

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router, prefix="/qingkong")

@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "0.1.0"}
