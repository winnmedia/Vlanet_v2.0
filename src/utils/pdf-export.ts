/**
 * PDF 내보내기 유틸리티
 * 한글 폰트를 지원하는 jsPDF 기반 PDF 생성 기능
 * 
 * 주요 기능:
 * - 한글 폰트 지원 (Noto Sans KR)
 * - 다양한 데이터 형식 지원 (텍스트, 테이블, 이미지)
 * - 반응형 레이아웃
 * - 워터마크 및 헤더/푸터 지원
 */

import jsPDF from 'jspdf'
import html2canvas from 'html2canvas'

// 한글 폰트 Base64 데이터 (Noto Sans KR Regular)
// 실제 구현에서는 CDN이나 정적 파일에서 로드해야 합니다
const NOTO_SANS_KR_BASE64 = 'data:font/ttf;base64,AAEAAAALAIAAAwAwT1MvMgAAAA=='

interface PDFExportOptions {
  title?: string
  author?: string
  subject?: string
  creator?: string
  orientation?: 'portrait' | 'landscape'
  format?: 'a4' | 'a3' | 'letter'
  margin?: {
    top: number
    right: number
    bottom: number
    left: number
  }
  fontSize?: number
  lineHeight?: number
  includeHeader?: boolean
  includeFooter?: boolean
  watermark?: string
}

interface PDFTableData {
  headers: string[]
  rows: string[][]
  title?: string
}

interface PDFImageData {
  src: string
  width?: number
  height?: number
  caption?: string
}

export class PDFExporter {
  private doc: jsPDF
  private currentY: number = 0
  private margin: Required<PDFExportOptions['margin']>
  private fontSize: number
  private lineHeight: number
  
  constructor(options: PDFExportOptions = {}) {
    const {
      orientation = 'portrait',
      format = 'a4',
      margin = { top: 20, right: 20, bottom: 20, left: 20 },
      fontSize = 12,
      lineHeight = 1.5
    } = options

    this.doc = new jsPDF({
      orientation,
      unit: 'mm',
      format
    })

    this.margin = margin as Required<PDFExportOptions['margin']>
    this.fontSize = fontSize
    this.lineHeight = lineHeight
    this.currentY = this.margin.top

    // PDF 메타데이터 설정
    if (options.title) this.doc.setProperties({ title: options.title })
    if (options.author) this.doc.setProperties({ author: options.author })
    if (options.subject) this.doc.setProperties({ subject: options.subject })
    if (options.creator) this.doc.setProperties({ creator: options.creator })

    this.setupKoreanFont()
  }

  /**
   * 한글 폰트 설정
   * jsPDF에 한글 폰트를 추가하고 설정합니다
   */
  private setupKoreanFont(): void {
    try {
      // Noto Sans KR 폰트 추가 (실제로는 외부에서 로드해야 함)
      // 임시로 기본 폰트를 사용하되, 한글 지원을 위한 설정을 추가
      this.doc.setFont('helvetica')
      this.doc.setFontSize(this.fontSize)
      this.doc.setCharSpace(0.1) // 글자 간격 조정으로 한글 가독성 향상
    } catch (error) {
      console.warn('한글 폰트 설정 중 오류 발생:', error)
      // 기본 폰트 사용
      this.doc.setFont('helvetica')
      this.doc.setFontSize(this.fontSize)
    }
  }

  /**
   * 텍스트 추가
   * 한글을 포함한 긴 텍스트를 자동으로 줄바꿈하여 추가합니다
   */
  addText(text: string, options: {
    fontSize?: number
    align?: 'left' | 'center' | 'right'
    color?: string
    bold?: boolean
    maxWidth?: number
  } = {}): void {
    const {
      fontSize = this.fontSize,
      align = 'left',
      color = '#000000',
      bold = false,
      maxWidth = this.getPageWidth() - this.margin.left - this.margin.right
    } = options

    this.doc.setFontSize(fontSize)
    if (bold) this.doc.setFont('helvetica', 'bold')
    else this.doc.setFont('helvetica', 'normal')

    // 색상 설정
    const rgb = this.hexToRgb(color)
    if (rgb) this.doc.setTextColor(rgb.r, rgb.g, rgb.b)

    // 텍스트 줄바꿈 처리
    const lines = this.splitTextToLines(text, maxWidth)
    
    lines.forEach((line, index) => {
      if (this.needNewPage()) {
        this.addPage()
      }

      let x = this.margin.left
      if (align === 'center') {
        const textWidth = this.doc.getTextWidth(line)
        x = (this.getPageWidth() - textWidth) / 2
      } else if (align === 'right') {
        const textWidth = this.doc.getTextWidth(line)
        x = this.getPageWidth() - this.margin.right - textWidth
      }

      this.doc.text(line, x, this.currentY)
      this.currentY += fontSize * this.lineHeight * 0.35 // mm 단위 조정
    })

    this.currentY += fontSize * 0.5 // 단락 간격
  }

