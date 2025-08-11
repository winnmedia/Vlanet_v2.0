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


class PDFExportService:
    """  PDF  """
    
    def __init__(self):
        self.setup_fonts()
        self.styles = self.setup_styles()
    
    def setup_fonts(self):
        """  """
        try:
            # CID   ( )
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
        
        # CID   ( )
        font_name = 'HYGothic-Medium'
        
        #   
        styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=styles['Title'],
            fontName=font_name,
            fontSize=20,
            textColor=HexColor('#1a1a1a'),
            spaceAfter=15,
            alignment=TA_CENTER
        ))
        
        styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=styles['Heading1'],
            fontName=font_name,
            fontSize=14,
            textColor=HexColor('#2c3e50'),
            spaceAfter=10,
            spaceBefore=10
        ))
        
        styles.add(ParagraphStyle(
            name='CustomSubHeading',
            parent=styles['Heading2'],
            fontName=font_name,
            fontSize=12,
            textColor=HexColor('#34495e'),
            spaceAfter=8,
            spaceBefore=8
        ))
        
        styles.add(ParagraphStyle(
            name='CustomBody',
            parent=styles['BodyText'],
            fontName=font_name,
            fontSize=9,
            textColor=HexColor('#4a4a4a'),
            spaceAfter=4,
            leading=12
        ))
        
        styles.add(ParagraphStyle(
            name='SceneTitle',
            parent=styles['Heading3'],
            fontName=font_name,
            fontSize=10,
            textColor=HexColor('#2980b9'),
            spaceAfter=4
        ))
        
        return styles
    
    def generate_pdf(self, planning_data, output_buffer=None):
        """  PDF """
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
        
        #   (  )
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
        
        # 4.    ( )
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
            [' ', project_info.get('type', 'N/A')],
            [' ', project_info.get('target_audience', 'N/A')],
            ['', project_info.get('duration', 'N/A')],
            ['', project_info.get('genre', 'N/A')]
        ]
        
        right_column_data = [
            ['', project_info.get('concept', 'N/A')],
            ['', project_info.get('tone_manner', 'N/A')],
            [' ', project_info.get('key_message', 'N/A')],
            ['', project_info.get('mood', 'N/A')]
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
    
    def _create_overview_section(self, planning_data):
        """   """
        elements = []
        
        elements.append(Paragraph(' ', self.styles['CustomHeading']))
        
        #  
        planning_text = planning_data.get('planning_text', '')
        if planning_text:
            elements.append(Paragraph(' ', self.styles['CustomSubHeading']))
            elements.append(Paragraph(planning_text, self.styles['CustomBody']))
            elements.append(Spacer(1, 0.5*cm))
        
        # 
        concept = planning_data.get('concept', '')
        if concept:
            elements.append(Paragraph('', self.styles['CustomSubHeading']))
            elements.append(Paragraph(concept, self.styles['CustomBody']))
            elements.append(Spacer(1, 0.5*cm))
        
        # 
        tone = planning_data.get('tone', '')
        if tone:
            elements.append(Paragraph('', self.styles['CustomSubHeading']))
            elements.append(Paragraph(tone, self.styles['CustomBody']))
        
        return elements
    
    def _create_story_section(self, planning_data):
        """   """
        elements = []
        
        elements.append(Paragraph(' ', self.styles['CustomHeading']))
        
        stories = planning_data.get('stories', [])
        story_phases = ['', '', '', '']
        
        for idx, story in enumerate(stories):
            phase = story_phases[idx] if idx < 4 else f' {idx+1}'
            
            #   
            phase_title = f"{phase} - {story.get('phase', '')}"
            elements.append(Paragraph(phase_title, self.styles['CustomSubHeading']))
            
            #  
            content = story.get('content', '')
            if content:
                elements.append(Paragraph(content, self.styles['CustomBody']))
            
            #  
            key_point = story.get('key_point', '')
            if key_point:
                elements.append(Paragraph(f" : {key_point}", self.styles['CustomBody']))
            
            elements.append(Spacer(1, 0.5*cm))
        
        return elements
    
    def _create_scenes_section(self, planning_data):
        """   """
        elements = []
        
        elements.append(Paragraph(' ', self.styles['CustomHeading']))
        
        scenes = planning_data.get('scenes', [])
        
        for idx, scene in enumerate(scenes):
            #  
            scene_title = f" {idx + 1}: {scene.get('title', '')}"
            elements.append(Paragraph(scene_title, self.styles['SceneTitle']))
            
            #    
            storyboard = scene.get('storyboard', {})
            image_url = storyboard.get('image_url')
            
            if image_url and image_url != 'generated_image_placeholder':
                try:
                    #    
                    img_element = self._create_image_element(image_url)
                    if img_element:
                        elements.append(img_element)
                        elements.append(Spacer(1, 0.3*cm))
                except Exception as e:
                    logger.error(f"  : {str(e)}")
            
            #  
            description = storyboard.get('description_kr') or scene.get('description', '')
            if description:
                elements.append(Paragraph(description, self.styles['CustomBody']))
            
            #  
            visual_desc = storyboard.get('visual_description', '')
            if visual_desc and visual_desc != description:
                elements.append(Paragraph(f" : {visual_desc}", self.styles['CustomBody']))
            
            elements.append(Spacer(1, 0.8*cm))
            
            #     
            if (idx + 1) % 3 == 0 and idx < len(scenes) - 1:
                elements.append(PageBreak())
        
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
            rl_image = Image(tmp_path, width=new_width, height=new_height)
            
            #   
            os.unlink(tmp_path)
            
            return rl_image
            
        except Exception as e:
            logger.error(f"   : {str(e)}")
            return None
    
    def _create_compressed_layout(self, planning_data):
        """    """
        elements = []
        
        #      ( 2 )
        title = planning_data.get('title', ' ')
        elements.append(Paragraph(title, self.styles['CustomTitle']))
        elements.append(Spacer(1, 0.5*cm))
        
        #   2  
        info_data = []
        info_data.append(['', planning_data.get('genre', 'N/A'), '', planning_data.get('target', 'N/A')])
        info_data.append(['', planning_data.get('duration', 'N/A'), '', planning_data.get('purpose', 'N/A')])
        
        info_table = Table(info_data, colWidths=[3*cm, 5*cm, 3*cm, 5*cm])
        info_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'HYGothic-Medium'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), HexColor('#2c3e50')),
            ('TEXTCOLOR', (1, 0), (1, -1), HexColor('#4a4a4a')),
            ('TEXTCOLOR', (2, 0), (2, -1), HexColor('#2c3e50')),
            ('TEXTCOLOR', (3, 0), (3, -1), HexColor('#4a4a4a')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BACKGROUND', (0, 0), (-1, -1), HexColor('#f8f9fa')),
            ('BOX', (0, 0), (-1, -1), 0.5, HexColor('#e0e0e0')),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 0.5*cm))
        
        #     ( )
        concept_data = []
        planning_text = planning_data.get('planning_text', '')[:200] + '...' if len(planning_data.get('planning_text', '')) > 200 else planning_data.get('planning_text', '')
        concept = planning_data.get('concept', '')
        
        if planning_text or concept:
            concept_row = []
            if planning_text:
                concept_row.append(Paragraph(f"<b>:</b> {planning_text}", self.styles['CustomBody']))
            if concept:
                concept_row.append(Paragraph(f"<b>:</b> {concept}", self.styles['CustomBody']))
            
            if concept_row:
                concept_table = Table([concept_row], colWidths=[12*cm, 12*cm] if len(concept_row) > 1 else [24*cm])
                concept_table.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ]))
                elements.append(concept_table)
                elements.append(Spacer(1, 0.3*cm))
        
        #   () -  4
        stories = planning_data.get('stories', [])
        if stories:
            elements.append(Paragraph(' ', self.styles['CustomSubHeading']))
            story_data = []
            story_row = []
            story_phases = ['', '', '', '']
            
            for idx, story in enumerate(stories[:4]):
                phase = story_phases[idx] if idx < 4 else f' {idx+1}'
                content = story.get('content', '')[:100] + '...' if len(story.get('content', '')) > 100 else story.get('content', '')
                story_cell = Paragraph(f"<b>{phase}</b><br/>{content}", self.styles['CustomBody'])
                story_row.append(story_cell)
            
            if story_row:
                story_table = Table([story_row], colWidths=[6*cm, 6*cm, 6*cm, 6*cm])
                story_table.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('BOX', (0, 0), (-1, -1), 0.5, HexColor('#e0e0e0')),
                    ('INNERGRID', (0, 0), (-1, -1), 0.5, HexColor('#e0e0e0')),
                    ('BACKGROUND', (0, 0), (-1, -1), HexColor('#f8f9fa')),
                    ('LEFTPADDING', (0, 0), (-1, -1), 8),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                    ('TOPPADDING', (0, 0), (-1, -1), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ]))
                elements.append(story_table)
                elements.append(Spacer(1, 0.5*cm))
        
        #   ( )
        scenes = planning_data.get('scenes', [])
        if scenes:
            elements.append(Paragraph(' ', self.styles['CustomSubHeading']))
            
            # 3   
            scene_rows = []
            current_row = []
            
            for idx, scene in enumerate(scenes):
                scene_content = []
                scene_title = f" {idx + 1}"
                if scene.get('location'):
                    scene_title += f" - {scene.get('location')}"
                
                scene_content.append(Paragraph(scene_title, self.styles['SceneTitle']))
                
                description = scene.get('description', scene.get('action', ''))[:80] + '...' if len(scene.get('description', scene.get('action', ''))) > 80 else scene.get('description', scene.get('action', ''))
                if description:
                    scene_content.append(Paragraph(description, ParagraphStyle(
                        'CompactBody',
                        parent=self.styles['CustomBody'],
                        fontSize=9,
                        leading=11
                    )))
                
                #     
                storyboard = scene.get('storyboard', {})
                image_url = storyboard.get('image_url')
                if image_url and image_url != 'generated_image_placeholder':
                    img_element = self._create_image_element(image_url, max_width=4*cm, max_height=3*cm)
                    if img_element:
                        scene_content.append(img_element)
                
                current_row.append(scene_content)
                
                if len(current_row) == 3 or idx == len(scenes) - 1:
                    #   
                    while len(current_row) < 3:
                        current_row.append('')
                    scene_rows.append(current_row)
                    current_row = []
            
            if scene_rows:
                scene_table = Table(scene_rows, colWidths=[8*cm, 8*cm, 8*cm])
                scene_table.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('BOX', (0, 0), (-1, -1), 0.5, HexColor('#e0e0e0')),
                    ('INNERGRID', (0, 0), (-1, -1), 0.5, HexColor('#e0e0e0')),
                    ('LEFTPADDING', (0, 0), (-1, -1), 8),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                    ('TOPPADDING', (0, 0), (-1, -1), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ]))
                elements.append(scene_table)
        
        return elements
    
    def generate_storyboard_only_pdf(self, planning_data, output_buffer=None):
        """    PDF """
        if output_buffer is None:
            output_buffer = io.BytesIO()
        
        #   PDF 
        doc = SimpleDocTemplate(
            output_buffer,
            pagesize=landscape(A4),
            rightMargin=1*cm,
            leftMargin=1*cm,
            topMargin=1*cm,
            bottomMargin=1*cm
        )
        
        story = []
        
        # 
        title = planning_data.get('title', '')
        story.append(Paragraph(title, self.styles['CustomTitle']))
        story.append(Spacer(1, 1*cm))
        
        #  
        scenes = planning_data.get('scenes', [])
        scenes_per_page = 2  #   2 
        
        for idx, scene in enumerate(scenes):
            if idx > 0 and idx % scenes_per_page == 0:
                story.append(PageBreak())
            
            #  
            scene_title = f" {idx + 1}"
            story.append(Paragraph(scene_title, self.styles['SceneTitle']))
            
            #  
            storyboard = scene.get('storyboard', {})
            image_url = storyboard.get('image_url')
            
            if image_url and image_url != 'generated_image_placeholder':
                img_element = self._create_image_element(image_url, max_width=18*cm, max_height=10*cm)
                if img_element:
                    story.append(img_element)
            
            # 
            description = storyboard.get('description_kr', scene.get('description', ''))
            if description:
                story.append(Paragraph(description, self.styles['CustomBody']))
            
            story.append(Spacer(1, 1*cm))
        
        doc.build(story)
        output_buffer.seek(0)
        
        return output_buffer