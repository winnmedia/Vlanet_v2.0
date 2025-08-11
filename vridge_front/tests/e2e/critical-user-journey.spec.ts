/**
 * VideoPlanet Critical User Journey E2E Tests
 * Grace QA Lead     
 */

import { test, expect, Page } from '@playwright/test';
import { faker } from '@faker-js/faker';

// Test configuration
const TEST_CONFIG = {
  baseURL: process.env.BASE_URL || 'http://localhost:3000',
  apiURL: process.env.API_URL || 'https://videoplanet.up.railway.app',
  timeout: 30000,
};

// Test data factory
const testDataFactory = {
  createUser: () => ({
    email: faker.internet.email(),
    password: 'Test123!@#',
    name: faker.person.fullName(),
    company: faker.company.name(),
  }),
  
  createProject: () => ({
    title: `${faker.company.catchPhrase()} - ${Date.now()}`,
    description: faker.lorem.paragraph(),
    deadline: faker.date.future(),
    visibility: 'private',
  }),
  
  createFeedback: () => ({
    content: faker.lorem.sentence(),
    timestamp: faker.number.int({ min: 0, max: 300 }),
    priority: faker.helpers.arrayElement(['low', 'medium', 'high', 'critical']),
  }),
};

// Page Object Models
class LoginPage {
  constructor(private page: Page) {}
  
  async goto() {
    await this.page.goto('/login');
  }
  
  async login(email: string, password: string) {
    await this.page.fill('[data-testid="email-input"]', email);
    await this.page.fill('[data-testid="password-input"]', password);
    await this.page.click('[data-testid="login-button"]');
    await this.page.waitForURL('/dashboard', { timeout: 5000 });
  }
  
  async verifyErrorMessage(message: string) {
    const errorElement = this.page.locator('[data-testid="error-message"]');
    await expect(errorElement).toBeVisible();
    await expect(errorElement).toContainText(message);
  }
}

class SignupPage {
  constructor(private page: Page) {}
  
  async goto() {
    await this.page.goto('/signup');
  }
  
  async signup(userData: any) {
    await this.page.fill('[data-testid="name-input"]', userData.name);
    await this.page.fill('[data-testid="email-input"]', userData.email);
    await this.page.fill('[data-testid="password-input"]', userData.password);
    await this.page.fill('[data-testid="password-confirm-input"]', userData.password);
    await this.page.check('[data-testid="terms-checkbox"]');
    await this.page.click('[data-testid="signup-button"]');
  }
  
  async verifyEmailVerification() {
    await expect(this.page.locator('[data-testid="verification-message"]')).toBeVisible();
  }
}

class DashboardPage {
  constructor(private page: Page) {}
  
  async verifyWelcomeMessage(userName: string) {
    await expect(this.page.locator('[data-testid="welcome-message"]')).toContainText(userName);
  }
  
  async getProjectCount() {
    const projectCards = await this.page.locator('[data-testid="project-card"]').count();
    return projectCards;
  }
  
  async createNewProject() {
    await this.page.click('[data-testid="create-project-button"]');
  }
  
  async verifyStatistics() {
    const stats = {
      totalProjects: await this.page.locator('[data-testid="stat-total-projects"]').textContent(),
      activeProjects: await this.page.locator('[data-testid="stat-active-projects"]').textContent(),
      teamMembers: await this.page.locator('[data-testid="stat-team-members"]').textContent(),
    };
    return stats;
  }
}

class ProjectPage {
  constructor(private page: Page) {}
  
  async fillProjectDetails(projectData: any) {
    await this.page.fill('[data-testid="project-title"]', projectData.title);
    await this.page.fill('[data-testid="project-description"]', projectData.description);
    await this.page.fill('[data-testid="project-deadline"]', projectData.deadline.toISOString().split('T')[0]);
    await this.page.selectOption('[data-testid="project-visibility"]', projectData.visibility);
  }
  
