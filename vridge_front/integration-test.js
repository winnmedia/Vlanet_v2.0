#!/usr/bin/env node

/**
 * VideoPlanet 통합 테스트 스크립트
 * 실제 사용자 플로우를 시뮬레이션하는 E2E 테스트
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
    const status = success === null ? '📝' : (success ? '✅' : '❌');
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
        // JSON이 아닌 응답도 처리
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
    this.log('사용자 회원가입 테스트 시작');
    
    const response = await this.makeAPIRequest('/api/auth/signup/', {
      method: 'POST',
      body: JSON.stringify({
        email: this.testUser.email,
        password: this.testUser.password,
        nickname: this.testUser.username
      })
    });

    if (response.success) {
      this.log('회원가입 성공', true);
      return true;
    } else {
      this.log(`회원가입 실패: ${response.error || response.status}`, false);
      return false;
    }
  }

  async testUserLogin() {
    this.log('사용자 로그인 테스트 시작');
    
    const response = await this.makeAPIRequest('/api/auth/login/', {
      method: 'POST',
      body: JSON.stringify({
        email: this.testUser.email,
        password: this.testUser.password
      })
    });

    if (response.success && response.data?.access) {
      this.authToken = response.data.access;
      this.log('로그인 성공', true);
      return true;
    } else {
      this.log(`로그인 실패: ${response.error || response.status}`, false);
      return false;
    }
  }

  async testUserProfile() {
    this.log('사용자 프로필 조회 테스트');
    
    const response = await this.makeAPIRequest('/api/users/me/', {
      method: 'GET'
    });

    if (response.success && response.data?.email === this.testUser.email) {
      this.log('프로필 조회 성공', true);
      return true;
    } else {
      this.log(`프로필 조회 실패: ${response.error || response.status}`, false);
      return false;
    }
  }

  async testProjectCreation() {
    this.log('프로젝트 생성 테스트');
    
    const projectData = {
      title: `테스트 프로젝트 ${Date.now()}`,
      description: '통합 테스트용 프로젝트입니다.',
      video_url: 'https://example.com/test-video.mp4'
    };

    const response = await this.makeAPIRequest('/api/projects/create/', {
      method: 'POST',
      body: JSON.stringify(projectData)
    });

    if (response.success && response.data?.id) {
      this.log('프로젝트 생성 성공', true);
      this.testProjectId = response.data.id;
      return true;
    } else {
      this.log(`프로젝트 생성 실패: ${response.error || response.status} - ${response.data?.message || 'Unknown error'}`, false);
      return false;
    }
  }

  async testProjectsList() {
    this.log('프로젝트 목록 조회 테스트');
    
    const response = await this.makeAPIRequest('/api/projects/', {
      method: 'GET'
    });

    if (response.success || response.status === 200) {
      // 데이터가 배열이거나 객체 형태로 올 수 있음
      const projectCount = Array.isArray(response.data) ? response.data.length : 
                          (response.data && response.data.results) ? response.data.results.length : 0;
      this.log(`프로젝트 목록 조회 성공 (${projectCount}개 프로젝트)`, true);
      return true;
    } else {
      this.log(`프로젝트 목록 조회 실패: ${response.error || response.status} - ${response.data?.message || 'Unknown error'}`, false);
      return false;
    }
  }

  async testVideoPlanning() {
    this.log('영상 기획 기능 테스트');
    
    const planningData = {
      project: this.testProjectId,
      title: '테스트 영상 기획',
      description: '통합 테스트용 영상 기획입니다.',
      target_audience: '일반 사용자',
      duration: '5분'
    };

    const response = await this.makeAPIRequest('/api/video-planning/', {
      method: 'POST',
      body: JSON.stringify(planningData)
    });

    if (response.success) {
      this.log('영상 기획 생성 성공', true);
      return true;
    } else {
      this.log(`영상 기획 생성 실패: ${response.error || response.status}`, false);
      return false;
    }
  }

  async testAPIPerformance() {
    this.log('API 성능 테스트 시작');
    
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
        this.log(`${endpoint}: ${responseTime}ms ✓`);
      } else {
        this.log(`${endpoint}: ${responseTime}ms ✗ (${response.status})`);
      }
    }

    const averageResponseTime = totalResponseTime / endpoints.length;
    const performanceGood = averageResponseTime < 1000; // 1초 이내

    this.log(`평균 응답시간: ${averageResponseTime.toFixed(0)}ms`, performanceGood);
    return performanceGood;
  }

  async cleanup() {
    this.log('테스트 데이터 정리 시작');
    
    // 생성된 프로젝트 삭제 (있다면)
    if (this.testProjectId) {
      await this.makeAPIRequest(`/api/projects/${this.testProjectId}/`, {
        method: 'DELETE'
      });
    }
    
    this.log('정리 완료');
  }

  async runIntegrationTests() {
    console.log('🚀 VideoPlanet 통합 테스트 시작\n');
    
    try {
      // 1. 회원가입 테스트
      const signupSuccess = await this.testUserRegistration();
      
      if (signupSuccess) {
        // 2. 로그인 테스트
        const loginSuccess = await this.testUserLogin();
        
        if (loginSuccess) {
          // 3. 인증이 필요한 기능들 테스트
          await this.testUserProfile();
          await this.testProjectsList();
          
          const projectCreated = await this.testProjectCreation();
          if (projectCreated) {
            await this.testVideoPlanning();
          }
        }
      }
      
      // 4. 성능 테스트 (인증 필요 없는 것들도 포함)
      await this.testAPIPerformance();
      
      // 5. 정리
      await this.cleanup();
      
      // 결과 요약
      this.printSummary();
      
    } catch (error) {
      this.log(`통합 테스트 중 오류 발생: ${error.message}`, false);
      console.error(error);
    }
  }

  printSummary() {
    console.log('\n' + '=' * 50);
    console.log('📊 통합 테스트 결과 요약');
    console.log('=' * 50);
    
    const totalTests = this.testResults.length;
    const passedTests = this.testResults.filter(r => r.success).length;
    const failedTests = totalTests - passedTests;
    const successRate = totalTests > 0 ? ((passedTests / totalTests) * 100).toFixed(1) : 0;
    
    console.log(`총 테스트: ${totalTests}`);
    console.log(`성공: ${passedTests} ✅`);
    console.log(`실패: ${failedTests} ❌`);
    console.log(`성공률: ${successRate}%`);
    
    if (failedTests > 0) {
      console.log('\n❌ 실패한 테스트:');
      this.testResults
        .filter(r => !r.success)
        .forEach(r => {
          console.log(`  - ${r.message}`);
        });
    }
    
    // CI/CD용 exit code
    if (failedTests > 0) {
      process.exit(1);
    }
  }
}

// 스크립트 실행
if (import.meta.url === `file://${process.argv[1]}`) {
  const tester = new IntegrationTester();
  tester.runIntegrationTests().catch(console.error);
}

export default IntegrationTester;