# AI Prospecting Service with Groq AI and Apollo.io Integration
import asyncio
import httpx
import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from groq import Groq
import os
import logging
from urllib.parse import quote

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIProspectingService:
    def __init__(self):
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.apollo_api_key = "01fe975866msh9ba2aba2d44e55ap193b18jsnad0c05952c37"
        self.apollo_base_url = "https://apollo-io-no-cookies-required.p.rapidapi.com/search_people_via_url"
        
        # Industry to Tag ID mapping - will be populated from database
        self.industry_tags = {}
        
    async def initialize_industry_tags(self, db_service):
        """Initialize industry tags from database"""
        try:
            await db_service.connect()
            # Get industry tags from database
            industry_tags = await db_service.get_industry_tags()
            self.industry_tags = {tag['industry'].lower(): tag['tag_id'] for tag in industry_tags}
            logger.info(f"Initialized {len(self.industry_tags)} industry tags")
        except Exception as e:
            logger.error(f"Error initializing industry tags: {e}")
            # Fallback to default tags
            self.industry_tags = {
                'accounting': '5567ce1f7369643b78570000',
                'agriculture': '55718f947369642142b84a12',
                'airlines': '5567e0bf7369641d115f0200',
                'aviation': '5567e0bf7369641d115f0200',
                'technology': '5567ce1f7369643b78570000',
                'software': '55718f947369642142b84a12',
                'healthcare': '5567e0bf7369641d115f0200'
            }

    async def process_natural_language_query(self, query: str, target_list: str = None) -> Dict:
        """Process natural language query using Groq AI to extract Apollo.io parameters"""
        try:
            # Create system prompt for parameter extraction
            system_prompt = """You are an AI assistant that extracts prospect search parameters from natural language queries for Apollo.io searches.

Extract the following parameters from the user query:
- personTitles: Job titles to include (e.g., "CEO", "Manager", "Director")
- personNotTitles: Job titles to exclude (e.g., "Manager")
- personLocations: Geographic locations (e.g., "California, US", "New York, US")
- personNotLocations: Locations to exclude (e.g., "Montana, US")
- organizationNumEmployeesRanges: Company size range (e.g., "5,200" for 5-200 employees)
- organizationIndustryTagIds: Industry keywords that need to be mapped to tag IDs
- contactEmailStatusV2: Email status (default to "verified")
- includeSimilarTitles: boolean (default false)

Respond in JSON format with extracted parameters. If information is missing or unclear, include a "missing_info" field with questions to ask the user.

Example:
{
  "personTitles": ["CEO", "Founder"],
  "personLocations": ["California, US", "New York, US"],
  "organizationIndustryTagIds": ["technology", "software"],
  "organizationNumEmployeesRanges": "10,500",
  "contactEmailStatusV2": ["verified"],
  "includeSimilarTitles": false,
  "missing_info": ["What company size range are you looking for?"]
}"""

            # Call Groq API
            response = self.groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Extract prospect parameters from: {query}"}
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.1,
                max_tokens=1000
            )
            
            # Parse response
            result_text = response.choices[0].message.content
            logger.info(f"Groq response: {result_text}")
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                extracted_params = json.loads(json_match.group())
                
                # Add target list if provided
                if target_list:
                    extracted_params['target_list'] = target_list
                
                return {
                    "success": True,
                    "parameters": extracted_params,
                    "needs_clarification": "missing_info" in extracted_params and len(extracted_params.get("missing_info", [])) > 0
                }
            else:
                return {
                    "success": False,
                    "error": "Could not parse AI response",
                    "raw_response": result_text
                }
                
        except Exception as e:
            logger.error(f"Error processing natural language query: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def map_industries_to_tags(self, industry_keywords: List[str]) -> List[str]:
        """Map industry keywords to Apollo.io tag IDs"""
        tag_ids = []
        
        for keyword in industry_keywords:
            keyword_lower = keyword.lower()
            
            # Direct match
            if keyword_lower in self.industry_tags:
                tag_ids.append(self.industry_tags[keyword_lower])
                continue
            
            # Partial match
            for industry, tag_id in self.industry_tags.items():
                if keyword_lower in industry or industry in keyword_lower:
                    tag_ids.append(tag_id)
                    break
        
        return list(set(tag_ids))  # Remove duplicates

    def build_apollo_search_url(self, parameters: Dict) -> str:
        """Build Apollo.io search URL from extracted parameters"""
        base_url = "https://app.apollo.io/#/people"
        params = []
        
        # Add sorting parameters
        params.append("sortAscending=false")
        params.append("sortByField=recommendations_score")
        
        # Add person titles
        if 'personTitles' in parameters and parameters['personTitles']:
            for title in parameters['personTitles']:
                params.append(f"personTitles[]={quote(title)}")
        
        # Include similar titles
        include_similar = parameters.get('includeSimilarTitles', False)
        params.append(f"includeSimilarTitles={str(include_similar).lower()}")
        
        # Add person not titles
        if 'personNotTitles' in parameters and parameters['personNotTitles']:
            for title in parameters['personNotTitles']:
                params.append(f"personNotTitles[]={quote(title)}")
        
        # Add person locations
        if 'personLocations' in parameters and parameters['personLocations']:
            for location in parameters['personLocations']:
                params.append(f"personLocations[]={quote(location)}")
        
        # Add person not locations
        if 'personNotLocations' in parameters and parameters['personNotLocations']:
            for location in parameters['personNotLocations']:
                params.append(f"personNotLocations[]={quote(location)}")
        
        # Add organization employee ranges
        if 'organizationNumEmployeesRanges' in parameters and parameters['organizationNumEmployeesRanges']:
            employee_range = parameters['organizationNumEmployeesRanges']
            params.append(f"organizationNumEmployeesRanges[]={quote(employee_range)}")
        
        # Add organization industry tag IDs
        if 'organizationIndustryTagIds' in parameters and parameters['organizationIndustryTagIds']:
            # Map industry keywords to tag IDs
            if isinstance(parameters['organizationIndustryTagIds'][0], str):
                tag_ids = self.map_industries_to_tags(parameters['organizationIndustryTagIds'])
            else:
                tag_ids = parameters['organizationIndustryTagIds']
            
            for tag_id in tag_ids:
                params.append(f"organizationIndustryTagIds[]={tag_id}")
        
        # Add email status
        email_status = parameters.get('contactEmailStatusV2', ['verified'])
        for status in email_status:
            params.append(f"contactEmailStatusV2[]={status}")
        
        # Add page parameter
        params.append("page=1")
        
        # Construct final URL
        url = f"{base_url}?{'&'.join(params)}"
        return url

    async def search_apollo_prospects(self, search_url: str, page: int = 1) -> Dict:
        """Search for prospects using Apollo.io API"""
        try:
            headers = {
                'Content-Type': 'application/json',
                'x-rapidapi-host': 'apollo-io-no-cookies-required.p.rapidapi.com',
                'x-rapidapi-key': self.apollo_api_key
            }
            
            payload = {
                "url": search_url,
                "page": page
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.apollo_base_url,
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    return {
                        "success": True,
                        "data": response.json()
                    }
                else:
                    logger.error(f"Apollo API error: {response.status_code} - {response.text}")
                    return {
                        "success": False,
                        "error": f"Apollo API error: {response.status_code}",
                        "details": response.text
                    }
                    
        except Exception as e:
            logger.error(f"Error searching Apollo prospects: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def extract_prospect_data(self, apollo_response: Dict) -> List[Dict]:
        """Extract and format prospect data from Apollo.io response"""
        prospects = []
        
        try:
            people_data = apollo_response.get('data', {}).get('people', [])
            
            for person in people_data:
                # Extract basic information
                prospect = {
                    'apollo_id': person.get('id', ''),
                    'first_name': person.get('first_name', ''),
                    'last_name': person.get('last_name', ''),
                    'email': person.get('email', ''),
                    'title': person.get('title', ''),
                    'linkedin_url': person.get('linkedin_url', ''),
                    'photo_url': person.get('photo_url', ''),
                    'headline': person.get('headline', ''),
                    'city': person.get('city', ''),
                    'state': person.get('state', ''),
                    'country': person.get('country', ''),
                    'email_status': person.get('email_status', ''),
                    'seniority': person.get('seniority', ''),
                    'functions': person.get('functions', []),
                    'departments': person.get('departments', [])
                }
                
                # Extract organization information
                org = person.get('organization', {})
                if org:
                    prospect.update({
                        'company': org.get('name', ''),
                        'company_website': org.get('website_url', ''),
                        'company_linkedin': org.get('linkedin_url', ''),
                        'company_phone': org.get('phone', ''),
                        'company_founded_year': org.get('founded_year', ''),
                        'company_employees': org.get('publicly_traded_symbol', ''),
                        'industry': org.get('primary_domain', '')
                    })
                
                # Add metadata
                prospect.update({
                    'source': 'apollo_ai',
                    'created_at': datetime.utcnow(),
                    'status': 'active'
                })
                
                # Only add prospects with email addresses
                if prospect['email'] and prospect['email'] != 'email_not_unlocked@domain.com':
                    prospects.append(prospect)
            
            return prospects
            
        except Exception as e:
            logger.error(f"Error extracting prospect data: {e}")
            return []

    async def save_prospects_to_database(self, prospects: List[Dict], target_list: str, db_service) -> Dict:
        """Save prospects to database and add to specified list"""
        try:
            await db_service.connect()
            
            saved_prospects = []
            failed_prospects = []
            
            for prospect_data in prospects:
                try:
                    # Generate unique ID
                    from app.utils.helpers import generate_id
                    prospect_id = generate_id()
                    prospect_data['id'] = prospect_id
                    
                    # Save prospect to database
                    success, error = await db_service.create_prospect(prospect_data)
                    
                    if success:
                        saved_prospects.append(prospect_data)
                        
                        # Add to specified list if provided
                        if target_list:
                            # Check if list exists first
                            existing_list = await db_service.get_list_by_name(target_list)
                            if existing_list:
                                # Add to existing list
                                await db_service.add_prospects_to_list(existing_list['id'], [prospect_id])
                                logger.info(f"Added prospect {prospect_id} to existing list: {target_list}")
                            else:
                                # List doesn't exist - check if user wants us to create it
                                # For now, let's be conservative and NOT auto-create lists
                                # Instead, add to a default "AI Prospecting" list or leave unassigned
                                default_list_name = "AI Prospecting Results"
                                default_list = await db_service.get_list_by_name(default_list_name)
                                
                                if not default_list:
                                    # Create the default AI prospecting list only if it doesn't exist
                                    from app.utils.helpers import generate_id
                                    list_data = {
                                        'id': generate_id(),
                                        'name': default_list_name,
                                        'description': f'Prospects found through AI prospecting when target list doesn\'t exist',
                                        'color': '#9333EA',  # Purple color for AI prospecting
                                        'tags': ['ai-generated', 'default-prospecting']
                                    }
                                    await db_service.create_list(list_data)
                                    default_list = await db_service.get_list_by_name(default_list_name)
                                
                                if default_list:
                                    await db_service.add_prospects_to_list(default_list['id'], [prospect_id])
                                    logger.warning(f"Target list '{target_list}' not found. Added prospect {prospect_id} to default AI Prospecting Results list")
                                
                                # Also track this issue in failed prospects with a warning
                                failed_prospects.append({
                                    'prospect': prospect_data,
                                    'error': f"Target list '{target_list}' not found. Added to 'AI Prospecting Results' instead.",
                                    'type': 'warning'
                                })
                    else:
                        failed_prospects.append({
                            'prospect': prospect_data,
                            'error': error
                        })
                        
                except Exception as e:
                    failed_prospects.append({
                        'prospect': prospect_data,
                        'error': str(e)
                    })
            
            return {
                'success': True,
                'saved_count': len(saved_prospects),
                'failed_count': len(failed_prospects),
                'saved_prospects': saved_prospects,
                'failed_prospects': failed_prospects,
                'target_list': target_list
            }
            
        except Exception as e:
            logger.error(f"Error saving prospects to database: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def complete_ai_prospecting(self, query: str, target_list: str = None, db_service = None) -> Dict:
        """Complete AI prospecting workflow"""
        try:
            # Initialize industry tags
            await self.initialize_industry_tags(db_service)
            
            # Step 1: Process natural language query
            logger.info(f"Processing query: {query}")
            nlp_result = await self.process_natural_language_query(query, target_list)
            
            if not nlp_result['success']:
                return nlp_result
            
            # Step 2: Check if clarification is needed
            if nlp_result.get('needs_clarification', False):
                return {
                    'success': True,
                    'needs_clarification': True,
                    'questions': nlp_result['parameters'].get('missing_info', []),
                    'extracted_parameters': nlp_result['parameters']
                }
            
            # Step 3: Build Apollo.io search URL
            logger.info("Building Apollo search URL")
            search_url = self.build_apollo_search_url(nlp_result['parameters'])
            logger.info(f"Search URL: {search_url}")
            
            # Step 4: Search Apollo.io for prospects
            logger.info("Searching Apollo.io for prospects")
            apollo_result = await self.search_apollo_prospects(search_url)
            
            if not apollo_result['success']:
                return apollo_result
            
            # Step 5: Extract prospect data
            logger.info("Extracting prospect data")
            prospects = self.extract_prospect_data(apollo_result['data'])
            
            if not prospects:
                return {
                    'success': True,
                    'message': 'No prospects found matching your criteria',
                    'prospects_count': 0
                }
            
            # Step 6: Save to database and add to list
            logger.info(f"Saving {len(prospects)} prospects to database")
            save_result = await self.save_prospects_to_database(prospects, target_list, db_service)
            
            if not save_result['success']:
                return save_result
            
            return {
                'success': True,
                'message': f'Successfully found and saved {save_result["saved_count"]} prospects',
                'prospects_count': save_result['saved_count'],
                'failed_count': save_result['failed_count'],
                'search_url': search_url,
                'target_list': target_list,
                'prospects': save_result['saved_prospects'][:10]  # Return first 10 for preview
            }
            
        except Exception as e:
            logger.error(f"Error in complete AI prospecting: {e}")
            return {
                'success': False,
                'error': str(e)
            }

# Global instance
ai_prospecting_service = AIProspectingService()