  async saveProject() {
    await this.page.click('[data-testid="save-project-button"]');
    await this.page.waitForURL(/\/projects\/[a-zA-Z0-9]+/, { timeout: 5000 });
  }
  
  async inviteTeamMember(email: string, role: string) {
    await this.page.click('[data-testid="invite-member-button"]');
    await this.page.fill('[data-testid="invite-email"]', email);
    await this.page.selectOption('[data-testid="invite-role"]', role);
    await this.page.click('[data-testid="send-invite-button"]');
  }
  
  async verifyProjectCreated(title: string) {
    await expect(this.page.locator('[data-testid="project-title-display"]')).toContainText(title);
  }
}

class FeedbackPage {
  constructor(private page: Page) {}
  
  async addFeedback(feedbackData: any) {
    // Click on timeline at specific timestamp
    await this.page.click(`[data-testid="timeline-marker-${feedbackData.timestamp}"]`);
    
    // Add feedback comment
    await this.page.fill('[data-testid="feedback-input"]', feedbackData.content);
    await this.page.selectOption('[data-testid="feedback-priority"]', feedbackData.priority);
    await this.page.click('[data-testid="submit-feedback-button"]');
  }
  
  async verifyFeedbackAdded(content: string) {
    const feedbackElement = this.page.locator(`[data-testid="feedback-item"]:has-text("${content}")`);
    await expect(feedbackElement).toBeVisible();
  }
  
  async verifyRealtimeSync(content: string) {
    // Wait for WebSocket sync
    await this.page.waitForFunction(
      (text) => document.querySelector(`[data-testid="feedback-item"]:has-text("${text}")`) !== null,
      content,
      { timeout: 5000 }
    );
  }
}

