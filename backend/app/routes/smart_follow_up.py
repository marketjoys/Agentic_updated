from fastapi import APIRouter, HTTPException
from app.models import FollowUpRule
from app.services.smart_follow_up_engine import smart_follow_up_engine
from app.services.database import db_service
from app.utils.helpers import generate_id
from typing import Dict
from datetime import datetime

router = APIRouter()

@router.post("/follow-up-engine/start")
async def start_follow_up_engine():
    """Start the smart follow-up engine"""
    try:
        result = await smart_follow_up_engine.start_follow_up_engine()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/follow-up-engine/stop")
async def stop_follow_up_engine():
    """Stop the smart follow-up engine"""
    try:
        result = await smart_follow_up_engine.stop_follow_up_engine()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/follow-up-engine/status")
async def get_follow_up_engine_status():
    """Get follow-up engine status"""
    return {
        "status": "running" if smart_follow_up_engine.processing else "stopped",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/follow-up-engine/statistics")
async def get_follow_up_statistics():
    """Get follow-up statistics"""
    try:
        stats = await smart_follow_up_engine.get_follow_up_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/follow-up-engine/process-response")
async def process_email_response(response_data: Dict):
    """Process an email response to determine follow-up action"""
    try:
        prospect_id = response_data.get("prospect_id")
        email_content = response_data.get("email_content")
        subject = response_data.get("subject", "")
        
        if not all([prospect_id, email_content]):
            raise HTTPException(status_code=400, detail="Missing required fields: prospect_id, email_content")
        
        result = await smart_follow_up_engine.process_email_response(
            prospect_id, email_content, subject
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Follow-up Rules Management
@router.post("/follow-up-rules")
async def create_follow_up_rule(rule: FollowUpRule):
    """Create a new follow-up rule"""
    rule.id = generate_id()
    rule_dict = rule.dict()
    
    result = await db_service.create_follow_up_rule(rule_dict)
    if not result:
        raise HTTPException(status_code=500, detail="Failed to create follow-up rule")
    
    return {"id": rule.id, "message": "Follow-up rule created successfully"}

@router.get("/follow-up-rules")
async def get_follow_up_rules():
    """Get all follow-up rules"""
    rules = await db_service.get_follow_up_rules()
    return rules

@router.get("/follow-up-rules/{rule_id}")
async def get_follow_up_rule(rule_id: str):
    """Get a specific follow-up rule by ID"""
    rule = await db_service.get_follow_up_rule_by_id(rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Follow-up rule not found")
    return rule

@router.put("/follow-up-rules/{rule_id}")
async def update_follow_up_rule(rule_id: str, rule_data: Dict):
    """Update a follow-up rule"""
    rule_data["updated_at"] = datetime.utcnow()
    result = await db_service.update_follow_up_rule(rule_id, rule_data)
    
    if not result:
        raise HTTPException(status_code=404, detail="Follow-up rule not found")
    
    return {"message": "Follow-up rule updated successfully"}

@router.delete("/follow-up-rules/{rule_id}")
async def delete_follow_up_rule(rule_id: str):
    """Delete a follow-up rule"""
    result = await db_service.delete_follow_up_rule(rule_id)
    
    if not result:
        raise HTTPException(status_code=404, detail="Follow-up rule not found")
    
    return {"message": "Follow-up rule deleted successfully"}

@router.post("/follow-up-rules/create-default")
async def create_default_follow_up_rules():
    """Create default follow-up rules"""
    default_rules = [
        {
            "name": "Standard B2B Follow-up",
            "description": "Standard follow-up sequence for B2B prospects",
            "trigger_after_days": 3,
            "max_follow_ups": 3,
            "stop_on_response": True,
            "stop_on_auto_reply": False,
            "send_time_start": "09:00",
            "send_time_end": "17:00",
            "timezone": "UTC",
            "exclude_weekends": True,
            "only_if_no_response": True,
            "only_if_not_opened": False,
            "is_active": True
        },
        {
            "name": "Aggressive Sales Follow-up",
            "description": "More frequent follow-up for hot leads",
            "trigger_after_days": 1,
            "max_follow_ups": 5,
            "stop_on_response": True,
            "stop_on_auto_reply": False,
            "send_time_start": "08:00",
            "send_time_end": "18:00",
            "timezone": "UTC",
            "exclude_weekends": False,
            "only_if_no_response": True,
            "only_if_not_opened": False,
            "is_active": True
        },
        {
            "name": "Gentle Nurture Follow-up",
            "description": "Gentle follow-up for nurturing prospects",
            "trigger_after_days": 7,
            "max_follow_ups": 2,
            "stop_on_response": True,
            "stop_on_auto_reply": True,
            "send_time_start": "10:00",
            "send_time_end": "16:00",
            "timezone": "UTC",
            "exclude_weekends": True,
            "only_if_no_response": True,
            "only_if_not_opened": True,
            "is_active": True
        }
    ]
    
    created_rules = []
    for rule_data in default_rules:
        rule_data["id"] = generate_id()
        rule_data["created_at"] = datetime.utcnow()
        
        result = await db_service.create_follow_up_rule(rule_data)
        if result:
            created_rules.append(rule_data["id"])
    
    return {
        "message": f"Created {len(created_rules)} default follow-up rules",
        "created_rules": created_rules
    }

@router.post("/follow-up-rules/{rule_id}/test")
async def test_follow_up_rule(rule_id: str, test_data: Dict):
    """Test a follow-up rule with sample data"""
    rule = await db_service.get_follow_up_rule_by_id(rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Follow-up rule not found")
    
    # Sample test scenario
    test_scenario = test_data.get("scenario", "default")
    
    scenarios = {
        "default": {
            "last_contact": "2024-01-01T10:00:00",
            "follow_up_count": 0,
            "responded": False
        },
        "first_follow_up": {
            "last_contact": "2024-01-01T10:00:00",
            "follow_up_count": 1,
            "responded": False
        },
        "responded": {
            "last_contact": "2024-01-01T10:00:00",
            "follow_up_count": 1,
            "responded": True
        }
    }
    
    scenario_data = scenarios.get(test_scenario, scenarios["default"])
    
    # Calculate next follow-up timing
    from datetime import datetime, timedelta
    last_contact = datetime.fromisoformat(scenario_data["last_contact"].replace('Z', '+00:00'))
    trigger_days = rule["trigger_after_days"]
    next_follow_up = last_contact + timedelta(days=trigger_days)
    
    # Determine action
    action = "send_follow_up"
    if scenario_data["responded"] and rule["stop_on_response"]:
        action = "stop_follow_up"
    elif scenario_data["follow_up_count"] >= rule["max_follow_ups"]:
        action = "limit_reached"
    
    return {
        "rule_id": rule_id,
        "rule_name": rule["name"],
        "test_scenario": test_scenario,
        "scenario_data": scenario_data,
        "rule_settings": {
            "trigger_after_days": rule["trigger_after_days"],
            "max_follow_ups": rule["max_follow_ups"],
            "stop_on_response": rule["stop_on_response"]
        },
        "result": {
            "action": action,
            "next_follow_up": next_follow_up.isoformat(),
            "days_until_next": trigger_days,
            "follow_up_sequence": scenario_data["follow_up_count"] + 1
        }
    }

@router.get("/follow-up-rules/time-windows/validate")
async def validate_time_window(start_time: str = "09:00", end_time: str = "17:00", 
                              timezone: str = "UTC", exclude_weekends: bool = True):
    """Validate and test time window settings"""
    try:
        from datetime import datetime
        import pytz
        
        # Validate time format
        try:
            datetime.strptime(start_time, "%H:%M")
            datetime.strptime(end_time, "%H:%M")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid time format. Use HH:MM")
        
        # Validate timezone
        try:
            pytz.timezone(timezone)
        except pytz.UnknownTimeZoneError:
            raise HTTPException(status_code=400, detail="Invalid timezone")
        
        # Get current time in specified timezone
        tz = pytz.timezone(timezone)
        current_time = datetime.now(tz)
        current_day = current_time.strftime("%A").lower()
        current_time_str = current_time.strftime("%H:%M")
        
        # Check if current time is in window
        in_time_window = start_time <= current_time_str <= end_time
        
        # Check if current day is allowed
        weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday"]
        is_weekend = current_day in ["saturday", "sunday"]
        day_allowed = not (exclude_weekends and is_weekend)
        
        can_send_now = in_time_window and day_allowed
        
        return {
            "time_window": {
                "start_time": start_time,
                "end_time": end_time,
                "timezone": timezone,
                "exclude_weekends": exclude_weekends
            },
            "current_status": {
                "current_time": current_time.isoformat(),
                "current_day": current_day,
                "current_time_only": current_time_str,
                "is_weekend": is_weekend,
                "in_time_window": in_time_window,
                "day_allowed": day_allowed,
                "can_send_now": can_send_now
            },
            "next_allowed_time": {
                "description": "Next time emails can be sent based on these settings",
                "calculation": "Based on time window and weekend exclusion"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error validating time window: {str(e)}")