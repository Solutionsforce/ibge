"""
Facebook Pixel API Integration for IBGE Registration System
Tracks conversion events and user interactions throughout the registration process
"""

import requests
import json
import logging
import hashlib
import time
from datetime import datetime
from typing import Dict, Any, Optional

class FacebookPixelTracker:
    """Facebook Pixel API integration for event tracking"""
    
    def __init__(self):
        self.pixel_id = "991515346327020"
        self.access_token = "EAAM7ZAnqyWNcBPJVc15lCvaY1jzpM7tfuVY2gsIA5Ual8VZBeVehxQGnRcFCiHl5BL6wLM3VhcZCZBtigvf39ITPVNvVF4ZApUNLB0YZBnxQKZBZBWLidlbkWiFYvfF6ZC3b0zQsfQKaOhSVEZCRZBuSXM3OFWjpdISv8NVkZBtwWTUKZBPy7AwNyWhfkUIQl34dkvQZDZD"
        self.api_version = "v21.0"
        self.base_url = f"https://graph.facebook.com/{self.api_version}/{self.pixel_id}/events"
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def _hash_data(self, data: str) -> str:
        """Hash sensitive data for Facebook Pixel compliance"""
        return hashlib.sha256(data.lower().strip().encode()).hexdigest()
    
    def _prepare_user_data(self, user_info: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare and hash user data for Facebook Pixel"""
        user_data = {}
        
        if user_info.get('email'):
            user_data['em'] = self._hash_data(user_info['email'])
        
        if user_info.get('phone'):
            # Remove formatting from phone number
            phone_clean = ''.join(filter(str.isdigit, user_info['phone']))
            if phone_clean.startswith('55'):  # Brazil country code
                user_data['ph'] = self._hash_data(phone_clean)
        
        if user_info.get('nome_completo'):
            names = user_info['nome_completo'].split()
            if names:
                user_data['fn'] = self._hash_data(names[0])
                if len(names) > 1:
                    user_data['ln'] = self._hash_data(names[-1])
        
        if user_info.get('cidade'):
            user_data['ct'] = self._hash_data(user_info['cidade'])
        
        if user_info.get('uf'):
            user_data['st'] = self._hash_data(user_info['uf'])
        
        # Always include country for Brazilian users
        user_data['country'] = self._hash_data('br')
        
        return user_data
    
    def _send_event(self, event_name: str, event_data: Dict[str, Any], user_data: Optional[Dict[str, Any]] = None) -> bool:
        """Send event to Facebook Pixel API"""
        try:
            event_time = int(time.time())
            
            event_payload = {
                "event_name": event_name,
                "event_time": event_time,
                "action_source": "website",
                "event_source_url": "https://gov.ibge-inscricao.org",
                "custom_data": event_data
            }
            
            if user_data:
                event_payload["user_data"] = user_data
            
            payload = {
                "data": [event_payload],
                "access_token": self.access_token
            }
            
            response = requests.post(
                self.base_url,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                self.logger.info(f"✅ Facebook Pixel: {event_name} event sent successfully")
                return True
            else:
                self.logger.error(f"❌ Facebook Pixel error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Facebook Pixel exception: {str(e)}")
            return False
    
    def track_page_view(self, page_name: str, user_info: Optional[Dict[str, Any]] = None) -> bool:
        """Track page view events"""
        event_data = {
            "content_name": f"IBGE Registration - {page_name}",
            "content_category": "Government Registration"
        }
        
        user_data = self._prepare_user_data(user_info) if user_info else {}
        return self._send_event("PageView", event_data, user_data)
    
    def track_registration_start(self, user_info: Dict[str, Any]) -> bool:
        """Track when user starts registration process"""
        event_data = {
            "content_name": "IBGE Registration Start",
            "content_category": "Government Registration",
            "value": 64.90,
            "currency": "BRL"
        }
        
        user_data = self._prepare_user_data(user_info)
        return self._send_event("InitiateCheckout", event_data, user_data)
    
    def track_form_completion(self, step: str, user_info: Dict[str, Any]) -> bool:
        """Track form step completion"""
        event_data = {
            "content_name": f"IBGE Registration - {step} Completed",
            "content_category": "Government Registration Form",
            "status": "completed"
        }
        
        user_data = self._prepare_user_data(user_info)
        return self._send_event("CompleteRegistration", event_data, user_data)
    
    def track_pix_generation(self, user_info: Dict[str, Any], transaction_id: str) -> bool:
        """Track PIX payment generation"""
        event_data = {
            "content_name": "IBGE Registration PIX Generated",
            "content_category": "Government Payment",
            "value": 64.90,
            "currency": "BRL",
            "transaction_id": transaction_id,
            "payment_method": "PIX"
        }
        
        user_data = self._prepare_user_data(user_info)
        return self._send_event("AddPaymentInfo", event_data, user_data)
    
    def track_payment_success(self, user_info: Dict[str, Any], transaction_id: str) -> bool:
        """Track successful payment"""
        event_data = {
            "content_name": "IBGE Registration Payment Success",
            "content_category": "Government Payment",
            "value": 64.90,
            "currency": "BRL",
            "transaction_id": transaction_id,
            "payment_method": "PIX"
        }
        
        user_data = self._prepare_user_data(user_info)
        return self._send_event("Purchase", event_data, user_data)
    
    def track_lead_generation(self, user_info: Dict[str, Any], position: str) -> bool:
        """Track lead generation when user selects position"""
        event_data = {
            "content_name": f"IBGE Registration Lead - {position}",
            "content_category": "Government Job Application",
            "lead_type": "job_application",
            "position": position
        }
        
        user_data = self._prepare_user_data(user_info)
        return self._send_event("Lead", event_data, user_data)
    
    def track_custom_event(self, event_name: str, user_info: Dict[str, Any], custom_data: Optional[Dict[str, Any]] = None) -> bool:
        """Track custom events"""
        event_data = {
            "content_name": f"IBGE Registration - {event_name}",
            "content_category": "Government Registration",
            **(custom_data or {})
        }
        
        user_data = self._prepare_user_data(user_info)
        return self._send_event(event_name, event_data, user_data)

# Global instance
facebook_pixel = FacebookPixelTracker()