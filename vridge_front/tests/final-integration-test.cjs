/**
 * 최종 통합 테스트 스크립트
 * 실제 API 스펙에 맞춘 정확한 테스트
 */

const axios = require('axios');
const fs = require('fs');

const CONFIG = {
  BASE_URL: 'https://vlanet.net',
  API_URL: 'https://videoplanet.up.railway.app/api',
  TEST_EMAIL: 'test@videoplanet.com',
  TEST_PASSWORD: 'TestUser123!',
  TIMEOUT: 15000
};

// 콘솔 색상 함수
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
  bold: '\x1b[1m'
};

const log = {
  error: (msg) => console.log(`${colors.red}❌ ${msg}${colors.reset}`),
  success: (msg) => console.log(`${colors.green}✅ ${msg}${colors.reset}`),
  warning: (msg) => console.log(`${colors.yellow}⚠️  ${msg}${colors.reset}`),
  info: (msg) => console.log(`${colors.blue}ℹ️  ${msg}${colors.reset}`),
  header: (msg) => console.log(`${colors.cyan}${colors.bold}${msg}${colors.reset}`)
};

class FinalIntegrationTest {
  constructor() {
    this.results = [];
    this.bugList = [];
    this.token = null;
    this.startTime = Date.now();
  }

  async makeRequest(method, url, data = null, requiresAuth = true) {
    const config = {
      method,
      url,
      timeout: CONFIG.TIMEOUT,
      validateStatus: () => true,
      headers: {
        'Content-Type': 'application/json',
        'User-Agent': 'VideoPlanet-FinalTest/1.0'
      }
    };

    if (data) config.data = data;
    if (requiresAuth && this.token) {
      config.headers.Authorization = `Bearer ${this.token}`;
    }

    try {
      const startTime = Date.now();
      const response = await axios(config);
      const responseTime = Date.now() - startTime;
      
      return { ...response, responseTime };
    } catch (error) {
      return {
        status: error.code === 'ECONNABORTED' ? 408 : 0,
        statusText: error.message,
        data: null,
        error: error.message,
        responseTime: 0
      };
    }
  }

  addResult(test, status, message, details = {}) {
    const result = {
      test,
      status,
      message,
      timestamp: new Date().toISOString(),
      ...details
    };
    
    this.results.push(result);
    
    if (status === 'FAIL' && details.critical) {
      this.bugList.push({
        id: `CRITICAL_${this.bugList.length + 1}`,
        category: details.category || 'Unknown',
        severity: details.severity || 'CRITICAL',
        title: test,
        description: message,
        status: 'OPEN',
        priority: details.priority || 'P0',
        impact: details.impact || 'Critical functionality blocked',
        endpoint: details.endpoint,
        httpStatus: details.httpStatus,
        timestamp: new Date().toISOString(),
        fix: details.fix || '즉시 조치 필요'
      });
    }
    
    return result;
  }

