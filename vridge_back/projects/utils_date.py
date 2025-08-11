"""   """
from datetime import datetime
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


def parse_date_flexible(date_value):
    """
         timezone-aware datetime  
    
     :
    - YYYY-MM-DD HH:mm
    - YYYY-MM-DD HH:MM
    - YYYY-MM-DD
    - YYYY-MM-DDTHH:mm:ss
    - YYYY-MM-DDTHH:mm:ssZ
    - YYYY-MM-DDTHH:mm:ss.fffZ
    - ISO 8601 
    """
    if not date_value:
        return None
        
    #  datetime  
    if isinstance(date_value, datetime):
        return timezone.make_aware(date_value) if timezone.is_naive(date_value) else date_value
    
    #   
    if not isinstance(date_value, str):
        logger.warning(f"Unexpected date type: {type(date_value)}, value: {date_value}")
        return None
    
    #   
    date_str = date_value.strip()
    if not date_str or date_str.lower() == 'null':
        return None
    
    #    (  )
    date_formats = [
        "%Y-%m-%d %H:%M",      # 2025-07-01 14:30
        "%Y-%m-%d %H:%M:%S",   # 2025-07-01 14:30:00
        "%Y-%m-%d",            # 2025-07-01
        "%Y-%m-%dT%H:%M",      # 2025-07-01T14:30
        "%Y-%m-%dT%H:%M:%S",   # 2025-07-01T14:30:00
        "%Y-%m-%dT%H:%M:%SZ",  # 2025-07-01T14:30:00Z
        "%Y-%m-%dT%H:%M:%S.%fZ",  # 2025-07-01T14:30:00.000Z
    ]
    
    #    
    for fmt in date_formats:
        try:
            parsed_date = datetime.strptime(date_str, fmt)
            # timezone aware 
            return timezone.make_aware(parsed_date) if timezone.is_naive(parsed_date) else parsed_date
        except ValueError:
            continue
    
    # ISO format 
    try:
        # Z +00:00  Python    
        iso_str = date_str.replace('Z', '+00:00')
        parsed_date = datetime.fromisoformat(iso_str)
        return timezone.make_aware(parsed_date) if timezone.is_naive(parsed_date) else parsed_date
    except ValueError:
        pass
    
    # JavaScript Date.toISOString()  
    try:
        if 'T' in date_str and date_str.endswith('Z'):
            # 2025-07-01T05:30:00.000Z 
            parsed_date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
            # UTC 
            return timezone.make_aware(parsed_date, timezone=timezone.utc)
    except ValueError:
        pass
    
    #    
    logger.error(f"Unable to parse date: '{date_str}'")
    raise ValueError(f"    : {date_str}")