/**
 * VideoPlanet 통합 테스트 스크립트
 * 모든 크리티컬 이슈를 체계적으로 검증하는 자동화 도구
 */

import axios from 'axios';
import chalk from 'chalk';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// 환경 설정
const CONFIG = {
  BASE_URL: process.env.BASE_URL || 'https://vlanet.net',
  API_URL: process.env.API_URL || 'https://videoplanet.up.railway.app/api',
  TEST_EMAIL: process.env.TEST_EMAIL || 'test@videoplanet.com',
  TEST_PASSWORD: process.env.TEST_PASSWORD || 'TestUser123!',
  TIMEOUT: 15000,
  RETRY_COUNT: 3,
  PARALLEL_TESTS: true
};

// 색상 정의
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

  // 헬퍼 메서드: HTTP 요청 실행
  async makeRequest(method, url, data = null, requiresAuth = true, retries = CONFIG.RETRY_COUNT) {
    const config = {
      method,
      url,
      timeout: CONFIG.TIMEOUT,
      validateStatus: () => true // 모든 status code 허용
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
          console.log(colors.warn(`   재시도 ${i + 1}/${retries}...`));
          await this.sleep(1000 * (i + 1)); // 지수적 백오프
        }
      }
    }
    throw lastError;
  }

  // 유틸리티: 대기
  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  // 결과 기록
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

  // 성능 메트릭 기록
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

  // 1. 인증 시스템 테스트
  async testAuthentication() {
    console.log(colors.info('\n🔐 인증 시스템 테스트 시작...'));
    
    // 로그인 테스트
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
          test: '로그인 인증',
          category: 'Authentication',
          status: 'PASS',
          message: 'JWT 토큰 발급 성공',
          details: {
            responseTime: `${responseTime}ms`,
            tokenType: 'Bearer',
            hasRefreshToken: !!response.data.refresh
          }
        });
        
        console.log(colors.pass('✅ 로그인 성공'));
        return true;
      } else if (response.status === 401) {
        // 테스트 계정 생성 시도
        return await this.createTestAccount();
      } else {
        throw new Error(`Unexpected response: ${response.status}`);
      }
    } catch (error) {
      this.addResult({
        test: '로그인 인증',
        category: 'Authentication',
        status: 'FAIL',
        message: `로그인 실패: ${error.message}`,
        severity: 'CRITICAL',
        priority: 'P0',
        impact: '시스템 접근 불가',
        error: error.response?.data || error.message
      });
      
      console.log(colors.fail('❌ 로그인 실패'));
      return false;
    }
  }

  // 테스트 계정 생성
  async createTestAccount() {
    console.log(colors.info('   테스트 계정 생성 시도...'));
    
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
        console.log(colors.pass('   테스트 계정 생성 성공'));
        // 다시 로그인 시도
        return await this.testAuthentication();
      } else {
        throw new Error(`Account creation failed: ${response.status}`);
      }
    } catch (error) {
      console.log(colors.fail('   테스트 계정 생성 실패'));
      return false;
    }
  }

  // 2. 영상 기획 기능 테스트
  async testVideoPlanning() {
    console.log(colors.info('\n🎬 영상 기획 기능 테스트...'));
    
    const tests = [
      {
        name: '영상 기획 목록 조회',
        endpoint: '/video-planning/',
        method: 'GET'
      },
      {
        name: '영상 기획 생성',
        endpoint: '/video-planning/create/',
        method: 'POST',
        data: {
          title: `테스트 영상 기획 ${Date.now()}`,
          description: '자동화 테스트로 생성된 영상 기획',
          target_audience: '일반 사용자',
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
            message: `${test.method} 요청 성공`,
            details: {
              statusCode: response.status,
              responseTime: `${response.responseTime}ms`,
              dataCount: Array.isArray(response.data) ? response.data.length : 1
            }
          });
          console.log(colors.pass(`✅ ${test.name} 성공`));
        } else {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
      } catch (error) {
        this.addResult({
          test: test.name,
          category: 'Video Planning',
          status: 'FAIL',
          message: `${test.method} 요청 실패: ${error.message}`,
          severity: 'CRITICAL',
          priority: 'P0',
          impact: '영상 기획 기능 사용 불가',
          details: {
            endpoint: test.endpoint,
            method: test.method,
            error: error.response?.data || error.message
          }
        });
        console.log(colors.fail(`❌ ${test.name} 실패`));
      }
    }
  }

  // 3. 프로젝트 관리 테스트
  async testProjectManagement() {
    console.log(colors.info('\n📁 프로젝트 관리 테스트...'));
    
    let createdProjectId = null;
    
    const tests = [
      {
        name: '프로젝트 목록 조회',
        endpoint: '/projects/',
        method: 'GET'
      },
      {
        name: '프로젝트 생성',
        endpoint: '/projects/create/',
        method: 'POST',
        data: {
          title: `테스트 프로젝트 ${Date.now()}`,
          description: '자동화 테스트로 생성된 프로젝트',
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
          // 프로젝트 생성 성공 시 ID 저장
          if (test.method === 'POST' && response.data?.id) {
            createdProjectId = response.data.id;
          }
          
          this.addResult({
            test: test.name,
            category: 'Project Management',
            status: 'PASS',
            message: `${test.method} 요청 성공`,
            details: {
              statusCode: response.status,
              responseTime: `${response.responseTime}ms`,
              projectId: response.data?.id,
              dataCount: Array.isArray(response.data) ? response.data.length : 1
            }
          });
          console.log(colors.pass(`✅ ${test.name} 성공`));
        } else if (response.status === 500) {
          throw new Error('Internal Server Error - 프로젝트 생성 500 에러 지속됨');
        } else {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
      } catch (error) {
        const severity = error.message.includes('500') ? 'CRITICAL' : 'MAJOR';
        
        this.addResult({
          test: test.name,
          category: 'Project Management',
          status: 'FAIL',
          message: `${test.method} 요청 실패: ${error.message}`,
          severity,
          priority: severity === 'CRITICAL' ? 'P0' : 'P1',
          impact: '프로젝트 관리 기능 차단',
          details: {
            endpoint: test.endpoint,
            method: test.method,
            expectedFix: '백엔드 API 엔드포인트 구현 및 데이터베이스 스키마 확인 필요',
            error: error.response?.data || error.message
          }
        });
        console.log(colors.fail(`❌ ${test.name} 실패`));
      }
    }
    
    // 생성된 프로젝트 정리
    if (createdProjectId) {
      await this.cleanupProject(createdProjectId);
    }
  }

  // 4. 일정관리 테스트
  async testCalendarSystem() {
    console.log(colors.info('\n📅 일정관리 시스템 테스트...'));
    
    const tests = [
      {
        name: '캘린더 이벤트 조회',
        endpoint: '/calendar/events/',
        method: 'GET'
      },
      {
        name: '새 일정 생성',
        endpoint: '/calendar/events/create/',
        method: 'POST',
        data: {
          title: `테스트 일정 ${Date.now()}`,
          description: '자동화 테스트 일정',
          start_date: new Date(Date.now() + 86400000).toISOString().split('T')[0], // 내일
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
            message: `${test.method} 요청 성공`,
            details: {
              statusCode: response.status,
              responseTime: `${response.responseTime}ms`,
              eventId: response.data?.id,
              eventsCount: Array.isArray(response.data) ? response.data.length : 1
            }
          });
          console.log(colors.pass(`✅ ${test.name} 성공`));
        } else if (response.status === 404) {
          throw new Error('Not Found - 캘린더 API 엔드포인트 누락');
        } else {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
      } catch (error) {
        const severity = error.message.includes('404') ? 'CRITICAL' : 'MAJOR';
        
        this.addResult({
          test: test.name,
          category: 'Calendar',
          status: 'FAIL',
          message: `${test.method} 요청 실패: ${error.message}`,
          severity,
          priority: severity === 'CRITICAL' ? 'P0' : 'P1',
          impact: '일정 관리 불가',
          details: {
            endpoint: test.endpoint,
            method: test.method,
            expectedFix: '캘린더 API 엔드포인트 구현 필요',
            error: error.response?.data || error.message
          }
        });
        console.log(colors.fail(`❌ ${test.name} 실패`));
      }
    }
  }

  // 5. 피드백 시스템 테스트
  async testFeedbackSystem() {
    console.log(colors.info('\n💬 피드백 시스템 테스트...'));
    
    const tests = [
      {
        name: '피드백 목록 조회',
        endpoint: '/feedbacks/',
        method: 'GET'
      },
      {
        name: '새 피드백 생성',
        endpoint: '/feedbacks/create/',
        method: 'POST',
        data: {
          subject: `테스트 피드백 ${Date.now()}`,
          message: '자동화 테스트에서 생성된 피드백입니다.',
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
            message: `${test.method} 요청 성공`,
            details: {
              statusCode: response.status,
              responseTime: `${response.responseTime}ms`,
              feedbackId: response.data?.id,
              feedbackCount: Array.isArray(response.data) ? response.data.length : 1
            }
          });
          console.log(colors.pass(`✅ ${test.name} 성공`));
        } else if (response.status === 404) {
          throw new Error('Not Found - 피드백 API 엔드포인트 누락');
        } else {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
      } catch (error) {
        const severity = error.message.includes('404') ? 'CRITICAL' : 'MAJOR';
        
        this.addResult({
          test: test.name,
          category: 'Feedback',
          status: 'FAIL',
          message: `${test.method} 요청 실패: ${error.message}`,
          severity,
          priority: severity === 'CRITICAL' ? 'P0' : 'P1',
          impact: '사용자 피드백 수집 불가',
          details: {
            endpoint: test.endpoint,
            method: test.method,
            expectedFix: '피드백 API 엔드포인트 구현 필요',
            error: error.response?.data || error.message
          }
        });
        console.log(colors.fail(`❌ ${test.name} 실패`));
      }
    }
  }

  // 6. 대시보드 데이터 테스트
  async testDashboard() {
    console.log(colors.info('\n📊 대시보드 데이터 테스트...'));
    
    const dashboardEndpoints = [
      { name: '프로젝트 통계', endpoint: '/dashboard/projects/stats/' },
      { name: '최근 활동', endpoint: '/dashboard/activities/' },
      { name: '사용자 통계', endpoint: '/dashboard/user/stats/' },
      { name: '알림 목록', endpoint: '/notifications/' }
    ];
    
    const results = [];
    
    for (const { name, endpoint } of dashboardEndpoints) {
      try {
        const response = await this.makeRequest('GET', `${CONFIG.API_URL}${endpoint}`);
        
        if (response.status >= 200 && response.status < 300) {
          results.push({ name, status: 'success', data: response.data });
          console.log(colors.pass(`✅ ${name} 로드 성공`));
        } else {
          results.push({ name, status: 'error', statusCode: response.status });
          console.log(colors.warn(`⚠️  ${name} 로드 실패 (${response.status})`));
        }
      } catch (error) {
        results.push({ name, status: 'error', error: error.message });
        console.log(colors.warn(`⚠️  ${name} 로드 실패`));
      }
    }
    
    const successCount = results.filter(r => r.status === 'success').length;
    const totalCount = results.length;
    const successRate = (successCount / totalCount) * 100;
    
    this.addResult({
      test: '대시보드 데이터 로드',
      category: 'Dashboard',
      status: successRate >= 75 ? 'PASS' : successRate >= 50 ? 'PARTIAL' : 'FAIL',
      message: `${successCount}/${totalCount} 데이터 소스 로드 성공`,
      severity: successRate < 50 ? 'MAJOR' : 'MINOR',
      details: {
        successRate: `${successRate.toFixed(1)}%`,
        results: results
      }
    });
  }

  // 7. 마이페이지 기능 테스트
  async testMyPage() {
    console.log(colors.info('\n👤 마이페이지 기능 테스트...'));
    
    const tests = [
      {
        name: '프로필 조회',
        endpoint: '/users/profile/',
        method: 'GET'
      },
      {
        name: '프로필 수정',
        endpoint: '/users/profile/update/',
        method: 'PATCH',
        data: {
          first_name: 'UpdatedTest',
          bio: '테스트 계정 프로필 업데이트'
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
            message: `${test.method} 요청 성공`,
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
          console.log(colors.pass(`✅ ${test.name} 성공`));
        } else {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
      } catch (error) {
        this.addResult({
          test: test.name,
          category: 'User Profile',
          status: 'FAIL',
          message: `${test.method} 요청 실패: ${error.message}`,
          severity: 'MAJOR',
          priority: 'P1',
          impact: '개인화 기능 제한',
          details: {
            endpoint: test.endpoint,
            method: test.method,
            error: error.response?.data || error.message
          }
        });
        console.log(colors.fail(`❌ ${test.name} 실패`));
      }
    }
  }

  // 프로젝트 정리
  async cleanupProject(projectId) {
    try {
      await this.makeRequest('DELETE', `${CONFIG.API_URL}/projects/delete/${projectId}/`);
      console.log(colors.info('   테스트 프로젝트 정리 완료'));
    } catch (error) {
      // 정리 실패는 무시
    }
  }

  // 모든 테스트 실행
  async runAllTests() {
    console.log(colors.header('\n' + '='.repeat(80)));
    console.log(colors.header('VideoPlanet 통합 테스트 시작'));
    console.log(colors.header('='.repeat(80)));
    console.log(colors.info(`환경: ${CONFIG.BASE_URL}`));
    console.log(colors.info(`API: ${CONFIG.API_URL}`));
    console.log(colors.info(`시작 시간: ${new Date().toLocaleString('ko-KR')}`));
    console.log(colors.info(`병렬 실행: ${CONFIG.PARALLEL_TESTS ? '활성화' : '비활성화'}`));
    
    this.startTime = Date.now();
    
    // 1. 인증 테스트 (필수 선행)
    const authSuccess = await this.testAuthentication();
    
    if (authSuccess) {
      if (CONFIG.PARALLEL_TESTS) {
        // 병렬 실행으로 성능 최적화
        console.log(colors.emphasis('\n⚡ 병렬 테스트 실행 시작...'));
        await Promise.all([
          this.testVideoPlanning(),
          this.testProjectManagement(),
          this.testCalendarSystem(),
          this.testFeedbackSystem(),
          this.testDashboard(),
          this.testMyPage()
        ]);
      } else {
        // 순차 실행
        await this.testVideoPlanning();
        await this.testProjectManagement();
        await this.testCalendarSystem();
        await this.testFeedbackSystem();
        await this.testDashboard();
        await this.testMyPage();
      }
    } else {
      console.log(colors.fail('\n❌ 인증 실패로 테스트 중단'));
    }
    
    this.endTime = Date.now();
    this.generateComprehensiveReport();
  }

  // 종합 리포트 생성
  generateComprehensiveReport() {
    console.log(colors.header('\n' + '='.repeat(80)));
    console.log(colors.header('통합 테스트 결과 리포트'));
    console.log(colors.header('='.repeat(80)));
    
    // 카테고리별 결과 분석
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
    
    // 카테고리별 결과 출력
    console.log(colors.header('\n📊 카테고리별 결과:'));
    Object.entries(categories).forEach(([category, stats]) => {
      const successRate = (stats.pass / stats.total) * 100;
      const status = successRate >= 80 ? colors.pass : 
                   successRate >= 60 ? colors.warn : colors.fail;
      
      console.log(`${status(category)}: ${stats.pass}/${stats.total} (${successRate.toFixed(1)}%)`);
    });
    
    // 전체 통계
    const overallSuccessRate = ((passedTests + partialTests * 0.5) / totalTests) * 100;
    const executionTime = ((this.endTime - this.startTime) / 1000).toFixed(2);
    
    console.log(colors.header('\n📈 전체 통계:'));
    console.log(`총 테스트: ${totalTests}`);
    console.log(`${colors.pass(`성공: ${passedTests}`)}`);
    console.log(`${colors.warn(`부분 성공: ${partialTests}`)}`);
    console.log(`${colors.fail(`실패: ${failedTests}`)}`);
    console.log(`전체 성공률: ${overallSuccessRate >= 70 ? colors.pass(overallSuccessRate.toFixed(1) + '%') : 
                                overallSuccessRate >= 50 ? colors.warn(overallSuccessRate.toFixed(1) + '%') :
                                colors.fail(overallSuccessRate.toFixed(1) + '%')}`);
    console.log(`실행 시간: ${executionTime}초`);
    
    // 크리티컬 이슈 분석
    if (this.criticalIssues.length > 0) {
      console.log(colors.header('\n🚨 크리티컬 이슈:'));
      this.criticalIssues.forEach((issue, index) => {
        console.log(colors.fail(`${index + 1}. [${issue.priority}] ${issue.test}`));
        console.log(colors.fail(`   영향: ${issue.impact}`));
        console.log(colors.fail(`   메시지: ${issue.message}`));
        if (issue.details?.expectedFix) {
          console.log(colors.emphasis(`   권장 해결책: ${issue.details.expectedFix}`));
        }
        console.log('');
      });
    }
    
    // 성능 메트릭 요약
    if (Object.keys(this.performanceMetrics).length > 0) {
      console.log(colors.header('\n⚡ 성능 메트릭:'));
      Object.entries(this.performanceMetrics).forEach(([operation, metrics]) => {
        const avgTime = metrics.reduce((sum, m) => sum + m.duration, 0) / metrics.length;
        const maxTime = Math.max(...metrics.map(m => m.duration));
        console.log(`${operation}: 평균 ${avgTime.toFixed(0)}ms, 최대 ${maxTime}ms`);
      });
    }
    
    // 권장 사항
    console.log(colors.header('\n💡 권장 사항:'));
    if (this.criticalIssues.length > 0) {
      console.log(colors.fail('• 크리티컬 이슈들을 즉시 해결해야 합니다.'));
    }
    if (overallSuccessRate < 70) {
      console.log(colors.warn('• 전체 성공률이 70% 미만입니다. 시스템 안정성 검토가 필요합니다.'));
    }
    if (failedTests > totalTests * 0.3) {
      console.log(colors.warn('• 실패 테스트가 30%를 초과합니다. 백엔드 API 점검이 필요합니다.'));
    }
    
    // 결과 저장
    this.saveDetailedResults();
    
    console.log(colors.header('\n' + '='.repeat(80)));
    console.log(overallSuccessRate >= 80 ? 
      colors.pass('✅ 테스트 완료 - 시스템 상태 양호') : 
      colors.warn('⚠️  테스트 완료 - 개선 필요'));
    console.log(colors.header('='.repeat(80)));
  }

  // 상세 결과 저장
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
      console.log(colors.info(`\n📁 상세 결과 저장: ${filename}`));
    } catch (error) {
      console.log(colors.warn(`결과 저장 실패: ${error.message}`));
    }
  }

  // 권장사항 생성
  generateRecommendations() {
    const recommendations = [];
    
    // 실패한 테스트 기반 권장사항
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
        action: `${category} 관련 API 엔드포인트 구현 및 테스트 필요`,
        failedTests: tests,
        estimatedEffort: '2-4 시간'
      });
    });
    
    return recommendations;
  }
}

// 실행부
if (import.meta.url === `file://${process.argv[1]}`) {
  const tester = new ComprehensiveIntegrationTest();
  
  // 명령행 인수 처리
  const args = process.argv.slice(2);
  if (args.includes('--sequential')) {
    CONFIG.PARALLEL_TESTS = false;
  }
  if (args.includes('--timeout')) {
    const timeoutIndex = args.indexOf('--timeout');
    CONFIG.TIMEOUT = parseInt(args[timeoutIndex + 1]) || CONFIG.TIMEOUT;
  }
  
  tester.runAllTests().catch(error => {
    console.error(colors.fail('\n💥 치명적 오류 발생:'), error);
    process.exit(1);
  });
}

export default ComprehensiveIntegrationTest;