  // 1. 인증 시스템 테스트 (실제 엔드포인트)
  async testAuthentication() {
    log.info('🔐 인증 시스템 테스트 (실제 API 엔드포인트)...');
    
    // 회원가입 테스트 (실제 엔드포인트: /api/auth/signup/)
    try {
      const signupResponse = await this.makeRequest('POST', `${CONFIG.API_URL}/auth/signup/`, {
        email: CONFIG.TEST_EMAIL,
        password: CONFIG.TEST_PASSWORD,
        password_confirm: CONFIG.TEST_PASSWORD,
        username: 'TestUser',
        first_name: 'Test',
        last_name: 'User'
      }, false);
      
      if (signupResponse.status === 201) {
        log.success('회원가입 성공');
      } else if (signupResponse.status === 400) {
        log.info('회원가입 스킵 (이미 존재하는 계정)');
      } else {
        log.warning(`회원가입 응답: ${signupResponse.status}`);
      }
      
    } catch (error) {
      log.warning(`회원가입 오류: ${error.message}`);
    }
    
    // 로그인 테스트 (실제 엔드포인트: /api/auth/login/)
    try {
      const loginResponse = await this.makeRequest('POST', `${CONFIG.API_URL}/auth/login/`, {
        email: CONFIG.TEST_EMAIL,
        password: CONFIG.TEST_PASSWORD
      }, false);
      
      if (loginResponse.status === 200 && loginResponse.data?.access) {
        this.token = loginResponse.data.access;
        this.addResult('로그인 인증', 'PASS', 'JWT 토큰 발급 성공', {
          category: 'Authentication',
          httpStatus: loginResponse.status,
          responseTime: loginResponse.responseTime
        });
        log.success(`로그인 성공 (${loginResponse.responseTime}ms)`);
        return true;
      } else if (loginResponse.status === 401) {
        this.addResult('로그인 인증', 'FAIL', '잘못된 인증 정보', {
          category: 'Authentication',
          severity: 'MAJOR',
          priority: 'P1',
          impact: '테스트 계정 인증 실패',
          httpStatus: loginResponse.status,
          fix: '테스트 계정 확인 필요'
        });
        log.error('로그인 실패 - 잘못된 인증 정보');
        return false;
      } else {
        throw new Error(`Unexpected login response: ${loginResponse.status}`);
      }
    } catch (error) {
      this.addResult('로그인 인증', 'FAIL', `로그인 실패: ${error.message}`, {
        category: 'Authentication',
        severity: 'CRITICAL',
        priority: 'P0',
        impact: '전체 시스템 접근 불가',
        critical: true,
        fix: '로그인 API 점검 필요'
      });
      log.error(`로그인 실패: ${error.message}`);
      return false;
    }
  }