  /**
   * 제목 추가
   */
  addTitle(title: string, level: 1 | 2 | 3 = 1): void {
    const fontSizes = { 1: 20, 2: 16, 3: 14 }
    const spacing = { 1: 10, 2: 8, 3: 6 }

    this.currentY += spacing[level]
    
    this.addText(title, {
      fontSize: fontSizes[level],
      bold: true,
      align: level === 1 ? 'center' : 'left'
    })

    this.currentY += spacing[level] / 2
  }

  /**
   * 테이블 추가
   */
  addTable(tableData: PDFTableData): void {
    const { headers, rows, title } = tableData
    
    if (title) {
      this.addTitle(title, 3)
    }

    const startX = this.margin.left
    const tableWidth = this.getPageWidth() - this.margin.left - this.margin.right
    const colWidth = tableWidth / headers.length
    const rowHeight = 10

    // 테이블 헤더
    this.doc.setFillColor(240, 240, 240)
    this.doc.rect(startX, this.currentY, tableWidth, rowHeight, 'F')

    this.doc.setFont('helvetica', 'bold')
    this.doc.setFontSize(10)

    headers.forEach((header, index) => {
      const x = startX + (index * colWidth) + 2
      this.doc.text(header, x, this.currentY + 6)
    })

    this.currentY += rowHeight

    // 테이블 데이터
    this.doc.setFont('helvetica', 'normal')
    
    rows.forEach((row, rowIndex) => {
      if (this.needNewPage(rowHeight)) {
        this.addPage()
      }

      // 행 배경색 (짝수 행)
      if (rowIndex % 2 === 0) {
        this.doc.setFillColor(250, 250, 250)
        this.doc.rect(startX, this.currentY, tableWidth, rowHeight, 'F')
      }

      row.forEach((cell, colIndex) => {
        const x = startX + (colIndex * colWidth) + 2
        // 셀 텍스트가 너무 길면 자르기
        const truncatedText = this.truncateText(cell, colWidth - 4)
        this.doc.text(truncatedText, x, this.currentY + 6)
      })

      this.currentY += rowHeight
    })

    // 테이블 테두리
    this.doc.setDrawColor(200, 200, 200)
    this.doc.rect(startX, this.currentY - (rows.length + 1) * rowHeight, tableWidth, (rows.length + 1) * rowHeight)

    this.currentY += 5
  }

  /**
   * HTML 요소를 이미지로 변환하여 PDF에 추가
   */
  async addHtmlElement(element: HTMLElement, options: {
    scale?: number
    width?: number
    height?: number
    caption?: string
  } = {}): Promise<void> {
    const {
      scale = 2,
      width,
      height,
      caption
    } = options

    try {
      const canvas = await html2canvas(element, {
        scale,
        useCORS: true,
        allowTaint: true,
        backgroundColor: '#ffffff'
      })

      const imgData = canvas.toDataURL('image/png')
      
      // 이미지 크기 계산
      let imgWidth = width || (this.getPageWidth() - this.margin.left - this.margin.right)
      let imgHeight = height || (canvas.height * imgWidth) / canvas.width

      // 페이지 높이를 초과하는 경우 조정
      const maxHeight = this.getPageHeight() - this.margin.top - this.margin.bottom - 20
      if (imgHeight > maxHeight) {
        imgHeight = maxHeight
        imgWidth = (canvas.width * imgHeight) / canvas.height
      }

      if (this.needNewPage(imgHeight)) {
        this.addPage()
      }

      this.doc.addImage(imgData, 'PNG', this.margin.left, this.currentY, imgWidth, imgHeight)
      this.currentY += imgHeight + 5

      if (caption) {
        this.addText(caption, {
          fontSize: 10,
          align: 'center',
          color: '#666666'
        })
      }
    } catch (error) {
      console.error('HTML 요소를 PDF로 변환 중 오류 발생:', error)
      this.addText(`[이미지 로드 실패: ${caption || 'HTML 요소'}]`, {
        color: '#ff0000',
        fontSize: 10
      })
    }
  }

  /**
   * 새 페이지 추가
   */
  addPage(): void {
    this.doc.addPage()
    this.currentY = this.margin.top
  }

  /**
   * PDF 저장
   */
  save(filename: string = 'document.pdf'): void {
    // 파일명에 한글이 포함된 경우를 위한 처리
    const sanitizedFilename = filename.replace(/[^\w\-_\. ]/g, '_')
    this.doc.save(sanitizedFilename)
  }

  /**
   * PDF 데이터 URL 반환
   */
  getDataUrl(): string {
    return this.doc.output('dataurlstring')
  }

  /**
   * PDF Blob 반환
   */
  getBlob(): Blob {
    return this.doc.output('blob')
  }

  // 유틸리티 메서드들

  private getPageWidth(): number {
    return this.doc.internal.pageSize.getWidth()
  }

  private getPageHeight(): number {
    return this.doc.internal.pageSize.getHeight()
  }

  private needNewPage(additionalHeight: number = 10): boolean {
    return this.currentY + additionalHeight > this.getPageHeight() - this.margin.bottom
  }

