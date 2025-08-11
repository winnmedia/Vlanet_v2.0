""" CORS   """
import logging

logger = logging.getLogger(__name__)


class ForceCorsMiddleware:
    """CORS    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        #  origin 
        self.allowed_origins = [
            "https://vlanet.net",
            "https://www.vlanet.net",
            "http://vlanet.net",
            "http://www.vlanet.net",
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "https://videoplanet.up.railway.app",
            "https://videoplanetready.vercel.app",
            "https://vlanet-v1-0.vercel.app",
        ]

    def __call__(self, request):
        #  Origin  
        origin = request.headers.get('Origin', '')
        
        #  
        response = self.get_response(request)
        
        # Origin   , Vercel  
        if origin in self.allowed_origins or '.vercel.app' in origin:
            # CORS   
            response['Access-Control-Allow-Origin'] = origin
            response['Access-Control-Allow-Credentials'] = 'true'
            response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Accept, Accept-Encoding, Authorization, Content-Type, Origin, X-Requested-With, X-CSRFToken, X-Idempotency-Key'
            response['Access-Control-Max-Age'] = '86400'
            
            # OPTIONS   (preflight)
            if request.method == 'OPTIONS':
                response['Content-Length'] = '0'
                response.status_code = 200
            
            logger.info(f"[Force CORS] Added headers for origin: {origin}")
        else:
            logger.warning(f"[Force CORS] Origin not allowed: {origin}")
        
        return response