// Test Suites
test.describe(' Critical User Journey -     ', () => {
  let loginPage: LoginPage;
  let signupPage: SignupPage;
  let dashboardPage: DashboardPage;
  let projectPage: ProjectPage;
  let feedbackPage: FeedbackPage;
  
  let testUser: any;
  let testProject: any;
  
  test.beforeEach(async ({ page }) => {
    // Initialize page objects
    loginPage = new LoginPage(page);
    signupPage = new SignupPage(page);
    dashboardPage = new DashboardPage(page);
    projectPage = new ProjectPage(page);
    feedbackPage = new FeedbackPage(page);
    
    // Generate test data
    testUser = testDataFactory.createUser();
    testProject = testDataFactory.createProject();
    
    // Set viewport for consistent testing
    await page.setViewportSize({ width: 1920, height: 1080 });
  });
  
  test('CUJ-001:    -  ', async ({ page }) => {
    // Step 1: 
    await test.step(' ', async () => {
      await signupPage.goto();
      await signupPage.signup(testUser);
      await signupPage.verifyEmailVerification();
      
      // Simulate email verification (in real test, would check email)
      await page.goto(`/verify-email?token=test-token`);
    });
    
    // Step 2: 
    await test.step(' ', async () => {
      await loginPage.goto();
      await loginPage.login(testUser.email, testUser.password);
      await dashboardPage.verifyWelcomeMessage(testUser.name);
    });
    
    // Step 3:  
    await test.step('  ', async () => {
      const initialProjectCount = await dashboardPage.getProjectCount();
      await dashboardPage.createNewProject();
      await projectPage.fillProjectDetails(testProject);
      await projectPage.saveProject();
      await projectPage.verifyProjectCreated(testProject.title);
      
      // Verify project count increased
      await page.goto('/dashboard');
      const newProjectCount = await dashboardPage.getProjectCount();
      expect(newProjectCount).toBe(initialProjectCount + 1);
    });
    
    // Step 4:  
    await test.step(' ', async () => {
      const inviteEmails = [
        'teammate1@example.com',
        'teammate2@example.com',
        'teammate3@example.com',
      ];
      
      for (const email of inviteEmails) {
        await projectPage.inviteTeamMember(email, 'creator');
        await page.waitForTimeout(500); // Wait for invitation to process
      }
      
      // Verify invitations sent
      await expect(page.locator('[data-testid="team-member-count"]')).toContainText('4');
    });
    
    // Step 5:  
    await test.step('  ', async () => {
      const feedback = testDataFactory.createFeedback();
      await page.click('[data-testid="feedback-tab"]');
      await feedbackPage.addFeedback(feedback);
      await feedbackPage.verifyFeedbackAdded(feedback.content);
    });
    
    // Step 6:   
    await test.step('  ', async () => {
      await page.goto('/dashboard');
      const stats = await dashboardPage.verifyStatistics();
      expect(parseInt(stats.totalProjects || '0')).toBeGreaterThan(0);
      expect(parseInt(stats.teamMembers || '0')).toBe(4);
    });
  });
  
  test('CUJ-002:    ', async ({ page }) => {
    // Pre-condition: Login as existing user
    await loginPage.goto();
    await loginPage.login('existing@example.com', 'Test123!@#');
    
    await test.step('  ', async () => {
      // Check today's schedule
      await expect(page.locator('[data-testid="today-schedule"]')).toBeVisible();
      
      // Check urgent notifications
      const notificationCount = await page.locator('[data-testid="notification-badge"]').textContent();
      console.log(`Urgent notifications: ${notificationCount}`);
      
      // Check deadline projects
      const deadlineProjects = await page.locator('[data-testid="deadline-warning"]').count();
      expect(deadlineProjects).toBeLessThanOrEqual(5);
    });
    
    await test.step('  ', async () => {
      // Navigate to first project
      await page.click('[data-testid="project-card"]:first-child');
      
      // Update status
      await page.selectOption('[data-testid="project-status"]', 'production');
      await page.click('[data-testid="save-status-button"]');
      
      // Verify status updated
      await expect(page.locator('[data-testid="status-badge"]')).toContainText('');
    });
    
    await test.step(' ', async () => {
      await page.click('[data-testid="feedback-tab"]');
      
      // Reply to first feedback
      await page.click('[data-testid="feedback-item"]:first-child [data-testid="reply-button"]');
      await page.fill('[data-testid="reply-input"]', ' . .');
      await page.click('[data-testid="send-reply-button"]');
      
      // Mark as resolved
      await page.click('[data-testid="mark-resolved-button"]');
      await expect(page.locator('[data-testid="feedback-status"]')).toContainText('');
    });
  });
  
  test('CUJ-003:    ', async ({ browser }) => {
    // Create multiple browser contexts for different users
    const contexts = await Promise.all([
      browser.newContext(),
      browser.newContext(),
      browser.newContext(),
    ]);
    
    const pages = await Promise.all(
      contexts.map(context => context.newPage())
    );
    
    // Login all users
    await Promise.all(pages.map(async (page, index) => {
      const loginPage = new LoginPage(page);
      await loginPage.goto();
      await loginPage.login(`user${index + 1}@example.com`, 'Test123!@#');
    }));
    
    await test.step('  ', async () => {
      // All users navigate to same project
      await Promise.all(pages.map(page => 
        page.goto('/projects/test-project-id')
      ));
      
      // User 1 edits title
      await pages[0].fill('[data-testid="project-title"]', 'Updated Title by User 1');
      
      // User 2 edits description
      await pages[1].fill('[data-testid="project-description"]', 'Updated Description by User 2');
      
      // User 3 changes status
      await pages[2].selectOption('[data-testid="project-status"]', 'review');
      
      // Save all changes
      await Promise.all(pages.map(page => 
        page.click('[data-testid="save-project-button"]')
      ));
      
      // Verify conflict resolution
      await pages[0].waitForTimeout(2000);
      await pages[0].reload();
      
      // Check that all changes are preserved or properly merged
      await expect(pages[0].locator('[data-testid="project-title-display"]')).toBeVisible();
      await expect(pages[0].locator('[data-testid="project-description-display"]')).toBeVisible();
      await expect(pages[0].locator('[data-testid="status-badge"]')).toContainText('');
    });
    
    await test.step('  ', async () => {
      // User 1 adds feedback
      const feedbackPage1 = new FeedbackPage(pages[0]);
      const feedback1 = testDataFactory.createFeedback();
      await pages[0].click('[data-testid="feedback-tab"]');
      await feedbackPage1.addFeedback(feedback1);
      
      // Verify feedback appears on other users' screens
      await pages[1].click('[data-testid="feedback-tab"]');
      await pages[2].click('[data-testid="feedback-tab"]');
      
      const feedbackPage2 = new FeedbackPage(pages[1]);
      const feedbackPage3 = new FeedbackPage(pages[2]);
      
      await feedbackPage2.verifyRealtimeSync(feedback1.content);
      await feedbackPage3.verifyRealtimeSync(feedback1.content);
    });
    
    // Cleanup
    await Promise.all(contexts.map(context => context.close()));
  });
});