  // 2. 핵심 기능 테스트
  async testCoreFeatures() {
    if (!this.token) {
      log.warning('인증 토큰이 없어 핵심 기능 테스트를 건너뜁니다.');
      return;
    }
    
    log.info('🎯 핵심 기능 테스트...');
    
    // 2.1 사용자 프로필 조회 (실제 엔드포인트: /api/users/me/)
    try {
      const profileResponse = await this.makeRequest('GET', `${CONFIG.API_URL}/users/me/`);
      
      if (profileResponse.status === 200) {
        this.addResult('사용자 프로필 조회', 'PASS', '프로필 정보 조회 성공', {
          category: 'User Management',
          httpStatus: profileResponse.status,
          responseTime: profileResponse.responseTime
        });
        log.success(`사용자 프로필 조회 성공 (${profileResponse.responseTime}ms)`);
      } else if (profileResponse.status === 401) {
        throw new Error('인증 토큰 만료 또는 무효');
      } else {
        throw new Error(`HTTP ${profileResponse.status}`);
      }
    } catch (error) {
      this.addResult('사용자 프로필 조회', 'FAIL', `프로필 조회 실패: ${error.message}`, {
        category: 'User Management',
        severity: 'MAJOR',
        priority: 'P1',
        impact: '마이페이지 기능 제한',
        endpoint: '/api/users/me/',
        fix: '사용자 프로필 API 점검'
      });
      log.error(`사용자 프로필 조회 실패: ${error.message}`);
    }
    
    // 2.2 프로젝트 목록 조회
    try {
      const projectsResponse = await this.makeRequest('GET', `${CONFIG.API_URL}/projects/`);
      
      if (projectsResponse.status === 200) {
        const projectCount = Array.isArray(projectsResponse.data) ? projectsResponse.data.length : 0;
        this.addResult('프로젝트 목록 조회', 'PASS', `프로젝트 목록 조회 성공 (${projectCount}개)`, {
          category: 'Project Management',
          httpStatus: projectsResponse.status,
          responseTime: projectsResponse.responseTime,
          dataCount: projectCount
        });
        log.success(`프로젝트 목록 조회 성공: ${projectCount}개 (${projectsResponse.responseTime}ms)`);
      } else if (projectsResponse.status === 401) {
        throw new Error('인증 토큰 문제');
      } else {
        throw new Error(`HTTP ${projectsResponse.status}`);
      }
    } catch (error) {
      this.addResult('프로젝트 목록 조회', 'FAIL', `프로젝트 목록 조회 실패: ${error.message}`, {
        category: 'Project Management',
        severity: 'CRITICAL',
        priority: 'P0',
        impact: '프로젝트 관리 기능 완전 차단',
        critical: true,
        endpoint: '/api/projects/',
        fix: '프로젝트 API 엔드포인트 점검'
      });
      log.error(`프로젝트 목록 조회 실패: ${error.message}`);
    }
    
    // 2.3 프로젝트 생성 테스트
    try {
      const createProjectData = {
        title: `테스트 프로젝트 ${Date.now()}`,
        description: '자동화 테스트로 생성된 프로젝트',
        status: 'planning'
      };
      
      const createResponse = await this.makeRequest('POST', `${CONFIG.API_URL}/projects/create/`, createProjectData);
      
      if (createResponse.status === 201) {
        this.addResult('프로젝트 생성', 'PASS', '프로젝트 생성 성공', {
          category: 'Project Management',
          httpStatus: createResponse.status,
          responseTime: createResponse.responseTime,
          projectId: createResponse.data?.id
        });
        log.success(`프로젝트 생성 성공 (${createResponse.responseTime}ms)`);
        
        // 생성된 프로젝트 정리
        if (createResponse.data?.id) {
          await this.cleanupProject(createResponse.data.id);
        }
      } else if (createResponse.status === 500) {
        throw new Error('서버 내부 오류 (500) - 프로젝트 생성 실패');
      } else {
        throw new Error(`HTTP ${createResponse.status}`);
      }
    } catch (error) {
      this.addResult('프로젝트 생성', 'FAIL', `프로젝트 생성 실패: ${error.message}`, {
        category: 'Project Management',
        severity: 'CRITICAL',
        priority: 'P0',
        impact: '새로운 프로젝트 생성 불가',
        critical: true,
        endpoint: '/api/projects/create/',
        fix: error.message.includes('500') ? '백엔드 서버 로직 점검 필요' : 'API 연결 점검 필요'
      });
      log.error(`프로젝트 생성 실패: ${error.message}`);
    }
    
    // 2.4 영상 기획 기능 테스트
    try {
      const videoPlanningResponse = await this.makeRequest('GET', `${CONFIG.API_URL}/video-planning/`);
      
      if (videoPlanningResponse.status === 200) {
        const planningCount = Array.isArray(videoPlanningResponse.data) ? videoPlanningResponse.data.length : 0;
        this.addResult('영상 기획 조회', 'PASS', `영상 기획 목록 조회 성공 (${planningCount}개)`, {
          category: 'Video Planning',
          httpStatus: videoPlanningResponse.status,
          responseTime: videoPlanningResponse.responseTime,
          dataCount: planningCount
        });
        log.success(`영상 기획 조회 성공: ${planningCount}개 (${videoPlanningResponse.responseTime}ms)`);
      } else if (videoPlanningResponse.status === 401) {
        throw new Error('인증 토큰 문제');
      } else {
        throw new Error(`HTTP ${videoPlanningResponse.status}`);
      }
    } catch (error) {
      this.addResult('영상 기획 조회', 'FAIL', `영상 기획 조회 실패: ${error.message}`, {
        category: 'Video Planning',
        severity: 'CRITICAL',
        priority: 'P0',
        impact: '영상 기획 핵심 기능 차단',
        critical: true,
        endpoint: '/api/video-planning/',
        fix: '영상 기획 API 엔드포인트 점검'
      });
      log.error(`영상 기획 조회 실패: ${error.message}`);
    }
    
    // 2.5 피드백 시스템 테스트
    try {
      const feedbackResponse = await this.makeRequest('GET', `${CONFIG.API_URL}/feedbacks/`);
      
      if (feedbackResponse.status === 200) {
        const feedbackCount = Array.isArray(feedbackResponse.data) ? feedbackResponse.data.length : 0;
        this.addResult('피드백 시스템', 'PASS', `피드백 목록 조회 성공 (${feedbackCount}개)`, {
          category: 'Feedback System',
          httpStatus: feedbackResponse.status,
          responseTime: feedbackResponse.responseTime,
          dataCount: feedbackCount
        });
        log.success(`피드백 시스템 정상: ${feedbackCount}개 (${feedbackResponse.responseTime}ms)`);
      } else {
        throw new Error(`HTTP ${feedbackResponse.status}`);
      }
    } catch (error) {
      this.addResult('피드백 시스템', 'FAIL', `피드백 시스템 오류: ${error.message}`, {
        category: 'Feedback System',
        severity: 'MAJOR',
        priority: 'P1',
        impact: '피드백 수집 기능 제한',
        endpoint: '/api/feedbacks/',
        fix: '피드백 API 엔드포인트 점검'
      });
      log.error(`피드백 시스템 오류: ${error.message}`);
    }
  }

