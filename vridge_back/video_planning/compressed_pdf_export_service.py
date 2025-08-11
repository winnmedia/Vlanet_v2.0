import os
import io
import logging
import re
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm, mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak, KeepTogether, Flowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.lib.colors import HexColor, white, black, lightgrey, grey
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib import colors
import requests
from PIL import Image as PILImage
from io import BytesIO
import tempfile
from datetime import datetime
from .gemini_service import GeminiService

logger = logging.getLogger(__name__)


class CompressedPDFExportService:
    """   PDF  """
    
    def __init__(self):
        self.page_width, self.page_height = A4  #  A4  (    )
        self.margin = 1.5*cm  #  
        self.content_width = self.page_width - (2 * self.margin)
        self.setup_fonts()
        self.styles = self.setup_styles()
        self.gemini_service = GeminiService()
    
    def setup_fonts(self):
        """  """
        try:
            pdfmetrics.registerFont(UnicodeCIDFont('HYGothic-Medium'))
            pdfmetrics.registerFont(UnicodeCIDFont('HYSMyeongJo-Medium'))
            logger.info("   ")
        except Exception as e:
            logger.warning(f"  : {str(e)}")
    
    def setup_styles(self):
        """PDF   -  """
        styles = getSampleStyleSheet()
        
        korean_font = 'HYGothic-Medium'
        
        #   ( )
        styles.add(ParagraphStyle(
            name='CompactTitle',
            parent=styles['Title'],
            fontName=korean_font,
            fontSize=20,
            textColor=HexColor('#1631F8'),
            spaceAfter=10,
            spaceBefore=5,
            alignment=TA_CENTER,
            leading=24
        ))
        
        #   
        styles.add(ParagraphStyle(
            name='CompactSection',
            parent=styles['Heading1'],
            fontName=korean_font,
            fontSize=14,
            textColor=HexColor('#2c3e50'),
            spaceAfter=8,
            spaceBefore=12,
            leading=18,
            borderWidth=0,
            borderPadding=0,
            backColor=HexColor('#f0f4ff'),
            borderColor=HexColor('#1631F8'),
            borderRadius=4
        ))
        
        #   
        styles.add(ParagraphStyle(
            name='CompactSubSection',
            parent=styles['Heading2'],
            fontName=korean_font,
            fontSize=11,
            textColor=HexColor('#34495e'),
            spaceAfter=5,
            spaceBefore=8,
            leading=14
        ))
        
        #   ( )
        styles.add(ParagraphStyle(
            name='CompactBody',
            parent=styles['Normal'],
            fontName=korean_font,
            fontSize=9,
            textColor=HexColor('#2c3e50'),
            spaceAfter=4,
            leading=12,
            alignment=TA_JUSTIFY
        ))
        
        #  
        styles.add(ParagraphStyle(
            name='CompactTable',
            parent=styles['Normal'],
            fontName=korean_font,
            fontSize=8,
            textColor=HexColor('#2c3e50'),
            spaceAfter=2,
            leading=10,
            alignment=TA_LEFT
        ))
        
        #  
        styles.add(ParagraphStyle(
            name='CompactCaption',
            parent=styles['Normal'],
            fontName=korean_font,
            fontSize=7,
            textColor=HexColor('#7f8c8d'),
            spaceAfter=2,
            leading=9,
            alignment=TA_CENTER
        ))
        
        return styles
    
    def generate_pdf(self, planning_data, output_buffer=None):
        """ PDF """
        if output_buffer is None:
            output_buffer = io.BytesIO()
        
        # A4   
        doc = SimpleDocTemplate(
            output_buffer,
            pagesize=A4,
            rightMargin=self.margin,
            leftMargin=self.margin,
            topMargin=self.margin,
            bottomMargin=self.margin,
            title=planning_data.get('title', ' '),
            author='VideoPlanet'
        )
        
        story = []
        
        # LLM   
        summary_result = self.gemini_service.summarize_for_pdf(planning_data)
        
        if summary_result['success']:
            #    PDF 
            story.extend(self._create_compressed_content(planning_data, summary_result))
        else:
            #      
            story.extend(self._create_default_compressed_content(planning_data))
        
        # PDF 
        try:
            doc.build(story, onFirstPage=self._add_header_footer, onLaterPages=self._add_header_footer)
            output_buffer.seek(0)
            logger.info(" PDF  ")
            return output_buffer
        except Exception as e:
            logger.error(f"PDF  : {str(e)}")
            raise
    
    def _create_compressed_content(self, planning_data, summary_result):
        """LLM     """
        elements = []
        summary_text = summary_result['summary']
        
        # 1:    
        elements.append(Paragraph(planning_data.get('title', ' '), self.styles['CompactTitle']))
        elements.append(Spacer(1, 5*mm))
        
        #   
        concept_match = re.search(r'1\.\s*\*\* \*\*[:\s]*(.+)', summary_text)
        if concept_match:
            concept = concept_match.group(1).strip()
            elements.append(Paragraph(f"<b> :</b> {concept}", self.styles['CompactBody']))
            elements.append(Spacer(1, 5*mm))
        
        #   
        elements.append(Paragraph(" ", self.styles['CompactSection']))
        spec_table_data = self._extract_spec_table(summary_result['original_settings'])
        
        spec_table = Table(spec_table_data, colWidths=[4*cm, 5*cm, 4*cm, 5*cm])
        spec_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'HYGothic-Medium'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (0, -1), HexColor('#f0f4ff')),
            ('BACKGROUND', (2, 0), (2, -1), HexColor('#f0f4ff')),
            ('TEXTCOLOR', (0, 0), (-1, -1), HexColor('#2c3e50')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#e0e0e0')),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        elements.append(spec_table)
        elements.append(Spacer(1, 5*mm))
        
        #  
        story_match = re.search(r'3\.\s*\*\* \*\*[:\s]*(.+?)(?=4\.|$)', summary_text, re.DOTALL)
        if story_match:
            story_summary = story_match.group(1).strip()
            elements.append(Paragraph(" ", self.styles['CompactSection']))
            elements.append(Paragraph(story_summary, self.styles['CompactBody']))
            elements.append(Spacer(1, 5*mm))
        
        #   (  )
        elements.append(Paragraph(" ", self.styles['CompactSection']))
        scene_table_data = self._create_compressed_scene_table(planning_data, summary_text)
        
        scene_table = Table(scene_table_data, colWidths=[1.5*cm, 3*cm, 8*cm, 5.5*cm])
        scene_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'HYGothic-Medium'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1631F8')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('TEXTCOLOR', (0, 1), (-1, -1), HexColor('#2c3e50')),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#e0e0e0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, HexColor('#f8f9fa')]),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(scene_table)
        
        #  
        notes_match = re.search(r'5\.\s*\*\* \*\*[:\s]*(.+)', summary_text, re.DOTALL)
        if notes_match:
            elements.append(Spacer(1, 5*mm))
            elements.append(Paragraph(" ", self.styles['CompactSection']))
            elements.append(Paragraph(notes_match.group(1).strip(), self.styles['CompactBody']))
        
        return elements
    
    def _create_default_compressed_content(self, planning_data):
        """    (LLM  )"""
        elements = []
        
        # 
        elements.append(Paragraph(planning_data.get('title', ' '), self.styles['CompactTitle']))
        elements.append(Spacer(1, 5*mm))
        
        #   
        elements.append(Paragraph(" ", self.styles['CompactSection']))
        
        info_data = []
        if planning_data.get('genre'):
            info_data.append(['', planning_data.get('genre', '-'), '', planning_data.get('target', '-')])
        if planning_data.get('duration'):
            info_data.append(['', planning_data.get('duration', '-'), '', planning_data.get('tone', '-')])
        if planning_data.get('purpose'):
            info_data.append(['', planning_data.get('purpose', '-'), '', planning_data.get('concept', '-')])
        
        if info_data:
            info_table = Table(info_data, colWidths=[3*cm, 6*cm, 3*cm, 6*cm])
            info_table.setStyle(self._get_compact_table_style())
            elements.append(info_table)
            elements.append(Spacer(1, 5*mm))
        
        #  
        if planning_data.get('stories'):
            elements.append(Paragraph(" ", self.styles['CompactSection']))
            story_data = [['', '']]
            for story in planning_data.get('stories', []):
                story_data.append([
                    story.get('stage', ''),
                    Paragraph(story.get('content', ''), self.styles['CompactTable'])
                ])
            
            story_table = Table(story_data, colWidths=[2*cm, 16*cm])
            story_table.setStyle(self._get_compact_table_style())
            elements.append(story_table)
            elements.append(Spacer(1, 5*mm))
        
        #   
        if planning_data.get('scenes'):
            elements.append(Paragraph(" ", self.styles['CompactSection']))
            scene_data = [['#', '', '', '']]
            
            for idx, scene in enumerate(planning_data.get('scenes', [])):
                scene_data.append([
                    str(idx + 1),
                    scene.get('title', ''),
                    Paragraph(scene.get('description', '')[:100] + '...', self.styles['CompactTable']),
                    scene.get('duration', '')
                ])
            
            scene_table = Table(scene_data, colWidths=[1*cm, 3*cm, 11*cm, 3*cm])
            scene_table.setStyle(self._get_compact_table_style())
            elements.append(scene_table)
        
        return elements
    
    def _extract_spec_table(self, settings):
        """   """
        data = []
        
        #  
        data.append(['', settings.get('genre', '-'), '', settings.get('target', '-')])
        data.append(['', settings.get('duration', '-'), '', settings.get('tone', '-')])
        data.append(['', settings.get('concept', '-'), '', settings.get('purpose', '-')])
        
        #  
        data.append(['', settings.get('aspectRatio', '-'), '', settings.get('platform', '-')])
        data.append(['', settings.get('colorTone', '-'), '', settings.get('editingStyle', '-')])
        
        #  
        if settings.get('characterName'):
            data.append(['', settings.get('characterName', '-'), '', settings.get('storyFramework', '-')])
        
        return data
    
    def _create_compressed_scene_table(self, planning_data, summary_text):
        """   """
        data = [['#', ' ', ' ', '']]
        
        #    
        scene_points = {}
        scene_match = re.search(r'4\.\s*\*\*  \*\*[:\s]*(.+?)(?=5\.|$)', summary_text, re.DOTALL)
        if scene_match:
            scene_text = scene_match.group(1)
            #  
            for line in scene_text.split('\n'):
                if '' in line and ':' in line:
                    match = re.search(r'\s*(\d+)[:\s]*(.+)', line)
                    if match:
                        scene_num = int(match.group(1))
                        scene_points[scene_num - 1] = match.group(2).strip()
        
        for idx, scene in enumerate(planning_data.get('scenes', [])):
            #   (LLM    )
            if idx in scene_points:
                core_content = scene_points[idx]
            else:
                core_content = scene.get('description', '')[:80] + '...'
            
            #  
            storyboard_info = ''
            if scene.get('storyboard') and scene['storyboard'].get('image_url'):
                if scene['storyboard']['image_url'] != 'generated_image_placeholder':
                    storyboard_info = ''
            
            data.append([
                str(idx + 1),
                scene.get('title', f' {idx + 1}'),
                Paragraph(core_content, self.styles['CompactTable']),
                storyboard_info
            ])
        
        return data
    
    def _get_compact_table_style(self):
        """  """
        return TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'HYGothic-Medium'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#34495e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('TEXTCOLOR', (0, 1), (-1, -1), HexColor('#2c3e50')),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#e0e0e0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, HexColor('#f8f9fa')]),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ])
    
    def _add_header_footer(self, canvas, doc):
        """  """
        canvas.saveState()
        
        #  -   
        canvas.setFont('HYGothic-Medium', 8)
        canvas.setFillColor(HexColor('#7f8c8d'))
        canvas.drawString(self.margin, self.page_height - self.margin/2, "VideoPlanet")
        canvas.drawRightString(self.page_width - self.margin, self.page_height - self.margin/2, 
                              datetime.now().strftime('%Y.%m.%d'))
        
        #  -  
        canvas.drawCentredString(self.page_width/2, self.margin/2, f"- {doc.page} -")
        
        canvas.restoreState()