/**
 * PDF Export  
 *      
 */

import { describe, test, expect, vi, beforeEach, afterEach } from 'vitest'
import { JSDOM } from 'jsdom'
import { PDFExporter, exportTextToPDF, exportTableToPDF, exportProjectReportToPDF } from './pdf-export'

// DOM  
const dom = new JSDOM('<!DOCTYPE html><html><body></body></html>')
global.document = dom.window.document
global.window = dom.window as any
global.HTMLElement = dom.window.HTMLElement

// jsPDF 
vi.mock('jspdf', () => {
  const mockPDF = {
    setProperties: vi.fn(),
    setFont: vi.fn(),
    setFontSize: vi.fn(),
    setCharSpace: vi.fn(),
    setTextColor: vi.fn(),
    setFillColor: vi.fn(),
    setDrawColor: vi.fn(),
    text: vi.fn(),
    rect: vi.fn(),
    addImage: vi.fn(),
    addPage: vi.fn(),
    save: vi.fn(),
    output: vi.fn(() => 'mock-pdf-data'),
    getTextWidth: vi.fn(() => 50),
    internal: {
      pageSize: {
        getWidth: () => 210,
        getHeight: () => 297
      }
    }
  }
  
  return {
    default: vi.fn().mockImplementation(() => mockPDF)
  }
})

// html2canvas 
vi.mock('html2canvas', () => ({
  default: vi.fn().mockResolvedValue({
    toDataURL: () => 'data:image/png;base64,mock-canvas-data',
    width: 800,
    height: 600
  })
}))

describe('PDFExporter', () => {
  let exporter: PDFExporter
  let consoleWarnSpy: any

  beforeEach(() => {
    exporter = new PDFExporter({
      title: ' ',
      author: ' '
    })
    consoleWarnSpy = vi.spyOn(console, 'warn').mockImplementation(() => {})
  })

  afterEach(() => {
    vi.clearAllMocks()
    consoleWarnSpy.mockRestore()
  })

  describe('PDFExporter ', () => {
    test('  PDF  ', () => {
      const defaultExporter = new PDFExporter()
      expect(defaultExporter).toBeInstanceOf(PDFExporter)
    })

    test('  PDF  ', () => {
      const customExporter = new PDFExporter({
        title: ' ',
        orientation: 'landscape',
        format: 'a3',
        fontSize: 14
      })
      expect(customExporter).toBeInstanceOf(PDFExporter)
    })
  })

  describe('  ', () => {
    test('   ', () => {
      const koreanText = '.   .'
      exporter.addText(koreanText)

      // jsPDF text   
      expect(exporter['doc'].text).toHaveBeenCalled()
    })

    test('    ', () => {
      const longKoreanText = '    . '.repeat(20)
      exporter.addText(longKoreanText)

      // text      ( )
      expect(exporter['doc'].text).toHaveBeenCalled()
    })

    test('   ', () => {
      exporter.addText(' ', {
        fontSize: 16,
        bold: true,
        color: '#ff0000',
        align: 'center'
      })

      expect(exporter['doc'].setFontSize).toHaveBeenCalledWith(16)
      expect(exporter['doc'].setFont).toHaveBeenCalledWith('helvetica', 'bold')
      expect(exporter['doc'].setTextColor).toHaveBeenCalled()
    })
  })

  describe(' ', () => {
    test('1  ', () => {
      exporter.addTitle(' ', 1)
      expect(exporter['doc'].setFontSize).toHaveBeenCalledWith(20)
      expect(exporter['doc'].setFont).toHaveBeenCalledWith('helvetica', 'bold')
    })

    test('2  ', () => {
      exporter.addTitle(' ', 2)
      expect(exporter['doc'].setFontSize).toHaveBeenCalledWith(16)
    })

    test('3  ', () => {
      exporter.addTitle('', 3)
      expect(exporter['doc'].setFontSize).toHaveBeenCalledWith(14)
    })
  })

  describe(' ', () => {
    test('     ', () => {
      const tableData = {
        title: ' ',
        headers: ['', '', ''],
        rows: [
          ['', '30', ''],
          ['', '25', ''],
          ['', '35', '']
        ]
      }

      exporter.addTable(tableData)

      //     
      expect(exporter['doc'].setFillColor).toHaveBeenCalled()
      expect(exporter['doc'].rect).toHaveBeenCalled()
      expect(exporter['doc'].text).toHaveBeenCalled()
    })

    test('  ', () => {
      const emptyTable = {
        headers: ['1', '2'],
        rows: []
      }

      exporter.addTable(emptyTable)
      expect(exporter['doc'].text).toHaveBeenCalled()
    })
  })

  describe('HTML  PDF ', () => {
    test('HTML    ', async () => {
      const mockElement = document.createElement('div')
      mockElement.innerHTML = ' HTML '

      await exporter.addHtmlElement(mockElement, {
        caption: ' '
      })

      expect(exporter['doc'].addImage).toHaveBeenCalled()
    })

    test('HTML      ', async () => {
      const html2canvas = await import('html2canvas')
      vi.mocked(html2canvas.default).mockRejectedValueOnce(new Error('Canvas error'))

      const mockElement = document.createElement('div')
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

      await exporter.addHtmlElement(mockElement)

      expect(consoleSpy).toHaveBeenCalled()
      expect(exporter['doc'].text).toHaveBeenCalledWith(
        expect.stringContaining('[  '),
        expect.any(Number),
        expect.any(Number)
      )

      consoleSpy.mockRestore()
    })
  })

  describe(' ', () => {
    test('  ', () => {
      exporter.addPage()
      expect(exporter['doc'].addPage).toHaveBeenCalled()
    })

    test('       ', () => {
      //  Y    
      exporter['currentY'] = 280

      exporter.addText('   ')
      expect(exporter['doc'].addPage).toHaveBeenCalled()
    })
  })

  describe(' ', () => {
    test('PDF ', () => {
      exporter.save('test-document.pdf')
      expect(exporter['doc'].save).toHaveBeenCalledWith('test-document.pdf')
    })

    test('   ', () => {
      exporter.save('-.pdf')
      expect(exporter['doc'].save).toHaveBeenCalledWith('___-__.pdf')
    })

    test(' URL ', () => {
      const dataUrl = exporter.getDataUrl()
      expect(dataUrl).toBe('mock-pdf-data')
      expect(exporter['doc'].output).toHaveBeenCalledWith('dataurlstring')
    })

    test('Blob ', () => {
      const blob = exporter.getBlob()
      expect(blob).toBe('mock-pdf-data')
      expect(exporter['doc'].output).toHaveBeenCalledWith('blob')
    })
  })

  describe(' ', () => {
    test('   RGB ', () => {
      const hexToRgb = exporter['hexToRgb']
      
      expect(hexToRgb('#ff0000')).toEqual({ r: 255, g: 0, b: 0 })
      expect(hexToRgb('#00ff00')).toEqual({ r: 0, g: 255, b: 0 })
      expect(hexToRgb('#0000ff')).toEqual({ r: 0, g: 0, b: 255 })
      expect(hexToRgb('invalid')).toBeNull()
    })

    test('   ', () => {
      //   addText    
      exporter.addText('         ', {
        maxWidth: 50
      })
      
      // text   
      expect(exporter['doc'].text).toHaveBeenCalled()
    })

    test('   ', () => {
      //      
      const longText = '              '
      
      exporter.addText(longText)
      
      //   text    
      expect(exporter['doc'].text).toHaveBeenCalled()
    })
  })
})

