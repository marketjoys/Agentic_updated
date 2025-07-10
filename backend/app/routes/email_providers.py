from fastapi import APIRouter, HTTPException
from app.models import EmailProvider
from app.services.email_provider_service import email_provider_service
from app.utils.helpers import generate_id
from typing import List, Dict

router = APIRouter()

@router.post("/email-providers")
async def create_email_provider(provider: EmailProvider):
    """Create a new email provider"""
    provider_dict = provider.dict()
    provider_id, error = await email_provider_service.create_email_provider(provider_dict)
    
    if error:
        raise HTTPException(status_code=400, detail=error)
    
    return {"id": provider_id, "message": "Email provider created successfully"}

@router.get("/email-providers")
async def get_email_providers():
    """Get all email providers"""
    providers = await email_provider_service.get_email_providers()
    return providers

@router.get("/email-providers/{provider_id}")
async def get_email_provider(provider_id: str):
    """Get a specific email provider by ID"""
    provider = await email_provider_service.get_email_provider_by_id(provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Email provider not found")
    return provider

@router.put("/email-providers/{provider_id}")
async def update_email_provider(provider_id: str, provider_data: Dict):
    """Update an email provider"""
    success, error = await email_provider_service.update_email_provider(provider_id, provider_data)
    
    if error:
        raise HTTPException(status_code=400, detail=error)
    
    if not success:
        raise HTTPException(status_code=404, detail="Email provider not found")
    
    return {"message": "Email provider updated successfully"}

@router.delete("/email-providers/{provider_id}")
async def delete_email_provider(provider_id: str):
    """Delete an email provider"""
    success, error = await email_provider_service.delete_email_provider(provider_id)
    
    if error:
        raise HTTPException(status_code=400, detail=error)
    
    if not success:
        raise HTTPException(status_code=404, detail="Email provider not found")
    
    return {"message": "Email provider deleted successfully"}

@router.post("/email-providers/{provider_id}/set-default")
async def set_default_provider(provider_id: str):
    """Set an email provider as default"""
    success = await email_provider_service.set_default_provider(provider_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Email provider not found")
    
    return {"message": "Default email provider set successfully"}

@router.get("/email-providers/default/current")
async def get_default_provider():
    """Get the current default email provider"""
    provider = await email_provider_service.get_default_provider()
    if not provider:
        raise HTTPException(status_code=404, detail="No default email provider set")
    return provider

@router.post("/email-providers/{provider_id}/test-connection")
async def test_provider_connection(provider_id: str):
    """Test email provider connection"""
    provider = await email_provider_service.get_email_provider_by_id(provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Email provider not found")
    
    # Test connection using the service
    error = await email_provider_service._test_provider_connection(provider)
    
    if error:
        return {"status": "failed", "error": error}
    else:
        return {"status": "success", "message": "Connection test passed"}

@router.post("/email-providers/{provider_id}/send-test-email")
async def send_test_email(provider_id: str, test_data: Dict):
    """Send a test email using the provider"""
    to_email = test_data.get("to_email")
    subject = test_data.get("subject", "Test Email")
    content = test_data.get("content", "This is a test email.")
    
    if not to_email:
        raise HTTPException(status_code=400, detail="to_email is required")
    
    success, error = await email_provider_service.send_email(
        provider_id, to_email, subject, content
    )
    
    if error:
        raise HTTPException(status_code=400, detail=error)
    
    return {"message": "Test email sent successfully"}

@router.get("/email-providers/{provider_id}/emails")
async def get_provider_emails(provider_id: str, folder: str = "INBOX", limit: int = 20):
    """Get emails from a provider"""
    emails = await email_provider_service.get_emails(provider_id, folder, limit)
    return emails

@router.get("/email-providers/types/available")
async def get_available_provider_types():
    """Get available email provider types and their configurations"""
    from app.models import EmailProviderType
    
    provider_configs = {
        EmailProviderType.GMAIL: {
            "name": "Gmail",
            "smtp_host": "smtp.gmail.com",
            "smtp_port": 587,
            "imap_host": "imap.gmail.com",
            "imap_port": 993,
            "supports_oauth2": True,
            "requires_app_password": True,
            "setup_instructions": "1. Enable 2FA on your Gmail account\n2. Generate an App Password\n3. Use the App Password for authentication"
        },
        EmailProviderType.OUTLOOK: {
            "name": "Outlook/Hotmail",
            "smtp_host": "smtp-mail.outlook.com",
            "smtp_port": 587,
            "imap_host": "outlook.office365.com",
            "imap_port": 993,
            "supports_oauth2": True,
            "requires_app_password": True,
            "setup_instructions": "1. Enable 2FA on your Microsoft account\n2. Generate an App Password\n3. Use the App Password for authentication"
        },
        EmailProviderType.YAHOO: {
            "name": "Yahoo Mail",
            "smtp_host": "smtp.mail.yahoo.com",
            "smtp_port": 587,
            "imap_host": "imap.mail.yahoo.com",
            "imap_port": 993,
            "supports_oauth2": False,
            "requires_app_password": True,
            "setup_instructions": "1. Enable 2FA on your Yahoo account\n2. Generate an App Password\n3. Use the App Password for authentication"
        },
        EmailProviderType.CUSTOM_SMTP: {
            "name": "Custom SMTP",
            "smtp_host": "",
            "smtp_port": 587,
            "imap_host": "",
            "imap_port": 993,
            "supports_oauth2": False,
            "requires_app_password": False,
            "setup_instructions": "Provide your custom SMTP and IMAP server details"
        }
    }
    
    return provider_configs