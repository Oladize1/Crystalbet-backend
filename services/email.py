import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from fastapi import HTTPException
from jinja2 import Environment, FileSystemLoader
import aiosmtplib
import logging

# Load SMTP configuration from environment variables
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.example.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "your_email@example.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "your_password")

# Load email templates
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "../templates")
env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

logger = logging.getLogger(__name__)

async def send_verification_email(recipient_email: str, verification_token: str):
    """Send email for verifying the user's account."""
    subject = "Verify your email"
    verification_url = f"{os.getenv('FRONTEND_URL', 'http://localhost:8000')}/verify-email/{verification_token}"
    template = env.get_template("email_verification.html")
    body = template.render(verification_url=verification_url)

    await send_email(recipient_email, subject, body)

async def send_reset_password_email(recipient_email: str, reset_token: str):
    """Send email for password reset."""
    subject = "Reset your password"
    reset_url = f"{os.getenv('FRONTEND_URL', 'http://localhost:8000')}/reset-password/{reset_token}"
    template = env.get_template("password_reset.html")
    body = template.render(reset_url=reset_url)

    await send_email(recipient_email, subject, body)

async def send_email(recipient_email: str, subject: str, body: str):
    """Sends an email using the SMTP configuration."""
    msg = MIMEMultipart()
    msg["From"] = SMTP_USERNAME
    msg["To"] = recipient_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "html"))

    try:
        async with aiosmtplib.SMTP(hostname=SMTP_SERVER, port=SMTP_PORT, start_tls=True) as server:
            await server.login(SMTP_USERNAME, SMTP_PASSWORD)
            await server.sendmail(SMTP_USERNAME, recipient_email, msg.as_string())
        logger.info(f"Email sent to {recipient_email}")
    except Exception as e:
        logger.error(f"Email sending failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Email sending failed: {str(e)}")
