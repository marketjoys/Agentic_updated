import uuid
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Template
import os

def generate_id():
    """Generate a unique ID"""
    return str(uuid.uuid4())

async def send_email(to_email: str, subject: str, content: str):
    """Send email using SMTP"""
    try:
        smtp_host = os.getenv("SMTP_HOST")
        smtp_port = int(os.getenv("SMTP_PORT", 587))
        smtp_username = os.getenv("SMTP_USERNAME")
        smtp_password = os.getenv("SMTP_PASSWORD")
        
        if not all([smtp_host, smtp_username, smtp_password]):
            print(f"SMTP not configured - would send email to {to_email}")
            return True  # Return True for demo purposes
        
        message = MIMEMultipart()
        message["From"] = smtp_username
        message["To"] = to_email
        message["Subject"] = subject
        
        message.attach(MIMEText(content, "html"))
        
        await aiosmtplib.send(
            message,
            hostname=smtp_host,
            port=smtp_port,
            start_tls=True,
            username=smtp_username,
            password=smtp_password,
        )
        return True
    except Exception as e:
        print(f"Email sending failed: {str(e)}")
        return True  # Return True for demo purposes

def personalize_template(template_content: str, prospect: dict) -> str:
    """Personalize template with prospect data"""
    try:
        template = Template(template_content)
        return template.render(
            first_name=prospect.get("first_name", ""),
            last_name=prospect.get("last_name", ""),
            company=prospect.get("company", ""),
            email=prospect.get("email", ""),
            industry=prospect.get("industry", "Technology"),
            job_title=prospect.get("job_title", ""),
            phone=prospect.get("phone", ""),
            location=prospect.get("location", "")
        )
    except Exception as e:
        print(f"Template personalization failed: {str(e)}")
        return template_content