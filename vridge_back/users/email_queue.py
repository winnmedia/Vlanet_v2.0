import os
import time
import threading
import uuid
import json
from queue import Queue, Empty, PriorityQueue
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.cache import cache
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

#   
try:
    from .email_monitor import email_monitor, EmailDeliveryStatus
except ImportError:
    email_monitor = None
    EmailDeliveryStatus = None
    logger.warning("Email monitor not available")

class EmailQueueManager:
    """     (Redis    )"""
    
    def __init__(self):
        self.queue = PriorityQueue()  #   
        self.worker_thread = None
        self.is_running = False
        self.retry_queue = Queue()
        self.max_retries = 3
        self.retry_delay = 30  # 30  
        self.batch_size = 10  #   
        self.batch_timeout = 5  # 5 
        self.pending_batch = []
        self.last_batch_time = time.time()
        
        # Redis  
        self.cache_prefix = 'email_queue:'
        self.cache_ttl = 3600  # 1
        
    def start(self):
        """  """
        if not self.is_running:
            self.is_running = True
            self.worker_thread = threading.Thread(target=self._process_emails, daemon=True)
            self.worker_thread.start()
            
            # Redis   
            self._recover_pending_emails()
            
            logger.info("[EmailQueue] Email queue manager started with Redis caching")
    
    def stop(self):
        """  """
        self.is_running = False
        
        #   
        if self.pending_batch:
            self._process_batch(self.pending_batch)
            
        if self.worker_thread:
            self.worker_thread.join(timeout=5)
            logger.info("[EmailQueue] Email queue manager stopped")
    
    def add_email(self, subject, body, recipient_list, html_message=None, priority=5, email_type='general'):
        """   (Redis  )"""
        email_id = str(uuid.uuid4())
        email_data = {
            'id': email_id,
            'subject': subject,
            'body': body,
            'recipient_list': recipient_list,
            'html_message': html_message,
            'priority': priority,
            'type': email_type,
            'retry_count': 0,
            'created_at': timezone.now().isoformat()
        }
        
        # Redis 
        cache_key = f"{self.cache_prefix}{email_id}"
        cache.set(cache_key, json.dumps(email_data), self.cache_ttl)
        
        #  
        if email_monitor:
            email_monitor.record_email_sent(
                email_id, 
                recipient_list[0] if recipient_list else 'unknown',
                subject,
                email_type
            )
        
        #    (   )
        self.queue.put((priority, email_id))
        
        logger.info(f"[EmailQueue] Email added to queue: {subject} to {recipient_list} (ID: {email_id})")
        return email_id
    
    def add_bulk_emails(self, email_list):
        """   """
        email_ids = []
        
        for email_data in email_list:
            email_id = self.add_email(
                subject=email_data.get('subject'),
                body=email_data.get('body'),
                recipient_list=email_data.get('recipient_list'),
                html_message=email_data.get('html_message'),
                priority=email_data.get('priority', 5),
                email_type=email_data.get('type', 'bulk')
            )
            email_ids.append(email_id)
            
        logger.info(f"[EmailQueue] Added {len(email_ids)} emails to queue for bulk processing")
        return email_ids
    
    def get_email_status(self, email_id):
        """  """
        if email_monitor:
            return email_monitor.get_email_status(email_id)
        
        # : Redis  
        cache_key = f"{self.cache_prefix}{email_id}"
        data = cache.get(cache_key)
        if data:
            return json.loads(data) if isinstance(data, str) else data
        return None
    
    def _recover_pending_emails(self):
        """Redis   """
        pattern = f"{self.cache_prefix}*"
        try:
            # Django      
            if hasattr(cache, 'keys'):
                keys = cache.keys(pattern)
                recovered = 0
                
                for key in keys:
                    data = cache.get(key)
                    if data:
                        email_data = json.loads(data) if isinstance(data, str) else data
                        if email_data.get('status') in [None, EmailDeliveryStatus.PENDING, EmailDeliveryStatus.RETRYING]:
                            email_id = email_data['id']
                            priority = email_data.get('priority', 5)
                            self.queue.put((priority, email_id))
                            recovered += 1
                            
                if recovered > 0:
                    logger.info(f"[EmailQueue] Recovered {recovered} pending emails from Redis")
        except Exception as e:
            logger.warning(f"[EmailQueue] Could not recover pending emails: {str(e)}")
    
    def _process_emails(self):
        """    (  )"""
        while self.is_running:
            try:
                #   
                self._process_retry_queue()
                
                #   
                if self.pending_batch and (time.time() - self.last_batch_time) >= self.batch_timeout:
                    self._process_batch(self.pending_batch)
                    self.pending_batch = []
                
                #   
                try:
                    priority, email_id = self.queue.get(timeout=1)
                    
                    # Redis   
                    cache_key = f"{self.cache_prefix}{email_id}"
                    data = cache.get(cache_key)
                    
                    if not data:
                        logger.warning(f"[EmailQueue] Email data not found in cache: {email_id}")
                        continue
                        
                    email_data = json.loads(data) if isinstance(data, str) else data
                    
                    #    
                    if email_data.get('type') == 'bulk' and len(self.pending_batch) < self.batch_size:
                        self.pending_batch.append(email_data)
                        self.last_batch_time = time.time()
                        
                        #     
                        if len(self.pending_batch) >= self.batch_size:
                            self._process_batch(self.pending_batch)
                            self.pending_batch = []
                    else:
                        #    
                        self._send_email(email_data)
                        
                except Empty:
                    continue
                    
            except Exception as e:
                logger.error(f"[EmailQueue] Error in worker thread: {str(e)}")
                time.sleep(1)
    
    def _process_batch(self, batch):
        """  """
        if not batch:
            return
            
        logger.info(f"[EmailQueue] Processing batch of {len(batch)} emails")
        
        #  
        grouped = {}
        for email_data in batch:
            key = (email_data['subject'], email_data['body'], email_data.get('html_message'))
            if key not in grouped:
                grouped[key] = []
            grouped[key].extend(email_data['recipient_list'])
        
        #  
        for (subject, body, html_message), recipients in grouped.items():
            try:
                #  
                unique_recipients = list(set(recipients))
                
                # BCC  
                email = EmailMultiAlternatives(
                    subject=subject,
                    body=body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[settings.DEFAULT_FROM_EMAIL],  # To 
                    bcc=unique_recipients  # BCC  
                )
                
                if html_message:
                    email.attach_alternative(html_message, "text/html")
                
                result = email.send(fail_silently=False)
                
                #    
                for email_data in batch:
                    if email_data['subject'] == subject:
                        if email_monitor:
                            email_monitor.update_email_status(
                                email_data['id'], 
                                EmailDeliveryStatus.DELIVERED
                            )
                        # Redis 
                        cache.delete(f"{self.cache_prefix}{email_data['id']}")
                
                logger.info(f"[EmailQueue] Batch sent successfully: {subject} to {len(unique_recipients)} recipients")
                
            except Exception as e:
                logger.error(f"[EmailQueue] Batch send failed: {str(e)}")
                #    
                for email_data in batch:
                    if email_data['subject'] == subject:
                        email_data['retry_count'] += 1
                        if email_data['retry_count'] < self.max_retries:
                            retry_time = timezone.now() + timezone.timedelta(seconds=self.retry_delay * email_data['retry_count'])
                            self.retry_queue.put((retry_time, email_data))
    
    def _process_retry_queue(self):
        """  """
        retry_items = []
        
        #    
        while not self.retry_queue.empty():
            try:
                retry_time, email_data = self.retry_queue.get_nowait()
                if timezone.now() >= retry_time:
                    self._send_email(email_data)
                else:
                    retry_items.append((retry_time, email_data))
            except Empty:
                break
        
        #         
        for item in retry_items:
            self.retry_queue.put(item)
    
    def _send_email(self, email_data):
        """  """
        try:
            #    
            if email_monitor:
                email_monitor.update_email_status(
                    email_data['id'], 
                    EmailDeliveryStatus.SENT
                )
            
            logger.info(f"[EmailQueue] Sending email: {email_data['subject']} to {email_data['recipient_list']}")
            
            email = EmailMultiAlternatives(
                subject=email_data['subject'],
                body=email_data['body'],
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=email_data['recipient_list']
            )
            
            if email_data.get('html_message'):
                email.attach_alternative(email_data['html_message'], "text/html")
            
            #  
            result = email.send(fail_silently=False)
            
            #   
            if email_monitor:
                email_monitor.update_email_status(
                    email_data['id'], 
                    EmailDeliveryStatus.DELIVERED
                )
            
            # Redis 
            cache.delete(f"{self.cache_prefix}{email_data['id']}")
            
            email_backend = 'SendGrid' if os.environ.get('SENDGRID_API_KEY') else 'Gmail'
            logger.info(f"[EmailQueue] Email sent successfully via {email_backend}: {email_data['subject']}")
            
        except Exception as e:
            logger.error(f"[EmailQueue] Failed to send email: {str(e)}")
            
            #   
            if email_monitor:
                email_monitor.update_email_status(
                    email_data['id'], 
                    EmailDeliveryStatus.FAILED if email_data['retry_count'] >= self.max_retries else EmailDeliveryStatus.RETRYING,
                    error=str(e)
                )
            
            #  
            email_data['retry_count'] += 1
            if email_data['retry_count'] < self.max_retries:
                retry_time = timezone.now() + timezone.timedelta(seconds=self.retry_delay * email_data['retry_count'])
                self.retry_queue.put((retry_time, email_data))
                
                # Redis 
                cache.set(f"{self.cache_prefix}{email_data['id']}", json.dumps(email_data), self.cache_ttl)
                
                logger.info(f"[EmailQueue] Email queued for retry {email_data['retry_count']}/{self.max_retries}")
            else:
                logger.error(f"[EmailQueue] Email failed after {self.max_retries} retries: {email_data['subject']}")

#  
email_queue_manager = EmailQueueManager()

# Django      
def start_email_queue():
    email_queue_manager.start()

# Django      
def stop_email_queue():
    email_queue_manager.stop()