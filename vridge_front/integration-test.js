#!/usr/bin/env node

/**
 * VideoPlanet   
 *     E2E 
 */

import fetch from 'node-fetch';

const API_BASE = 'https://videoplanet.up.railway.app';
const FRONTEND_URL = 'https://www.vlanet.net';

class IntegrationTester {
  constructor() {
    this.testResults = [];
    this.authToken = null;
    this.testUser = {
      email: `test_${Date.now()}@example.com`,
      password: 'testpass123',
      username: `testuser_${Date.now()}`
    };
  }

  log(message, success = null) {
    const timestamp = new Date().toISOString();
    const status = success === null ? '' : (success ? '' : '');
    console.log(`[${timestamp}] ${status} ${message}`);
    
    if (success !== null) {
      this.testResults.push({
        message,
        success,
        timestamp
      });
    }
  }

  async makeAPIRequest(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers
    };

    if (this.authToken) {
      headers['Authorization'] = `Bearer ${this.authToken}`;
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers
      });

      const responseData = await response.text();
      let jsonData = null;
      
      try {
        jsonData = JSON.parse(responseData);
      } catch (e) {
        // JSON   
      }

      return {
        success: response.ok,
        status: response.status,
        data: jsonData,
        rawData: responseData,
        headers: response.headers
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  async testUserRegistration() {
    this.log('   ');
    
    const response = await this.makeAPIRequest('/api/auth/signup/', {
      method: 'POST',
      body: JSON.stringify({
        email: this.testUser.email,
        password: this.testUser.password,
        nickname: this.testUser.username
      })
    });

    if (response.success) {
      this.log(' ', true);
      return true;
    } else {
      this.log(` : ${response.error || response.status}`, false);
      return false;
    }
  }

  async testUserLogin() {
    this.log('   ');
    
    const response = await this.makeAPIRequest('/api/auth/login/', {
      method: 'POST',
      body: JSON.stringify({
        email: this.testUser.email,
        password: this.testUser.password
      })
    });

    if (response.success && response.data?.access) {
      this.authToken = response.data.access;
      this.log(' ', true);
      return true;
    } else {
      this.log(` : ${response.error || response.status}`, false);
      return false;
    }
  }

  async testUserProfile() {
    this.log('   ');
    
    const response = await this.makeAPIRequest('/api/users/me/', {
      method: 'GET'
    });

    if (response.success && response.data?.email === this.testUser.email) {
      this.log('  ', true);
      return true;
    } else {
      this.log(`  : ${response.error || response.status}`, false);
      return false;
    }
  }

  async testProjectCreation() {
    this.log('  ');
    
    const projectData = {
      title: `  ${Date.now()}`,
      description: '  .',
      video_url: 'https://example.com/test-video.mp4'
    };

    const response = await this.makeAPIRequest('/api/projects/create/', {
      method: 'POST',
      body: JSON.stringify(projectData)
    });

    if (response.success && response.data?.id) {
      this.log('  ', true);
      this.testProjectId = response.data.id;
      return true;
    } else {
      this.log(`  : ${response.error || response.status} - ${response.data?.message || 'Unknown error'}`, false);
      return false;
    }
  }

  async testProjectsList() {
    this.log('   ');
    
    const response = await this.makeAPIRequest('/api/projects/', {
      method: 'GET'
    });

    if (response.success || response.status === 200) {
      //       
      const projectCount = Array.isArray(response.data) ? response.data.length : 
                          (response.data && response.data.results) ? response.data.results.length : 0;
      this.log(`    (${projectCount} )`, true);
      return true;
    } else {
      this.log(`   : ${response.error || response.status} - ${response.data?.message || 'Unknown error'}`, false);
      return false;
    }
  }

  async testVideoPlanning() {
    this.log('   ');
    
    const planningData = {
      project: this.testProjectId,
      title: '  ',
      description: '   .',
      target_audience: ' ',
      duration: '5'
    };

    const response = await this.makeAPIRequest('/api/video-planning/', {
      method: 'POST',
      body: JSON.stringify(planningData)
    });

    if (response.success) {
      this.log('   ', true);
      return true;
    } else {
      this.log(`   : ${response.error || response.status}`, false);
      return false;
    }
  }

  async testAPIPerformance() {
    this.log('API   ');
    
    const endpoints = [
      '/api/health/',
      '/api/',
      '/api/projects/',
      '/api/users/me/'
    ];

    let totalResponseTime = 0;
    let successCount = 0;

    for (const endpoint of endpoints) {
      const startTime = Date.now();
      const response = await this.makeAPIRequest(endpoint, { method: 'GET' });
      const responseTime = Date.now() - startTime;
      
      totalResponseTime += responseTime;
      
      if (response.success || [401, 403].includes(response.status)) {
        successCount++;
        this.log(`${endpoint}: ${responseTime}ms `);
      } else {
        this.log(`${endpoint}: ${responseTime}ms  (${response.status})`);
      }
    }

    const averageResponseTime = totalResponseTime / endpoints.length;
    const performanceGood = averageResponseTime < 1000; // 1 

    this.log(` : ${averageResponseTime.toFixed(0)}ms`, performanceGood);
    return performanceGood;
  }

  async cleanup() {
    this.log('   ');
    
    //    ()
    if (this.testProjectId) {
      await this.makeAPIRequest(`/api/projects/${this.testProjectId}/`, {
        method: 'DELETE'
      });
    }
    
    this.log(' ');
  }

  async runIntegrationTests() {
    console.log(' VideoPlanet   \n');
    
    try {
      // 1.  
      const signupSuccess = await this.testUserRegistration();
      
      if (signupSuccess) {
        // 2.  
        const loginSuccess = await this.testUserLogin();
        
        if (loginSuccess) {
          // 3.    
          await this.testUserProfile();
          await this.testProjectsList();
          
          const projectCreated = await this.testProjectCreation();
          if (projectCreated) {
            await this.testVideoPlanning();
          }
        }
      }
      
      // 4.   (    )
      await this.testAPIPerformance();
      
      // 5. 
      await this.cleanup();
      
      //  
      this.printSummary();
      
    } catch (error) {
      this.log(`    : ${error.message}`, false);
      console.error(error);
    }
  }

  printSummary() {
    console.log('\n' + '=' * 50);
    console.log('    ');
    console.log('=' * 50);
    
    const totalTests = this.testResults.length;
    const passedTests = this.testResults.filter(r => r.success).length;
    const failedTests = totalTests - passedTests;
    const successRate = totalTests > 0 ? ((passedTests / totalTests) * 100).toFixed(1) : 0;
    
    console.log(` : ${totalTests}`);
    console.log(`: ${passedTests} `);
    console.log(`: ${failedTests} `);
    console.log(`: ${successRate}%`);
    
    if (failedTests > 0) {
      console.log('\n  :');
      this.testResults
        .filter(r => !r.success)
        .forEach(r => {
          console.log(`  - ${r.message}`);
        });
    }
    
    // CI/CD exit code
    if (failedTests > 0) {
      process.exit(1);
    }
  }
}

//  
if (import.meta.url === `file://${process.argv[1]}`) {
  const tester = new IntegrationTester();
  tester.runIntegrationTests().catch(console.error);
}

export default IntegrationTester;