/**
 * PDF  
 *    jsPDF  PDF  
 * 
 *  :
 * -    (Noto Sans KR)
 * -     (, , )
 * -  
 * -   / 
 */

import jsPDF from 'jspdf'
import html2canvas from 'html2canvas'

//   Base64  (Noto Sans KR Regular)
//   CDN    
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

    // PDF  
    if (options.title) this.doc.setProperties({ title: options.title })
    if (options.author) this.doc.setProperties({ author: options.author })
    if (options.subject) this.doc.setProperties({ subject: options.subject })
    if (options.creator) this.doc.setProperties({ creator: options.creator })

    this.setupKoreanFont()
  }

  /**
   *   
   * jsPDF    
   */
  private setupKoreanFont(): void {
    try {
      // Noto Sans KR   (   )
      //    ,     
      this.doc.setFont('helvetica')
      this.doc.setFontSize(this.fontSize)
      this.doc.setCharSpace(0.1) //      
    } catch (error) {
      console.warn('     :', error)
      //   
      this.doc.setFont('helvetica')
      this.doc.setFontSize(this.fontSize)
    }
  }

  /**
   *  
   *       
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

    //  
    const rgb = this.hexToRgb(color)
    if (rgb) this.doc.setTextColor(rgb.r, rgb.g, rgb.b)

    //   
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
      this.currentY += fontSize * this.lineHeight * 0.35 // mm  
    })

    this.currentY += fontSize * 0.5 //  
  }

  /**
   *  
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
   *  
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

    //  
    this.doc.setFillColor(240, 240, 240)
    this.doc.rect(startX, this.currentY, tableWidth, rowHeight, 'F')

    this.doc.setFont('helvetica', 'bold')
    this.doc.setFontSize(10)

    headers.forEach((header, index) => {
      const x = startX + (index * colWidth) + 2
      this.doc.text(header, x, this.currentY + 6)
    })

    this.currentY += rowHeight

    //  
    this.doc.setFont('helvetica', 'normal')
    
    rows.forEach((row, rowIndex) => {
      if (this.needNewPage(rowHeight)) {
        this.addPage()
      }

      //   ( )
      if (rowIndex % 2 === 0) {
        this.doc.setFillColor(250, 250, 250)
        this.doc.rect(startX, this.currentY, tableWidth, rowHeight, 'F')
      }

      row.forEach((cell, colIndex) => {
        const x = startX + (colIndex * colWidth) + 2
        //     
        const truncatedText = this.truncateText(cell, colWidth - 4)
        this.doc.text(truncatedText, x, this.currentY + 6)
      })

      this.currentY += rowHeight
    })

    //  
    this.doc.setDrawColor(200, 200, 200)
    this.doc.rect(startX, this.currentY - (rows.length + 1) * rowHeight, tableWidth, (rows.length + 1) * rowHeight)

    this.currentY += 5
  }

  /**
   * HTML    PDF 
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
      
      //   
      let imgWidth = width || (this.getPageWidth() - this.margin.left - this.margin.right)
      let imgHeight = height || (canvas.height * imgWidth) / canvas.width

      //     
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
      console.error('HTML  PDF    :', error)
      this.addText(`[  : ${caption || 'HTML '}]`, {
        color: '#ff0000',
        fontSize: 10
      })
    }
  }

  /**
   *   
   */
  addPage(): void {
    this.doc.addPage()
    this.currentY = this.margin.top
  }

  /**
   * PDF 
   */
  save(filename: string = 'document.pdf'): void {
    //      
    const sanitizedFilename = filename.replace(/[^\w\-_\. ]/g, '_')
    this.doc.save(sanitizedFilename)
  }

  /**
   * PDF  URL 
   */
  getDataUrl(): string {
    return this.doc.output('dataurlstring')
  }

  /**
   * PDF Blob 
   */
  getBlob(): Blob {
    return this.doc.output('blob')
  }

  //  

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
 *  :  PDF 
 */
export async function exportTextToPDF(
  content: string,
  filename: string = 'document.pdf',
  options: PDFExportOptions = {}
): Promise<void> {
  const exporter = new PDFExporter({
    title: '',
    author: 'VideoPlanet',
    creator: 'VideoPlanet PDF Exporter',
    ...options
  })

  exporter.addTitle('', 1)
  exporter.addText(content)
  exporter.save(filename)
}

/**
 *  :   PDF 
 */
export async function exportTableToPDF(
  tableData: PDFTableData,
  filename: string = 'table.pdf',
  options: PDFExportOptions = {}
): Promise<void> {
  const exporter = new PDFExporter({
    title: tableData.title || '',
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
 *  : HTML  PDF 
 */
export async function exportHtmlToPDF(
  element: HTMLElement,
  filename: string = 'document.pdf',
  options: PDFExportOptions & { caption?: string } = {}
): Promise<void> {
  const { caption, ...pdfOptions } = options
  
  const exporter = new PDFExporter({
    title: ' ',
    author: 'VideoPlanet',
    creator: 'VideoPlanet PDF Exporter',
    ...pdfOptions
  })

  await exporter.addHtmlElement(element, { caption })
  exporter.save(filename)
}

/**
 *   PDF 
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
    title: `${projectData.title} -  `,
    author: 'VideoPlanet',
    creator: 'VideoPlanet PDF Exporter'
  })

  //  
  exporter.addTitle(projectData.title, 1)
  exporter.addText(`: ${projectData.status}`)
  exporter.addText(`: ${new Date(projectData.createdAt).toLocaleDateString('ko-KR')}`)
  exporter.addText(`: ${new Date(projectData.updatedAt).toLocaleDateString('ko-KR')}`)
  exporter.addText('') //  
  
  exporter.addTitle(' ', 2)
  exporter.addText(projectData.description)

  //  
  exporter.addTitle(' ', 2)
  exporter.addTable({
    headers: ['', '', ''],
    rows: projectData.teamMembers.map(member => [member.name, member.email, member.role])
  })

  //  
  exporter.addTitle(' ', 2)
  exporter.addTable({
    headers: ['', '', '', ''],
    rows: projectData.tasks.map(task => [
      task.title,
      task.status,
      task.assignee,
      new Date(task.dueDate).toLocaleDateString('ko-KR')
    ])
  })

  // 
  if (projectData.timeline.length > 0) {
    exporter.addTitle(' ', 2)
    exporter.addTable({
      headers: ['', '', ''],
      rows: projectData.timeline.map(item => [
        new Date(item.date).toLocaleDateString('ko-KR'),
        item.event,
        item.description
      ])
    })
  }

  exporter.save(filename)
}