  // 3. 프론트엔드 페이지 접근성 테스트
  async testFrontendPages() {
    log.info('🌐 프론트엔드 핵심 페이지 테스트...');
    
    const criticalPages = [
      { path: '/', name: '홈페이지', critical: true },
      { path: '/login', name: '로그인 페이지', critical: true },
      { path: '/signup', name: '회원가입 페이지', critical: true },
      { path: '/dashboard', name: '대시보드', critical: true },
      { path: '/projects', name: '프로젝트 목록', critical: true },
      { path: '/video-planning', name: '영상 기획 페이지', critical: true },
      { path: '/calendar', name: '일정관리 페이지', critical: false },
      { path: '/feedbacks', name: '피드백 페이지', critical: false },
      { path: '/mypage', name: '마이페이지', critical: false }
    ];
    
    for (const page of criticalPages) {
      try {
        const response = await this.makeRequest('GET', `${CONFIG.BASE_URL}${page.path}`, null, false);
        
        if (response.status === 200) {
          this.addResult(page.name, 'PASS', `페이지 로드 성공`, {
            category: 'Frontend Pages',
            httpStatus: response.status,
            responseTime: response.responseTime,
            endpoint: page.path
          });
          log.success(`${page.name} 로드 성공 (${response.responseTime}ms)`);
        } else if (response.status === 404) {
          this.addResult(page.name, 'FAIL', '페이지 404 에러', {
            category: 'Frontend Pages',
            severity: page.critical ? 'CRITICAL' : 'MAJOR',
            priority: page.critical ? 'P0' : 'P1',
            impact: page.critical ? '핵심 페이지 접근 불가' : '기능 페이지 접근 제한',
            critical: page.critical,
            httpStatus: response.status,
            endpoint: page.path,
            fix: 'Next.js 라우팅 설정 점검 필요'
          });
          log.error(`${page.name} 404 에러`);
        } else {
          this.addResult(page.name, 'PARTIAL', `비정상 응답: HTTP ${response.status}`, {
            category: 'Frontend Pages',
            httpStatus: response.status,
            responseTime: response.responseTime,
            endpoint: page.path
          });
          log.warning(`${page.name} 비정상 응답: ${response.status}`);
        }
      } catch (error) {
        this.addResult(page.name, 'FAIL', `페이지 테스트 실패: ${error.message}`, {
          category: 'Frontend Pages',
          severity: 'MAJOR',
          priority: 'P1',
          impact: '페이지 접근 불가',
          endpoint: page.path,
          fix: '네트워크 연결 또는 서버 점검'
        });
        log.error(`${page.name} 테스트 실패`);
      }
    }
  }

  // 프로젝트 정리
  async cleanupProject(projectId) {
    try {
      await this.makeRequest('DELETE', `${CONFIG.API_URL}/projects/${projectId}/`);
      log.info('테스트 프로젝트 정리 완료');
    } catch (error) {
      // 정리 실패는 무시
    }
  }

  // 모든 테스트 실행
  async runAllTests() {
    log.header('================================================================================');
    log.header('VideoPlanet 최종 통합 테스트');
    log.header('================================================================================');
    console.log(`프론트엔드: ${CONFIG.BASE_URL}`);
    console.log(`백엔드 API: ${CONFIG.API_URL}`);
    console.log(`시작 시간: ${new Date().toLocaleString('ko-KR')}`);
    console.log('');
    
    // 1. 인증 시스템 테스트
    const authSuccess = await this.testAuthentication();
    console.log('');
    
    // 2. 핵심 기능 테스트
    await this.testCoreFeatures();
    console.log('');
    
    // 3. 프론트엔드 페이지 테스트
    await this.testFrontendPages();
    
    // 최종 리포트 생성
    this.generateFinalReport();
  }