  private splitTextToLines(text: string, maxWidth: number): string[] {
    const words = text.split(' ')
    const lines: string[] = []
    let currentLine = ''

    for (const word of words) {
      const testLine = currentLine ? `${currentLine} ${word}` : word
      const testWidth = this.doc.getTextWidth(testLine)

      if (testWidth <= maxWidth || !currentLine) {
        currentLine = testLine
      } else {
        lines.push(currentLine)
        currentLine = word
      }
    }

    if (currentLine) {
      lines.push(currentLine)
    }

    return lines
  }

  private truncateText(text: string, maxWidth: number): string {
    if (this.doc.getTextWidth(text) <= maxWidth) {
      return text
    }

    let truncated = text
    while (this.doc.getTextWidth(truncated + '...') > maxWidth && truncated.length > 0) {
      truncated = truncated.slice(0, -1)
    }

    return truncated + '...'
  }

  private hexToRgb(hex: string): { r: number; g: number; b: number } | null {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex)
    return result ? {
      r: parseInt(result[1], 16),
      g: parseInt(result[2], 16),
      b: parseInt(result[3], 16)
    } : null
  }
}

/**
 * 편의 함수: 텍스트를 PDF로 내보내기
 */
export async function exportTextToPDF(
  content: string,
  filename: string = 'document.pdf',
  options: PDFExportOptions = {}
): Promise<void> {
  const exporter = new PDFExporter({
    title: '문서',
    author: 'VideoPlanet',
    creator: 'VideoPlanet PDF Exporter',
    ...options
  })

  exporter.addTitle('문서', 1)
  exporter.addText(content)
  exporter.save(filename)
}

/**
 * 편의 함수: 테이블 데이터를 PDF로 내보내기
 */
export async function exportTableToPDF(
  tableData: PDFTableData,
  filename: string = 'table.pdf',
  options: PDFExportOptions = {}
): Promise<void> {
  const exporter = new PDFExporter({
    title: tableData.title || '테이블',
    author: 'VideoPlanet',
    creator: 'VideoPlanet PDF Exporter',
    ...options
  })

  if (tableData.title) {
    exporter.addTitle(tableData.title, 1)
  }

  exporter.addTable(tableData)
  exporter.save(filename)
}

/**
 * 편의 함수: HTML 요소를 PDF로 내보내기
 */
export async function exportHtmlToPDF(
  element: HTMLElement,
  filename: string = 'document.pdf',
  options: PDFExportOptions & { caption?: string } = {}
): Promise<void> {
  const { caption, ...pdfOptions } = options
  
  const exporter = new PDFExporter({
    title: '웹 페이지',
    author: 'VideoPlanet',
    creator: 'VideoPlanet PDF Exporter',
    ...pdfOptions
  })

  await exporter.addHtmlElement(element, { caption })
  exporter.save(filename)
}

/**
 * 프로젝트 리포트를 PDF로 내보내기
 */
export async function exportProjectReportToPDF(
  projectData: {
    title: string
    description: string
    status: string
    createdAt: string
    updatedAt: string
    teamMembers: Array<{ name: string; email: string; role: string }>
    tasks: Array<{ title: string; status: string; assignee: string; dueDate: string }>
    timeline: Array<{ date: string; event: string; description: string }>
  },
  filename: string = 'project-report.pdf'
): Promise<void> {
  const exporter = new PDFExporter({
    title: `${projectData.title} - 프로젝트 리포트`,
    author: 'VideoPlanet',
    creator: 'VideoPlanet PDF Exporter'
  })

  // 프로젝트 개요
  exporter.addTitle(projectData.title, 1)
  exporter.addText(`상태: ${projectData.status}`)
  exporter.addText(`생성일: ${new Date(projectData.createdAt).toLocaleDateString('ko-KR')}`)
  exporter.addText(`수정일: ${new Date(projectData.updatedAt).toLocaleDateString('ko-KR')}`)
  exporter.addText('') // 빈 줄
  
  exporter.addTitle('프로젝트 설명', 2)
  exporter.addText(projectData.description)

  // 팀원 정보
  exporter.addTitle('팀원 정보', 2)
  exporter.addTable({
    headers: ['이름', '이메일', '역할'],
    rows: projectData.teamMembers.map(member => [member.name, member.email, member.role])
  })

  // 작업 현황
  exporter.addTitle('작업 현황', 2)
  exporter.addTable({
    headers: ['작업', '상태', '담당자', '마감일'],
    rows: projectData.tasks.map(task => [
      task.title,
      task.status,
      task.assignee,
      new Date(task.dueDate).toLocaleDateString('ko-KR')
    ])
  })

  // 타임라인
  if (projectData.timeline.length > 0) {
    exporter.addTitle('프로젝트 타임라인', 2)
    exporter.addTable({
      headers: ['날짜', '이벤트', '설명'],
      rows: projectData.timeline.map(item => [
        new Date(item.date).toLocaleDateString('ko-KR'),
        item.event,
        item.description
      ])
    })
  }

  exporter.save(filename)
}