import os
import json
import logging
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import requests
from io import BytesIO

logger = logging.getLogger(__name__)


class GoogleSlidesService:
    """Google Slides API    """
    
    def __init__(self):
        self.credentials = None
        self.service = None
        self.drive_service = None
        self.initialize_service()
    
    def initialize_service(self):
        """Google API  """
        try:
            #     
            credentials_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
            if not credentials_path:
                logger.warning("GOOGLE_APPLICATION_CREDENTIALS   .")
                #    
                logger.info("Google Slides  .")
                return
            
            #    
            if not os.path.exists(credentials_path):
                logger.error(f"      : {credentials_path}")
                return
            
            self.credentials = service_account.Credentials.from_service_account_file(
                credentials_path,
                scopes=[
                    'https://www.googleapis.com/auth/presentations',
                    'https://www.googleapis.com/auth/drive'
                ]
            )
            
            self.service = build('slides', 'v1', credentials=self.credentials)
            self.drive_service = build('drive', 'v3', credentials=self.credentials)
            logger.info("Google Slides   .")
            
        except Exception as e:
            logger.error(f"Google API   : {str(e)}", exc_info=True)
    
    def create_presentation(self, title, planning_data):
        """   Google Slides  """
        if not self.service:
            error_msg = 'Google Slides   . '
            error_msg += 'Railway  GOOGLE_APPLICATION_CREDENTIALS      .'
            logger.error(error_msg)
            return {'error': error_msg}
        
        try:
            # 1.   
            presentation = self.service.presentations().create(body={
                'title': title
            }).execute()
            
            presentation_id = presentation.get('presentationId')
            
            # 2.    
            requests = []
            
            #  
            requests.extend(self._create_title_slide(planning_data))
            
            #   
            requests.extend(self._create_overview_slide(planning_data))
            
            #    ()
            requests.extend(self._create_story_slides(planning_data))
            
            #   
            requests.extend(self._create_scene_slides(planning_data))
            
            # 3.    
            if requests:
                self.service.presentations().batchUpdate(
                    presentationId=presentation_id,
                    body={'requests': requests}
                ).execute()
            
            # 4.   ()
            self._set_sharing_permissions(presentation_id)
            
            return {
                'presentation_id': presentation_id,
                'url': f'https://docs.google.com/presentation/d/{presentation_id}/edit'
            }
            
        except HttpError as error:
            logger.error(f"Google Slides API : {error}")
            return {'error': str(error)}
        except Exception as e:
            logger.error(f"   : {str(e)}")
            return {'error': str(e)}
    
    def _create_title_slide(self, planning_data):
        """  """
        requests = []
        
        #   
        slide_id = 'title_slide'
        requests.append({
            'createSlide': {
                'objectId': slide_id,
                'slideLayoutReference': {
                    'predefinedLayout': 'TITLE'
                }
            }
        })
        
        #   
        title = planning_data.get('title', ' ')
        subtitle = f": {planning_data.get('genre', 'N/A')} | : {planning_data.get('target', 'N/A')}"
        
        requests.extend([
            {
                'insertText': {
                    'objectId': f'{slide_id}_title',
                    'text': title
                }
            },
            {
                'insertText': {
                    'objectId': f'{slide_id}_subtitle',
                    'text': subtitle
                }
            }
        ])
        
        return requests
    
    def _create_overview_slide(self, planning_data):
        """   """
        requests = []
        
        slide_id = 'overview_slide'
        requests.append({
            'createSlide': {
                'objectId': slide_id,
                'slideLayoutReference': {
                    'predefinedLayout': 'TITLE_AND_BODY'
                }
            }
        })
        
        #   
        overview_text = f""" 
        
• : {planning_data.get('tone', 'N/A')}
• : {planning_data.get('genre', 'N/A')}
• : {planning_data.get('concept', 'N/A')}
• : {planning_data.get('target', 'N/A')}
• : {planning_data.get('purpose', 'N/A')}
• : {planning_data.get('duration', 'N/A')}

 :
{planning_data.get('planning_text', '')}"""
        
        requests.extend([
            {
                'insertText': {
                    'objectId': f'{slide_id}_title',
                    'text': ' '
                }
            },
            {
                'insertText': {
                    'objectId': f'{slide_id}_body',
                    'text': overview_text
                }
            }
        ])
        
        return requests
    
    def _create_story_slides(self, planning_data):
        """   """
        requests = []
        stories = planning_data.get('stories', [])
        
        for idx, story in enumerate(stories):
            slide_id = f'story_slide_{idx}'
            requests.append({
                'createSlide': {
                    'objectId': slide_id,
                    'slideLayoutReference': {
                        'predefinedLayout': 'TITLE_AND_TWO_COLUMNS'
                    }
                }
            })
            
            story_phase = ['', '', '', ''][idx] if idx < 4 else f' {idx+1}'
            
            requests.extend([
                {
                    'insertText': {
                        'objectId': f'{slide_id}_title',
                        'text': f'{story_phase} - {story.get("phase", "")}'
                    }
                },
                {
                    'insertText': {
                        'objectId': f'{slide_id}_body1',
                        'text': story.get('content', '')
                    }
                },
                {
                    'insertText': {
                        'objectId': f'{slide_id}_body2',
                        'text': f" :\n{story.get('key_point', '')}"
                    }
                }
            ])
        
        return requests
    
    def _create_scene_slides(self, planning_data):
        """   """
        requests = []
        scenes = planning_data.get('scenes', [])
        
        for idx, scene in enumerate(scenes):
            slide_id = f'scene_slide_{idx}'
            
            #      
            if scene.get('storyboard', {}).get('image_url'):
                requests.extend(self._create_scene_slide_with_image(slide_id, scene, idx))
            else:
                requests.extend(self._create_scene_slide_text_only(slide_id, scene, idx))
        
        return requests
    
    def _create_scene_slide_with_image(self, slide_id, scene, idx):
        """    """
        requests = []
        
        #  
        requests.append({
            'createSlide': {
                'objectId': slide_id,
                'slideLayoutReference': {
                    'predefinedLayout': 'CAPTION_ONLY'
                }
            }
        })
        
        #  
        requests.append({
            'insertText': {
                'objectId': f'{slide_id}_title',
                'text': f' {idx + 1}: {scene.get("title", "")}'
            }
        })
        
        #  
        image_url = scene.get('storyboard', {}).get('image_url')
        if image_url:
            #  Google Drive  Slides 
            image_id = f'{slide_id}_image'
            requests.append({
                'createImage': {
                    'objectId': image_id,
                    'url': image_url,
                    'elementProperties': {
                        'pageObjectId': slide_id,
                        'size': {
                            'width': {'magnitude': 400, 'unit': 'PT'},
                            'height': {'magnitude': 300, 'unit': 'PT'}
                        },
                        'transform': {
                            'scaleX': 1,
                            'scaleY': 1,
                            'translateX': 50,
                            'translateY': 100,
                            'unit': 'PT'
                        }
                    }
                }
            })
        
        #   
        description = scene.get('storyboard', {}).get('description_kr', scene.get('description', ''))
        if description:
            text_id = f'{slide_id}_text'
            requests.append({
                'createTextBox': {
                    'objectId': text_id,
                    'elementProperties': {
                        'pageObjectId': slide_id,
                        'size': {
                            'width': {'magnitude': 600, 'unit': 'PT'},
                            'height': {'magnitude': 100, 'unit': 'PT'}
                        },
                        'transform': {
                            'scaleX': 1,
                            'scaleY': 1,
                            'translateX': 50,
                            'translateY': 420,
                            'unit': 'PT'
                        }
                    }
                }
            })
            
            requests.append({
                'insertText': {
                    'objectId': text_id,
                    'text': description
                }
            })
        
        return requests
    
    def _create_scene_slide_text_only(self, slide_id, scene, idx):
        """    """
        requests = []
        
        requests.append({
            'createSlide': {
                'objectId': slide_id,
                'slideLayoutReference': {
                    'predefinedLayout': 'TITLE_AND_BODY'
                }
            }
        })
        
        requests.extend([
            {
                'insertText': {
                    'objectId': f'{slide_id}_title',
                    'text': f' {idx + 1}: {scene.get("title", "")}'
                }
            },
            {
                'insertText': {
                    'objectId': f'{slide_id}_body',
                    'text': scene.get('description', '')
                }
            }
        ])
        
        return requests
    
    def _set_sharing_permissions(self, presentation_id):
        """   """
        try:
            #     
            self.drive_service.permissions().create(
                fileId=presentation_id,
                body={
                    'type': 'anyone',
                    'role': 'reader'
                }
            ).execute()
        except Exception as e:
            logger.error(f"   : {str(e)}")
    
    def create_structured_presentation(self, title, structured_data):
        """    """
        if not self.service:
            error_msg = 'Google Slides   . '
            error_msg += 'Railway  GOOGLE_APPLICATION_CREDENTIALS      .'
            logger.error(error_msg)
            return {'error': error_msg}
        
        try:
            # 1.   
            presentation = self.service.presentations().create(body={
                'title': title
            }).execute()
            
            presentation_id = presentation.get('presentationId')
            
            # 2.     (   )
            slide_ids = [slide['objectId'] for slide in presentation.get('slides', [])]
            delete_requests = []
            if slide_ids:
                delete_requests.append({
                    'deleteObject': {
                        'objectId': slide_ids[0]
                    }
                })
            
            # 3.    
            create_requests = []
            slides_data = structured_data.get('slides', [])
            
            for slide_info in slides_data:
                slide_requests = self._create_structured_slide(slide_info)
                create_requests.extend(slide_requests)
            
            # 4.   
            all_requests = delete_requests + create_requests
            if all_requests:
                self.service.presentations().batchUpdate(
                    presentationId=presentation_id,
                    body={'requests': all_requests}
                ).execute()
            
            # 5.  
            self._set_sharing_permissions(presentation_id)
            
            return {
                'presentation_id': presentation_id,
                'url': f'https://docs.google.com/presentation/d/{presentation_id}/edit'
            }
            
        except HttpError as error:
            logger.error(f"Google Slides API : {error}")
            return {'error': str(error)}
        except Exception as e:
            logger.error(f"    : {str(e)}")
            return {'error': str(e)}
    
    def _create_structured_slide(self, slide_info):
        """    """
        requests = []
        slide_id = f"slide_{slide_info['slide_number']}"
        layout = slide_info.get('layout', 'TITLE_AND_BODY')
        
        #  
        requests.append({
            'createSlide': {
                'objectId': slide_id,
                'slideLayoutReference': {
                    'predefinedLayout': layout
                }
            }
        })
        
        #   
        if layout == 'TITLE':
            requests.extend(self._add_title_slide_content(slide_id, slide_info))
        elif layout == 'TITLE_AND_BODY':
            requests.extend(self._add_title_body_content(slide_id, slide_info))
        elif layout == 'TITLE_AND_TWO_COLUMNS':
            requests.extend(self._add_two_column_content(slide_id, slide_info))
        
        return requests
    
    def _add_title_slide_content(self, slide_id, slide_info):
        """   """
        requests = []
        content = slide_info.get('content', {})
        
        #      
        title_box_id = f"{slide_id}_title_box"
        requests.extend([
            {
                'createTextBox': {
                    'objectId': title_box_id,
                    'elementProperties': {
                        'pageObjectId': slide_id,
                        'size': {
                            'width': {'magnitude': 600, 'unit': 'PT'},
                            'height': {'magnitude': 100, 'unit': 'PT'}
                        },
                        'transform': {
                            'scaleX': 1,
                            'scaleY': 1,
                            'translateX': 100,
                            'translateY': 150,
                            'unit': 'PT'
                        }
                    }
                }
            },
            {
                'insertText': {
                    'objectId': title_box_id,
                    'text': content.get('title_text', slide_info.get('title', ''))
                }
            }
        ])
        
        #  ( )
        if content.get('subtitle_text'):
            subtitle_box_id = f"{slide_id}_subtitle_box"
            requests.extend([
                {
                    'createTextBox': {
                        'objectId': subtitle_box_id,
                        'elementProperties': {
                            'pageObjectId': slide_id,
                            'size': {
                                'width': {'magnitude': 600, 'unit': 'PT'},
                                'height': {'magnitude': 60, 'unit': 'PT'}
                            },
                            'transform': {
                                'scaleX': 1,
                                'scaleY': 1,
                                'translateX': 100,
                                'translateY': 280,
                                'unit': 'PT'
                            }
                        }
                    }
                },
                {
                    'insertText': {
                        'objectId': subtitle_box_id,
                        'text': content.get('subtitle_text', '')
                    }
                }
            ])
        
        return requests
    
    def _add_title_body_content(self, slide_id, slide_info):
        """+   """
        requests = []
        content = slide_info.get('content', {})
        
        # 
        title_box_id = f"{slide_id}_title_box"
        requests.extend([
            {
                'createTextBox': {
                    'objectId': title_box_id,
                    'elementProperties': {
                        'pageObjectId': slide_id,
                        'size': {
                            'width': {'magnitude': 700, 'unit': 'PT'},
                            'height': {'magnitude': 60, 'unit': 'PT'}
                        },
                        'transform': {
                            'scaleX': 1,
                            'scaleY': 1,
                            'translateX': 50,
                            'translateY': 50,
                            'unit': 'PT'
                        }
                    }
                }
            },
            {
                'insertText': {
                    'objectId': title_box_id,
                    'text': slide_info.get('title', '')
                }
            }
        ])
        
        #  (    )
        body_text = ""
        if content.get('bullet_points'):
            body_text = '\n'.join(content['bullet_points'])
        elif content.get('budget_breakdown') and content.get('timeline'):
            #     
            body_text = " :\n" + '\n'.join(content['budget_breakdown'])
            body_text += "\n\n:\n" + '\n'.join(content['timeline'])
        
        if body_text:
            body_box_id = f"{slide_id}_body_box"
            requests.extend([
                {
                    'createTextBox': {
                        'objectId': body_box_id,
                        'elementProperties': {
                            'pageObjectId': slide_id,
                            'size': {
                                'width': {'magnitude': 650, 'unit': 'PT'},
                                'height': {'magnitude': 350, 'unit': 'PT'}
                            },
                            'transform': {
                                'scaleX': 1,
                                'scaleY': 1,
                                'translateX': 50,
                                'translateY': 130,
                                'unit': 'PT'
                            }
                        }
                    }
                },
                {
                    'insertText': {
                        'objectId': body_box_id,
                        'text': body_text
                    }
                }
            ])
        
        return requests
    
    def _add_two_column_content(self, slide_id, slide_info):
        """2    """
        requests = []
        content = slide_info.get('content', {})
        
        # 
        title_box_id = f"{slide_id}_title_box"
        requests.extend([
            {
                'createTextBox': {
                    'objectId': title_box_id,
                    'elementProperties': {
                        'pageObjectId': slide_id,
                        'size': {
                            'width': {'magnitude': 700, 'unit': 'PT'},
                            'height': {'magnitude': 60, 'unit': 'PT'}
                        },
                        'transform': {
                            'scaleX': 1,
                            'scaleY': 1,
                            'translateX': 50,
                            'translateY': 50,
                            'unit': 'PT'
                        }
                    }
                }
            },
            {
                'insertText': {
                    'objectId': title_box_id,
                    'text': slide_info.get('title', '')
                }
            }
        ])
        
        #  
        if content.get('left_column'):
            left_box_id = f"{slide_id}_left_box"
            left_text = '\n'.join(content['left_column'])
            requests.extend([
                {
                    'createTextBox': {
                        'objectId': left_box_id,
                        'elementProperties': {
                            'pageObjectId': slide_id,
                            'size': {
                                'width': {'magnitude': 300, 'unit': 'PT'},
                                'height': {'magnitude': 300, 'unit': 'PT'}
                            },
                            'transform': {
                                'scaleX': 1,
                                'scaleY': 1,
                                'translateX': 50,
                                'translateY': 130,
                                'unit': 'PT'
                            }
                        }
                    }
                },
                {
                    'insertText': {
                        'objectId': left_box_id,
                        'text': left_text
                    }
                }
            ])
        
        #  
        if content.get('right_column'):
            right_box_id = f"{slide_id}_right_box"
            right_text = '\n'.join(content['right_column'])
            requests.extend([
                {
                    'createTextBox': {
                        'objectId': right_box_id,
                        'elementProperties': {
                            'pageObjectId': slide_id,
                            'size': {
                                'width': {'magnitude': 300, 'unit': 'PT'},
                                'height': {'magnitude': 300, 'unit': 'PT'}
                            },
                            'transform': {
                                'scaleX': 1,
                                'scaleY': 1,
                                'translateX': 400,
                                'translateY': 130,
                                'unit': 'PT'
                            }
                        }
                    }
                },
                {
                    'insertText': {
                        'objectId': right_box_id,
                        'text': right_text
                    }
                }
            ])
        
        return requests