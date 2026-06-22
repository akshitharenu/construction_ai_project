from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Anthropic
    anthropic_api_key: str

    # Supabase
    supabase_url: str
    supabase_anon_key: str

    # Twilio (WhatsApp)
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_whatsapp_from: str = "whatsapp:+14155238886"

    # SendGrid (email)
    sendgrid_api_key: str = ""
    report_email_to: str = ""
    report_email_from: str = "reports@construction-ai.com"

    # App
    pm_whatsapp_number: str = "+971500000000"
    default_project_id: str = "PROJ-001"

    class Config:
        env_file = ".env"


settings = Settings()