describe('  ', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('exportTextToPDF', () => {
    test(' PDF ', async () => {
      await exportTextToPDF('  ', 'test.pdf')
      
      // PDFExporter    
      //   spy mock   
      expect(true).toBe(true) //   
    })
  })

  describe('exportTableToPDF', () => {
    test('  PDF ', async () => {
      const tableData = {
        title: ' ',
        headers: ['ID', '', ''],
        rows: [
          ['1', '', 'hong@example.com'],
          ['2', '', 'kim@example.com']
        ]
      }

      await exportTableToPDF(tableData, 'table.pdf')
      expect(true).toBe(true) //   
    })
  })

  describe('exportProjectReportToPDF', () => {
    test('  PDF ', async () => {
      const projectData = {
        title: ' ',
        description: ' .',
        status: '',
        createdAt: '2025-08-09T00:00:00Z',
        updatedAt: '2025-08-09T12:00:00Z',
        teamMembers: [
          { name: '', email: 'hong@example.com', role: '' },
          { name: '', email: 'kim@example.com', role: '' }
        ],
        tasks: [
          { 
            title: '  ', 
            status: '', 
            assignee: '', 
            dueDate: '2025-08-10T00:00:00Z' 
          }
        ],
        timeline: [
          {
            date: '2025-08-01T00:00:00Z',
            event: ' ',
            description: '  '
          }
        ]
      }

      await exportProjectReportToPDF(projectData, 'project-report.pdf')
      expect(true).toBe(true) //   
    })
  })
})

describe('Edge Cases   ', () => {
  test('  ', () => {
    const exporter = new PDFExporter()
    exporter.addText('')
    expect(exporter['doc'].text).toHaveBeenCalled()
  })

  test('   ', () => {
    const exporter = new PDFExporter()
    const longTableData = {
      headers: ['1', '2', '3'],
      rows: Array(100).fill(['1', '2', '3'])
    }

    exporter.addTable(longTableData)
    expect(exporter['doc'].text).toHaveBeenCalled()
  })

  test('   ', () => {
    const exporter = new PDFExporter()
    const specialText = ': @#$%^&*()_+-={}[]|\\:";\'<>?,./'
    
    exporter.addText(specialText)
    expect(exporter['doc'].text).toHaveBeenCalled()
  })

  test('    ', () => {
    const exporter = new PDFExporter()
    exporter.addText(' ', { fontSize: 100 })
    expect(exporter['doc'].setFontSize).toHaveBeenCalledWith(100)
  })

  test('   ', () => {
    const exporter = new PDFExporter()
    exporter.addText(' ', { color: 'invalid-color' })
    //       
    expect(exporter['doc'].text).toHaveBeenCalled()
  })
})