  // 최종 리포트 생성
  generateFinalReport() {
    const endTime = Date.now();
    const executionTime = ((endTime - this.startTime) / 1000).toFixed(2);
    
    log.header('================================================================================');
    log.header('🎯 VideoPlanet 크리티컬 이슈 최종 분석');
    log.header('================================================================================');
    
    // 전체 통계
    const totalTests = this.results.length;
    const passedTests = this.results.filter(r => r.status === 'PASS').length;
    const failedTests = this.results.filter(r => r.status === 'FAIL').length;
    const partialTests = this.results.filter(r => r.status === 'PARTIAL').length;
    const overallSuccessRate = ((passedTests + partialTests * 0.5) / totalTests) * 100;
    
    console.log(`${colors.cyan}${colors.bold}📊 전체 테스트 결과:${colors.reset}`);
    console.log(`총 테스트: ${totalTests}`);
    console.log(`${colors.green}✅ 성공: ${passedTests}${colors.reset}`);
    console.log(`${colors.yellow}⚠️  부분 성공: ${partialTests}${colors.reset}`);
    console.log(`${colors.red}❌ 실패: ${failedTests}${colors.reset}`);
    console.log(`전체 성공률: ${overallSuccessRate >= 70 ? colors.green : overallSuccessRate >= 50 ? colors.yellow : colors.red}${overallSuccessRate.toFixed(1)}%${colors.reset}`);
    console.log(`실행 시간: ${executionTime}초`);
    console.log('');
    
    // 크리티컬 이슈 분석
    if (this.bugList.length > 0) {
      log.header('🚨 크리티컬 이슈 발견:');
      this.bugList.forEach((bug, index) => {
        console.log(`${colors.red}${colors.bold}${index + 1}. [${bug.priority}] ${bug.title}${colors.reset}`);
        console.log(`   ${colors.red}문제: ${bug.description}${colors.reset}`);
        console.log(`   영향: ${bug.impact}`);
        console.log(`   권장 해결책: ${colors.yellow}${bug.fix}${colors.reset}`);
        if (bug.endpoint) {
          console.log(`   엔드포인트: ${bug.endpoint}`);
        }
        console.log('');
      });
    }
    
    // 카테고리별 성공률
    const categories = {};
    this.results.forEach(result => {
      const category = result.category || 'Unknown';
      if (!categories[category]) {
        categories[category] = { pass: 0, total: 0 };
      }
      categories[category].total++;
      if (result.status === 'PASS') {
        categories[category].pass++;
      }
    });
    
    log.header('📈 카테고리별 성공률:');
    Object.entries(categories).forEach(([category, stats]) => {
      const rate = (stats.pass / stats.total * 100).toFixed(1);
      const color = stats.pass === stats.total ? colors.green : 
                   stats.pass >= stats.total * 0.7 ? colors.yellow : colors.red;
      console.log(`${color}${category}: ${stats.pass}/${stats.total} (${rate}%)${colors.reset}`);
    });
    
    console.log('');
    
    // 최종 권장사항
    log.header('💡 최종 권장사항:');
    if (this.bugList.length === 0) {
      console.log(`${colors.green}✅ 모든 크리티컬 이슈가 해결되었습니다!${colors.reset}`);
    } else {
      console.log(`${colors.red}📋 ${this.bugList.length}개의 크리티컬 이슈가 발견되었습니다:${colors.reset}`);
      console.log(`${colors.yellow}1. 우선순위: P0 이슈들을 즉시 해결하세요${colors.reset}`);
      console.log(`${colors.yellow}2. 백엔드: API 엔드포인트 및 데이터베이스 점검${colors.reset}`);
      console.log(`${colors.yellow}3. 프론트엔드: Next.js 라우팅 설정 확인${colors.reset}`);
      console.log(`${colors.yellow}4. 인증: JWT 토큰 관리 시스템 점검${colors.reset}`);
    }
    
    // 결과 저장
    this.saveDetailedResults(executionTime);
    
    console.log('');
    // 최종 상태 판정
    if (overallSuccessRate >= 80 && this.bugList.length === 0) {
      log.success('🎉 시스템 상태 우수 - 모든 크리티컬 이슈 해결됨');
    } else if (overallSuccessRate >= 60) {
      log.warning('⚠️  시스템 일부 개선 필요 - 빠른 시일 내 조치 권장');
    } else {
      log.error('🚨 시스템 심각한 문제 - 즉시 조치 필요');
    }
  }

