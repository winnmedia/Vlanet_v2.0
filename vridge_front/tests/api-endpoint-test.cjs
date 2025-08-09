/**
 * API 엔드포인트 직접 테스트 스크립트
 * 인증 없이 기본 API 상태 확인
 */

const axios = require('axios');
const fs = require('fs');

const CONFIG = {
  BASE_URL: 'https://vlanet.net',
  API_URL: 'https://videoplanet.up.railway.app',
  TIMEOUT: 10000
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

class APIEndpointTester {
  constructor() {
    this.results = [];
    this.bugList = [];
    this.startTime = Date.now();
  }

  async makeRequest(method, url, data = null, headers = {}) {
    const config = {
      method,
      url,
      timeout: CONFIG.TIMEOUT,
      validateStatus: () => true, // 모든 status code 허용
      headers: {
        'Content-Type': 'application/json',
        'User-Agent': 'VideoPlanet-Test/1.0',
        ...headers
      }
    };

    if (data) config.data = data;

    try {
      const startTime = Date.now();
      const response = await axios(config);
      const responseTime = Date.now() - startTime;
      
      return {
        ...response,
        responseTime
      };
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
    
    if (status === 'FAIL') {
      this.bugList.push({
        id: `BUG_${this.bugList.length + 1}`,
        category: details.category || 'API',
        severity: details.severity || 'MEDIUM',
        title: test,
        description: message,
        status: 'OPEN',
        priority: details.priority || 'P2',
        impact: details.impact || 'API 기능 제한',
        endpoint: details.endpoint,
        httpStatus: details.httpStatus,
        timestamp: new Date().toISOString()
      });
    }
    
    return result;
  }

  // 1. 백엔드 서버 기본 상태 확인
  async testServerStatus() {
    log.info('🌐 백엔드 서버 상태 확인...');
    
    try {
      const response = await this.makeRequest('GET', CONFIG.API_URL);
      
      if (response.status === 200) {
        this.addResult('백엔드 서버 상태', 'PASS', `서버 응답 정상 (${response.responseTime}ms)`, {
          category: 'Infrastructure',
          httpStatus: response.status,
          responseTime: response.responseTime
        });
        log.success(`백엔드 서버 정상 작동 (${response.responseTime}ms)`);
        return true;
      } else if (response.status === 0) {
        throw new Error(`연결 실패: ${response.error}`);
      } else {
        this.addResult('백엔드 서버 상태', 'PARTIAL', `비정상 응답: HTTP ${response.status}`, {
          category: 'Infrastructure',
          httpStatus: response.status,
          responseTime: response.responseTime
        });
        log.warning(`백엔드 서버 비정상 응답: ${response.status}`);
        return true; // 서버는 살아있음
      }
    } catch (error) {
      this.addResult('백엔드 서버 상태', 'FAIL', `서버 연결 실패: ${error.message}`, {
        category: 'Infrastructure',
        severity: 'CRITICAL',
        priority: 'P0',
        impact: '전체 시스템 접근 불가'
      });
      log.error(`백엔드 서버 연결 실패: ${error.message}`);
      return false;
    }
  }

  // 2. API 엔드포인트 존재 여부 확인
  async testAPIEndpoints() {
    log.info('🔍 API 엔드포인트 존재 여부 확인...');
    
    const endpoints = [
      { path: '/api/', name: 'API 루트', critical: true },
      { path: '/api/auth/', name: '인증 API', critical: true },
      { path: '/api/auth/login/', name: '로그인 API', critical: true },
      { path: '/api/auth/register/', name: '회원가입 API', critical: true },
      { path: '/api/projects/', name: '프로젝트 API', critical: true },
      { path: '/api/video-planning/', name: '영상 기획 API', critical: true },
      { path: '/api/calendar/', name: '캘린더 API', critical: false },
      { path: '/api/calendar/events/', name: '캘린더 이벤트 API', critical: false },
      { path: '/api/feedbacks/', name: '피드백 API', critical: false },
      { path: '/api/users/profile/', name: '사용자 프로필 API', critical: false }
    ];
    
    const results = [];
    
    for (const endpoint of endpoints) {
      try {
        const response = await this.makeRequest('GET', `${CONFIG.API_URL}${endpoint.path}`);
        
        let status = 'UNKNOWN';
        let message = '';
        
        if (response.status === 200) {
          status = 'PASS';
          message = 'API 엔드포인트 존재하며 정상 응답';
        } else if (response.status === 401 || response.status === 403) {
          status = 'PASS';
          message = 'API 엔드포인트 존재 (인증 필요)';
        } else if (response.status === 405) {
          status = 'PASS';
          message = 'API 엔드포인트 존재 (Method Not Allowed)';
        } else if (response.status === 404) {
          status = 'FAIL';
          message = 'API 엔드포인트 존재하지 않음';
        } else if (response.status === 500) {
          status = 'FAIL';
          message = 'API 엔드포인트 서버 에러';
        } else if (response.status === 0) {
          status = 'FAIL';
          message = `연결 실패: ${response.error}`;
        } else {
          status = 'PARTIAL';
          message = `예상치 못한 응답: HTTP ${response.status}`;
        }
        
        this.addResult(endpoint.name, status, message, {
          category: 'API Endpoints',
          httpStatus: response.status,
          responseTime: response.responseTime,
          endpoint: endpoint.path,
          critical: endpoint.critical,
          severity: endpoint.critical && status === 'FAIL' ? 'CRITICAL' : 'MEDIUM',
          priority: endpoint.critical && status === 'FAIL' ? 'P0' : 'P1',
          impact: endpoint.critical && status === 'FAIL' ? '핵심 기능 차단' : '기능 제한'
        });
        
        results.push({ endpoint: endpoint.name, status, httpStatus: response.status });
        
        const icon = status === 'PASS' ? '✅' : status === 'PARTIAL' ? '⚠️' : '❌';
        console.log(`${icon} ${endpoint.name}: ${message} (HTTP ${response.status}, ${response.responseTime}ms)`);
        
      } catch (error) {
        this.addResult(endpoint.name, 'FAIL', `테스트 실패: ${error.message}`, {
          category: 'API Endpoints',
          endpoint: endpoint.path,
          severity: 'MAJOR',
          priority: 'P1',
          impact: 'API 테스트 불가'
        });
        
        results.push({ endpoint: endpoint.name, status: 'FAIL', error: error.message });
        log.error(`${endpoint.name}: 테스트 실패 - ${error.message}`);
      }
    }
    
    return results;
  }

  // 3. 프론트엔드 페이지 접근성 테스트
  async testFrontendPages() {
    log.info('🌐 프론트엔드 페이지 접근성 테스트...');
    
    const pages = [
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
    
    for (const page of pages) {
      try {
        const response = await this.makeRequest('GET', `${CONFIG.BASE_URL}${page.path}`, null, {
          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        });
        
        let status = 'UNKNOWN';
        let message = '';
        
        if (response.status === 200) {
          status = 'PASS';
          message = '페이지 정상 로드';
        } else if (response.status === 401 || response.status === 403) {
          status = 'PASS';
          message = '페이지 존재 (인증 필요)';
        } else if (response.status === 404) {
          status = 'FAIL';
          message = '페이지 존재하지 않음 (404 에러)';
        } else if (response.status === 500) {
          status = 'FAIL';
          message = '서버 에러 (500 에러)';
        } else if (response.status === 0) {
          status = 'FAIL';
          message = `연결 실패: ${response.error}`;
        } else {
          status = 'PARTIAL';
          message = `비정상 응답: HTTP ${response.status}`;
        }
        
        this.addResult(page.name, status, message, {
          category: 'Frontend Pages',
          httpStatus: response.status,
          responseTime: response.responseTime,
          endpoint: page.path,
          critical: page.critical,
          severity: page.critical && status === 'FAIL' ? 'CRITICAL' : 'MEDIUM',
          priority: page.critical && status === 'FAIL' ? 'P0' : 'P1',
          impact: page.critical && status === 'FAIL' ? '핵심 페이지 접근 불가' : '기능 페이지 접근 제한'
        });
        
        const icon = status === 'PASS' ? '✅' : status === 'PARTIAL' ? '⚠️' : '❌';
        console.log(`${icon} ${page.name}: ${message} (HTTP ${response.status}, ${response.responseTime}ms)`);
        
      } catch (error) {
        this.addResult(page.name, 'FAIL', `페이지 테스트 실패: ${error.message}`, {
          category: 'Frontend Pages',
          endpoint: page.path,
          severity: 'MAJOR',
          priority: 'P1',
          impact: '페이지 접근 불가'
        });
        
        log.error(`${page.name}: 테스트 실패 - ${error.message}`);
      }
    }
  }

  // 모든 테스트 실행
  async runAllTests() {
    log.header('================================================================================');
    log.header('VideoPlanet API 엔드포인트 직접 테스트');
    log.header('================================================================================');
    console.log(`프론트엔드: ${CONFIG.BASE_URL}`);
    console.log(`백엔드 API: ${CONFIG.API_URL}`);
    console.log(`시작 시간: ${new Date().toLocaleString('ko-KR')}`);
    console.log('');
    
    // 1. 서버 상태 확인
    const serverAlive = await this.testServerStatus();
    console.log('');
    
    // 2. API 엔드포인트 테스트
    if (serverAlive) {
      await this.testAPIEndpoints();
      console.log('');
    }
    
    // 3. 프론트엔드 페이지 테스트
    await this.testFrontendPages();
    
    // 결과 분석
    this.generateReport();
  }

  // 리포트 생성
  generateReport() {
    const endTime = Date.now();
    const executionTime = ((endTime - this.startTime) / 1000).toFixed(2);
    
    log.header('================================================================================');
    log.header('테스트 결과 종합 분석');
    log.header('================================================================================');
    
    // 카테고리별 분석
    const categories = {};
    let totalTests = 0;
    let passedTests = 0;
    let failedTests = 0;
    let partialTests = 0;
    
    this.results.forEach(result => {
      const category = result.category || 'Unknown';
      if (!categories[category]) {
        categories[category] = { pass: 0, fail: 0, partial: 0, total: 0 };
      }
      
      categories[category].total++;
      totalTests++;
      
      if (result.status === 'PASS') {
        categories[category].pass++;
        passedTests++;
      } else if (result.status === 'PARTIAL') {
        categories[category].partial++;
        partialTests++;
      } else {
        categories[category].fail++;
        failedTests++;
      }
    });
    
    // 카테고리별 결과 출력
    console.log(`${colors.cyan}${colors.bold}📊 카테고리별 결과:${colors.reset}`);
    Object.entries(categories).forEach(([category, stats]) => {
      const successRate = (stats.pass / stats.total) * 100;
      const statusColor = successRate >= 80 ? colors.green : 
                         successRate >= 60 ? colors.yellow : colors.red;
      
      console.log(`${statusColor}${category}: ${stats.pass}/${stats.total} 성공 (${successRate.toFixed(1)}%)${colors.reset}`);
      if (stats.fail > 0) {
        console.log(`  ${colors.red}실패: ${stats.fail}개${colors.reset}`);
      }
      if (stats.partial > 0) {
        console.log(`  ${colors.yellow}부분 성공: ${stats.partial}개${colors.reset}`);
      }
    });
    
    console.log('');
    
    // 전체 통계
    const overallSuccessRate = ((passedTests + partialTests * 0.5) / totalTests) * 100;
    
    console.log(`${colors.cyan}${colors.bold}📈 전체 통계:${colors.reset}`);
    console.log(`총 테스트: ${totalTests}`);
    console.log(`${colors.green}성공: ${passedTests}${colors.reset}`);
    console.log(`${colors.yellow}부분 성공: ${partialTests}${colors.reset}`);
    console.log(`${colors.red}실패: ${failedTests}${colors.reset}`);
    console.log(`전체 성공률: ${overallSuccessRate >= 70 ? colors.green : overallSuccessRate >= 50 ? colors.yellow : colors.red}${overallSuccessRate.toFixed(1)}%${colors.reset}`);
    console.log(`실행 시간: ${executionTime}초`);
    
    // 크리티컬 이슈
    const criticalBugs = this.bugList.filter(bug => bug.severity === 'CRITICAL');
    if (criticalBugs.length > 0) {
      console.log(`\n${colors.red}${colors.bold}🚨 크리티컬 이슈: ${criticalBugs.length}개${colors.reset}`);
      criticalBugs.forEach((bug, index) => {
        console.log(`${colors.red}${index + 1}. [${bug.priority}] ${bug.title}${colors.reset}`);
        console.log(`   ${bug.description}`);
        if (bug.endpoint) {
          console.log(`   엔드포인트: ${bug.endpoint}`);
        }
      });
    }
    
    // 결과 저장
    this.saveResults(executionTime);
    
    // 최종 상태
    console.log('');
    if (overallSuccessRate >= 80) {
      log.success('시스템 상태 양호');
    } else if (overallSuccessRate >= 60) {
      log.warning('시스템 일부 개선 필요');
    } else {
      log.error('시스템 심각한 문제 발견 - 즉시 조치 필요');
    }
  }

  // 결과 저장
  saveResults(executionTime) {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = `api-test-results-${timestamp}.json`;
    
    const report = {
      summary: {
        totalTests: this.results.length,
        passed: this.results.filter(r => r.status === 'PASS').length,
        failed: this.results.filter(r => r.status === 'FAIL').length,
        partial: this.results.filter(r => r.status === 'PARTIAL').length,
        criticalBugs: this.bugList.filter(b => b.severity === 'CRITICAL').length,
        executionTime: `${executionTime}s`,
        timestamp: new Date().toISOString()
      },
      environment: CONFIG,
      results: this.results,
      bugList: this.bugList,
      recommendations: this.generateRecommendations()
    };
    
    try {
      fs.writeFileSync(filename, JSON.stringify(report, null, 2));
      console.log(`\n${colors.blue}📁 상세 결과 저장: ${filename}${colors.reset}`);
    } catch (error) {
      console.log(`${colors.yellow}결과 저장 실패: ${error.message}${colors.reset}`);
    }
  }

  // 권장사항 생성
  generateRecommendations() {
    const recommendations = [];
    
    // API 엔드포인트 관련
    const apiFailures = this.bugList.filter(bug => 
      bug.category === 'API Endpoints' && bug.httpStatus === 404
    );
    
    if (apiFailures.length > 0) {
      recommendations.push({
        category: 'Backend Development',
        priority: 'CRITICAL',
        action: '누락된 API 엔드포인트 구현',
        details: apiFailures.map(bug => bug.endpoint),
        estimatedEffort: `${apiFailures.length * 2}시간`,
        impact: '핵심 기능 복원'
      });
    }
    
    // 프론트엔드 페이지 관련
    const pageFailures = this.bugList.filter(bug => 
      bug.category === 'Frontend Pages' && bug.httpStatus === 404
    );
    
    if (pageFailures.length > 0) {
      recommendations.push({
        category: 'Frontend Development',
        priority: 'HIGH',
        action: '누락된 페이지 라우팅 구현',
        details: pageFailures.map(bug => bug.endpoint),
        estimatedEffort: `${pageFailures.length}시간`,
        impact: '사용자 경험 개선'
      });
    }
    
    return recommendations;
  }
}

// 실행
const tester = new APIEndpointTester();
tester.runAllTests().catch(error => {
  console.error(`${colors.red}💥 치명적 오류 발생:${colors.reset}`, error);
  process.exit(1);
});