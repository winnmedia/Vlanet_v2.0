/**
 * VideoPlanet   
 *       
 */

import axios from 'axios';
import chalk from 'chalk';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

//  
const CONFIG = {
  BASE_URL: process.env.BASE_URL || 'https://vlanet.net',
  API_URL: process.env.API_URL || 'https://videoplanet.up.railway.app/api',
  TEST_EMAIL: process.env.TEST_EMAIL || 'test@videoplanet.com',
  TEST_PASSWORD: process.env.TEST_PASSWORD || 'TestUser123!',
  TIMEOUT: 15000,
  RETRY_COUNT: 3,
  PARALLEL_TESTS: true
};

//  
const colors = {
  pass: chalk.green,
  fail: chalk.red,
  warn: chalk.yellow,
  info: chalk.blue,
  header: chalk.cyan.bold,
  emphasis: chalk.magenta
};

class ComprehensiveIntegrationTest {
  constructor() {
    this.results = [];
    this.token = null;
    this.testUser = null;
    this.startTime = null;
    this.endTime = null;
    this.criticalIssues = [];
    this.performanceMetrics = {};
  }

  //  : HTTP  
  async makeRequest(method, url, data = null, requiresAuth = true, retries = CONFIG.RETRY_COUNT) {
    const config = {
      method,
      url,
      timeout: CONFIG.TIMEOUT,
      validateStatus: () => true //  status code 
    };

    if (data) config.data = data;
    if (requiresAuth && this.token) {
      config.headers = { Authorization: `Bearer ${this.token}` };
    }

    let lastError = null;
    for (let i = 0; i <= retries; i++) {
      try {
        const startTime = Date.now();
        const response = await axios(config);
        const responseTime = Date.now() - startTime;
        
        return {
          ...response,
          responseTime,
          attempt: i + 1
        };
      } catch (error) {
        lastError = error;
        if (i < retries) {
          console.log(colors.warn(`    ${i + 1}/${retries}...`));
          await this.sleep(1000 * (i + 1)); //  
        }
      }
    }
    throw lastError;
  }

