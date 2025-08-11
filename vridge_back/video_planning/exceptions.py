"""
     
"""

class ProposalExportError(Exception):
    """    """
    pass


class GeminiAPIError(ProposalExportError):
    """Gemini API  """
    
    def __init__(self, message, error_type=None, quota_exceeded=False):
        super().__init__(message)
        self.error_type = error_type
        self.quota_exceeded = quota_exceeded


class GoogleSlidesAPIError(ProposalExportError):
    """Google Slides API  """
    
    def __init__(self, message, http_status=None):
        super().__init__(message)
        self.http_status = http_status


class TextProcessingError(ProposalExportError):
    """   """
    pass


class ServiceInitializationError(ProposalExportError):
    """   """
    pass


class APIQuotaExceededError(ProposalExportError):
    """API   """
    
    def __init__(self, service_name, daily_limit=None, reset_time=None):
        message = f"{service_name} API  ."
        if daily_limit:
            message += f"  : {daily_limit}"
        if reset_time:
            message += f"  : {reset_time}"
        
        super().__init__(message)
        self.service_name = service_name
        self.daily_limit = daily_limit
        self.reset_time = reset_time


class InvalidInputError(ProposalExportError):
    """   """
    
    def __init__(self, field_name, message):
        super().__init__(f"{field_name}: {message}")
        self.field_name = field_name