// Performance Tests
test.describe(' Performance Tests', () => {
  test('PERF-001:   ', async ({ page }) => {
    const metrics = [];
    
    const pagesToTest = [
      { url: '/', name: 'Landing Page' },
      { url: '/login', name: 'Login Page' },
      { url: '/dashboard', name: 'Dashboard' },
      { url: '/projects', name: 'Projects List' },
    ];
    
    for (const pageInfo of pagesToTest) {
      await test.step(`${pageInfo.name}   `, async () => {
        const startTime = Date.now();
        await page.goto(pageInfo.url);
        await page.waitForLoadState('networkidle');
        const loadTime = Date.now() - startTime;
        
        metrics.push({
          page: pageInfo.name,
          loadTime,
          passed: loadTime < 2000,
        });
        
        // Core Web Vitals
        const vitals = await page.evaluate(() => {
          return new Promise((resolve) => {
            let lcp = 0;
            let fid = 0;
            let cls = 0;
            
            new PerformanceObserver((list) => {
              const entries = list.getEntries();
              const lastEntry = entries[entries.length - 1];
              lcp = lastEntry.renderTime || lastEntry.loadTime;
            }).observe({ type: 'largest-contentful-paint', buffered: true });
            
            new PerformanceObserver((list) => {
              const entries = list.getEntries();
              fid = entries[0].processingStart - entries[0].startTime;
            }).observe({ type: 'first-input', buffered: true });
            
            new PerformanceObserver((list) => {
              const entries = list.getEntries();
              entries.forEach((entry) => {
                if (!entry.hadRecentInput) {
                  cls += entry.value;
                }
              });
            }).observe({ type: 'layout-shift', buffered: true });
            
            setTimeout(() => {
              resolve({ lcp, fid, cls });
            }, 3000);
          });
        });
        
        console.log(`${pageInfo.name} Metrics:`, {
          loadTime: `${loadTime}ms`,
          ...vitals,
        });
        
        // Assert performance targets
        expect(loadTime).toBeLessThan(2000); // Page load < 2s
      });
    }
    
    console.log('Performance Test Results:', metrics);
  });
  
  test('PERF-002: API  ', async ({ request }) => {
    const endpoints = [
      { path: '/api/projects', method: 'GET' },
      { path: '/api/auth/refresh', method: 'POST' },
      { path: '/api/feedbacks', method: 'GET' },
    ];
    
    for (const endpoint of endpoints) {
      await test.step(`${endpoint.method} ${endpoint.path}  `, async () => {
        const startTime = Date.now();
        
        const response = await request[endpoint.method.toLowerCase()](
          `${TEST_CONFIG.apiURL}${endpoint.path}`,
          {
            headers: {
              'Authorization': 'Bearer test-token',
            },
          }
        );
        
        const responseTime = Date.now() - startTime;
        
        console.log(`${endpoint.method} ${endpoint.path}: ${responseTime}ms`);
        
        // Assert response time targets
        expect(responseTime).toBeLessThan(500); // API response < 500ms
        expect(response.status()).toBeLessThan(400); // No errors
      });
    }
  });
});

