"""
 PDF  
Google Gemini API        PDF 
"""

import os
import io
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
import google.generativeai as genai
from django.conf import settings
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm, mm
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, Color
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, 
    Image, PageBreak, KeepTogether, Frame, PageTemplate,
    BaseDocTemplate, NextPageTemplate, FrameBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.platypus.flowables import Flowable
import requests
from PIL import Image as PILImage
from io import BytesIO
import tempfile
from datetime import datetime

logger = logging.getLogger(__name__)


class DesignedHeaderFooter(Flowable):
    """ / """
    
    def __init__(self, title="", page_num=1, total_pages=1, is_header=True):
        Flowable.__init__(self)
        self.title = title
        self.page_num = page_num
        self.total_pages = total_pages
        self.is_header = is_header
        self.width = landscape(A4)[0] - 2*cm
        self.height = 1.5*cm
        
    def draw(self):
        canvas = self.canv
        
        if self.is_header:
            #  
            canvas.setStrokeColor(HexColor('#1631F8'))
            canvas.setLineWidth(2)
            canvas.line(0, 0, self.width, 0)
            
            #  
            canvas.setFillColor(HexColor('#1631F8'))
            canvas.setFont('HYGothic-Medium', 10)
            canvas.drawString(0, 5, "VideoPlanet")
            
            # 
            canvas.setFillColor(HexColor('#333333'))
            canvas.setFont('HYGothic-Medium', 12)
            canvas.drawCentredString(self.width/2, 5, self.title)
            
            # 
            canvas.setFillColor(HexColor('#666666'))
            canvas.setFont('HYGothic-Medium', 9)
            canvas.drawRightString(self.width, 5, datetime.now().strftime("%Y.%m.%d"))
        else:
            #  
            canvas.setStrokeColor(HexColor('#E0E0E0'))
            canvas.setLineWidth(1)
            canvas.line(0, self.height-2, self.width, self.height-2)
            
            #  
            canvas.setFillColor(HexColor('#666666'))
            canvas.setFont('HYGothic-Medium', 9)
            page_text = f"{self.page_num} / {self.total_pages}"
            canvas.drawCentredString(self.width/2, 5, page_text)
            
            # 
            canvas.setFillColor(HexColor('#999999'))
            canvas.setFont('HYGothic-Medium', 8)
            canvas.drawString(0, 5, "© 2024 VideoPlanet. All rights reserved.")


