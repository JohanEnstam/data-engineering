"""
API Token Manager
Manages API requests and tracks usage to avoid exceeding limits
"""
import os
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APITokenManager:
    """Manages API tokens and tracks usage to prevent exceeding limits"""
    
    def __init__(self, usage_file: str = "data/api_usage.json"):
        self.usage_file = usage_file
        self.usage_data = self._load_usage_data()
        
        # API limits (from Trafiklab documentation)
        self.api_limits = {
            'gtfs_sweden_3_static': {
                'bronze': 50,
                'silver': 250,
                'gold': 1000,
                'period': 'month'
            },
            'gtfs_sweden_3_realtime': {
                'bronze': 30000,
                'silver': 2000000,
                'gold': 22500000,
                'period': 'month'
            }
        }
    
    def _load_usage_data(self) -> Dict:
        """Load usage data from file"""
        try:
            if os.path.exists(self.usage_file):
                with open(self.usage_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load usage data: {e}")
        
        # Default structure
        return {
            'last_updated': datetime.now().isoformat(),
            'api_usage': {
                'gtfs_sweden_3_static': {
                    'requests_this_month': 0,
                    'last_request': None,
                    'month_start': datetime.now().replace(day=1).isoformat()
                },
                'gtfs_sweden_3_realtime': {
                    'requests_this_month': 0,
                    'last_request': None,
                    'month_start': datetime.now().replace(day=1).isoformat()
                }
            },
            'request_history': []
        }
    
    def _save_usage_data(self):
        """Save usage data to file"""
        try:
            os.makedirs(os.path.dirname(self.usage_file), exist_ok=True)
            self.usage_data['last_updated'] = datetime.now().isoformat()
            
            with open(self.usage_file, 'w') as f:
                json.dump(self.usage_data, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save usage data: {e}")
    
    def _reset_monthly_usage(self, api_type: str):
        """Reset monthly usage if new month has started"""
        usage = self.usage_data['api_usage'].get(api_type, {})
        month_start = usage.get('month_start')
        
        if month_start:
            month_start_date = datetime.fromisoformat(month_start)
            current_month_start = datetime.now().replace(day=1)
            
            if current_month_start > month_start_date:
                # New month, reset counters
                self.usage_data['api_usage'][api_type] = {
                    'requests_this_month': 0,
                    'last_request': None,
                    'month_start': current_month_start.isoformat()
                }
                logger.info(f"Reset monthly usage for {api_type}")
    
    def can_make_request(self, api_type: str, api_level: str = 'bronze') -> bool:
        """
        Check if we can make a request without exceeding limits
        
        Args:
            api_type: Type of API (gtfs_sweden_3_static, gtfs_sweden_3_realtime)
            api_level: API level (bronze, silver, gold)
        
        Returns:
            bool: True if request can be made
        """
        self._reset_monthly_usage(api_type)
        
        usage = self.usage_data['api_usage'].get(api_type, {})
        current_usage = usage.get('requests_this_month', 0)
        limit = self.api_limits.get(api_type, {}).get(api_level, 0)
        
        if current_usage >= limit:
            logger.warning(f"API limit reached for {api_type}: {current_usage}/{limit}")
            return False
        
        remaining = limit - current_usage
        logger.info(f"API usage for {api_type}: {current_usage}/{limit} (remaining: {remaining})")
        return True
    
    def record_request(self, api_type: str, endpoint: str, success: bool, response_size: int = 0):
        """
        Record an API request
        
        Args:
            api_type: Type of API
            endpoint: API endpoint
            success: Whether request was successful
            response_size: Size of response in bytes
        """
        self._reset_monthly_usage(api_type)
        
        # Update usage counter
        if api_type not in self.usage_data['api_usage']:
            self.usage_data['api_usage'][api_type] = {
                'requests_this_month': 0,
                'last_request': None,
                'month_start': datetime.now().replace(day=1).isoformat()
            }
        
        self.usage_data['api_usage'][api_type]['requests_this_month'] += 1
        self.usage_data['api_usage'][api_type]['last_request'] = datetime.now().isoformat()
        
        # Record in history
        request_record = {
            'timestamp': datetime.now().isoformat(),
            'api_type': api_type,
            'endpoint': endpoint,
            'success': success,
            'response_size': response_size
        }
        
        self.usage_data['request_history'].append(request_record)
        
        # Keep only last 1000 requests in history
        if len(self.usage_data['request_history']) > 1000:
            self.usage_data['request_history'] = self.usage_data['request_history'][-1000:]
        
        self._save_usage_data()
        
        logger.info(f"Recorded {api_type} request: {endpoint} ({'success' if success else 'failed'})")
    
    def get_usage_summary(self) -> Dict:
        """Get current usage summary"""
        summary = {
            'timestamp': datetime.now().isoformat(),
            'api_usage': {},
            'warnings': []
        }
        
        for api_type, usage in self.usage_data['api_usage'].items():
            current_usage = usage.get('requests_this_month', 0)
            limit = self.api_limits.get(api_type, {}).get('bronze', 0)
            percentage = (current_usage / limit * 100) if limit > 0 else 0
            
            summary['api_usage'][api_type] = {
                'current_usage': current_usage,
                'limit': limit,
                'remaining': limit - current_usage,
                'percentage_used': round(percentage, 1),
                'last_request': usage.get('last_request')
            }
            
            # Add warnings
            if percentage >= 80:
                summary['warnings'].append(f"{api_type}: {percentage}% of limit used")
            elif percentage >= 100:
                summary['warnings'].append(f"{api_type}: LIMIT EXCEEDED!")
        
        return summary
    
    def print_usage_summary(self):
        """Print usage summary to console"""
        summary = self.get_usage_summary()
        
        print("\n" + "="*60)
        print("📊 API USAGE SUMMARY")
        print("="*60)
        
        for api_type, usage in summary['api_usage'].items():
            status = "🟢" if usage['percentage_used'] < 80 else "🟡" if usage['percentage_used'] < 100 else "🔴"
            print(f"{status} {api_type}:")
            print(f"   Usage: {usage['current_usage']}/{usage['limit']} ({usage['percentage_used']}%)")
            print(f"   Remaining: {usage['remaining']}")
            if usage['last_request']:
                print(f"   Last request: {usage['last_request']}")
            print()
        
        if summary['warnings']:
            print("⚠️  WARNINGS:")
            for warning in summary['warnings']:
                print(f"   • {warning}")
            print()
        
        print(f"📄 Usage data saved to: {self.usage_file}")
        print("="*60)

# Global instance
token_manager = APITokenManager()

if __name__ == "__main__":
    # Test the token manager
    token_manager.print_usage_summary()
