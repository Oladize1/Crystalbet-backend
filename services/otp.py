import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from fastapi import HTTPException
from jinja2 import Environment, FileSystemLoader
from db.mongodb import get_db

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.example.com")
SMTP_PORT = os.getenv("SMTP_PORT", 587)
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "your_email@example.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "your_password")

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "../templates")
env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

async def send_verification_email(recipient_email: str, verification_token: str):
    """
    Send email for verifying the user's account.
    """
    try:
        subject = "Verify your email"
        verification_url = f"{os.getenv('FRONTEND_URL', 'http://localhost:8000')}/verify-email/{verification_token}"
        template = env.get_template("email_verification.html")
        body = template.render(verification_url=verification_url)

        await send_email(recipient_email, subject, body)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending email: {str(e)}")

async def send_reset_password_email(recipient_email: str, reset_token: str):
    """
    Send email for password reset.
    """
    try:
        subject = "Reset your password"
        reset_url = f"{os.getenv('FRONTEND_URL', 'http://localhost:8000')}/reset-password/{reset_token}"
        template = env.get_template("password_reset.html")
        body = template.render(reset_url=reset_url)

        await send_email(recipient_email, subject, body)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending email: {str(e)}")

async def send_email(recipient_email: str, subject: str, body: str):
    """
    Sends an email using the SMTP configuration.
    """
    msg = MIMEMultipart()
    msg["From"] = SMTP_USERNAME
    msg["To"] = recipient_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "html"))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(SMTP_USERNAME, recipient_email, msg.as_string())
        server.quit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Email sending failed: {str(e)}")
