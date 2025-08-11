"""
   
"""
from django.core.cache import cache
from django.utils import timezone
from django.db import models
from datetime import datetime, timedelta
import json
import logging

logger = logging.getLogger(__name__)


class EmailDeliveryStatus:
    """   """
    PENDING = 'pending'
    SENT = 'sent'
    FAILED = 'failed'
    RETRYING = 'retrying'
    DELIVERED = 'delivered'
    BOUNCED = 'bounced'


class EmailMonitor:
    """   """
    
    def __init__(self):
        self.cache_prefix = 'email_monitor:'
        self.stats_prefix = 'email_stats:'
        self.ttl = 86400 * 7  # 7 
        
    def record_email_sent(self, email_id, recipient, subject, email_type='general'):
        """  """
        key = f"{self.cache_prefix}{email_id}"
        data = {
            'id': email_id,
            'recipient': recipient,
            'subject': subject,
            'type': email_type,
            'status': EmailDeliveryStatus.PENDING,
            'created_at': timezone.now().isoformat(),
            'attempts': 1,
            'last_attempt': timezone.now().isoformat(),
            'delivered_at': None,
            'error': None
        }
        
        # Redis 
        cache.set(key, json.dumps(data), self.ttl)
        
        #  
        self._update_stats('sent', email_type)
        
        logger.info(f"  : {email_id} -> {recipient}")
        return data
    
    def update_email_status(self, email_id, status, error=None):
        """  """
        key = f"{self.cache_prefix}{email_id}"
        data = cache.get(key)
        
        if not data:
            logger.warning(f"     : {email_id}")
            return None
            
        data = json.loads(data) if isinstance(data, str) else data
        data['status'] = status
        data['last_attempt'] = timezone.now().isoformat()
        
        if status == EmailDeliveryStatus.DELIVERED:
            data['delivered_at'] = timezone.now().isoformat()
            self._update_stats('delivered', data.get('type', 'general'))
        elif status == EmailDeliveryStatus.FAILED:
            data['error'] = error
            self._update_stats('failed', data.get('type', 'general'))
        elif status == EmailDeliveryStatus.RETRYING:
            data['attempts'] = data.get('attempts', 0) + 1
            
        cache.set(key, json.dumps(data), self.ttl)
        logger.info(f"  : {email_id} -> {status}")
        return data
    
    def get_email_status(self, email_id):
        """  """
        key = f"{self.cache_prefix}{email_id}"
        data = cache.get(key)
        
        if not data:
            return None
            
        return json.loads(data) if isinstance(data, str) else data
    
    def get_recent_emails(self, limit=50, email_type=None):
        """   """
        #       (Redis ZSET )
        #   
        pattern = f"{self.cache_prefix}*"
        keys = cache.keys(pattern)
        
        emails = []
        for key in keys[-limit:]:  #  N
            data = cache.get(key)
            if data:
                email_data = json.loads(data) if isinstance(data, str) else data
                if not email_type or email_data.get('type') == email_type:
                    emails.append(email_data)
                    
        #  
        emails.sort(key=lambda x: x['created_at'], reverse=True)
        return emails[:limit]
    
    def get_statistics(self, hours=24):
        """   """
        stats = {
            'total_sent': 0,
            'total_delivered': 0,
            'total_failed': 0,
            'delivery_rate': 0,
            'by_type': {},
            'hourly': []
        }
        
        #  
        now = timezone.now()
        for i in range(hours):
            hour_key = f"{self.stats_prefix}{(now - timedelta(hours=i)).strftime('%Y%m%d%H')}"
            hour_data = cache.get(hour_key)
            if hour_data:
                hour_stats = json.loads(hour_data) if isinstance(hour_data, str) else hour_data
                stats['hourly'].append({
                    'hour': (now - timedelta(hours=i)).strftime('%Y-%m-%d %H:00'),
                    'data': hour_stats
                })
                
                #   
                stats['total_sent'] += hour_stats.get('sent', 0)
                stats['total_delivered'] += hour_stats.get('delivered', 0)
                stats['total_failed'] += hour_stats.get('failed', 0)
                
                #  
                for email_type, type_stats in hour_stats.get('by_type', {}).items():
                    if email_type not in stats['by_type']:
                        stats['by_type'][email_type] = {
                            'sent': 0,
                            'delivered': 0,
                            'failed': 0
                        }
                    stats['by_type'][email_type]['sent'] += type_stats.get('sent', 0)
                    stats['by_type'][email_type]['delivered'] += type_stats.get('delivered', 0)
                    stats['by_type'][email_type]['failed'] += type_stats.get('failed', 0)
        
        #  
        if stats['total_sent'] > 0:
            stats['delivery_rate'] = (stats['total_delivered'] / stats['total_sent']) * 100
            
        return stats
    
    def _update_stats(self, action, email_type):
        """ """
        hour_key = f"{self.stats_prefix}{timezone.now().strftime('%Y%m%d%H')}"
        stats = cache.get(hour_key)
        
        if not stats:
            stats = {
                'sent': 0,
                'delivered': 0,
                'failed': 0,
                'by_type': {}
            }
        else:
            stats = json.loads(stats) if isinstance(stats, str) else stats
            
        #   
        if action in ['sent', 'delivered', 'failed']:
            stats[action] = stats.get(action, 0) + 1
            
        #   
        if email_type not in stats['by_type']:
            stats['by_type'][email_type] = {
                'sent': 0,
                'delivered': 0,
                'failed': 0
            }
            
        if action in ['sent', 'delivered', 'failed']:
            stats['by_type'][email_type][action] = stats['by_type'][email_type].get(action, 0) + 1
            
        # 1  
        cache.set(hour_key, json.dumps(stats), 3600)
    
    def cleanup_old_records(self, days=7):
        """  """
        pattern = f"{self.cache_prefix}*"
        keys = cache.keys(pattern)
        
        cutoff_date = timezone.now() - timedelta(days=days)
        deleted_count = 0
        
        for key in keys:
            data = cache.get(key)
            if data:
                email_data = json.loads(data) if isinstance(data, str) else data
                created_at = datetime.fromisoformat(email_data['created_at'])
                
                if created_at < cutoff_date:
                    cache.delete(key)
                    deleted_count += 1
                    
        logger.info(f"{deleted_count}    ")
        return deleted_count


#   
email_monitor = EmailMonitor()