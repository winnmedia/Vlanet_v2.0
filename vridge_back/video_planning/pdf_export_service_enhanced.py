import os
import io
import logging
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
import requests
from PIL import Image as PILImage
from io import BytesIO
import tempfile

logger = logging.getLogger(__name__)


class EnhancedPDFExportService:
    """   PDF  """
    
    def __init__(self):
        self.setup_fonts()
        self.styles = self.setup_styles()
    
    def setup_fonts(self):
        """  """
        try:
            pdfmetrics.registerFont(UnicodeCIDFont('HeiseiMin-W3'))
            pdfmetrics.registerFont(UnicodeCIDFont('HeiseiKakuGo-W5'))
            pdfmetrics.registerFont(UnicodeCIDFont('HYSMyeongJo-Medium'))
            pdfmetrics.registerFont(UnicodeCIDFont('HYGothic-Medium'))
            logger.info("CID   ")
        except Exception as e:
            logger.error(f"  : {str(e)}")
    
    def setup_styles(self):
        """PDF  """
        styles = getSampleStyleSheet()
        font_name = 'HYGothic-Medium'
        
        #   
        styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=styles['Title'],
            fontName=font_name,
            fontSize=24,
            textColor=HexColor('#1631F8'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=styles['Heading1'],
            fontName=font_name,
            fontSize=18,
            textColor=HexColor('#2c3e50'),
            spaceAfter=15,
            spaceBefore=15
        ))
        
        styles.add(ParagraphStyle(
            name='CustomSubHeading',
            parent=styles['Heading2'],
            fontName=font_name,
            fontSize=14,
            textColor=HexColor('#34495e'),
            spaceAfter=10,
            spaceBefore=10
        ))
        
        styles.add(ParagraphStyle(
            name='CustomBody',
            parent=styles['BodyText'],
            fontName=font_name,
            fontSize=11,
            textColor=HexColor('#4a4a4a'),
            spaceAfter=5,
            leading=15
        ))
        
        styles.add(ParagraphStyle(
            name='SceneTitle',
            parent=styles['Heading3'],
            fontName=font_name,
            fontSize=12,
            textColor=HexColor('#1631F8'),
            spaceAfter=5
        ))
        
        return styles
    
    def generate_pdf(self, planning_data, output_buffer=None):
        """   PDF """
        if output_buffer is None:
            output_buffer = io.BytesIO()
        
        #    JSON  
        normalized_data = self._normalize_planning_data(planning_data)
        logger.info(f"  : {normalized_data}")
        
        # PDF   (A4 )
        doc = SimpleDocTemplate(
            output_buffer,
            pagesize=landscape(A4),
            rightMargin=1.5*cm,
            leftMargin=1.5*cm,
            topMargin=1.5*cm,
            bottomMargin=1.5*cm
        )
        
        #  
        story = []
        
        # 1.  
        story.extend(self._create_title_page(normalized_data))
        story.append(PageBreak())
        
        # 2.   
        story.extend(self._create_overview_page(normalized_data))
        story.append(PageBreak())
        
        # 3.   
        story.extend(self._create_story_flow_page(normalized_data))
        story.append(PageBreak())
        
        # 4.   
        story.extend(self._create_scenes_grid_layout(normalized_data))
        
        # 5.    ( )
        if normalized_data.get('pro_options'):
            story.append(PageBreak())
            story.extend(self._create_pro_options_page(normalized_data))
        
        # PDF 
        doc.build(story)
        output_buffer.seek(0)
        
        return output_buffer
    
    def _normalize_planning_data(self, planning_data):
        """    JSON  """
        return {
            'title': planning_data.get('title', ' '),
            'planning_text': planning_data.get('planning', '') or planning_data.get('planning_text', ''),
            'project_info': {
                'type': planning_data.get('project_type', ''),
                'duration': planning_data.get('duration', ''),
                'target_audience': planning_data.get('target_audience', ''),
                'genre': planning_data.get('genre', ''),
                'concept': planning_data.get('concept', ''),
                'tone_manner': planning_data.get('tone_manner', ''),
                'key_message': planning_data.get('key_message', ''),
                'mood': planning_data.get('desired_mood', ''),
            },
            'stories': planning_data.get('stories', []),
            'scenes': planning_data.get('scenes', []),
            'shots': planning_data.get('shots', []),
            'storyboards': planning_data.get('storyboards', []),
            'pro_options': planning_data.get('planning_options', {})
        }
    
    def _create_title_page(self, normalized_data):
        """   ()"""
        elements = []
        
        # 
        title = normalized_data.get('title', ' ')
        elements.append(Paragraph(title, self.styles['CustomTitle']))
        elements.append(Spacer(1, 2*cm))
        
        #   2 
        project_info = normalized_data.get('project_info', {})
        
        left_column_data = [
            [' ', project_info.get('type') or 'N/A'],
            [' ', project_info.get('target_audience') or 'N/A'],
            ['', project_info.get('duration') or 'N/A'],
            ['', project_info.get('genre') or 'N/A']
        ]
        
        right_column_data = [
            ['', project_info.get('concept') or 'N/A'],
            ['', project_info.get('tone_manner') or 'N/A'],
            [' ', project_info.get('key_message') or 'N/A'],
            ['', project_info.get('mood') or 'N/A']
        ]
        
        # 2  
        main_table_data = []
        for i in range(4):
            row = left_column_data[i] + right_column_data[i]
            main_table_data.append(row)
        
        main_table = Table(main_table_data, colWidths=[4*cm, 8*cm, 4*cm, 8*cm])
        main_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'HYGothic-Medium'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TEXTCOLOR', (0, 0), (-1, -1), HexColor('#2c3e50')),
            ('TEXTCOLOR', (1, 0), (1, -1), HexColor('#4a4a4a')),
            ('TEXTCOLOR', (3, 0), (3, -1), HexColor('#4a4a4a')),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('ALIGN', (3, 0), (3, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#ecf0f1')),
            ('BACKGROUND', (0, 0), (0, -1), HexColor('#f8f9fa')),
            ('BACKGROUND', (2, 0), (2, -1), HexColor('#f8f9fa')),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        
        elements.append(main_table)
        
        return elements
    
    def _create_overview_page(self, normalized_data):
        """    ()"""
        elements = []
        
        elements.append(Paragraph(' ', self.styles['CustomHeading']))
        elements.append(Spacer(1, 1*cm))
        
        #     
        planning_text = normalized_data.get('planning_text', '')
        if planning_text:
            planning_box_data = [[Paragraph(planning_text, self.styles['CustomBody'])]]
            planning_box = Table(planning_box_data, colWidths=[26*cm])
            planning_box.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), HexColor('#f0f4f8')),
                ('BOX', (0, 0), (-1, -1), 1, HexColor('#1631F8')),
                ('LEFTPADDING', (0, 0), (-1, -1), 15),
                ('RIGHTPADDING', (0, 0), (-1, -1), 15),
                ('TOPPADDING', (0, 0), (-1, -1), 15),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
            ]))
            elements.append(planning_box)
        
        return elements
    
    def _create_story_flow_page(self, normalized_data):
        """    ( )"""
        elements = []
        
        elements.append(Paragraph(' ', self.styles['CustomHeading']))
        elements.append(Spacer(1, 0.5*cm))
        
        stories = normalized_data.get('stories', [])
        if not stories:
            return elements
        
        #    
        story_phases = ['', '', '', '']
        story_data = []
        
        #  
        header_row = []
        for idx, phase in enumerate(story_phases[:len(stories)]):
            header_row.append(Paragraph(f'<b>{phase}</b>', self.styles['CustomSubHeading']))
        story_data.append(header_row)
        
        #  
        content_row = []
        for story in stories[:4]:
            content = story.get('content', '')
            key_point = story.get('key_point', '')
            
            story_text = content
            if key_point:
                story_text += f"<br/><br/><b>:</b> {key_point}"
            
            content_row.append(Paragraph(story_text, self.styles['CustomBody']))
        story_data.append(content_row)
        
        #   
        col_width = 26*cm / len(content_row)
        story_table = Table(story_data, colWidths=[col_width] * len(content_row))
        story_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'HYGothic-Medium'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#e0e0e0')),
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1631F8')),
            ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#ffffff')),
            ('BACKGROUND', (0, 1), (-1, -1), HexColor('#f8f9fa')),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        
        elements.append(story_table)
        
        return elements
    
    def _create_scenes_grid_layout(self, normalized_data):
        """    """
        elements = []
        
        elements.append(Paragraph('  ', self.styles['CustomHeading']))
        elements.append(Spacer(1, 0.5*cm))
        
        scenes = normalized_data.get('scenes', [])
        if not scenes:
            return elements
        
        # 2x2    (  4)
        scenes_per_page = 4
        
        for page_idx in range(0, len(scenes), scenes_per_page):
            if page_idx > 0:
                elements.append(PageBreak())
            
            page_scenes = scenes[page_idx:page_idx + scenes_per_page]
            scene_grid_data = []
            
            # 2 
            for row in range(2):
                scene_row = []
                for col in range(2):
                    scene_idx = row * 2 + col
                    if scene_idx < len(page_scenes):
                        scene = page_scenes[scene_idx]
                        scene_content = self._create_scene_cell(scene, page_idx + scene_idx + 1)
                        scene_row.append(scene_content)
                    else:
                        scene_row.append('')
                scene_grid_data.append(scene_row)
            
            scene_grid = Table(scene_grid_data, colWidths=[13*cm, 13*cm], rowHeights=[8*cm, 8*cm])
            scene_grid.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#e0e0e0')),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ]))
            
            elements.append(scene_grid)
        
        return elements
    
    def _create_scene_cell(self, scene, scene_number):
        """   """
        cell_content = []
        
        #  
        scene_title = f" {scene_number}"
        if scene.get('title'):
            scene_title += f": {scene.get('title')}"
        cell_content.append(Paragraph(scene_title, self.styles['SceneTitle']))
        
        #  
        storyboards = scene.get('storyboards', [])
        if storyboards and len(storyboards) > 0:
            storyboard = storyboards[0]
            image_url = storyboard.get('image_url')
            if image_url and image_url != 'generated_image_placeholder':
                img_element = self._create_image_element(image_url, max_width=10*cm, max_height=5*cm)
                if img_element:
                    cell_content.append(img_element)
        
        #  
        description = scene.get('description', '')
        if description:
            cell_content.append(Paragraph(description[:150] + '...' if len(description) > 150 else description, 
                                        self.styles['CustomBody']))
        
        #   ( )
        if scene.get('location'):
            cell_content.append(Paragraph(f"<b>:</b> {scene.get('location')}", self.styles['CustomBody']))
        
        return cell_content
    
    def _create_pro_options_page(self, normalized_data):
        """   """
        elements = []
        
        elements.append(Paragraph('  ', self.styles['CustomHeading']))
        elements.append(Spacer(1, 1*cm))
        
        pro_options = normalized_data.get('pro_options', {})
        
        options_data = [
            [' ', pro_options.get('colorTone', 'natural')],
            [' ', pro_options.get('aspectRatio', '16:9')],
            [' ', pro_options.get('cameraType', 'dslr')],
            [' ', pro_options.get('lensType', '35mm')],
            [' ', pro_options.get('cameraMovement', 'static')]
        ]
        
        options_table = Table(options_data, colWidths=[6*cm, 20*cm])
        options_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'HYGothic-Medium'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TEXTCOLOR', (0, 0), (0, -1), HexColor('#2c3e50')),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#e0e0e0')),
            ('BACKGROUND', (0, 0), (0, -1), HexColor('#f8f9fa')),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        
        elements.append(options_table)
        
        return elements
    
    def _create_image_element(self, image_url, max_width=12*cm, max_height=8*cm):
        """ URL ReportLab Image  """
        try:
            #  
            response = requests.get(image_url, timeout=10)
            if response.status_code != 200:
                return None
            
            # PIL  
            img = PILImage.open(BytesIO(response.content))
            
            #   
            img_width, img_height = img.size
            aspect_ratio = img_width / img_height
            
            if img_width > max_width or img_height > max_height:
                if aspect_ratio > max_width / max_height:
                    new_width = max_width
                    new_height = max_width / aspect_ratio
                else:
                    new_height = max_height
                    new_width = max_height * aspect_ratio
            else:
                new_width = img_width
                new_height = img_height
            
            #   
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                img.save(tmp_file.name, 'PNG')
                tmp_path = tmp_file.name
            
            # ReportLab Image  
            rl_img = Image(tmp_path, width=new_width, height=new_height)
            
            #   
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            
            return rl_img
            
        except Exception as e:
            logger.error(f"   : {str(e)}")
            return None