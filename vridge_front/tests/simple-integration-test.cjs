/**
 * VideoPlanet 간단 통합 테스트 스크립트
 * 모든 크리티컬 이슈를 검증하는 자동화 도구
 */

const axios = require('axios');
const fs = require('fs');

// 환경 설정
const CONFIG = {
  BASE_URL: process.env.BASE_URL || 'https://vlanet.net',
  API_URL: process.env.API_URL || 'https://videoplanet.up.railway.app/api',
  TEST_EMAIL: process.env.TEST_EMAIL || 'test@videoplanet.com',
  TEST_PASSWORD: process.env.TEST_PASSWORD || 'TestUser123!',
  TIMEOUT: 10000
};

// 콘솔 색상 함수 (chalk 없이)
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
  white: '\x1b[37m',
  bold: '\x1b[1m'
};

const log = {
  error: (msg) => console.log(`${colors.red}❌ ${msg}${colors.reset}`),
  success: (msg) => console.log(`${colors.green}✅ ${msg}${colors.reset}`),
  warning: (msg) => console.log(`${colors.yellow}⚠️  ${msg}${colors.reset}`),
  info: (msg) => console.log(`${colors.blue}ℹ️  ${msg}${colors.reset}`),
  header: (msg) => console.log(`${colors.cyan}${colors.bold}${msg}${colors.reset}`)
};

class SimpleIntegrationTest {
  constructor() {
    this.results = [];
    this.token = null;
    this.startTime = null;
    this.endTime = null;
    this.bugList = [];
  }

  // HTTP 요청 헬퍼
  async makeRequest(method, url, data = null, requiresAuth = true) {
    const config = {
      method,
      url,
      timeout: CONFIG.TIMEOUT,
      validateStatus: () => true
    };

    if (data) config.data = data;
    if (requiresAuth && this.token) {
      config.headers = { Authorization: `Bearer ${this.token}` };
    }

    try {
      const response = await axios(config);
      return response;
    } catch (error) {
      return {
        status: error.code === 'ECONNABORTED' ? 408 : 500,
        statusText: error.message,
        data: null,
        error: error
      };
    }
  }

  // 결과 추가
  addResult(test, status, message, details = {}) {
    const result = {
      test,
      status,
      message,
      timestamp: new Date().toISOString(),
      ...details
    };
    
    this.results.push(result);
    
    if (status === 'FAIL') {
      this.bugList.push({
        id: `BUG_${this.bugList.length + 1}`,
        category: details.category || 'Unknown',
        severity: details.severity || 'MEDIUM',
        title: test,
        description: message,
        status: 'OPEN',
        priority: details.priority || 'P2',
        impact: details.impact || 'Unknown impact',
        timestamp: new Date().toISOString()
      });
    }
    
    return result;
  }

  // 1. 인증 테스트
  async testAuthentication() {
    log.info('🔐 인증 시스템 테스트 시작...');
    
    try {
      const response = await this.makeRequest('POST', `${CONFIG.API_URL}/auth/login/`, {
        email: CONFIG.TEST_EMAIL,
        password: CONFIG.TEST_PASSWORD
      }, false);
      
      if (response.status === 200 && response.data?.access) {
        this.token = response.data.access;
        this.addResult('로그인 인증', 'PASS', 'JWT 토큰 발급 성공', {
          category: 'Authentication',
          responseTime: 'N/A'
        });
        log.success('로그인 성공');
        return true;
      } else if (response.status === 401) {
        // 테스트 계정 생성 시도
        log.info('테스트 계정 생성 시도...');
        const createResponse = await this.makeRequest('POST', `${CONFIG.API_URL}/auth/register/`, {
          email: CONFIG.TEST_EMAIL,
          password: CONFIG.TEST_PASSWORD,
          password_confirm: CONFIG.TEST_PASSWORD,
          username: 'TestUser',
          first_name: 'Test',
          last_name: 'User'
        }, false);
        
        if (createResponse.status === 201) {
          log.success('테스트 계정 생성 성공');
          return await this.testAuthentication(); // 재시도
        } else {
          throw new Error(`Account creation failed: ${createResponse.status}`);
        }
      } else {
        throw new Error(`Login failed: ${response.status} - ${response.statusText}`);
      }
    } catch (error) {
      this.addResult('로그인 인증', 'FAIL', `로그인 실패: ${error.message}`, {
        category: 'Authentication',
        severity: 'CRITICAL',
        priority: 'P0',
        impact: '전체 시스템 접근 불가',
        error: error.message
      });
      log.error('로그인 실패');
      return false;
    }
  }

