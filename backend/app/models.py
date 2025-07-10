from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum

class EmailProviderType(str, Enum):
    GMAIL = "gmail"
    OUTLOOK = "outlook"
    YAHOO = "yahoo"
    CUSTOM_SMTP = "custom_smtp"
    
class FollowUpStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    STOPPED = "stopped"

class EmailProvider(BaseModel):
    id: str = None
    name: str
    provider_type: EmailProviderType
    email_address: EmailStr
    display_name: str = ""
    
    # SMTP Settings
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_use_tls: bool = True
    smtp_use_ssl: bool = False
    
    # IMAP Settings
    imap_host: str = ""
    imap_port: int = 993
    imap_username: str = ""
    imap_password: str = ""
    imap_use_ssl: bool = True
    
    # OAuth2 Settings (for Gmail, Outlook)
    oauth2_client_id: str = ""
    oauth2_client_secret: str = ""
    oauth2_refresh_token: str = ""
    oauth2_access_token: str = ""
    oauth2_token_expires: Optional[datetime] = None
    
    # Provider-specific settings
    provider_settings: Dict[str, Any] = {}
    
    # Status and configuration
    is_active: bool = True
    is_default: bool = False
    last_sync: Optional[datetime] = None
    daily_send_limit: int = 500
    hourly_send_limit: int = 50
    current_daily_count: int = 0
    current_hourly_count: int = 0
    
    # Metadata
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    
class KnowledgeBase(BaseModel):
    id: str = None
    title: str
    content: str
    category: str = "general"
    tags: List[str] = []
    keywords: List[str] = []
    
    # AI Integration
    embedding_vector: List[float] = []  # Vector embeddings for AI search
    relevance_score: float = 0.0
    
    # Usage tracking
    usage_count: int = 0
    last_used: Optional[datetime] = None
    
    # Metadata
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    is_active: bool = True

class SystemPrompt(BaseModel):
    id: str = None
    name: str
    description: str = ""
    prompt_text: str
    prompt_type: str = "general"  # general, intent_classification, response_generation
    
    # Configuration
    is_active: bool = True
    is_default: bool = False
    temperature: float = 0.7
    max_tokens: int = 1000
    
    # Usage tracking
    usage_count: int = 0
    last_used: Optional[datetime] = None
    
    # Metadata
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()

class FollowUpRule(BaseModel):
    id: str = None
    name: str
    description: str = ""
    
    # Trigger conditions
    trigger_after_days: int = 3
    max_follow_ups: int = 3
    stop_on_response: bool = True
    stop_on_auto_reply: bool = False
    
    # Email content
    template_ids: List[str] = []  # Templates for each follow-up
    subject_templates: List[str] = []
    
    # Timing
    send_time_start: str = "09:00"
    send_time_end: str = "17:00"
    timezone: str = "UTC"
    exclude_weekends: bool = True
    
    # Conditions
    only_if_no_response: bool = True
    only_if_not_opened: bool = False
    
    # Metadata
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    is_active: bool = True
    id: str = None
    name: str
    description: str = ""
    color: str = "#3B82F6"  # Default blue color
    prospect_count: int = 0
    tags: List[str] = []
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()

class Prospect(BaseModel):
    id: str = None
    email: EmailStr
    first_name: str
    last_name: str
    company: str = ""
    phone: str = ""
    linkedin_url: str = ""
    company_domain: str = ""
    industry: str = ""
    company_linkedin_url: str = ""
    job_title: str = ""
    location: str = ""
    company_size: str = ""
    annual_revenue: str = ""
    lead_source: str = ""
    list_ids: List[str] = []  # Can belong to multiple lists
    tags: List[str] = []
    additional_fields: Dict[str, str] = {}
    status: str = "active"
    campaign_id: str = ""
    last_contact: Optional[datetime] = None
    created_at: datetime = datetime.utcnow()

class Template(BaseModel):
    id: str = None
    name: str
    subject: str
    content: str
    type: str = "initial"  # initial, follow_up, auto_response
    placeholders: List[str] = []
    created_at: datetime = datetime.utcnow()

class Campaign(BaseModel):
    id: str = None
    name: str
    template_id: str
    list_ids: List[str] = []  # Target specific lists
    prospect_count: int = 0
    max_emails: int = 1000
    # Advanced Scheduling Options
    schedule_type: str = "immediate"  # immediate, scheduled, recurring
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    timezone: str = "UTC"
    send_window_start: str = "09:00"  # 24-hour format
    send_window_end: str = "17:00"
    send_days: List[str] = ["monday", "tuesday", "wednesday", "thursday", "friday"]
    rate_limit_per_hour: int = 100
    rate_limit_per_day: int = 1000
    delay_between_emails: int = 60  # seconds
    # Existing fields
    status: str = "draft"  # draft, scheduled, active, paused, completed
    follow_up_intervals: List[int] = [3, 7, 14]  # days
    follow_up_templates: List[str] = []
    created_at: datetime = datetime.utcnow()

class IntentConfig(BaseModel):
    id: str = None
    name: str
    description: str
    keywords: List[str] = []
    # Enhanced Template System
    primary_template_id: str = ""
    fallback_template_id: str = ""
    combination_templates: List[Dict[str, str]] = []  # For multiple intents
    auto_respond: bool = True
    response_delay_min: int = 5  # minutes
    response_delay_max: int = 60  # minutes
    confidence_threshold: float = 0.7
    escalate_to_human: bool = False
    created_at: datetime = datetime.utcnow()

class EmailMessage(BaseModel):
    id: str = None
    prospect_id: str
    campaign_id: str
    subject: str
    content: str
    status: str = "pending"  # pending, sent, failed
    sent_at: Optional[datetime] = None
    opened_at: Optional[datetime] = None
    replied_at: Optional[datetime] = None
    created_at: datetime = datetime.utcnow()

class ThreadContext(BaseModel):
    id: str = None
    prospect_id: str
    campaign_id: str
    messages: List[Dict[str, Any]] = []
    last_activity: datetime = datetime.utcnow()
    created_at: datetime = datetime.utcnow()