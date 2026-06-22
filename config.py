from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    # Anthropic
    anthropic_api_key: str = ""

    # Supabase
    supabase_url: str = ""
    supabase_anon_key: str = ""

    # Twilio (optional)
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_whatsapp_from: str = "whatsapp:+14155238886"

    # SendGrid (optional)
    sendgrid_api_key: str = ""
    report_email_to: str = ""
    report_email_from: str = "reports@construction-ai.com"

    # App
    pm_whatsapp_number: str = "+971500000000"
    default_project_id: str = "PROJ-001"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()

# Warn on startup if critical keys are missing
if not settings.anthropic_api_key:
    print("[WARNING] ANTHROPIC_API_KEY not set — AI features will fail")
if not settings.supabase_url:
    print("[WARNING] SUPABASE_URL not set — database features will fail")
if not settings.supabase_anon_key:
    print("[WARNING] SUPABASE_ANON_KEY not set — database features will fail")
