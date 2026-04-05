"""
Email notification service using Gmail SMTP (aiosmtplib for async).
"""

import os
import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")


def _build_html(title: str, message: str, crop: str, task_type: str) -> str:
    """Build a styled HTML email body."""
    emoji_map = {
        "irrigation": "💧",
        "fertilizer": "🌿",
        "pest_check": "🐛",
        "harvest": "🌾",
        "heat_warning": "🌡️",
        "rain_alert": "🌧️",
        "sowing": "🌱",
        "general": "📬",
    }
    emoji = emoji_map.get(task_type, "📬")

    return f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family: Arial, sans-serif; background:#f4f7f0; padding:20px;">
      <div style="max-width:560px;margin:auto;background:#fff;border-radius:12px;
                  overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.1);">
        <div style="background:#2d7a3a;padding:24px;color:#fff;text-align:center;">
          <div style="font-size:48px;">{emoji}</div>
          <h1 style="margin:8px 0;font-size:22px;">{title}</h1>
          <p style="margin:0;opacity:0.85;">AgroSmart AI — Your Farming Assistant</p>
        </div>
        <div style="padding:28px;">
          <p style="font-size:16px;color:#333;line-height:1.6;">{message}</p>
          <div style="margin-top:20px;padding:14px;background:#f0f7f0;
                      border-left:4px solid #2d7a3a;border-radius:4px;">
            <strong>🌱 Current Crop:</strong> {crop.title()}
          </div>
        </div>
        <div style="padding:16px;text-align:center;background:#f4f7f0;
                    font-size:12px;color:#888;">
          AgroSmart AI · Smart Farming for Better Yields
        </div>
      </div>
    </body>
    </html>
    """


async def send_notification_email(
    to_email: str,
    subject: str,
    message: str,
    crop: str,
    task_type: str = "general",
) -> bool:
    """
    Send an HTML notification email via Gmail SMTP.
    Returns True on success, False on failure.
    """
    if not SMTP_USER or not SMTP_PASSWORD:
        print(f"[EMAIL MOCK] To: {to_email} | Subject: {subject} | {message}")
        return True  # Pretend success in dev mode

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"🌱 AgroSmart: {subject}"
        msg["From"] = f"AgroSmart AI <{SMTP_USER}>"
        msg["To"] = to_email

        html_body = _build_html(subject, message, crop, task_type)
        msg.attach(MIMEText(message, "plain"))
        msg.attach(MIMEText(html_body, "html"))

        await aiosmtplib.send(
            msg,
            hostname=SMTP_HOST,
            port=SMTP_PORT,
            start_tls=True,
            username=SMTP_USER,
            password=SMTP_PASSWORD,
        )
        print(f"✅ Email sent to {to_email}: {subject}")
        return True

    except Exception as e:
        print(f"❌ Email failed to {to_email}: {e}")
        return False
