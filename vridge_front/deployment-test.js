#!/usr/bin/env node

/**
 * VideoPlanet    
 * CI/CD     
 */

import https from 'https';
import http from 'http';
import { performance } from 'perf_hooks';
import fs from 'fs';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

//  
const CONFIG = {
  PRODUCTION_URL: 'https://www.vlanet.net',
  STAGING_URL: 'https://videoplanet-seven.vercel.app',
  API_URL: 'https://videoplanet.up.railway.app',
  TIMEOUT: 10000, // 10
  RETRY_COUNT: 3
};

//   
const testResults = {
  timestamp: new Date().toISOString(),
  environment: process.env.NODE_ENV || 'test',
  results: [],
  summary: {
    total: 0,
    passed: 0,
    failed: 0,
    duration: 0
  }
};

class DeploymentTester {
  constructor() {
    this.startTime = performance.now();
  }

  // HTTP   
  async makeRequest(url, options = {}) {
    return new Promise((resolve, reject) => {
      const startTime = performance.now();
      const protocol = url.startsWith('https') ? https : http;
      
      const req = protocol.get(url, {
        timeout: CONFIG.TIMEOUT,
        ...options
      }, (res) => {
        let data = '';
        
        res.on('data', chunk => {
          data += chunk;
        });
        
        res.on('end', () => {
          const endTime = performance.now();
          resolve({
            statusCode: res.statusCode,
            headers: res.headers,
            data: data,
            responseTime: Math.round(endTime - startTime),
            success: res.statusCode >= 200 && res.statusCode < 400
          });
        });
      });
      
      req.on('timeout', () => {
        req.destroy();
        reject(new Error('Request timeout'));
      });
      
      req.on('error', (err) => {
        reject(err);
      });
    });
  }

  //   
  logResult(testName, success, details = {}) {
    const result = {
      test: testName,
      success,
      timestamp: new Date().toISOString(),
      details
    };
    
    testResults.results.push(result);
    testResults.summary.total++;
    
    if (success) {
      testResults.summary.passed++;
      console.log(` ${testName}`);
    } else {
      testResults.summary.failed++;
      console.log(` ${testName}`);
      if (details.error) {
        console.log(`   Error: ${details.error}`);
      }
    }
    
    if (details.responseTime) {
      console.log(`   Response time: ${details.responseTime}ms`);
    }
  }

  // 1.   
  async testFrontendDeployment() {
    console.log('\n    ...');
    
    //   
    try {
      const response = await this.makeRequest(CONFIG.PRODUCTION_URL);
      this.logResult('Production Frontend (vlanet.net)', response.success, {
        statusCode: response.statusCode,
        responseTime: response.responseTime,
        hasContent: response.data.length > 0
      });
      
      // HTML   
      const hasTitle = response.data.includes('<title>');
      const hasReact = response.data.includes('react') || response.data.includes('React');
      
      this.logResult('Frontend Content Validation', hasTitle, {
        hasTitle,
        hasReact,
        contentLength: response.data.length
      });
      
    } catch (error) {
      this.logResult('Production Frontend (vlanet.net)', false, {
        error: error.message
      });
    }

    //   
    try {
      const response = await this.makeRequest(CONFIG.STAGING_URL);
      this.logResult('Staging Frontend (videoplanet-seven.vercel.app)', response.success, {
        statusCode: response.statusCode,
        responseTime: response.responseTime
      });
    } catch (error) {
      this.logResult('Staging Frontend (videoplanet-seven.vercel.app)', false, {
        error: error.message
      });
    }
  }

  // 2.  API 
  async testBackendAPI() {
    console.log('\n  API  ...');
    
    //  
    try {
      const response = await this.makeRequest(`${CONFIG.API_URL}/api/health/`);
      const healthData = JSON.parse(response.data);
      
      this.logResult('API Health Check', response.success && healthData.status === 'healthy', {
        statusCode: response.statusCode,
        responseTime: response.responseTime,
        healthStatus: healthData.status,
        database: healthData.database,
        cache: healthData.cache
      });
    } catch (error) {
      this.logResult('API Health Check', false, {
        error: error.message
      });
    }

    // API  
    try {
      const response = await this.makeRequest(`${CONFIG.API_URL}/api/`);
      const apiData = JSON.parse(response.data);
      
      this.logResult('API Documentation', response.success, {
        statusCode: response.statusCode,
        responseTime: response.responseTime,
        version: apiData.version,
        endpointCount: Object.keys(apiData.endpoints || {}).length
      });
    } catch (error) {
      this.logResult('API Documentation', false, {
        error: error.message
      });
    }

    //   
    const endpoints = [
      '/api/auth/login/',
      '/api/users/me/',
      '/api/projects/',
      '/api/video-planning/'
    ];

    for (const endpoint of endpoints) {
      try {
        const response = await this.makeRequest(`${CONFIG.API_URL}${endpoint}`);
        // 401/403    
        const isValidResponse = response.statusCode < 500;
        
        this.logResult(`Endpoint ${endpoint}`, isValidResponse, {
          statusCode: response.statusCode,
          responseTime: response.responseTime,
          authenticated: response.statusCode === 401 || response.statusCode === 403
        });
      } catch (error) {
        this.logResult(`Endpoint ${endpoint}`, false, {
          error: error.message
        });
      }
    }
  }

