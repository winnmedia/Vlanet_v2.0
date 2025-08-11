import os
import io
import logging
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm, mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.colors import HexColor, white, black, lightgrey
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
import requests
from PIL import Image as PILImage
from io import BytesIO
import tempfile
from datetime import datetime

logger = logging.getLogger(__name__)


class EnhancedPDFExportService:
    """   PDF  """
    
    def __init__(self):
        self.page_width, self.page_height = landscape(A4)  #  A4
        self.margin = 2*cm
        self.content_width = self.page_width - (2 * self.margin)
        self.setup_fonts()
        self.styles = self.setup_styles()
    
    def setup_fonts(self):
        """  """
        try:
            # CID   ( )
            pdfmetrics.registerFont(UnicodeCIDFont('HYGothic-Medium'))
            pdfmetrics.registerFont(UnicodeCIDFont('HYSMyeongJo-Medium'))
            logger.info("   ")
        except Exception as e:
            logger.warning(f"  : {str(e)}")
    
    def setup_styles(self):
        """PDF  """
        styles = getSampleStyleSheet()
        
        #   
        korean_font = 'HYGothic-Medium'
        
        #  
        styles.add(ParagraphStyle(
            name='MainTitle',
            parent=styles['Title'],
            fontName=korean_font,
            fontSize=28,
            textColor=HexColor('#1631F8'),
            spaceAfter=20,
            spaceBefore=10,
            alignment=TA_CENTER,
            leading=34
        ))
        
        #   
        styles.add(ParagraphStyle(
            name='SectionTitle',
            parent=styles['Heading1'],
            fontName=korean_font,
            fontSize=18,
            textColor=HexColor('#2c3e50'),
            spaceAfter=12,
            spaceBefore=20,
            leading=22
        ))
        
        #   
        styles.add(ParagraphStyle(
            name='SubTitle',
            parent=styles['Heading2'],
            fontName=korean_font,
            fontSize=14,
            textColor=HexColor('#34495e'),
            spaceAfter=8,
            spaceBefore=10,
            leading=18
        ))
        
        #  
        styles.add(ParagraphStyle(
            name='BodyText',
            parent=styles['Normal'],
            fontName=korean_font,
            fontSize=10,
            textColor=HexColor('#2c3e50'),
            spaceAfter=6,
            leading=14,
            alignment=TA_LEFT
        ))
        
        #   
        styles.add(ParagraphStyle(
            name='TableHeader',
            parent=styles['Normal'],
            fontName=korean_font,
            fontSize=11,
            textColor=white,
            alignment=TA_CENTER,
            leading=14
        ))
        
        #   
        styles.add(ParagraphStyle(
            name='TableCell',
            parent=styles['Normal'],
            fontName=korean_font,
            fontSize=10,
            textColor=HexColor('#2c3e50'),
            alignment=TA_LEFT,
            leading=13
        ))
        
        return styles
    
    def generate_pdf(self, planning_data, output_buffer=None):
        """ PDF """
        if output_buffer is None:
            output_buffer = io.BytesIO()
        
        #  A4  
        doc = SimpleDocTemplate(
            output_buffer,
            pagesize=landscape(A4),
            rightMargin=self.margin,
            leftMargin=self.margin,
            topMargin=self.margin,
            bottomMargin=self.margin,
            title=planning_data.get('title', ' ')
        )
        
        #  
        story = []
        
        # 1.  
        story.extend(self._create_cover_page(planning_data))
        story.append(PageBreak())
        
        # 2.   
        story.extend(self._create_project_overview(planning_data))
        story.append(Spacer(1, 15*mm))
        
        # 3.   
        story.extend(self._create_story_table(planning_data))
        story.append(PageBreak())
        
        # 4.   
        story.extend(self._create_scenes_table(planning_data))
        
        # PDF 
        try:
            doc.build(story)
            output_buffer.seek(0)
            logger.info("PDF  ")
            return output_buffer
        except Exception as e:
            logger.error(f"PDF  : {str(e)}")
            raise
    
    def _create_cover_page(self, planning_data):
        """  """
        elements = []
        
        #  
        title = planning_data.get('title', ' ')
        elements.append(Paragraph(title, self.styles['MainTitle']))
        elements.append(Spacer(1, 30*mm))
        
        #    
        info_data = [
            ['', title],
            ['', planning_data.get('genre', '-')],
            [' ', planning_data.get('target', '-')],
            ['', planning_data.get('duration', '-')],
            [' ', planning_data.get('purpose', '-')],
            ['', planning_data.get('tone', '-')],
            ['', datetime.now().strftime('%Y %m %d')]
        ]
        
        #   
        info_table = Table(info_data, colWidths=[6*cm, 12*cm])
        info_table.setStyle(TableStyle([
            #  
            ('FONTNAME', (0, 0), (0, -1), 'HYGothic-Medium'),
            ('FONTNAME', (1, 0), (1, -1), 'HYGothic-Medium'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            
            # 
            ('BACKGROUND', (0, 0), (0, -1), HexColor('#1631F8')),
            ('TEXTCOLOR', (0, 0), (0, -1), white),
            ('BACKGROUND', (1, 0), (1, -1), HexColor('#f8f9fa')),
            ('TEXTCOLOR', (1, 0), (1, -1), HexColor('#2c3e50')),
            
            # 
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # 
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#dee2e6')),
            ('LINEWIDTH', (0, 0), (-1, -1), 0.5),
            
            # 
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        
        elements.append(info_table)
        elements.append(Spacer(1, 20*mm))
        
        #  
        planning_text = planning_data.get('planning_text', '')
        if planning_text:
            elements.append(Paragraph(' ', self.styles['SectionTitle']))
            elements.append(Paragraph(planning_text, self.styles['BodyText']))
        
        return elements
    
    def _create_project_overview(self, planning_data):
        """  """
        elements = []
        
        elements.append(Paragraph(' ', self.styles['SectionTitle']))
        
        #    
        overview_data = []
        
        if planning_data.get('concept'):
            overview_data.append(['', planning_data['concept']])
        
        if planning_data.get('story_framework'):
            framework_map = {
                'hook_immersion': '---',
                'classic': ' ',
                'pixar': ' ',
                'deductive': ' ',
                'inductive': ' ',
                'documentary': ' '
            }
            framework_name = framework_map.get(planning_data['story_framework'], planning_data['story_framework'])
            overview_data.append([' ', framework_name])
        
        if planning_data.get('development_level'):
            level_map = {
                'minimal': ' ',
                'light': ' ',
                'balanced': ' ',
                'detailed': ' '
            }
            level_name = level_map.get(planning_data['development_level'], planning_data['development_level'])
            overview_data.append([' ', level_name])
        
        if overview_data:
            overview_table = Table(overview_data, colWidths=[6*cm, 18*cm])
            overview_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'HYGothic-Medium'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('BACKGROUND', (0, 0), (0, -1), HexColor('#e9ecef')),
                ('ALIGN', (0, 0), (0, -1), 'CENTER'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 1, HexColor('#dee2e6')),
                ('LEFTPADDING', (0, 0), (-1, -1), 12),
                ('RIGHTPADDING', (0, 0), (-1, -1), 12),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            elements.append(overview_table)
        
        return elements
    
    def _create_story_table(self, planning_data):
        """   """
        elements = []
        
        elements.append(Paragraph('  ()', self.styles['SectionTitle']))
        
        stories = planning_data.get('stories', [])
        if not stories:
            elements.append(Paragraph('   .', self.styles['BodyText']))
            return elements
        
        #  
        story_data = [
            [
                Paragraph('', self.styles['TableHeader']),
                Paragraph('', self.styles['TableHeader']),
                Paragraph(' ', self.styles['TableHeader']),
                Paragraph('', self.styles['TableHeader'])
            ]
        ]
        
        #   
        for story in stories[:4]:  #  4
            stage = story.get('stage', '')
            stage_name = story.get('stage_name', '')
            stage_display = f"{stage}\n({stage_name})" if stage_name else stage
            
            title = story.get('title', '')
            key_content = story.get('key_content', '')
            summary = story.get('summary', '')
            
            story_data.append([
                Paragraph(stage_display, self.styles['TableCell']),
                Paragraph(title, self.styles['TableCell']),
                Paragraph(key_content, self.styles['TableCell']),
                Paragraph(summary, self.styles['TableCell'])
            ])
        
        #  
        story_table = Table(story_data, colWidths=[3*cm, 5*cm, 8*cm, 8*cm])
        story_table.setStyle(TableStyle([
            #  
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1631F8')),
            ('FONTNAME', (0, 0), (-1, 0), 'HYGothic-Medium'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            
            #   
            ('FONTNAME', (0, 1), (-1, -1), 'HYGothic-Medium'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BACKGROUND', (0, 1), (-1, -1), white),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, HexColor('#f8f9fa')]),
            
            # 
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            
            # 
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#dee2e6')),
            ('LINEWIDTH', (0, 0), (-1, -1), 0.5),
            
            # 
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(story_table)
        
        return elements
    
    def _create_scenes_table(self, planning_data):
        """   """
        elements = []
        
        elements.append(Paragraph('  ', self.styles['SectionTitle']))
        
        scenes = planning_data.get('scenes', [])
        if not scenes:
            elements.append(Paragraph('   .', self.styles['BodyText']))
            return elements
        
        #     ( 6)
        scenes_per_page = 6
        for page_start in range(0, len(scenes), scenes_per_page):
            page_scenes = scenes[page_start:page_start + scenes_per_page]
            
            #  
            scene_data = [
                [
                    Paragraph('', self.styles['TableHeader']),
                    Paragraph('', self.styles['TableHeader']),
                    Paragraph('/', self.styles['TableHeader']),
                    Paragraph('/', self.styles['TableHeader']),
                    Paragraph('', self.styles['TableHeader'])
                ]
            ]
            
            #   
            for idx, scene in enumerate(page_scenes):
                scene_number = page_start + idx + 1
                
                #   
                storyboard_cell = self._create_storyboard_cell(scene)
                
                # / 
                location = scene.get('location', '')
                time = scene.get('time', '')
                location_time = f"{location}\n({time})" if time else location
                
                #  
                action = scene.get('action', '')
                dialogue = scene.get('dialogue', '')
                action_dialogue = f": {action}\n: {dialogue}" if dialogue else f": {action}"
                
                # 
                purpose = scene.get('purpose', '')
                
                scene_data.append([
                    Paragraph(f" {scene_number}", self.styles['TableCell']),
                    storyboard_cell,
                    Paragraph(location_time, self.styles['TableCell']),
                    Paragraph(action_dialogue, self.styles['TableCell']),
                    Paragraph(purpose, self.styles['TableCell'])
                ])
            
            #  
            scene_table = Table(scene_data, colWidths=[2*cm, 6*cm, 4*cm, 6*cm, 6*cm])
            scene_table.setStyle(TableStyle([
                #  
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1631F8')),
                ('FONTNAME', (0, 0), (-1, 0), 'HYGothic-Medium'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('TEXTCOLOR', (0, 0), (-1, 0), white),
                
                #   
                ('FONTNAME', (0, 1), (-1, -1), 'HYGothic-Medium'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('BACKGROUND', (0, 1), (-1, -1), white),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, HexColor('#f8f9fa')]),
                
                # 
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                
                # 
                ('GRID', (0, 0), (-1, -1), 1, HexColor('#dee2e6')),
                ('LINEWIDTH', (0, 0), (-1, -1), 0.5),
                
                # 
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                
                #   
                ('ROWSIZE', (0, 1), (-1, -1), 4*cm),
            ]))
            
            elements.append(scene_table)
            
            #     
            if page_start + scenes_per_page < len(scenes):
                elements.append(PageBreak())
        
        return elements
    
    def _create_storyboard_cell(self, scene):
        """   """
        storyboard = scene.get('storyboard', {})
        image_url = storyboard.get('image_url')
        description = storyboard.get('description_kr', '')
        
        #   
        if image_url and image_url != 'generated_image_placeholder':
            try:
                img_element = self._create_small_image(image_url, max_width=5*cm, max_height=3*cm)
                if img_element:
                    return img_element
            except Exception as e:
                logger.warning(f"  : {str(e)}")
        
        #       
        if description:
            return Paragraph(description, self.styles['TableCell'])
        else:
            return Paragraph('  ', self.styles['TableCell'])
    
    def _create_small_image(self, image_url, max_width=5*cm, max_height=3*cm):
        """   """
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
            
            #     
            if aspect_ratio > max_width / max_height:
                new_width = max_width
                new_height = max_width / aspect_ratio
            else:
                new_height = max_height
                new_width = max_height * aspect_ratio
            
            #   
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                # RGB  (PDF )
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                #   
                img_resized = img.resize((int(new_width * 72 / cm), int(new_height * 72 / cm)), PILImage.Resampling.LANCZOS)
                img_resized.save(temp_file.name, 'JPEG', quality=85)
                
                # ReportLab Image 
                return Image(temp_file.name, width=new_width, height=new_height)
                
        except Exception as e:
            logger.error(f"  : {str(e)}")
            return None