  // 상세 결과 저장
  saveDetailedResults(executionTime) {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = `final-test-results-${timestamp}.json`;
    
    const report = {
      summary: {
        testName: 'VideoPlanet 최종 통합 테스트',
        totalTests: this.results.length,
        passed: this.results.filter(r => r.status === 'PASS').length,
        failed: this.results.filter(r => r.status === 'FAIL').length,
        partial: this.results.filter(r => r.status === 'PARTIAL').length,
        criticalIssues: this.bugList.length,
        overallSuccessRate: `${(((this.results.filter(r => r.status === 'PASS').length + this.results.filter(r => r.status === 'PARTIAL').length * 0.5) / this.results.length) * 100).toFixed(1)}%`,
        executionTime: `${executionTime}s`,
        timestamp: new Date().toISOString()
      },
      environment: CONFIG,
      testResults: this.results,
      criticalIssues: this.bugList,
      recommendations: this.generateRecommendations(),
      nextSteps: this.generateNextSteps()
    };
    
    try {
      fs.writeFileSync(filename, JSON.stringify(report, null, 2));
      console.log(`${colors.blue}📁 최종 결과 저장: ${filename}${colors.reset}`);
    } catch (error) {
      console.log(`${colors.yellow}결과 저장 실패: ${error.message}${colors.reset}`);
    }
  }

  // 권장사항 생성
  generateRecommendations() {
    const recommendations = [];
    
    // 크리티컬 이슈 기반 권장사항
    const criticalCategories = {};
    this.bugList.forEach(bug => {
      if (!criticalCategories[bug.category]) {
        criticalCategories[bug.category] = [];
      }
      criticalCategories[bug.category].push(bug);
    });
    
    Object.entries(criticalCategories).forEach(([category, bugs]) => {
      recommendations.push({
        category,
        priority: 'CRITICAL',
        issueCount: bugs.length,
        action: `${category} 관련 ${bugs.length}개 이슈 해결`,
        estimatedEffort: `${bugs.length * 2} 시간`,
        impact: 'CRITICAL',
        bugs: bugs.map(bug => ({ title: bug.title, fix: bug.fix }))
      });
    });
    
    return recommendations;
  }

  // 다음 단계 생성
  generateNextSteps() {
    const steps = [];
    
    if (this.bugList.some(bug => bug.category === 'Authentication')) {
      steps.push({
        step: 1,
        action: '인증 시스템 점검 및 수정',
        priority: 'IMMEDIATE',
        description: '로그인/회원가입 API 엔드포인트 확인 및 JWT 토큰 시스템 점검'
      });
    }
    
    if (this.bugList.some(bug => bug.category === 'Project Management')) {
      steps.push({
        step: 2,
        action: '프로젝트 관리 시스템 점검',
        priority: 'HIGH',
        description: '프로젝트 CRUD API 및 데이터베이스 스키마 확인'
      });
    }
    
    if (this.bugList.some(bug => bug.category === 'Frontend Pages')) {
      steps.push({
        step: 3,
        action: '프론트엔드 라우팅 수정',
        priority: 'HIGH',
        description: 'Next.js 라우터 설정 및 페이지 컴포넌트 생성'
      });
    }
    
    steps.push({
      step: steps.length + 1,
      action: '회귀 테스트 실행',
      priority: 'MEDIUM',
      description: '모든 수정 사항 완료 후 동일한 테스트를 재실행하여 이슈 해결 확인'
    });
    
    return steps;
  }
}

// 실행
const tester = new FinalIntegrationTest();
tester.runAllTests().catch(error => {
  console.error(`${colors.red}💥 치명적 오류 발생:${colors.reset}`, error);
  process.exit(1);
});