  // 3.  
  async testPerformance() {
    console.log('\n   ...');
    
    const urls = [
      { name: 'Production Frontend', url: CONFIG.PRODUCTION_URL },
      { name: 'API Health', url: `${CONFIG.API_URL}/api/health/` }
    ];

    for (const { name, url } of urls) {
      try {
        const response = await this.makeRequest(url);
        const isGoodPerformance = response.responseTime < 2000; // 2 
        
        this.logResult(`Performance - ${name}`, isGoodPerformance, {
          responseTime: response.responseTime,
          threshold: '2000ms',
          performance: response.responseTime < 1000 ? 'excellent' : 
                      response.responseTime < 2000 ? 'good' : 'slow'
        });
      } catch (error) {
        this.logResult(`Performance - ${name}`, false, {
          error: error.message
        });
      }
    }
  }

  // 4. SSL   
  async testSecurity() {
    console.log('\n   ...');
    
    const urls = [CONFIG.PRODUCTION_URL, CONFIG.API_URL];
    
    for (const url of urls) {
      try {
        const response = await this.makeRequest(url);
        const hasHTTPS = url.startsWith('https');
        const hasSecurityHeaders = response.headers['strict-transport-security'] || 
                                  response.headers['x-frame-options'] ||
                                  response.headers['x-content-type-options'];
        
        this.logResult(`SSL/Security - ${new URL(url).hostname}`, hasHTTPS, {
          https: hasHTTPS,
          hasSecurityHeaders: !!hasSecurityHeaders,
          statusCode: response.statusCode
        });
      } catch (error) {
        this.logResult(`SSL/Security - ${new URL(url).hostname}`, false, {
          error: error.message
        });
      }
    }
  }

  // 5. CORS 
  async testCORS() {
    console.log('\n CORS   ...');
    
    try {
      const response = await this.makeRequest(`${CONFIG.API_URL}/api/`, {
        headers: {
          'Origin': 'https://www.vlanet.net'
        }
      });
      
      const hasCORS = response.headers['access-control-allow-origin'] || 
                      response.headers['access-control-allow-credentials'];
      
      this.logResult('CORS Configuration', !!hasCORS, {
        statusCode: response.statusCode,
        allowOrigin: response.headers['access-control-allow-origin'],
        allowCredentials: response.headers['access-control-allow-credentials']
      });
    } catch (error) {
      this.logResult('CORS Configuration', false, {
        error: error.message
      });
    }
  }

  //   
  async runAllTests() {
    console.log(' VideoPlanet   \n');
    console.log('=' * 50);
    
    try {
      await this.testFrontendDeployment();
      await this.testBackendAPI();
      await this.testPerformance();
      await this.testSecurity();
      await this.testCORS();
      
      //    
      const endTime = performance.now();
      testResults.summary.duration = Math.round(endTime - this.startTime);
      
      //  
      this.printSummary();
      
      //   
      await this.saveResults();
      
      //    exit code 1
      if (testResults.summary.failed > 0) {
        process.exit(1);
      }
      
    } catch (error) {
      console.error('    :', error);
      process.exit(1);
    }
  }

  //    
  printSummary() {
    console.log('\n' + '=' * 50);
    console.log('   ');
    console.log('=' * 50);
    console.log(` : ${testResults.summary.total}`);
    console.log(`: ${testResults.summary.passed} `);
    console.log(`: ${testResults.summary.failed} `);
    console.log(`: ${((testResults.summary.passed / testResults.summary.total) * 100).toFixed(1)}%`);
    console.log(` : ${testResults.summary.duration}ms`);
    
    if (testResults.summary.failed > 0) {
      console.log('\n  :');
      testResults.results
        .filter(r => !r.success)
        .forEach(r => {
          console.log(`  - ${r.test}: ${r.details.error || 'Unknown error'}`);
        });
    }
  }

  //  JSON  
  async saveResults() {
    const filename = `deployment-test-results-${Date.now()}.json`;
    const filepath = `/home/winnmedia/VideoPlanet/videoplanet-clean/${filename}`;
    
    try {
      fs.writeFileSync(filepath, JSON.stringify(testResults, null, 2));
      console.log(`\n  : ${filepath}`);
    } catch (error) {
      console.error('  :', error.message);
    }
  }
}

//  
if (import.meta.url === `file://${process.argv[1]}`) {
  const tester = new DeploymentTester();
  tester.runAllTests().catch(console.error);
}

export default DeploymentTester;