// Security Tests
test.describe(' Security Tests', () => {
  test('SEC-001: XSS  ', async ({ page }) => {
    const xssPayloads = [
      '<script>alert("XSS")</script>',
      '<img src=x onerror=alert("XSS")>',
      'javascript:alert("XSS")',
      '<svg onload=alert("XSS")>',
    ];
    
    await page.goto('/login');
    await page.fill('[data-testid="email-input"]', 'test@example.com');
    await page.fill('[data-testid="password-input"]', 'Test123!@#');
    await page.click('[data-testid="login-button"]');
    await page.waitForURL('/dashboard');
    
    await page.goto('/projects/create');
    
    for (const payload of xssPayloads) {
      await test.step(`XSS  : ${payload.substring(0, 30)}...`, async () => {
        await page.fill('[data-testid="project-title"]', payload);
        await page.fill('[data-testid="project-description"]', payload);
        await page.click('[data-testid="save-project-button"]');
        
        // Check that script is not executed
        const alertPromise = page.waitForEvent('dialog', { timeout: 1000 }).catch(() => null);
        const alert = await alertPromise;
        
        expect(alert).toBeNull(); // No alert should appear
        
        // Check that content is properly escaped
        const titleElement = page.locator('[data-testid="project-title-display"]');
        const titleText = await titleElement.textContent();
        expect(titleText).not.toContain('<script>');
      });
    }
  });
  
  test('SEC-002: SQL Injection  ', async ({ request }) => {
    const sqlPayloads = [
      "'; DROP TABLE users; --",
      "1' OR '1'='1",
      "admin'--",
      "' UNION SELECT * FROM users--",
    ];
    
    for (const payload of sqlPayloads) {
      await test.step(`SQL Injection : ${payload}`, async () => {
        const response = await request.post(`${TEST_CONFIG.apiURL}/api/auth/login`, {
          data: {
            email: payload,
            password: payload,
          },
        });
        
        // Should return 400 or 401, not 500 (which would indicate SQL error)
        expect(response.status()).toBeGreaterThanOrEqual(400);
        expect(response.status()).toBeLessThan(500);
        
        const body = await response.json();
        expect(body).not.toContain('SQL');
        expect(body).not.toContain('syntax');
      });
    }
  });
  
  test('SEC-003:    ', async ({ request }) => {
    await test.step('JWT     ', async () => {
      const response = await request.get(`${TEST_CONFIG.apiURL}/api/projects`);
      expect(response.status()).toBe(401);
    });
    
    await test.step('  ', async () => {
      const expiredToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyLCJleHAiOjB9.abc123';
      
      const response = await request.get(`${TEST_CONFIG.apiURL}/api/projects`, {
        headers: {
          'Authorization': `Bearer ${expiredToken}`,
        },
      });
      
      expect(response.status()).toBe(401);
    });
    
    await test.step('    ', async () => {
      // Login as user1 and get token
      const loginResponse = await request.post(`${TEST_CONFIG.apiURL}/api/auth/login`, {
        data: {
          email: 'user1@example.com',
          password: 'Test123!@#',
        },
      });
      
      const { access: token } = await loginResponse.json();
      
      // Try to access user2's private project
      const response = await request.get(`${TEST_CONFIG.apiURL}/api/projects/user2-private-project`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      
      expect(response.status()).toBe(403); // Forbidden
    });
  });
});

// Accessibility Tests
test.describe(' Accessibility Tests', () => {
  test('A11Y-001: WCAG 2.1 Level AA ', async ({ page }) => {
    const pages = [
      '/',
      '/login',
      '/signup',
      '/dashboard',
      '/projects',
    ];
    
    for (const url of pages) {
      await test.step(`${url}  `, async () => {
        await page.goto(url);
        
        // Check for proper heading structure
        const headings = await page.evaluate(() => {
          const h1 = document.querySelectorAll('h1').length;
          const h2 = document.querySelectorAll('h2').length;
          const h3 = document.querySelectorAll('h3').length;
          return { h1, h2, h3 };
        });
        
        expect(headings.h1).toBeGreaterThan(0); // At least one h1
        
        // Check for alt text on images
        const imagesWithoutAlt = await page.evaluate(() => {
          const images = Array.from(document.querySelectorAll('img'));
          return images.filter(img => !img.alt).length;
        });
        
        expect(imagesWithoutAlt).toBe(0);
        
        // Check for proper form labels
        const inputsWithoutLabels = await page.evaluate(() => {
          const inputs = Array.from(document.querySelectorAll('input, select, textarea'));
          return inputs.filter(input => {
            const id = input.id;
            if (!id) return true;
            const label = document.querySelector(`label[for="${id}"]`);
            return !label;
          }).length;
        });
        
        expect(inputsWithoutLabels).toBe(0);
        
        // Check color contrast (simplified check)
        const lowContrastElements = await page.evaluate(() => {
          const elements = Array.from(document.querySelectorAll('*'));
          return elements.filter(el => {
            const style = window.getComputedStyle(el);
            const bg = style.backgroundColor;
            const fg = style.color;
            
            // Simple check - in real test would calculate actual contrast ratio
            if (bg === 'rgb(255, 255, 255)' && fg === 'rgb(255, 255, 255)') {
              return true; // White on white
            }
            if (bg === 'rgb(0, 0, 0)' && fg === 'rgb(0, 0, 0)') {
              return true; // Black on black
            }
            
            return false;
          }).length;
        });
        
        expect(lowContrastElements).toBe(0);
      });
    }
  });
  
  test('A11Y-002:  ', async ({ page }) => {
    await page.goto('/');
    
    // Test tab navigation
    await page.keyboard.press('Tab');
    const firstFocused = await page.evaluate(() => document.activeElement?.tagName);
    expect(firstFocused).toBeTruthy();
    
    // Navigate through interactive elements
    for (let i = 0; i < 10; i++) {
      await page.keyboard.press('Tab');
      const focused = await page.evaluate(() => {
        const el = document.activeElement;
        return {
          tag: el?.tagName,
          role: el?.getAttribute('role'),
          ariaLabel: el?.getAttribute('aria-label'),
        };
      });
      
      console.log(`Tab ${i + 1}:`, focused);
      
      // Verify focus is visible
      const focusVisible = await page.evaluate(() => {
        const el = document.activeElement;
        if (!el) return false;
        const style = window.getComputedStyle(el);
        return style.outline !== 'none' || style.boxShadow !== 'none';
      });
      
      expect(focusVisible).toBeTruthy();
    }
    
    // Test escape key for modals
    await page.click('[data-testid="create-project-button"]');
    await page.waitForSelector('[data-testid="modal"]');
    await page.keyboard.press('Escape');
    await expect(page.locator('[data-testid="modal"]')).not.toBeVisible();
  });
});

// Mobile Responsiveness Tests
test.describe(' Mobile Responsiveness Tests', () => {
  const devices = [
    { name: 'iPhone SE', width: 375, height: 667 },
    { name: 'iPhone 13', width: 390, height: 844 },
    { name: 'iPad', width: 768, height: 1024 },
    { name: 'Galaxy S21', width: 412, height: 915 },
  ];
  
  for (const device of devices) {
    test(`MOBILE-001: ${device.name}  `, async ({ page }) => {
      await page.setViewportSize({ width: device.width, height: device.height });
      
      await test.step(' ', async () => {
        await page.goto('/');
        
        // Check if hamburger menu is visible on mobile
        if (device.width < 768) {
          await expect(page.locator('[data-testid="mobile-menu-button"]')).toBeVisible();
          
          // Open mobile menu
          await page.click('[data-testid="mobile-menu-button"]');
          await expect(page.locator('[data-testid="mobile-menu"]')).toBeVisible();
          
          // Close mobile menu
          await page.click('[data-testid="mobile-menu-close"]');
          await expect(page.locator('[data-testid="mobile-menu"]')).not.toBeVisible();
        } else {
          // Desktop navigation should be visible
          await expect(page.locator('[data-testid="desktop-nav"]')).toBeVisible();
        }
      });
      
      await test.step('   ', async () => {
        await page.goto('/login');
        
        // Check button sizes
        const buttonSize = await page.evaluate(() => {
          const button = document.querySelector('[data-testid="login-button"]');
          if (!button) return { width: 0, height: 0 };
          const rect = button.getBoundingClientRect();
          return { width: rect.width, height: rect.height };
        });
        
        // Touch targets should be at least 44x44px
        expect(buttonSize.width).toBeGreaterThanOrEqual(44);
        expect(buttonSize.height).toBeGreaterThanOrEqual(44);
      });
      
      await test.step('  ', async () => {
        await page.goto('/projects');
        
        // Check for horizontal scroll
        const hasHorizontalScroll = await page.evaluate(() => {
          return document.documentElement.scrollWidth > document.documentElement.clientWidth;
        });
        
        expect(hasHorizontalScroll).toBeFalsy();
      });
    });
  }
  
  test('MOBILE-002:  ', async ({ page }) => {
    // Start in portrait
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto('/dashboard');
    
    const portraitLayout = await page.evaluate(() => {
      return {
        bodyWidth: document.body.clientWidth,
        mainContentWidth: document.querySelector('main')?.clientWidth,
      };
    });
    
    // Switch to landscape
    await page.setViewportSize({ width: 844, height: 390 });
    await page.waitForTimeout(500); // Wait for re-render
    
    const landscapeLayout = await page.evaluate(() => {
      return {
        bodyWidth: document.body.clientWidth,
        mainContentWidth: document.querySelector('main')?.clientWidth,
      };
    });
    
    // Content should adapt to new orientation
    expect(landscapeLayout.bodyWidth).toBeGreaterThan(portraitLayout.bodyWidth);
    
    // Check that no content is cut off
    const hasOverflow = await page.evaluate(() => {
      return document.documentElement.scrollWidth > document.documentElement.clientWidth ||
             document.documentElement.scrollHeight > document.documentElement.clientHeight;
    });
    
    expect(hasOverflow).toBeFalsy();
  });
});

// Helper function for visual regression
async function captureScreenshot(page: Page, name: string) {
  await page.screenshot({
    path: `./test-results/screenshots/${name}.png`,
    fullPage: true,
  });
}

// Helper function for performance metrics
async function measurePerformance(page: Page) {
  return await page.evaluate(() => {
    const perfData = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
    return {
      domContentLoaded: perfData.domContentLoadedEventEnd - perfData.domContentLoadedEventStart,
      loadComplete: perfData.loadEventEnd - perfData.loadEventStart,
      domInteractive: perfData.domInteractive - perfData.fetchStart,
      ttfb: perfData.responseStart - perfData.requestStart,
    };
  });
}

// Test configuration for different environments
export const testConfig = {
  use: {
    baseURL: TEST_CONFIG.baseURL,
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    trace: 'on-first-retry',
  },
  
  projects: [
    {
      name: 'Desktop Chrome',
      use: {
        browserName: 'chromium',
        viewport: { width: 1920, height: 1080 },
      },
    },
    {
      name: 'Mobile Safari',
      use: {
        browserName: 'webkit',
        viewport: { width: 390, height: 844 },
        isMobile: true,
      },
    },
  ],
  
  reporter: [
    ['html', { outputFolder: 'test-results/html' }],
    ['json', { outputFile: 'test-results/results.json' }],
    ['junit', { outputFile: 'test-results/junit.xml' }],
  ],
};