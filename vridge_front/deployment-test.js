#!/usr/bin/env node

/**
 * VideoPlanet 배포 상태 테스트 스크립트
 * CI/CD 파이프라인용 자동화된 배포 검증 도구
 */

import https from 'https';
import http from 'http';
import { performance } from 'perf_hooks';
import fs from 'fs';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// 테스트 설정
const CONFIG = {
  PRODUCTION_URL: 'https://www.vlanet.net',
  STAGING_URL: 'https://videoplanet-seven.vercel.app',
  API_URL: 'https://videoplanet.up.railway.app',
  TIMEOUT: 10000, // 10초
  RETRY_COUNT: 3
};

// 테스트 결과 저장용
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

  // HTTP 요청 헬퍼 함수
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

  // 테스트 결과 기록
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
      console.log(`✅ ${testName}`);
    } else {
      testResults.summary.failed++;
      console.log(`❌ ${testName}`);
      if (details.error) {
        console.log(`   Error: ${details.error}`);
      }
    }
    
    if (details.responseTime) {
      console.log(`   Response time: ${details.responseTime}ms`);
    }
  }

  // 1. 프론트엔드 배포 테스트
  async testFrontendDeployment() {
    console.log('\n🌐 프론트엔드 배포 테스트 시작...');
    
    // 프로덕션 환경 테스트
    try {
      const response = await this.makeRequest(CONFIG.PRODUCTION_URL);
      this.logResult('Production Frontend (vlanet.net)', response.success, {
        statusCode: response.statusCode,
        responseTime: response.responseTime,
        hasContent: response.data.length > 0
      });
      
      // HTML 내용 기본 검증
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

    // 스테이징 환경 테스트
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

  // 2. 백엔드 API 테스트
  async testBackendAPI() {
    console.log('\n🔧 백엔드 API 테스트 시작...');
    
    // 헬스 체크
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

    // API 문서 엔드포인트
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

    // 주요 엔드포인트 테스트
    const endpoints = [
      '/api/auth/login/',
      '/api/users/me/',
      '/api/projects/',
      '/api/video-planning/'
    ];

    for (const endpoint of endpoints) {
      try {
        const response = await this.makeRequest(`${CONFIG.API_URL}${endpoint}`);
        // 401/403은 인증이 필요한 정상적인 응답
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

  // 3. 성능 테스트
  async testPerformance() {
    console.log('\n⚡ 성능 테스트 시작...');
    
    const urls = [
      { name: 'Production Frontend', url: CONFIG.PRODUCTION_URL },
      { name: 'API Health', url: `${CONFIG.API_URL}/api/health/` }
    ];

    for (const { name, url } of urls) {
      try {
        const response = await this.makeRequest(url);
        const isGoodPerformance = response.responseTime < 2000; // 2초 이내
        
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

  // 4. SSL 및 보안 테스트
  async testSecurity() {
    console.log('\n🔒 보안 테스트 시작...');
    
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

  // 5. CORS 테스트
  async testCORS() {
    console.log('\n🌐 CORS 설정 테스트 시작...');
    
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

  // 전체 테스트 실행
  async runAllTests() {
    console.log('🚀 VideoPlanet 배포 테스트 시작\n');
    console.log('=' * 50);
    
    try {
      await this.testFrontendDeployment();
      await this.testBackendAPI();
      await this.testPerformance();
      await this.testSecurity();
      await this.testCORS();
      
      // 테스트 완료 시간 기록
      const endTime = performance.now();
      testResults.summary.duration = Math.round(endTime - this.startTime);
      
      // 결과 출력
      this.printSummary();
      
      // 결과 파일 저장
      await this.saveResults();
      
      // 실패한 테스트가 있으면 exit code 1
      if (testResults.summary.failed > 0) {
        process.exit(1);
      }
      
    } catch (error) {
      console.error('테스트 실행 중 오류 발생:', error);
      process.exit(1);
    }
  }

  // 테스트 결과 요약 출력
  printSummary() {
    console.log('\n' + '=' * 50);
    console.log('📊 테스트 결과 요약');
    console.log('=' * 50);
    console.log(`총 테스트: ${testResults.summary.total}`);
    console.log(`성공: ${testResults.summary.passed} ✅`);
    console.log(`실패: ${testResults.summary.failed} ❌`);
    console.log(`성공률: ${((testResults.summary.passed / testResults.summary.total) * 100).toFixed(1)}%`);
    console.log(`실행 시간: ${testResults.summary.duration}ms`);
    
    if (testResults.summary.failed > 0) {
      console.log('\n❌ 실패한 테스트:');
      testResults.results
        .filter(r => !r.success)
        .forEach(r => {
          console.log(`  - ${r.test}: ${r.details.error || 'Unknown error'}`);
        });
    }
  }

  // 결과를 JSON 파일로 저장
  async saveResults() {
    const filename = `deployment-test-results-${Date.now()}.json`;
    const filepath = `/home/winnmedia/VideoPlanet/videoplanet-clean/${filename}`;
    
    try {
      fs.writeFileSync(filepath, JSON.stringify(testResults, null, 2));
      console.log(`\n📁 결과가 저장되었습니다: ${filepath}`);
    } catch (error) {
      console.error('결과 저장 실패:', error.message);
    }
  }
}

// 스크립트 실행
if (import.meta.url === `file://${process.argv[1]}`) {
  const tester = new DeploymentTester();
  tester.runAllTests().catch(console.error);
}

export default DeploymentTester;