class AdvancedPDFExportService:
    """Gemini API   PDF  """
    
    #   
    COLORS = {
        'primary': '#1631F8',
        'primary_dark': '#0F23C9',
        'secondary': '#E8EBFF',
        'danger': '#dc3545',
        'success': '#28a745',
        'warning': '#ffc107',
        'info': '#17a2b8',
        'dark': '#333333',
        'gray': '#666666',
        'light_gray': '#E0E0E0',
        'background': '#F8F9FA'
    }
    
    def __init__(self):
        # Gemini API 
        api_key = getattr(settings, 'GOOGLE_API_KEY', None) or os.environ.get('GOOGLE_API_KEY')
        if api_key:
            genai.configure(api_key=api_key)
            self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            logger.warning("GOOGLE_API_KEY  . AI  .")
            self.gemini_model = None
            
        self.setup_fonts()
        self.styles = self.setup_advanced_styles()
    
    def setup_fonts(self):
        """  """
        try:
            # CID   ( )
            pdfmetrics.registerFont(UnicodeCIDFont('HYSMyeongJo-Medium'))
            pdfmetrics.registerFont(UnicodeCIDFont('HYGothic-Medium'))
            logger.info(" PDF: CID   ")
        except Exception as e:
            logger.error(f" PDF:   : {str(e)}")
    
    def setup_advanced_styles(self):
        """ PDF  """
        styles = getSampleStyleSheet()
        font_name = 'HYGothic-Medium'
        
        #  
        styles.add(ParagraphStyle(
            name='CoverTitle',
            fontName=font_name,
            fontSize=36,
            textColor=HexColor(self.COLORS['primary']),
            spaceAfter=20,
            alignment=TA_CENTER,
            leading=44
        ))
        
        styles.add(ParagraphStyle(
            name='CoverSubtitle',
            fontName=font_name,
            fontSize=20,
            textColor=HexColor(self.COLORS['dark']),
            spaceAfter=40,
            alignment=TA_CENTER,
            leading=28
        ))
        
        #  
        styles.add(ParagraphStyle(
            name='SectionTitle',
            fontName=font_name,
            fontSize=24,
            textColor=HexColor(self.COLORS['primary']),
            spaceAfter=20,
            spaceBefore=30,
            alignment=TA_LEFT,
            borderWidth=0,
            borderPadding=0,
            borderColor=HexColor(self.COLORS['primary']),
            borderRadius=0
        ))
        
        #  
        styles.add(ParagraphStyle(
            name='ContentHeading',
            fontName=font_name,
            fontSize=16,
            textColor=HexColor(self.COLORS['dark']),
            spaceAfter=12,
            spaceBefore=16,
            leading=20
        ))
        
        styles.add(ParagraphStyle(
            name='ContentBody',
            fontName=font_name,
            fontSize=11,
            textColor=HexColor(self.COLORS['gray']),
            spaceAfter=8,
            leading=16,
            alignment=TA_JUSTIFY
        ))
        
        #  
        styles.add(ParagraphStyle(
            name='Highlight',
            fontName=font_name,
            fontSize=12,
            textColor=HexColor(self.COLORS['primary']),
            backColor=HexColor(self.COLORS['secondary']),
            spaceAfter=10,
            spaceBefore=10,
            leading=18,
            borderWidth=1,
            borderColor=HexColor(self.COLORS['primary']),
            borderPadding=8,
            borderRadius=4
        ))
        
        #  
        styles.add(ParagraphStyle(
            name='SceneHeader',
            fontName=font_name,
            fontSize=14,
            textColor=HexColor('#FFFFFF'),
            backColor=HexColor(self.COLORS['primary']),
            spaceAfter=8,
            leading=20,
            alignment=TA_CENTER,
            borderPadding=6
        ))
        
        #   
        styles.add(ParagraphStyle(
            name='CodeBlock',
            fontName='Courier',
            fontSize=10,
            textColor=HexColor('#2E3440'),
            backColor=HexColor('#F8F9FA'),
            spaceAfter=12,
            spaceBefore=12,
            leading=14,
            leftIndent=10,
            rightIndent=10,
            borderWidth=1,
            borderColor=HexColor('#E0E0E0'),
            borderPadding=10
        ))
        
        return styles
    
    def create_ai_structured_content(self, planning_data: Dict[str, Any]) -> Dict[str, Any]:
        """Gemini API      """
        if not self.gemini_model:
            return planning_data
            
        try:
            prompt = self._create_design_structuring_prompt(planning_data)
            response = self.gemini_model.generate_content(prompt)
            response_text = response.text.strip()
            
            # JSON 
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
                
            structured = json.loads(response_text)
            return structured
            
        except Exception as e:
            logger.error(f"AI  : {e}")
            return planning_data
    
    def _create_design_structuring_prompt(self, data: Dict[str, Any]) -> str:
        """    """
        return f"""
    .       PDF     .

 :
{json.dumps(data, ensure_ascii=False, indent=2)}

 JSON  :

{{
    "document": {{
        "title": " ",
        "subtitle": "",
        "version": "v1.0",
        "date": "2024-01-01",
        "author": "",
        "summary": "  "
    }},
    "sections": [
        {{
            "type": "overview",
            "title": " ",
            "content": {{
                "intro": "  ",
                "key_points": [
                    {{"icon": "", "title": "", "description": "  "}},
                    {{"icon": "", "title": "", "description": " "}},
                    {{"icon": "", "title": "", "description": " "}}
                ],
                "visual_style": {{
                    "layout": "grid",
                    "color_scheme": "primary"
                }}
            }}
        }},
        {{
            "type": "story_structure",
            "title": " ",
            "content": {{
                "narrative_arc": [
                    {{"stage": "", "percentage": 25, "description": " ", "color": "#FF6B6B"}},
                    {{"stage": "", "percentage": 25, "description": " ", "color": "#4ECDC4"}},
                    {{"stage": "", "percentage": 25, "description": " ", "color": "#45B7D1"}},
                    {{"stage": "", "percentage": 25, "description": " ", "color": "#96CEB4"}}
                ],
                "visual_representation": "pie_chart"
            }}
        }},
        {{
            "type": "scenes",
            "title": " ",
            "content": {{
                "total_scenes": 10,
                "scenes": [
                    {{
                        "number": 1,
                        "title": " ",
                        "location": "",
                        "time": "",
                        "description": " ",
                        "duration": "30",
                        "key_elements": ["1", "2"],
                        "mood": "",
                        "color_palette": ["#color1", "#color2"]
                    }}
                ],
                "timeline_view": true
            }}
        }},
        {{
            "type": "production_plan",
            "title": " ",
            "content": {{
                "schedule": {{
                    "pre_production": {{"duration": "2", "tasks": ["", "", ""]}},
                    "production": {{"duration": "1", "tasks": ["", " "]}},
                    "post_production": {{"duration": "2", "tasks": ["", "", ""]}}
                }},
                "budget_breakdown": {{
                    "visualization": "bar_chart",
                    "categories": [
                        {{"name": "", "amount": 5000000, "percentage": 40}},
                        {{"name": "", "amount": 3000000, "percentage": 24}},
                        {{"name": "", "amount": 2500000, "percentage": 20}},
                        {{"name": "", "amount": 2000000, "percentage": 16}}
                    ]
                }}
            }}
        }},
        {{
            "type": "visual_reference",
            "title": " ",
            "content": {{
                "mood_board": {{
                    "primary_color": "#1631F8",
                    "secondary_colors": ["#E8EBFF", "#333333"],
                    "style_keywords": ["", "", ""],
                    "reference_images": []
                }},
                "storyboards": []
            }}
        }}
    ],
    "design_guidelines": {{
        "use_brand_colors": true,
        "include_charts": true,
        "page_numbers": true,
        "header_footer": true,
        "table_of_contents": true
    }}
}}

 :
1.    
2.  (, , )  
3.   
4.   
5.  (#1631F8)   
"""
    
    def create_cover_page(self, doc_info: Dict[str, Any]) -> List[Any]:
        """  """
        elements = []
        
        #  
        elements.append(Spacer(1, 10*cm))
        
        #  
        title = Paragraph(doc_info.get('title', ' '), self.styles['CoverTitle'])
        elements.append(title)
        
        # 
        if doc_info.get('subtitle'):
            subtitle = Paragraph(doc_info['subtitle'], self.styles['CoverSubtitle'])
            elements.append(subtitle)
        
        #  
        elements.append(Spacer(1, 5*cm))
        
        #   
        meta_data = [
            ['', doc_info.get('date', datetime.now().strftime('%Y-%m-%d'))],
            ['', doc_info.get('version', 'v1.0')],
            ['', doc_info.get('author', 'VideoPlanet')]
        ]
        
        meta_table = Table(meta_data, colWidths=[5*cm, 10*cm])
        meta_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'HYGothic-Medium'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('TEXTCOLOR', (0, 0), (0, -1), HexColor(self.COLORS['primary'])),
            ('TEXTCOLOR', (1, 0), (1, -1), HexColor(self.COLORS['gray'])),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        
        elements.append(meta_table)
        elements.append(PageBreak())
        
        return elements
    
    def create_table_of_contents(self, sections: List[Dict[str, Any]]) -> List[Any]:
        """  """
        elements = []
        
        #  
        elements.append(Paragraph('', self.styles['SectionTitle']))
        elements.append(Spacer(1, 20))
        
        #  
        toc_data = []
        for i, section in enumerate(sections, 1):
            toc_data.append([
                f"{i}.",
                section['title'],
                f"{i + 1}"  #   (   )
            ])
        
        toc_table = Table(toc_data, colWidths=[1.5*cm, 20*cm, 2*cm])
        toc_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'HYGothic-Medium'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('TEXTCOLOR', (0, 0), (0, -1), HexColor(self.COLORS['primary'])),
            ('TEXTCOLOR', (1, 0), (1, -1), HexColor(self.COLORS['dark'])),
            ('TEXTCOLOR', (2, 0), (2, -1), HexColor(self.COLORS['gray'])),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LINEBELOW', (0, 0), (-1, -2), 0.5, HexColor(self.COLORS['light_gray'])),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
            ('TOPPADDING', (0, 0), (-1, -1), 15),
        ]))
        
        elements.append(toc_table)
        elements.append(PageBreak())
        
        return elements
    
    def create_overview_section(self, content: Dict[str, Any]) -> List[Any]:
        """  """
        elements = []
        
        #  
        elements.append(Paragraph(' ', self.styles['SectionTitle']))
        
        #  
        if content.get('intro'):
            elements.append(Paragraph(content['intro'], self.styles['ContentBody']))
            elements.append(Spacer(1, 20))
        
        #   
        if content.get('key_points'):
            key_points_data = []
            for point in content['key_points']:
                icon = point.get('icon', '•')
                title = point.get('title', '')
                desc = point.get('description', '')
                
                #   
                title_with_icon = f"<font size='16'>{icon}</font> <b>{title}</b>"
                point_content = f"{title_with_icon}<br/>{desc}"
                
                key_points_data.append([Paragraph(point_content, self.styles['ContentBody'])])
            
            # 3  
            if len(key_points_data) >= 3:
                grid_data = []
                for i in range(0, len(key_points_data), 3):
                    row = key_points_data[i:i+3]
                    while len(row) < 3:
                        row.append([''])  #   
                    grid_data.append([cell[0] for cell in row])
                
                grid_table = Table(grid_data, colWidths=[8.5*cm, 8.5*cm, 8.5*cm])
                grid_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), HexColor(self.COLORS['secondary'])),
                    ('TEXTCOLOR', (0, 0), (-1, -1), HexColor(self.COLORS['dark'])),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('FONTNAME', (0, 0), (-1, -1), 'HYGothic-Medium'),
                    ('FONTSIZE', (0, 0), (-1, -1), 11),
                    ('LEFTPADDING', (0, 0), (-1, -1), 15),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 15),
                    ('TOPPADDING', (0, 0), (-1, -1), 15),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
                    ('GRID', (0, 0), (-1, -1), 1, HexColor(self.COLORS['primary'])),
                    ('BOX', (0, 0), (-1, -1), 2, HexColor(self.COLORS['primary'])),
                ]))
                
                elements.append(grid_table)
        
        return elements
    
    def create_story_structure_section(self, content: Dict[str, Any]) -> List[Any]:
        """   """
        elements = []
        
        #  
        elements.append(Paragraph(' ', self.styles['SectionTitle']))
        
        #   
        if content.get('narrative_arc'):
            #    ( )
            arc_data = []
            colors = []
            labels = []
            
            for arc in content['narrative_arc']:
                arc_data.append(arc['percentage'])
                colors.append(HexColor(arc.get('color', self.COLORS['primary'])))
                labels.append(f"{arc['stage']} ({arc['percentage']}%)")
            
            #  
            for arc in content['narrative_arc']:
                desc = f"<b>{arc['stage']}</b> - {arc['description']}"
                elements.append(Paragraph(desc, self.styles['ContentBody']))
            
            elements.append(Spacer(1, 20))
        
        return elements
    
    def create_scenes_section(self, scenes: List[Dict[str, Any]]) -> List[Any]:
        """   """
        elements = []
        
        #  
        elements.append(Paragraph(' ', self.styles['SectionTitle']))
        
        for scene in scenes:
            #  
            scene_title = f" {scene.get('number', '')} - {scene.get('title', '')}"
            elements.append(Paragraph(scene_title, self.styles['SceneHeader']))
            
            #   
            scene_info = [
                ['', scene.get('location', '')],
                ['', scene.get('time', '')],
                ['', scene.get('mood', '')],
                ['', scene.get('duration', '')]
            ]
            
            info_table = Table(scene_info, colWidths=[3*cm, 22*cm])
            info_table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), 'HYGothic-Medium'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('TEXTCOLOR', (0, 0), (0, -1), HexColor(self.COLORS['primary'])),
                ('TEXTCOLOR', (1, 0), (1, -1), HexColor(self.COLORS['gray'])),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            
            elements.append(info_table)
            
            #  
            if scene.get('description'):
                elements.append(Paragraph(scene['description'], self.styles['ContentBody']))
            
            #   ( )
            if scene.get('storyboard') and scene['storyboard'].get('image_url'):
                try:
                    img = self._get_image_from_url(scene['storyboard']['image_url'])
                    if img:
                        elements.append(img)
                except Exception as e:
                    logger.error(f"   : {e}")
            
            elements.append(Spacer(1, 20))
        
        return elements
    
    def _get_image_from_url(self, url: str, max_width: float = 20*cm, max_height: float = 15*cm) -> Optional[Image]:
        """URL   ReportLab Image  """
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                img_buffer = BytesIO(response.content)
                pil_img = PILImage.open(img_buffer)
                
                #   
                width, height = pil_img.size
                aspect = height / float(width)
                
                if width > max_width:
                    width = max_width
                    height = width * aspect
                    
                if height > max_height:
                    height = max_height
                    width = height / aspect
                
                #   
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                    pil_img.save(tmp_file.name, 'PNG')
                    return Image(tmp_file.name, width=width, height=height)
                    
        except Exception as e:
            logger.error(f"  : {e}")
            return None
    
    def generate_advanced_pdf(self, planning_data: Dict[str, Any], output_buffer: io.BytesIO) -> bool:
        """ PDF   """
        try:
            # AI   
            structured_content = self.create_ai_structured_content(planning_data)
            
            # PDF  
            doc = SimpleDocTemplate(
                output_buffer,
                pagesize=landscape(A4),
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=3*cm,
                bottomMargin=2.5*cm,
                title=structured_content.get('document', {}).get('title', ' '),
                author='VideoPlanet'
            )
            
            #   
            elements = []
            
            # 1. 
            if structured_content.get('document'):
                elements.extend(self.create_cover_page(structured_content['document']))
            
            # 2. 
            if structured_content.get('sections'):
                elements.extend(self.create_table_of_contents(structured_content['sections']))
            
            # 3.   
            for section in structured_content.get('sections', []):
                section_type = section.get('type')
                
                if section_type == 'overview':
                    elements.extend(self.create_overview_section(section.get('content', {})))
                elif section_type == 'story_structure':
                    elements.extend(self.create_story_structure_section(section.get('content', {})))
                elif section_type == 'scenes':
                    scenes = section.get('content', {}).get('scenes', [])
                    elements.extend(self.create_scenes_section(scenes))
                
                elements.append(PageBreak())
            
            # PDF 
            doc.build(elements)
            return True
            
        except Exception as e:
            logger.error(f" PDF  : {e}")
            return False
    
    def export_to_pdf(self, planning_data: Dict[str, Any]) -> Optional[bytes]:
        """  PDF  """
        output_buffer = io.BytesIO()
        
        if self.generate_advanced_pdf(planning_data, output_buffer):
            output_buffer.seek(0)
            return output_buffer.getvalue()
        
        return None