  // 2. 영상 기획 메뉴 테스트
  async testVideoPlanning() {
    log.info('🎬 영상 기획 메뉴 테스트...');
    
    try {
      const response = await this.makeRequest('GET', `${CONFIG.API_URL}/video-planning/`);
      
      if (response.status >= 200 && response.status < 300) {
        this.addResult('영상 기획 메뉴 접근', 'PASS', '영상 기획 API 접근 성공', {
          category: 'Video Planning',
          statusCode: response.status
        });
        log.success('영상 기획 메뉴 정상 작동');
      } else if (response.status === 404) {
        throw new Error('영상 기획 API 엔드포인트 없음');
      } else {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
    } catch (error) {
      this.addResult('영상 기획 메뉴 접근', 'FAIL', `영상 기획 메뉴 접근 실패: ${error.message}`, {
        category: 'Video Planning',
        severity: 'CRITICAL',
        priority: 'P0',
        impact: '핵심 비즈니스 기능 완전 차단'
      });
      log.error('영상 기획 메뉴 접근 실패');
    }
  }

  // 3. 프로젝트 생성 테스트
  async testProjectCreation() {
    log.info('📁 프로젝트 생성 테스트...');
    
    const projectData = {
      title: `테스트 프로젝트 ${Date.now()}`,
      description: '자동화 테스트로 생성된 프로젝트',
      status: 'planning'
    };
    
    try {
      const response = await this.makeRequest('POST', `${CONFIG.API_URL}/projects/create/`, projectData);
      
      if (response.status >= 200 && response.status < 300) {
        this.addResult('프로젝트 생성', 'PASS', '프로젝트 생성 성공', {
          category: 'Project Management',
          statusCode: response.status,
          projectId: response.data?.id
        });
        log.success('프로젝트 생성 성공');
        
        // 생성된 프로젝트 정리
        if (response.data?.id) {
          await this.cleanupProject(response.data.id);
        }
      } else if (response.status === 500) {
        throw new Error('Internal Server Error - 프로젝트 생성 500 에러');
      } else {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
    } catch (error) {
      this.addResult('프로젝트 생성', 'FAIL', `프로젝트 생성 실패: ${error.message}`, {
        category: 'Project Management',
        severity: 'CRITICAL',
        priority: 'P0',
        impact: '신규 프로젝트 생성 불가'
      });
      log.error('프로젝트 생성 실패');
    }
  }

  // 4. 일정관리 테스트
  async testCalendar() {
    log.info('📅 일정관리 테스트...');
    
    try {
      const response = await this.makeRequest('GET', `${CONFIG.API_URL}/calendar/events/`);
      
      if (response.status >= 200 && response.status < 300) {
        this.addResult('일정관리 페이지', 'PASS', '캘린더 API 접근 성공', {
          category: 'Calendar',
          statusCode: response.status
        });
        log.success('일정관리 정상 작동');
      } else if (response.status === 404) {
        throw new Error('캘린더 API 엔드포인트 404 에러');
      } else {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
    } catch (error) {
      this.addResult('일정관리 페이지', 'FAIL', `일정관리 접근 실패: ${error.message}`, {
        category: 'Calendar',
        severity: 'CRITICAL',
        priority: 'P0',
        impact: '프로젝트 일정 관리 불가'
      });
      log.error('일정관리 접근 실패');
    }
  }

  // 5. 피드백 시스템 테스트
  async testFeedback() {
    log.info('💬 피드백 시스템 테스트...');
    
    try {
      const response = await this.makeRequest('GET', `${CONFIG.API_URL}/feedbacks/`);
      
      if (response.status >= 200 && response.status < 300) {
        this.addResult('피드백 시스템', 'PASS', '피드백 API 접근 성공', {
          category: 'Feedback',
          statusCode: response.status
        });
        log.success('피드백 시스템 정상 작동');
      } else if (response.status === 404) {
        throw new Error('피드백 API 엔드포인트 404 에러');
      } else {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
    } catch (error) {
      this.addResult('피드백 시스템', 'FAIL', `피드백 시스템 접근 실패: ${error.message}`, {
        category: 'Feedback',
        severity: 'CRITICAL',
        priority: 'P0',
        impact: '팀 협업 및 커뮤니케이션 차단'
      });
      log.error('피드백 시스템 접근 실패');
    }
  }

  // 6. 대시보드 테스트
  async testDashboard() {
    log.info('📊 대시보드 테스트...');
    
    try {
      // 프로젝트 목록 조회로 대시보드 데이터 테스트
      const response = await this.makeRequest('GET', `${CONFIG.API_URL}/projects/`);
      
      if (response.status >= 200 && response.status < 300) {
        this.addResult('대시보드 데이터', 'PASS', '대시보드 데이터 로드 성공', {
          category: 'Dashboard',
          statusCode: response.status,
          dataCount: Array.isArray(response.data) ? response.data.length : 0
        });
        log.success('대시보드 정상 작동');
      } else {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
    } catch (error) {
      this.addResult('대시보드 데이터', 'FAIL', `대시보드 데이터 로드 실패: ${error.message}`, {
        category: 'Dashboard',
        severity: 'MAJOR',
        priority: 'P1',
        impact: '사용자 경험 저하'
      });
      log.error('대시보드 데이터 로드 실패');
    }
  }

  // 7. 마이페이지 테스트
  async testMyPage() {
    log.info('👤 마이페이지 테스트...');
    
    try {
      const response = await this.makeRequest('GET', `${CONFIG.API_URL}/users/profile/`);
      
      if (response.status >= 200 && response.status < 300) {
        this.addResult('마이페이지', 'PASS', '프로필 API 접근 성공', {
          category: 'User Profile',
          statusCode: response.status
        });
        log.success('마이페이지 정상 작동');
      } else {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
    } catch (error) {
      this.addResult('마이페이지', 'FAIL', `마이페이지 접근 실패: ${error.message}`, {
        category: 'User Profile',
        severity: 'MAJOR',
        priority: 'P1',
        impact: '개인화 기능 사용 불가'
      });
      log.error('마이페이지 접근 실패');
    }
  }

  // 프로젝트 정리
  async cleanupProject(projectId) {
    try {
      await this.makeRequest('DELETE', `${CONFIG.API_URL}/projects/delete/${projectId}/`);
      log.info('테스트 프로젝트 정리 완료');
    } catch (error) {
      // 정리 실패는 무시
    }
  }

  // 모든 테스트 실행
  async runAllTests() {
    log.header('================================================================================');
    log.header('VideoPlanet 크리티컬 이슈 검증 시작');
    log.header('================================================================================');
    console.log(`환경: ${CONFIG.BASE_URL}`);
    console.log(`API: ${CONFIG.API_URL}`);
    console.log(`시작 시간: ${new Date().toLocaleString('ko-KR')}`);
    
    this.startTime = Date.now();
    
    // 1. 인증 테스트 (필수 선행)
    const authSuccess = await this.testAuthentication();
    
    if (authSuccess) {
      // 2. 모든 기능 테스트 실행
      await this.testVideoPlanning();
      await this.testProjectCreation();
      await this.testCalendar();
      await this.testFeedback();
      await this.testDashboard();
      await this.testMyPage();
    } else {
      log.error('인증 실패로 테스트 중단');
    }
    
    this.endTime = Date.now();
    this.generateReport();
  }

  // 리포트 생성
  generateReport() {
    log.header('================================================================================');
    log.header('테스트 결과 리포트');
    log.header('================================================================================');
    
    let passCount = 0;
    let failCount = 0;
    const criticalIssues = [];
    
    // 결과 분석
    this.results.forEach(result => {
      const icon = result.status === 'PASS' ? '✅' : '❌';
      const color = result.status === 'PASS' ? colors.green : colors.red;
      
      console.log(`\n${icon} ${color}${result.test}${colors.reset}`);
      console.log(`   상태: ${result.status}`);
      console.log(`   메시지: ${result.message}`);
      
      if (result.severity === 'CRITICAL') {
        console.log(`   ${colors.red}우선순위: ${result.priority}${colors.reset}`);
        console.log(`   ${colors.red}심각도: ${result.severity}${colors.reset}`);
        console.log(`   영향: ${result.impact}`);
        criticalIssues.push(result);
      }
      
      if (result.status === 'PASS') passCount++;
      else failCount++;
    });
    
    // 요약
    log.header('================================================================================');
    log.header('요약');
    log.header('================================================================================');
    
    const totalTests = this.results.length;
    const successRate = totalTests > 0 ? ((passCount / totalTests) * 100).toFixed(1) : 0;
    const executionTime = ((this.endTime - this.startTime) / 1000).toFixed(2);
    
    console.log(`총 테스트: ${totalTests}`);
    console.log(`${colors.green}성공: ${passCount}${colors.reset}`);
    console.log(`${colors.red}실패: ${failCount}${colors.reset}`);
    console.log(`성공률: ${successRate < 50 ? colors.red : successRate < 80 ? colors.yellow : colors.green}${successRate}%${colors.reset}`);
    console.log(`실행 시간: ${executionTime}초`);
    
    // 크리티컬 이슈 요약
    if (criticalIssues.length > 0) {
      log.header('================================================================================');
      console.log(`${colors.red}${colors.bold}⚠️  크리티컬 이슈 발견!${colors.reset}`);
      log.header('================================================================================');
      
      console.log(`${colors.red}총 ${criticalIssues.length}개의 크리티컬 이슈:${colors.reset}`);
      criticalIssues.forEach((issue, index) => {
        console.log(`${colors.red}${index + 1}. [${issue.priority}] ${issue.test}: ${issue.impact}${colors.reset}`);
      });
      
      console.log(`${colors.red}즉시 조치가 필요합니다!${colors.reset}`);
    } else {
      console.log(`${colors.green}✅ 모든 테스트 통과! 크리티컬 이슈 없음${colors.reset}`);
    }
    
    // 결과 저장
    this.saveResults();
  }

  // 결과 저장
  saveResults() {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = `test-results-${timestamp}.json`;
    
    const report = {
      summary: {
        totalTests: this.results.length,
        passed: this.results.filter(r => r.status === 'PASS').length,
        failed: this.results.filter(r => r.status === 'FAIL').length,
        criticalIssues: this.results.filter(r => r.severity === 'CRITICAL').length,
        executionTime: `${((this.endTime - this.startTime) / 1000).toFixed(2)}s`,
        timestamp: new Date().toISOString()
      },
      environment: CONFIG,
      results: this.results,
      bugList: this.bugList,
      recommendations: this.generateRecommendations()
    };
    
    try {
      fs.writeFileSync(filename, JSON.stringify(report, null, 2));
      console.log(`\n${colors.blue}📁 결과 저장: ${filename}${colors.reset}`);
    } catch (error) {
      console.log(`${colors.yellow}결과 저장 실패: ${error.message}${colors.reset}`);
    }
  }

  // 권장사항 생성
  generateRecommendations() {
    const recommendations = [];
    
    // 카테고리별 실패 분석
    const failuresByCategory = {};
    this.results.filter(r => r.status === 'FAIL').forEach(result => {
      const category = result.category || 'Unknown';
      if (!failuresByCategory[category]) {
        failuresByCategory[category] = [];
      }
      failuresByCategory[category].push(result.test);
    });
    
    Object.entries(failuresByCategory).forEach(([category, tests]) => {
      recommendations.push({
        category,
        priority: 'HIGH',
        action: `${category} 관련 백엔드 API 엔드포인트 구현`,
        failedTests: tests,
        estimatedEffort: '2-4 시간',
        impact: 'CRITICAL'
      });
    });
    
    return recommendations;
  }

  // 버그 리스트 출력
  printBugList() {
    if (this.bugList.length === 0) {
      log.success('발견된 버그 없음');
      return;
    }

    log.header('================================================================================');
    log.header('🐛 버그 리스트');
    log.header('================================================================================');
    
    this.bugList.forEach(bug => {
      console.log(`\n${colors.red}${bug.id}: ${bug.title}${colors.reset}`);
      console.log(`카테고리: ${bug.category}`);
      console.log(`심각도: ${colors.red}${bug.severity}${colors.reset}`);
      console.log(`우선순위: ${bug.priority}`);
      console.log(`설명: ${bug.description}`);
      console.log(`영향: ${bug.impact}`);
      console.log(`상태: ${bug.status}`);
      console.log(`발견일: ${new Date(bug.timestamp).toLocaleString('ko-KR')}`);
    });
    
    log.header('================================================================================');
    console.log(`${colors.red}총 ${this.bugList.length}개의 버그가 발견되었습니다.${colors.reset}`);
  }
}

// 실행
const tester = new SimpleIntegrationTest();
tester.runAllTests()
  .then(() => {
    console.log('\n');
    tester.printBugList();
  })
  .catch(error => {
    console.error(`${colors.red}💥 치명적 오류 발생:${colors.reset}`, error);
    process.exit(1);
  });