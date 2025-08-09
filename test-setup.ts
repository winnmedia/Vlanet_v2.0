import { beforeAll, afterEach, afterAll, vi } from 'vitest'
import '@testing-library/jest-dom'

// Mock window properties
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: (query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => {},
  }),
})

// Mock HTMLMediaElement methods globally
global.HTMLMediaElement.prototype.play = () => Promise.resolve()
global.HTMLMediaElement.prototype.pause = () => {}
global.HTMLMediaElement.prototype.load = () => {}

// Mock WebSocket
global.WebSocket = class WebSocket {
  constructor(url: string) {}
  send() {}
  close() {}
  addEventListener() {}
  removeEventListener() {}
} as any

// Mock URL.createObjectURL
global.URL.createObjectURL = () => 'mock-url'
global.URL.revokeObjectURL = () => {}

// Mock ResizeObserver
global.ResizeObserver = class ResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
}

// Mock IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  observe() {}
  unobserve() {}
  disconnect() {}
}

// Mock DOM element methods
Element.prototype.scrollIntoView = vi.fn()
Element.prototype.getBoundingClientRect = vi.fn(() => ({
  x: 0,
  y: 0,
  width: 100,
  height: 100,
  top: 0,
  right: 100,
  bottom: 100,
  left: 0,
  toJSON: vi.fn()
}))

// Mock document methods
Object.defineProperty(document, 'fullscreenElement', {
  value: null,
  writable: true
})

document.exitFullscreen = vi.fn()
document.addEventListener = vi.fn()
document.removeEventListener = vi.fn()
document.querySelector = vi.fn(() => null)

// Mock global confirm
global.confirm = vi.fn(() => true)

// Mock canvas context
HTMLCanvasElement.prototype.getContext = () => ({
  fillRect: () => {},
  clearRect: () => {},
  getImageData: () => ({ data: new Array(4) }),
  putImageData: () => {},
  createImageData: () => ({ data: new Array(4) }),
  setTransform: () => {},
  drawImage: () => {},
  save: () => {},
  fillText: () => {},
  restore: () => {},
  beginPath: () => {},
  moveTo: () => {},
  lineTo: () => {},
  closePath: () => {},
  stroke: () => {},
  translate: () => {},
  scale: () => {},
  rotate: () => {},
  arc: () => {},
  fill: () => {},
  measureText: () => ({ width: 0 }),
  transform: () => {},
  rect: () => {},
  clip: () => {},
}) as any