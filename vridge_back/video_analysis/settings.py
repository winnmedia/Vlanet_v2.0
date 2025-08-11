"""
Twelve Labs API 
"""
from django.conf import settings

# Twelve Labs API 
TWELVE_LABS_API_KEY = getattr(settings, 'TWELVE_LABS_API_KEY', '')
TWELVE_LABS_INDEX_ID = getattr(settings, 'TWELVE_LABS_INDEX_ID', '')

# API 
TWELVE_LABS_BASE_URL = 'https://api.twelvelabs.io/v1.2'

#   
SUPPORTED_VIDEO_FORMATS = [
    'mp4', 'mov', 'avi', 'mkv', 'wmv', 'flv', 'webm', 'm4v', '3gp'
]

#    ()
MAX_VIDEO_SIZE = 2 * 1024 * 1024 * 1024  # 2GB

#    ()
MAX_VIDEO_DURATION = 3600  # 1

# API  
API_TIMEOUT = {
    'upload': 600,      # 10
    'generate': 300,    # 5
    'classify': 120,    # 2
    'search': 60        # 1
}

#  
ANALYSIS_OPTIONS = {
    'generate_summary': True,
    'classify_content': True,
    'analyze_scenes': True,
    'extract_thumbnails': False,
    'transcribe_audio': True
}

#  
PROMPTS = {
    'summary': """
      .     :

1.  (Composition):  ,  ,    
2.  (Lighting):  , , 
3.  (Color): , ,  
4.  (Movement):  ,  , 
5.  (Audio):  , ,  
6.  (Editing):  , , 

  (1-10)  .
""",
    
    'quality_analysis': """
    :
-  
-    
-  
-  
-  
""",

    'improvement_suggestions': """
       3-5  .
     .
"""
}

#   ( )
SCENE_ANALYSIS_QUERIES = [
    #  
    " ",
    " ", 
    " ",
    " ",
    
    #  
    " ",
    " ",
    " ",
    " ",
    
    #  
    " ",
    " ",
    "  ",
    "/",
    
    # /
    " ",
    " ",
    " ",
    " "
]

#   
CONTENT_CATEGORIES = [
    "/",
    "",
    "/",
    "",
    "/",
    "/e",
    "/",
    "/",
    " ",
    "/",
    ""
]

#   
SCORING_WEIGHTS = {
    'composition': 0.2,    #  20%
    'lighting': 0.2,       #  20%
    'audio': 0.15,         #  15%
    'stability': 0.15,     #  15%
    'color': 0.15,         #  15%
    'editing': 0.15        #  15%
}

#  
ERROR_MESSAGES = {
    'api_key_missing': 'Twelve Labs API   .',
    'index_id_missing': 'Twelve Labs Index ID  .',
    'upload_failed': '  .',
    'analysis_failed': '  .',
    'file_too_large': f'  {MAX_VIDEO_SIZE // (1024*1024)}MB .',
    'unsupported_format': f'   .  : {", ".join(SUPPORTED_VIDEO_FORMATS)}',
    'video_too_long': f'  {MAX_VIDEO_DURATION // 60} .'
}