from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app import models
from app.users import router as users_router
from app.projects import router as project_router
from app.redis_client import test_redis_connection, redis_client
from app.scheduler import start_scheduler, stop_scheduler


# =====================================================
# Lifespan — start/stop scheduler with the app
# =====================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Redis connected:", test_redis_connection())
    start_scheduler()
    yield
    # Shutdown
    stop_scheduler()


app = FastAPI(
    title="PR Health Dashboard API",
    version="0.1.0",
    lifespan=lifespan,
)

# Create tables
Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "http://localhost:3000",
    "https://d3vdqggl4icojs.cloudfront.net",
    "http://d3vdqggl4icojs.cloudfront.net"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(users_router)
app.include_router(project_router)


@app.get("/")
def root():
    return {"message": "PR Health Dashboard API is running"}


@app.get("/test/redis")
def test_redis():
    try:
        redis_client.set("sample_key", "Hello Redis")
        value = redis_client.get("sample_key")
        return {"message": "Redis working", "value": value}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.get("/test/send-notifications")
def test_send_notifications():
    from app.services.notification_service import send_pr_review_notifications
    try:
        send_pr_review_notifications()
        return {"message": "Notification job executed. Check your terminal for logs."}
    except Exception as e:
        return {"message": "Failed", "error": str(e)}
@app.get("/test/ses-debug")
def ses_debug():
    from app.config import settings
    from app.services.ses_service import SESService
    try:
        ses = SESService()
        result = ses.send_otp_email(
            recipient="deepakkumar.somasundaram@gmail.com",
            otp="123456",
            purpose="login"
        )
        return {
            "sent": result,
            "sender": settings.SES_SENDER_EMAIL,
            "region": settings.AWS_REGION,
            "access_key_prefix": settings.AWS_ACCESS_KEY_ID[:8] + "..."
        }
    except Exception as e:
        return {
            "sent": False,
            "error": str(e),
            "sender": settings.SES_SENDER_EMAIL,
            "region": settings.AWS_REGION,
            "access_key_prefix": settings.AWS_ACCESS_KEY_ID[:8] + "..."
        }

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="PR Health Dashboard API",
        version="0.1.0",
        description="API for PR Health Dashboard",
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }

    for path in openapi_schema["paths"].values():
        for method in path.values():
            method["security"] = [{"BearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi