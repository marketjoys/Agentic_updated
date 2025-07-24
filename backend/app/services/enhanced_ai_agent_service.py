# Enhanced AI Agent Service with Confirmation Flow
import logging
import json
import re
from typing import Dict, List, Optional, Any
from datetime import datetime

from app.models.conversation_models import ConversationState, InformationRequest, ConfirmationRequest
from app.services.enhanced_conversation_service import enhanced_conversation_service
from app.services.endpoint_mapping_service import endpoint_mapping_service
from app.services.groq_service import groq_service
from app.services.action_router_service import action_router_service
from app.utils.helpers import generate_id

logger = logging.getLogger(__name__)

class EnhancedAIAgentService:
    """Enhanced AI Agent with multi-turn confirmation flow"""
    
    def __init__(self):
        self.conversation_service = enhanced_conversation_service
        self.endpoint_service = endpoint_mapping_service
        self.groq = groq_service
        self.action_router = action_router_service
    
    async def process_conversation(self, message: str, user_id: str, session_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main conversation processing method with enhanced confirmation flow
        """
        try:
            # Get conversation context
            conv_context = await self.conversation_service.get_conversation_context(session_id, user_id)
            
            # Process based on current conversation state
            if conv_context.current_state == ConversationState.ANALYZING:
                return await self._handle_analyzing_state(message, conv_context)
            
            elif conv_context.current_state == ConversationState.GATHERING_INFO:
                return await self._handle_gathering_info_state(message, conv_context)
            
            elif conv_context.current_state == ConversationState.CONFIRMING:
                return await self._handle_confirming_state(message, conv_context)
            
            elif conv_context.current_state == ConversationState.EXECUTING:
                return await self._handle_executing_state(message, conv_context)
            
            else:  # ERROR or COMPLETED state
                return await self._handle_completed_or_error_state(message, conv_context)
                
        except Exception as e:
            logger.error(f"Error processing conversation: {e}")
            return {
                "response": f"I apologize, but I encountered an error while processing your request: {str(e)}. Let's start over - what would you like to do?",
                "action_taken": "error",
                "data": None,
                "suggestions": ["Try asking: 'What can you help me with?'", "Say: 'Show me my campaigns'", "Ask: 'How do I create a new prospect?'"],
                "conversation_state": "error"
            }
    
    async def _handle_analyzing_state(self, message: str, conv_context) -> Dict[str, Any]:
        """Handle message when in analyzing state"""
        try:
            # Step 1: Analyze user intent
            intent_analysis = await self._analyze_user_intent(message)
            
            # Step 2: Map to endpoint
            action = intent_analysis.get('action')
            endpoint_mapping = self.endpoint_service.get_endpoint_mapping(action)
            
            if not endpoint_mapping:
                return {
                    "response": f"I'm not sure how to help with that. I can assist with campaigns, prospects, templates, lists, email providers, and analytics. What would you like to do?",
                    "action_taken": "help",
                    "data": None,
                    "suggestions": [
                        "Show me my campaigns",
                        "Create a new prospect", 
                        "Add John Smith from TechCorp",
                        "What are my analytics?"
                    ],
                    "conversation_state": "analyzing"
                }
            
            # Step 3: Extract parameters from message
            extracted_params = self._extract_parameters_from_message(message, action)
            
            # Step 4: Validate parameters
            validation = self.endpoint_service.validate_parameters(action, extracted_params)
            missing_required = validation['missing_required']
            
            # Update conversation context
            await self.conversation_service.update_extracted_params(conv_context.session_id, extracted_params)
            conv_context.endpoint_mapping = endpoint_mapping
            
            # Step 5: Determine next state based on missing parameters
            if missing_required:
                # Need to gather more information
                await self.conversation_service.set_missing_params(conv_context.session_id, missing_required)
                await self.conversation_service.update_conversation_state(conv_context.session_id, ConversationState.GATHERING_INFO)
                
                # Set pending action to preserve context
                await self.conversation_service.set_pending_action(conv_context.session_id, {
                    "action": action,
                    "parameters": extracted_params,
                    "endpoint_mapping": endpoint_mapping.dict()
                })
                
                # Generate information request  
                response = await self._generate_info_gathering_response(action, missing_required, extracted_params)
                
                # Add conversation turn
                await self.conversation_service.add_conversation_turn(
                    conv_context.session_id,
                    message,
                    response,
                    ConversationState.GATHERING_INFO,
                    intent=action,
                    extracted_params=extracted_params,
                    missing_params=missing_required
                )
                
                return {
                    "response": response,
                    "action_taken": "gathering_info",
                    "data": {
                        "action": action,
                        "extracted_params": extracted_params,
                        "missing_params": missing_required,
                        "endpoint": endpoint_mapping.endpoint,
                        "method": endpoint_mapping.method
                    },
                    "suggestions": ["Cancel this action", "Start over"],
                    "conversation_state": "gathering_info"
                }
            
            else:
                # All parameters available, move to confirmation
                await self.conversation_service.update_conversation_state(conv_context.session_id, ConversationState.CONFIRMING)
                await self.conversation_service.set_pending_action(conv_context.session_id, {
                    "action": action,
                    "parameters": extracted_params,
                    "endpoint_mapping": endpoint_mapping.dict()
                })
                
                # Generate confirmation request
                confirmation_msg = await self._generate_confirmation_message(action, extracted_params, endpoint_mapping)
                
                # Add conversation turn
                await self.conversation_service.add_conversation_turn(
                    conv_context.session_id,
                    message,
                    confirmation_msg,
                    ConversationState.CONFIRMING,
                    intent=action,
                    extracted_params=extracted_params
                )
                
                return {
                    "response": confirmation_msg,
                    "action_taken": "requesting_confirmation",
                    "data": {
                        "action": action,
                        "parameters": extracted_params,
                        "endpoint": endpoint_mapping.endpoint,
                        "method": endpoint_mapping.method
                    },
                    "suggestions": ["Yes, proceed", "No, cancel", "Make changes"],
                    "conversation_state": "confirming"
                }
                
        except Exception as e:
            logger.error(f"Error in analyzing state: {e}")
            return {
                "response": f"I had trouble analyzing your request: {str(e)}. Could you please rephrase it?",
                "action_taken": "error",
                "data": None,
                "suggestions": ["Try a different request", "Ask for help"],
                "conversation_state": "error"
            }
    
    async def _handle_gathering_info_state(self, message: str, conv_context) -> Dict[str, Any]:
        """Handle message when gathering information"""
        try:
            # Check if user wants to cancel
            if any(word in message.lower() for word in ['cancel', 'stop', 'abort', 'never mind', 'forget it']):
                await self.conversation_service.clear_pending_action(conv_context.session_id)
                return {
                    "response": "Okay, I've cancelled that action. What else can I help you with?",
                    "action_taken": "cancelled",
                    "data": None,
                    "suggestions": ["Show me my campaigns", "Create a new prospect", "What can you help me with?"],
                    "conversation_state": "analyzing"
                }
            
            # Extract new parameters from user's response
            pending_action = conv_context.pending_action or {}
            action = pending_action.get('action', '')
            current_params = conv_context.extracted_params.copy()
            
            # Extract parameters from this message
            new_params = self._extract_parameters_from_message(message, action)
            current_params.update(new_params)
            
            # Update conversation context
            await self.conversation_service.update_extracted_params(conv_context.session_id, new_params)
            
            # Re-validate parameters
            endpoint_mapping = self.endpoint_service.get_endpoint_mapping(action)
            if not endpoint_mapping:
                await self.conversation_service.clear_pending_action(conv_context.session_id)
                return {
                    "response": "I seem to have lost track of what we were doing. Let's start over - what would you like to do?",
                    "action_taken": "error",
                    "data": None,
                    "suggestions": ["Show me my campaigns", "Create a new prospect"],
                    "conversation_state": "analyzing"
                }
            
            validation = self.endpoint_service.validate_parameters(action, current_params)
            missing_required = validation['missing_required']
            
            if missing_required:
                # Still missing parameters, continue gathering
                await self.conversation_service.set_missing_params(conv_context.session_id, missing_required)
                
                response = await self._generate_info_gathering_response(action, missing_required, current_params)
                
                await self.conversation_service.add_conversation_turn(
                    conv_context.session_id,
                    message,
                    response,
                    ConversationState.GATHERING_INFO,
                    extracted_params=new_params,
                    missing_params=missing_required
                )
                
                return {
                    "response": response,
                    "action_taken": "gathering_info",
                    "data": {
                        "action": action,
                        "extracted_params": current_params,
                        "missing_params": missing_required
                    },
                    "suggestions": ["Cancel this action"],
                    "conversation_state": "gathering_info"
                }
            
            else:
                # All parameters collected, move to confirmation
                await self.conversation_service.update_conversation_state(conv_context.session_id, ConversationState.CONFIRMING)
                await self.conversation_service.set_pending_action(conv_context.session_id, {
                    "action": action,
                    "parameters": current_params,
                    "endpoint_mapping": endpoint_mapping.dict()
                })
                
                confirmation_msg = await self._generate_confirmation_message(action, current_params, endpoint_mapping)
                
                await self.conversation_service.add_conversation_turn(
                    conv_context.session_id,
                    message,
                    confirmation_msg,
                    ConversationState.CONFIRMING,
                    extracted_params=new_params
                )
                
                return {
                    "response": confirmation_msg,
                    "action_taken": "requesting_confirmation",
                    "data": {
                        "action": action,
                        "parameters": current_params,
                        "endpoint": endpoint_mapping.endpoint,
                        "method": endpoint_mapping.method
                    },
                    "suggestions": ["Yes, proceed", "No, cancel", "Make changes"],
                    "conversation_state": "confirming"
                }
                
        except Exception as e:
            logger.error(f"Error in gathering info state: {e}")
            await self.conversation_service.clear_pending_action(conv_context.session_id)
            return {
                "response": f"I had trouble processing your information: {str(e)}. Let's start over - what would you like to do?",
                "action_taken": "error",
                "data": None,
                "suggestions": ["Try a different request"],
                "conversation_state": "analyzing"
            }
    
    async def _handle_confirming_state(self, message: str, conv_context) -> Dict[str, Any]:
        """Handle message when confirming action"""
        try:
            message_lower = message.lower()
            
            # Check for positive confirmation
            positive_patterns = [
                r'\b(?:yes|yeah|yep|sure|okay|ok|proceed|go ahead|confirm|do it|execute|run|send|create|add|make)\b',
                r'\b(?:let\'s do it|let\'s go|sounds good|looks good|that\'s right|correct)\b'
            ]
            
            # Check for negative confirmation  
            negative_patterns = [
                r'\b(?:no|nope|cancel|stop|abort|don\'t|never mind|not now|skip)\b',
                r'\b(?:forget it|cancel that|not right now|maybe later)\b'
            ]
            
            # Check for modification requests
            modification_patterns = [
                r'\b(?:change|modify|edit|update|different|wrong|incorrect)\b',
                r'\b(?:let me change|can I change|want to change|need to change)\b'
            ]
            
            is_positive = any(re.search(pattern, message_lower) for pattern in positive_patterns)
            is_negative = any(re.search(pattern, message_lower) for pattern in negative_patterns)
            is_modification = any(re.search(pattern, message_lower) for pattern in modification_patterns)
            
            pending_action = conv_context.pending_action or {}
            action = pending_action.get('action', '')
            parameters = pending_action.get('parameters', {})
            
            if is_positive and not is_negative:
                # User confirmed - execute the action
                await self.conversation_service.update_conversation_state(conv_context.session_id, ConversationState.EXECUTING)
                
                # Execute the action
                # Extract entity and operation from action
                if '_' in action:
                    operation, entity_raw = action.split('_', 1)
                    # Convert plural entities to singular for routing
                    entity_mapping = {
                        'campaigns': 'campaign',
                        'prospects': 'prospect', 
                        'templates': 'template',
                        'lists': 'list',
                        'email_providers': 'email_provider',
                        'providers': 'email_provider'
                    }
                    entity = entity_mapping.get(entity_raw, entity_raw)
                else:
                    operation = action
                    entity = 'general'
                
                result = await self.action_router.execute_action(
                    action=action,
                    entity=entity,
                    operation=operation,
                    parameters=parameters,
                    user_id=conv_context.user_id
                )
                
                # Generate response based on result
                if result.get('success', False):
                    response = await self._generate_success_response(action, result.get('data'), parameters)
                    state = ConversationState.COMPLETED
                    action_taken = action
                    suggestions = await self._generate_follow_up_suggestions(action, result.get('data'))
                else:
                    response = await self._generate_error_response(action, result.get('error', 'Unknown error'))
                    state = ConversationState.ERROR
                    action_taken = "error"
                    suggestions = ["Try again", "Start over", "Ask for help"]
                
                # Clear pending action and reset state
                await self.conversation_service.clear_pending_action(conv_context.session_id)
                
                # Add conversation turn
                await self.conversation_service.add_conversation_turn(
                    conv_context.session_id,
                    message,
                    response,
                    state,
                    action_taken=action_taken,
                    data=result.get('data')
                )
                
                return {
                    "response": response,
                    "action_taken": action_taken,
                    "data": result.get('data'),
                    "suggestions": suggestions,
                    "conversation_state": state.value
                }
            
            elif is_negative:
                # User cancelled
                await self.conversation_service.clear_pending_action(conv_context.session_id)
                
                response = "Okay, I've cancelled that action. What else can I help you with?"
                
                await self.conversation_service.add_conversation_turn(
                    conv_context.session_id,
                    message,
                    response,
                    ConversationState.ANALYZING,
                    action_taken="cancelled"
                )
                
                return {
                    "response": response,
                    "action_taken": "cancelled",
                    "data": None,
                    "suggestions": ["Show me my campaigns", "Create a new prospect", "What are my analytics?"],
                    "conversation_state": "analyzing"
                }
            
            elif is_modification:
                # User wants to make changes - go back to gathering info
                await self.conversation_service.update_conversation_state(conv_context.session_id, ConversationState.GATHERING_INFO)
                
                response = f"Sure! What would you like to change about this {action.replace('_', ' ')}? Please tell me the new details."
                
                await self.conversation_service.add_conversation_turn(
                    conv_context.session_id,
                    message,
                    response,
                    ConversationState.GATHERING_INFO,
                    action_taken="requesting_changes"
                )
                
                return {
                    "response": response,
                    "action_taken": "requesting_changes",
                    "data": {"current_parameters": parameters},
                    "suggestions": ["Cancel this action"],
                    "conversation_state": "gathering_info"
                }
            
            else:
                # Unclear response - ask for clarification
                response = "I'm not sure if you want to proceed or not. Please say 'yes' to confirm and execute the action, 'no' to cancel, or 'change' to modify the details."
                
                await self.conversation_service.add_conversation_turn(
                    conv_context.session_id,
                    message,
                    response,
                    ConversationState.CONFIRMING,
                    action_taken="clarification_needed"
                )
                
                return {
                    "response": response,
                    "action_taken": "clarification_needed",
                    "data": {"pending_action": pending_action},
                    "suggestions": ["Yes, proceed", "No, cancel", "Make changes"],
                    "conversation_state": "confirming"
                }
                
        except Exception as e:
            logger.error(f"Error in confirming state: {e}")
            await self.conversation_service.clear_pending_action(conv_context.session_id)
            return {
                "response": f"I had trouble processing your confirmation: {str(e)}. Let's start over - what would you like to do?",
                "action_taken": "error",
                "data": None,
                "suggestions": ["Try a different request"],
                "conversation_state": "analyzing"
            }
    
    async def _handle_executing_state(self, message: str, conv_context) -> Dict[str, Any]:
        """Handle message when executing action"""
        # In this state, we're already executing, so this should be rare
        # But we can handle follow-up questions or new requests
        await self.conversation_service.clear_pending_action(conv_context.session_id)
        
        return {
            "response": "I'm currently processing your previous request. Once it's complete, I'll be ready to help with your next task. What would you like to do next?",
            "action_taken": "processing",
            "data": None,
            "suggestions": ["Show me my campaigns", "Create a new prospect", "What are my analytics?"],
            "conversation_state": "analyzing"
        }
    
    async def _handle_completed_or_error_state(self, message: str, conv_context) -> Dict[str, Any]:
        """Handle message when in completed or error state"""
        # Reset to analyzing state and process the new message
        await self.conversation_service.clear_pending_action(conv_context.session_id)
        return await self._handle_analyzing_state(message, conv_context)
    
    async def _analyze_user_intent(self, message: str) -> Dict[str, Any]:
        """Analyze user intent using enhanced pattern matching"""
        try:
            # Use existing fallback logic as it's quite comprehensive
            from app.services.ai_agent_service import ai_agent_service
            return await ai_agent_service.fallback_intent_extraction(message)
            
        except Exception as e:
            logger.error(f"Error analyzing intent: {e}")
            return {
                "action": "help",
                "entity": "general",
                "operation": "help",
                "parameters": {},
                "confidence": 0.3,
                "requires_clarification": True
            }
    
    def _extract_parameters_from_message(self, message: str, action: str) -> Dict[str, Any]:
        """Extract parameters from message based on action type"""
        try:
            # Use existing extraction methods
            from app.services.ai_agent_service import ai_agent_service
            
            if 'campaign' in action:
                return ai_agent_service.extract_campaign_params(message)
            elif 'prospect' in action:
                return ai_agent_service.extract_prospect_params(message)
            elif 'template' in action:
                return ai_agent_service.extract_template_params(message)
            elif 'list' in action:
                return ai_agent_service.extract_list_params(message)
            else:
                # Generic parameter extraction
                params = {}
                
                # Extract common patterns
                patterns = {
                    'name': r'(?:name|called|named)\s+["\']?([^"\']+)["\']?',
                    'email': r'\b([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b',
                    'id': r'\b([a-f0-9\-]{36})\b',  # UUID pattern
                    'company': r'(?:from|at|company)\s+([A-Z][A-Za-z\s&\.]+)',
                }
                
                for param, pattern in patterns.items():
                    match = re.search(pattern, message, re.IGNORECASE)
                    if match:
                        params[param] = match.group(1).strip()
                
                return params
                
        except Exception as e:
            logger.error(f"Error extracting parameters: {e}")
            return {}
    
    async def _generate_info_gathering_response(self, action: str, missing_params: List[str], current_params: Dict[str, Any]) -> str:
        """Generate response for gathering missing information"""
        try:
            questions = self.endpoint_service.get_parameter_questions(action, missing_params)
            
            # Create friendly response
            action_display = action.replace('_', ' ').title()
            
            if len(missing_params) == 1:
                param = missing_params[0]
                question = questions.get(param, f"What should be the {param.replace('_', ' ')}?")
                return f"I'd like to help you {action_display.lower()}. {question}"
            
            else:
                response = f"I'd like to help you {action_display.lower()}. I need a few more details:\n\n"
                for i, param in enumerate(missing_params[:3], 1):  # Limit to 3 questions at once
                    question = questions.get(param, f"What should be the {param.replace('_', ' ')}?")
                    response += f"{i}. {question}\n"
                
                if len(missing_params) > 3:
                    response += f"\n(I'll ask about the remaining {len(missing_params) - 3} details after these)"
                
                response += "\nYou can provide all the information in one message or answer one question at a time."
                return response
                
        except Exception as e:
            logger.error(f"Error generating info gathering response: {e}")
            return f"I need some more information to {action.replace('_', ' ')}. Could you provide the missing details?"
    
    async def _generate_confirmation_message(self, action: str, parameters: Dict[str, Any], endpoint_mapping) -> str:
        """Generate confirmation message"""
        try:
            base_message = self.endpoint_service.generate_confirmation_message(action, parameters)
            
            # Add technical details
            technical_info = f"\n\n📋 **Technical Details:**\n"
            technical_info += f"• Endpoint: {endpoint_mapping.method} {endpoint_mapping.endpoint}\n"
            
            # Show parameters that will be used
            param_display = []
            for key, value in parameters.items():
                if isinstance(value, str) and len(value) > 50:
                    value = value[:47] + "..."
                param_display.append(f"  - {key}: {value}")
            
            if param_display:
                technical_info += f"• Parameters:\n" + "\n".join(param_display)
            
            return base_message + technical_info
            
        except Exception as e:
            logger.error(f"Error generating confirmation message: {e}")
            return f"I'm ready to {action.replace('_', ' ')} with the provided information. Should I proceed?"
    
    async def _generate_success_response(self, action: str, data: Any, parameters: Dict[str, Any]) -> str:
        """Generate success response after action execution"""
        try:
            # Use existing response generation logic
            from app.services.ai_agent_service import ai_agent_service
            
            # Create mock intent analysis for the response generator
            intent_analysis = {"action": action}
            action_result = {"success": True, "data": data}
            
            return await ai_agent_service.generate_response(intent_analysis, action_result)
            
        except Exception as e:
            logger.error(f"Error generating success response: {e}")
            return f"✅ Successfully completed {action.replace('_', ' ')}! Is there anything else I can help you with?"
    
    async def _generate_error_response(self, action: str, error: str) -> str:
        """Generate error response after failed action execution"""
        return f"❌ I wasn't able to {action.replace('_', ' ')} due to an error: {error}\n\nWould you like to try again or do something else?"
    
    async def _generate_follow_up_suggestions(self, action: str, data: Any) -> List[str]:
        """Generate follow-up suggestions after successful action"""
        try:
            # Use existing suggestion generation logic
            from app.services.ai_agent_service import ai_agent_service
            
            intent_analysis = {"action": action}
            action_result = {"success": True, "data": data}
            
            return await ai_agent_service.generate_suggestions(intent_analysis, action_result)
            
        except Exception as e:
            logger.error(f"Error generating follow-up suggestions: {e}")
            return ["What else can I help you with?", "Show me my dashboard", "Create something new"]
    
    async def get_agent_capabilities(self) -> Dict[str, Any]:
        """Get enhanced agent capabilities"""
        base_capabilities = {
            "conversation_flow": {
                "description": "Multi-turn conversation with explicit confirmation",
                "states": ["analyzing", "gathering_info", "confirming", "executing", "completed", "error"],
                "features": ["Parameter validation", "Information gathering", "User confirmation", "Context retention"]
            },
            "context_management": {
                "description": "Enhanced conversation context with configurable turn limits",
                "features": ["Regex-based analysis", "State persistence", "Turn history", "Context variables"]
            }
        }
        
        # Get endpoint capabilities
        endpoint_capabilities = {}
        for action, mapping in self.endpoint_service.endpoint_mappings.items():
            entity = action.split('_')[-1] if '_' in action else action
            if entity not in endpoint_capabilities:
                endpoint_capabilities[entity] = {
                    "actions": [],
                    "description": f"{entity.title()} management operations"
                }
            endpoint_capabilities[entity]["actions"].append(action.split('_')[0])
        
        return {**base_capabilities, **endpoint_capabilities}

# Global instance
enhanced_ai_agent_service = EnhancedAIAgentService()