  // : 
  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  //  
  addResult(testData) {
    const result = {
      ...testData,
      timestamp: new Date().toISOString(),
      id: `test_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    };
    
    this.results.push(result);
    
    if (result.status === 'FAIL' && result.severity === 'CRITICAL') {
      this.criticalIssues.push(result);
    }
    
    return result;
  }

  //   
  recordPerformance(operation, duration, details = {}) {
    if (!this.performanceMetrics[operation]) {
      this.performanceMetrics[operation] = [];
    }
    
    this.performanceMetrics[operation].push({
      duration,
      timestamp: new Date().toISOString(),
      ...details
    });
  }

  // 1.   
  async testAuthentication() {
    console.log(colors.info('\n    ...'));
    
    //  
    try {
      const startTime = Date.now();
      const response = await this.makeRequest('POST', `${CONFIG.API_URL}/auth/login/`, {
        email: CONFIG.TEST_EMAIL,
        password: CONFIG.TEST_PASSWORD
      }, false);
      
      const responseTime = Date.now() - startTime;
      this.recordPerformance('login', responseTime);
      
      if (response.status === 200 && response.data?.access) {
        this.token = response.data.access;
        
        this.addResult({
          test: ' ',
          category: 'Authentication',
          status: 'PASS',
          message: 'JWT   ',
          details: {
            responseTime: `${responseTime}ms`,
            tokenType: 'Bearer',
            hasRefreshToken: !!response.data.refresh
          }
        });
        
        console.log(colors.pass('  '));
        return true;
      } else if (response.status === 401) {
        //    
        return await this.createTestAccount();
      } else {
        throw new Error(`Unexpected response: ${response.status}`);
      }
    } catch (error) {
      this.addResult({
        test: ' ',
        category: 'Authentication',
        status: 'FAIL',
        message: ` : ${error.message}`,
        severity: 'CRITICAL',
        priority: 'P0',
        impact: '  ',
        error: error.response?.data || error.message
      });
      
      console.log(colors.fail('  '));
      return false;
    }
  }

  //   
  async createTestAccount() {
    console.log(colors.info('      ...'));
    
    try {
      const response = await this.makeRequest('POST', `${CONFIG.API_URL}/auth/register/`, {
        email: CONFIG.TEST_EMAIL,
        password: CONFIG.TEST_PASSWORD,
        password_confirm: CONFIG.TEST_PASSWORD,
        username: 'TestUser',
        first_name: 'Test',
        last_name: 'User'
      }, false);
      
      if (response.status === 201) {
        console.log(colors.pass('      '));
        //   
        return await this.testAuthentication();
      } else {
        throw new Error(`Account creation failed: ${response.status}`);
      }
    } catch (error) {
      console.log(colors.fail('      '));
      return false;
    }
  }

  // 2.    
  async testVideoPlanning() {
    console.log(colors.info('\n    ...'));
    
    const tests = [
      {
        name: '   ',
        endpoint: '/video-planning/',
        method: 'GET'
      },
      {
        name: '  ',
        endpoint: '/video-planning/create/',
        method: 'POST',
        data: {
          title: `   ${Date.now()}`,
          description: '    ',
          target_audience: ' ',
          duration: 300,
          status: 'planning'
        }
      }
    ];
    
    for (const test of tests) {
      try {
        const response = await this.makeRequest(
          test.method, 
          `${CONFIG.API_URL}${test.endpoint}`, 
          test.data
        );
        
        if (response.status >= 200 && response.status < 300) {
          this.addResult({
            test: test.name,
            category: 'Video Planning',
            status: 'PASS',
            message: `${test.method}  `,
            details: {
              statusCode: response.status,
              responseTime: `${response.responseTime}ms`,
              dataCount: Array.isArray(response.data) ? response.data.length : 1
            }
          });
          console.log(colors.pass(` ${test.name} `));
        } else {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
      } catch (error) {
        this.addResult({
          test: test.name,
          category: 'Video Planning',
          status: 'FAIL',
          message: `${test.method}  : ${error.message}`,
          severity: 'CRITICAL',
          priority: 'P0',
          impact: '    ',
          details: {
            endpoint: test.endpoint,
            method: test.method,
            error: error.response?.data || error.message
          }
        });
        console.log(colors.fail(` ${test.name} `));
      }
    }
  }

  // 3.   
  async testProjectManagement() {
    console.log(colors.info('\n   ...'));
    
    let createdProjectId = null;
    
    const tests = [
      {
        name: '  ',
        endpoint: '/projects/',
        method: 'GET'
      },
      {
        name: ' ',
        endpoint: '/projects/create/',
        method: 'POST',
        data: {
          title: `  ${Date.now()}`,
          description: '   ',
          status: 'planning',
          category: 'video',
          priority: 'medium'
        }
      }
    ];
    
    for (const test of tests) {
      try {
        const response = await this.makeRequest(
          test.method,
          `${CONFIG.API_URL}${test.endpoint}`,
          test.data
        );
        
        if (response.status >= 200 && response.status < 300) {
          //     ID 
          if (test.method === 'POST' && response.data?.id) {
            createdProjectId = response.data.id;
          }
          
          this.addResult({
            test: test.name,
            category: 'Project Management',
            status: 'PASS',
            message: `${test.method}  `,
            details: {
              statusCode: response.status,
              responseTime: `${response.responseTime}ms`,
              projectId: response.data?.id,
              dataCount: Array.isArray(response.data) ? response.data.length : 1
            }
          });
          console.log(colors.pass(` ${test.name} `));
        } else if (response.status === 500) {
          throw new Error('Internal Server Error -   500  ');
        } else {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
      } catch (error) {
        const severity = error.message.includes('500') ? 'CRITICAL' : 'MAJOR';
        
        this.addResult({
          test: test.name,
          category: 'Project Management',
          status: 'FAIL',
          message: `${test.method}  : ${error.message}`,
          severity,
          priority: severity === 'CRITICAL' ? 'P0' : 'P1',
          impact: '   ',
          details: {
            endpoint: test.endpoint,
            method: test.method,
            expectedFix: ' API       ',
            error: error.response?.data || error.message
          }
        });
        console.log(colors.fail(` ${test.name} `));
      }
    }
    
    //   
    if (createdProjectId) {
      await this.cleanupProject(createdProjectId);
    }
  }

  // 4.  
  async testCalendarSystem() {
    console.log(colors.info('\n   ...'));
    
    const tests = [
      {
        name: '  ',
        endpoint: '/calendar/events/',
        method: 'GET'
      },
      {
        name: '  ',
        endpoint: '/calendar/events/create/',
        method: 'POST',
        data: {
          title: `  ${Date.now()}`,
          description: '  ',
          start_date: new Date(Date.now() + 86400000).toISOString().split('T')[0], // 
          start_time: '09:00:00',
          end_time: '10:00:00',
          type: 'meeting'
        }
      }
    ];
    
    for (const test of tests) {
      try {
        const response = await this.makeRequest(
          test.method,
          `${CONFIG.API_URL}${test.endpoint}`,
          test.data
        );
        
        if (response.status >= 200 && response.status < 300) {
          this.addResult({
            test: test.name,
            category: 'Calendar',
            status: 'PASS',
            message: `${test.method}  `,
            details: {
              statusCode: response.status,
              responseTime: `${response.responseTime}ms`,
              eventId: response.data?.id,
              eventsCount: Array.isArray(response.data) ? response.data.length : 1
            }
          });
          console.log(colors.pass(` ${test.name} `));
        } else if (response.status === 404) {
          throw new Error('Not Found -  API  ');
        } else {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
      } catch (error) {
        const severity = error.message.includes('404') ? 'CRITICAL' : 'MAJOR';
        
        this.addResult({
          test: test.name,
          category: 'Calendar',
          status: 'FAIL',
          message: `${test.method}  : ${error.message}`,
          severity,
          priority: severity === 'CRITICAL' ? 'P0' : 'P1',
          impact: '  ',
          details: {
            endpoint: test.endpoint,
            method: test.method,
            expectedFix: ' API   ',
            error: error.response?.data || error.message
          }
        });
        console.log(colors.fail(` ${test.name} `));
      }
    }
  }

  // 5.   
  async testFeedbackSystem() {
    console.log(colors.info('\n   ...'));
    
    const tests = [
      {
        name: '  ',
        endpoint: '/feedbacks/',
        method: 'GET'
      },
      {
        name: '  ',
        endpoint: '/feedbacks/create/',
        method: 'POST',
        data: {
          subject: `  ${Date.now()}`,
          message: '   .',
          category: 'bug',
          priority: 'medium'
        }
      }
    ];
    
    for (const test of tests) {
      try {
        const response = await this.makeRequest(
          test.method,
          `${CONFIG.API_URL}${test.endpoint}`,
          test.data
        );
        
        if (response.status >= 200 && response.status < 300) {
          this.addResult({
            test: test.name,
            category: 'Feedback',
            status: 'PASS',
            message: `${test.method}  `,
            details: {
              statusCode: response.status,
              responseTime: `${response.responseTime}ms`,
              feedbackId: response.data?.id,
              feedbackCount: Array.isArray(response.data) ? response.data.length : 1
            }
          });
          console.log(colors.pass(` ${test.name} `));
        } else if (response.status === 404) {
          throw new Error('Not Found -  API  ');
        } else {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
      } catch (error) {
        const severity = error.message.includes('404') ? 'CRITICAL' : 'MAJOR';
        
        this.addResult({
          test: test.name,
          category: 'Feedback',
          status: 'FAIL',
          message: `${test.method}  : ${error.message}`,
          severity,
          priority: severity === 'CRITICAL' ? 'P0' : 'P1',
          impact: '   ',
          details: {
            endpoint: test.endpoint,
            method: test.method,
            expectedFix: ' API   ',
            error: error.response?.data || error.message
          }
        });
        console.log(colors.fail(` ${test.name} `));
      }
    }
  }

  // 6.   
  async testDashboard() {
    console.log(colors.info('\n   ...'));
    
    const dashboardEndpoints = [
      { name: ' ', endpoint: '/dashboard/projects/stats/' },
      { name: ' ', endpoint: '/dashboard/activities/' },
      { name: ' ', endpoint: '/dashboard/user/stats/' },
      { name: ' ', endpoint: '/notifications/' }
    ];
    
    const results = [];
    
    for (const { name, endpoint } of dashboardEndpoints) {
      try {
        const response = await this.makeRequest('GET', `${CONFIG.API_URL}${endpoint}`);
        
        if (response.status >= 200 && response.status < 300) {
          results.push({ name, status: 'success', data: response.data });
          console.log(colors.pass(` ${name}  `));
        } else {
          results.push({ name, status: 'error', statusCode: response.status });
          console.log(colors.warn(`  ${name}   (${response.status})`));
        }
      } catch (error) {
        results.push({ name, status: 'error', error: error.message });
        console.log(colors.warn(`  ${name}  `));
      }
    }
    
    const successCount = results.filter(r => r.status === 'success').length;
    const totalCount = results.length;
    const successRate = (successCount / totalCount) * 100;
    
    this.addResult({
      test: '  ',
      category: 'Dashboard',
      status: successRate >= 75 ? 'PASS' : successRate >= 50 ? 'PARTIAL' : 'FAIL',
      message: `${successCount}/${totalCount}    `,
      severity: successRate < 50 ? 'MAJOR' : 'MINOR',
      details: {
        successRate: `${successRate.toFixed(1)}%`,
        results: results
      }
    });
  }

  // 7.   
  async testMyPage() {
    console.log(colors.info('\n   ...'));
    
    const tests = [
      {
        name: ' ',
        endpoint: '/users/profile/',
        method: 'GET'
      },
      {
        name: ' ',
        endpoint: '/users/profile/update/',
        method: 'PATCH',
        data: {
          first_name: 'UpdatedTest',
          bio: '   '
        }
      }
    ];
    
    for (const test of tests) {
      try {
        const response = await this.makeRequest(
          test.method,
          `${CONFIG.API_URL}${test.endpoint}`,
          test.data
        );
        
        if (response.status >= 200 && response.status < 300) {
          this.addResult({
            test: test.name,
            category: 'User Profile',
            status: 'PASS',
            message: `${test.method}  `,
            details: {
              statusCode: response.status,
              responseTime: `${response.responseTime}ms`,
              profileData: {
                email: response.data?.email,
                username: response.data?.username,
                lastLogin: response.data?.last_login
              }
            }
          });
          console.log(colors.pass(` ${test.name} `));
        } else {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
      } catch (error) {
        this.addResult({
          test: test.name,
          category: 'User Profile',
          status: 'FAIL',
          message: `${test.method}  : ${error.message}`,
          severity: 'MAJOR',
          priority: 'P1',
          impact: '  ',
          details: {
            endpoint: test.endpoint,
            method: test.method,
            error: error.response?.data || error.message
          }
        });
        console.log(colors.fail(` ${test.name} `));
      }
    }
  }

  //  
  async cleanupProject(projectId) {
    try {
      await this.makeRequest('DELETE', `${CONFIG.API_URL}/projects/delete/${projectId}/`);
      console.log(colors.info('      '));
    } catch (error) {
      //   
    }
  }

  //   
  async runAllTests() {
    console.log(colors.header('\n' + '='.repeat(80)));
    console.log(colors.header('VideoPlanet   '));
    console.log(colors.header('='.repeat(80)));
    console.log(colors.info(`: ${CONFIG.BASE_URL}`));
    console.log(colors.info(`API: ${CONFIG.API_URL}`));
    console.log(colors.info(` : ${new Date().toLocaleString('ko-KR')}`));
    console.log(colors.info(` : ${CONFIG.PARALLEL_TESTS ? '' : ''}`));
    
    this.startTime = Date.now();
    
    // 1.   ( )
    const authSuccess = await this.testAuthentication();
    
    if (authSuccess) {
      if (CONFIG.PARALLEL_TESTS) {
        //    
        console.log(colors.emphasis('\n    ...'));
        await Promise.all([
          this.testVideoPlanning(),
          this.testProjectManagement(),
          this.testCalendarSystem(),
          this.testFeedbackSystem(),
          this.testDashboard(),
          this.testMyPage()
        ]);
      } else {
        //  
        await this.testVideoPlanning();
        await this.testProjectManagement();
        await this.testCalendarSystem();
        await this.testFeedbackSystem();
        await this.testDashboard();
        await this.testMyPage();
      }
    } else {
      console.log(colors.fail('\n    '));
    }
    
    this.endTime = Date.now();
    this.generateComprehensiveReport();
  }

  //   
  generateComprehensiveReport() {
    console.log(colors.header('\n' + '='.repeat(80)));
    console.log(colors.header('   '));
    console.log(colors.header('='.repeat(80)));
    
    //   
    const categories = {};
    let totalTests = 0;
    let passedTests = 0;
    let failedTests = 0;
    let partialTests = 0;
    
    this.results.forEach(result => {
      if (!categories[result.category]) {
        categories[result.category] = { pass: 0, fail: 0, partial: 0, total: 0 };
      }
      
      categories[result.category].total++;
      totalTests++;
      
      if (result.status === 'PASS') {
        categories[result.category].pass++;
        passedTests++;
      } else if (result.status === 'PARTIAL') {
        categories[result.category].partial++;
        partialTests++;
      } else {
        categories[result.category].fail++;
        failedTests++;
      }
    });
    
    //   
    console.log(colors.header('\n  :'));
    Object.entries(categories).forEach(([category, stats]) => {
      const successRate = (stats.pass / stats.total) * 100;
      const status = successRate >= 80 ? colors.pass : 
                   successRate >= 60 ? colors.warn : colors.fail;
      
      console.log(`${status(category)}: ${stats.pass}/${stats.total} (${successRate.toFixed(1)}%)`);
    });
    
    //  
    const overallSuccessRate = ((passedTests + partialTests * 0.5) / totalTests) * 100;
    const executionTime = ((this.endTime - this.startTime) / 1000).toFixed(2);
    
    console.log(colors.header('\n  :'));
    console.log(` : ${totalTests}`);
    console.log(`${colors.pass(`: ${passedTests}`)}`);
    console.log(`${colors.warn(` : ${partialTests}`)}`);
    console.log(`${colors.fail(`: ${failedTests}`)}`);
    console.log(` : ${overallSuccessRate >= 70 ? colors.pass(overallSuccessRate.toFixed(1) + '%') : 
                                overallSuccessRate >= 50 ? colors.warn(overallSuccessRate.toFixed(1) + '%') :
                                colors.fail(overallSuccessRate.toFixed(1) + '%')}`);
    console.log(` : ${executionTime}`);
    
    //   
    if (this.criticalIssues.length > 0) {
      console.log(colors.header('\n  :'));
      this.criticalIssues.forEach((issue, index) => {
        console.log(colors.fail(`${index + 1}. [${issue.priority}] ${issue.test}`));
        console.log(colors.fail(`   : ${issue.impact}`));
        console.log(colors.fail(`   : ${issue.message}`));
        if (issue.details?.expectedFix) {
          console.log(colors.emphasis(`    : ${issue.details.expectedFix}`));
        }
        console.log('');
      });
    }
    
    //   
    if (Object.keys(this.performanceMetrics).length > 0) {
      console.log(colors.header('\n  :'));
      Object.entries(this.performanceMetrics).forEach(([operation, metrics]) => {
        const avgTime = metrics.reduce((sum, m) => sum + m.duration, 0) / metrics.length;
        const maxTime = Math.max(...metrics.map(m => m.duration));
        console.log(`${operation}:  ${avgTime.toFixed(0)}ms,  ${maxTime}ms`);
      });
    }
    
    //  
    console.log(colors.header('\n  :'));
    if (this.criticalIssues.length > 0) {
      console.log(colors.fail('•     .'));
    }
    if (overallSuccessRate < 70) {
      console.log(colors.warn('•   70% .    .'));
    }
    if (failedTests > totalTests * 0.3) {
      console.log(colors.warn('•   30% .  API  .'));
    }
    
    //  
    this.saveDetailedResults();
    
    console.log(colors.header('\n' + '='.repeat(80)));
    console.log(overallSuccessRate >= 80 ? 
      colors.pass('   -   ') : 
      colors.warn('    -  '));
    console.log(colors.header('='.repeat(80)));
  }

  //   
  saveDetailedResults() {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = `integration-test-results-${timestamp}.json`;
    
    const report = {
      summary: {
        totalTests: this.results.length,
        passed: this.results.filter(r => r.status === 'PASS').length,
        failed: this.results.filter(r => r.status === 'FAIL').length,
        partial: this.results.filter(r => r.status === 'PARTIAL').length,
        criticalIssues: this.criticalIssues.length,
        executionTime: `${((this.endTime - this.startTime) / 1000).toFixed(2)}s`,
        timestamp: new Date().toISOString(),
        environment: CONFIG
      },
      results: this.results,
      criticalIssues: this.criticalIssues,
      performanceMetrics: this.performanceMetrics,
      recommendations: this.generateRecommendations()
    };
    
    try {
      fs.writeFileSync(filename, JSON.stringify(report, null, 2));
      console.log(colors.info(`\n   : ${filename}`));
    } catch (error) {
      console.log(colors.warn(`  : ${error.message}`));
    }
  }

  //  
  generateRecommendations() {
    const recommendations = [];
    
    //    
    const failedCategories = {};
    this.results.filter(r => r.status === 'FAIL').forEach(result => {
      if (!failedCategories[result.category]) {
        failedCategories[result.category] = [];
      }
      failedCategories[result.category].push(result.test);
    });
    
    Object.entries(failedCategories).forEach(([category, tests]) => {
      recommendations.push({
        category,
        priority: 'HIGH',
        action: `${category}  API     `,
        failedTests: tests,
        estimatedEffort: '2-4 '
      });
    });
    
    return recommendations;
  }
}

// 
if (import.meta.url === `file://${process.argv[1]}`) {
  const tester = new ComprehensiveIntegrationTest();
  
  //   
  const args = process.argv.slice(2);
  if (args.includes('--sequential')) {
    CONFIG.PARALLEL_TESTS = false;
  }
  if (args.includes('--timeout')) {
    const timeoutIndex = args.indexOf('--timeout');
    CONFIG.TIMEOUT = parseInt(args[timeoutIndex + 1]) || CONFIG.TIMEOUT;
  }
  
  tester.runAllTests().catch(error => {
    console.error(colors.fail('\n   :'), error);
    process.exit(1);
  });
}

export default ComprehensiveIntegrationTest;