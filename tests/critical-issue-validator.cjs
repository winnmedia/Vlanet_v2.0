/**
 * VideoPlanet 크리티컬 이슈 자동 검증 스크립트
 * 즉시 실행 가능한 테스트 도구
 */

const axios = require('axios');
const chalk = require('chalk');

// 환경 설정
const CONFIG = {
  BASE_URL: process.env.BASE_URL || 'https://vlanet.net',
  API_URL: process.env.API_URL || 'https://videoplanet.up.railway.app/api',
  TEST_EMAIL: process.env.TEST_EMAIL || 'test@example.com',
  TEST_PASSWORD: process.env.TEST_PASSWORD || 'Test123!',
  TIMEOUT: 10000
};

// 색상 정의
const colors = {
  pass: chalk.green,
  fail: chalk.red,
  warn: chalk.yellow,
  info: chalk.blue,
  header: chalk.cyan.bold
};

class CriticalIssueValidator {
  constructor() {
    this.results = [];
    this.token = null;
    this.startTime = null;
    this.endTime = null;
  }

  // 로그인 테스트
  async testLogin() {
    const testName = '로그인 인증';
    console.log(colors.info(`\n🔐 ${testName} 테스트 시작...`));
    
    try {
      const response = await axios.post(
        `${CONFIG.API_URL}/auth/login/`,
        {
          email: CONFIG.TEST_EMAIL,
          password: CONFIG.TEST_PASSWORD
        },
        { timeout: CONFIG.TIMEOUT }
      );
      
      this.token = response.data.access;
      
      this.addResult({
        test: testName,
        status: 'PASS',
        message: '로그인 성공 - JWT 토큰 발급 완료',
        responseTime: response.headers['x-response-time'] || 'N/A'
      });
      
      console.log(colors.pass('✅ 로그인 성공'));
      return true;
    } catch (error) {
      this.addResult({
        test: testName,
        status: 'FAIL',
        message: `로그인 실패: ${error.message}`,
        priority: 'P0',
        error: error.response?.data || error.message
      });
      
      console.log(colors.fail('❌ 로그인 실패'));
      return false;
    }
  }

  // 영상 기획 메뉴 테스트
  async testVideoPlanning() {
    const testName = '영상 기획 메뉴';
    console.log(colors.info(`\n🎬 ${testName} 테스트 시작...`));
    
    try {
      const response = await axios.get(
        `${CONFIG.API_URL}/video-planning/`,
        {
          headers: { Authorization: `Bearer ${this.token}` },
          timeout: CONFIG.TIMEOUT
        }
      );
      
      this.addResult({
        test: testName,
        status: 'PASS',
        message: '영상 기획 API 접근 성공',
        dataCount: response.data.length || 0
      });
      
      console.log(colors.pass('✅ 영상 기획 메뉴 정상 작동'));
    } catch (error) {
      const statusCode = error.response?.status;
      const isNotFound = statusCode === 404;
      
      this.addResult({
        test: testName,
        status: 'FAIL',
        message: `${statusCode} Error - ${error.message}`,
        priority: 'P0',
        severity: 'BLOCKER',
        impact: '핵심 비즈니스 기능 완전 차단'
      });
      
      console.log(colors.fail(`❌ 영상 기획 메뉴 접근 실패 (${statusCode})`));
    }
  }

  // 프로젝트 생성 테스트
  async testProjectCreation() {
    const testName = '프로젝트 생성';
    console.log(colors.info(`\n📁 ${testName} 테스트 시작...`));
    
    const projectData = {
      title: `테스트 프로젝트 ${Date.now()}`,
      description: '자동화 테스트로 생성된 프로젝트',
      status: 'planning'
    };
    
    try {
      const response = await axios.post(
        `${CONFIG.API_URL}/projects/create/`,
        projectData,
        {
          headers: { Authorization: `Bearer ${this.token}` },
          timeout: CONFIG.TIMEOUT
        }
      );
      
      this.addResult({
        test: testName,
        status: 'PASS',
        message: '프로젝트 생성 성공',
        projectId: response.data.id
      });
      
      console.log(colors.pass('✅ 프로젝트 생성 성공'));
      
      // 생성된 프로젝트 정리 (선택사항)
      if (response.data.id) {
        await this.cleanupProject(response.data.id);
      }
    } catch (error) {
      const statusCode = error.response?.status;
      
      this.addResult({
        test: testName,
        status: 'FAIL',
        message: `${statusCode} Error - ${error.message}`,
        priority: 'P0',
        severity: 'BLOCKER',
        impact: '신규 프로젝트 생성 불가',
        requestData: projectData
      });
      
      console.log(colors.fail(`❌ 프로젝트 생성 실패 (${statusCode})`));
    }
  }

  // 일정관리 테스트
  async testCalendar() {
    const testName = '일정관리 (캘린더)';
    console.log(colors.info(`\n📅 ${testName} 테스트 시작...`));
    
    try {
      const response = await axios.get(
        `${CONFIG.API_URL}/calendar/events/`,
        {
          headers: { Authorization: `Bearer ${this.token}` },
          timeout: CONFIG.TIMEOUT
        }
      );
      
      this.addResult({
        test: testName,
        status: 'PASS',
        message: '캘린더 API 접근 성공',
        eventCount: response.data.length || 0
      });
      
      console.log(colors.pass('✅ 일정관리 정상 작동'));
    } catch (error) {
      const statusCode = error.response?.status;
      
      this.addResult({
        test: testName,
        status: 'FAIL',
        message: `${statusCode} Error - ${error.message}`,
        priority: 'P0',
        severity: 'CRITICAL',
        impact: '프로젝트 일정 관리 불가'
      });
      
      console.log(colors.fail(`❌ 일정관리 접근 실패 (${statusCode})`));
    }
  }

  // 피드백 시스템 테스트
  async testFeedback() {
    const testName = '피드백 시스템';
    console.log(colors.info(`\n💬 ${testName} 테스트 시작...`));
    
    try {
      const response = await axios.get(
        `${CONFIG.API_URL}/feedbacks/`,
        {
          headers: { Authorization: `Bearer ${this.token}` },
          timeout: CONFIG.TIMEOUT
        }
      );
      
      this.addResult({
        test: testName,
        status: 'PASS',
        message: '피드백 API 접근 성공',
        feedbackCount: response.data.length || 0
      });
      
      console.log(colors.pass('✅ 피드백 시스템 정상 작동'));
    } catch (error) {
      const statusCode = error.response?.status;
      
      this.addResult({
        test: testName,
        status: 'FAIL',
        message: `${statusCode} Error - ${error.message}`,
        priority: 'P0',
        severity: 'CRITICAL',
        impact: '팀 협업 및 커뮤니케이션 차단'
      });
      
      console.log(colors.fail(`❌ 피드백 시스템 접근 실패 (${statusCode})`));
    }
  }

  // 대시보드 테스트
  async testDashboard() {
    const testName = '대시보드';
    console.log(colors.info(`\n📊 ${testName} 테스트 시작...`));
    
    try {
      // 대시보드 데이터 가져오기 (여러 API 호출)
      const [projects, notifications, stats] = await Promise.all([
        axios.get(`${CONFIG.API_URL}/projects/`, {
          headers: { Authorization: `Bearer ${this.token}` },
          timeout: CONFIG.TIMEOUT
        }),
        axios.get(`${CONFIG.API_URL}/users/notifications/`, {
          headers: { Authorization: `Bearer ${this.token}` },
          timeout: CONFIG.TIMEOUT
        }),
        axios.get(`${CONFIG.API_URL}/users/stats/`, {
          headers: { Authorization: `Bearer ${this.token}` },
          timeout: CONFIG.TIMEOUT
        }).catch(() => ({ data: null })) // stats API가 없을 수 있음
      ]);
      
      this.addResult({
        test: testName,
        status: 'PASS',
        message: '대시보드 데이터 로드 성공',
        data: {
          projects: projects.data.length || 0,
          notifications: notifications.data.length || 0,
          stats: stats.data ? 'Available' : 'Not implemented'
        }
      });
      
      console.log(colors.pass('✅ 대시보드 정상 작동'));
    } catch (error) {
      this.addResult({
        test: testName,
        status: 'PARTIAL',
        message: '대시보드 일부 기능 미흡',
        priority: 'P1',
        severity: 'MAJOR',
        impact: '사용자 경험 저하'
      });
      
      console.log(colors.warn('⚠️  대시보드 기능 부분 작동'));
    }
  }

  // 마이페이지 테스트
  async testMyPage() {
    const testName = '마이페이지';
    console.log(colors.info(`\n👤 ${testName} 테스트 시작...`));
    
    try {
      const response = await axios.get(
        `${CONFIG.API_URL}/users/profile/`,
        {
          headers: { Authorization: `Bearer ${this.token}` },
          timeout: CONFIG.TIMEOUT
        }
      );
      
      this.addResult({
        test: testName,
        status: 'PASS',
        message: '프로필 API 접근 성공',
        profile: {
          email: response.data.email,
          username: response.data.username
        }
      });
      
      console.log(colors.pass('✅ 마이페이지 정상 작동'));
    } catch (error) {
      const statusCode = error.response?.status;
      
      this.addResult({
        test: testName,
        status: 'FAIL',
        message: `${statusCode} Error - 마이페이지 기능 부재`,
        priority: 'P1',
        severity: 'MAJOR',
        impact: '개인화 기능 사용 불가'
      });
      
      console.log(colors.fail(`❌ 마이페이지 접근 실패 (${statusCode})`));
    }
  }

  // 프로젝트 정리 (테스트 후 cleanup)
  async cleanupProject(projectId) {
    try {
      await axios.delete(
        `${CONFIG.API_URL}/projects/delete/${projectId}/`,
        {
          headers: { Authorization: `Bearer ${this.token}` },
          timeout: CONFIG.TIMEOUT
        }
      );
      console.log(colors.info('   테스트 프로젝트 정리 완료'));
    } catch (error) {
      // 정리 실패는 무시
    }
  }

  // 결과 추가
  addResult(result) {
    this.results.push({
      ...result,
      timestamp: new Date().toISOString()
    });
  }

  // 모든 테스트 실행
  async runAllTests() {
    console.log(colors.header('\n' + '='.repeat(60)));
    console.log(colors.header('VideoPlanet 크리티컬 이슈 검증 시작'));
    console.log(colors.header('='.repeat(60)));
    console.log(colors.info(`환경: ${CONFIG.BASE_URL}`));
    console.log(colors.info(`API: ${CONFIG.API_URL}`));
    console.log(colors.info(`시작 시간: ${new Date().toLocaleString('ko-KR')}`));
    
    this.startTime = Date.now();
    
    // 로그인 먼저 수행
    const loginSuccess = await this.testLogin();
    
    if (loginSuccess) {
      // 병렬로 테스트 실행 (더 빠른 실행)
      await Promise.all([
        this.testVideoPlanning(),
        this.testProjectCreation(),
        this.testCalendar(),
        this.testFeedback(),
        this.testDashboard(),
        this.testMyPage()
      ]);
    } else {
      console.log(colors.fail('\n❌ 로그인 실패로 테스트 중단'));
    }
    
    this.endTime = Date.now();
    this.generateReport();
  }

  // 리포트 생성
  generateReport() {
    console.log(colors.header('\n' + '='.repeat(60)));
    console.log(colors.header('테스트 결과 리포트'));
    console.log(colors.header('='.repeat(60)));
    
    let passCount = 0;
    let failCount = 0;
    let partialCount = 0;
    const criticalIssues = [];
    
    // 결과 분석
    this.results.forEach(result => {
      const icon = result.status === 'PASS' ? '✅' : 
                   result.status === 'PARTIAL' ? '⚠️ ' : '❌';
      const color = result.status === 'PASS' ? colors.pass :
                    result.status === 'PARTIAL' ? colors.warn : colors.fail;
      
      console.log(`\n${icon} ${color(result.test)}`);
      console.log(`   상태: ${result.status}`);
      console.log(`   메시지: ${result.message}`);
      
      if (result.priority) {
        console.log(`   우선순위: ${colors.fail(result.priority)}`);
        console.log(`   심각도: ${colors.fail(result.severity)}`);
        console.log(`   영향: ${result.impact}`);
        criticalIssues.push(result);
      }
      
      if (result.status === 'PASS') passCount++;
      else if (result.status === 'PARTIAL') partialCount++;
      else failCount++;
    });
    
    // 요약
    console.log(colors.header('\n' + '='.repeat(60)));
    console.log(colors.header('요약'));
    console.log(colors.header('='.repeat(60)));
    
    const totalTests = this.results.length;
    const successRate = ((passCount / totalTests) * 100).toFixed(1);
    const executionTime = ((this.endTime - this.startTime) / 1000).toFixed(2);
    
    console.log(`총 테스트: ${totalTests}`);
    console.log(`${colors.pass(`성공: ${passCount}`)}`);
    console.log(`${colors.warn(`부분 성공: ${partialCount}`)}`);
    console.log(`${colors.fail(`실패: ${failCount}`)}`);
    console.log(`성공률: ${successRate < 50 ? colors.fail(successRate + '%') : 
                          successRate < 80 ? colors.warn(successRate + '%') :
                          colors.pass(successRate + '%')}`);
    console.log(`실행 시간: ${executionTime}초`);
    
    // 크리티컬 이슈 요약
    if (criticalIssues.length > 0) {
      console.log(colors.header('\n' + '='.repeat(60)));
      console.log(colors.fail('⚠️  크리티컬 이슈 발견!'));
      console.log(colors.header('='.repeat(60)));
      
      console.log(colors.fail(`\n총 ${criticalIssues.length}개의 크리티컬 이슈:`));
      criticalIssues.forEach((issue, index) => {
        console.log(colors.fail(`${index + 1}. [${issue.priority}] ${issue.test}: ${issue.impact}`));
      });
      
      console.log(colors.fail('\n즉시 조치가 필요합니다!'));
    } else {
      console.log(colors.pass('\n✅ 모든 테스트 통과! 크리티컬 이슈 없음'));
    }
    
    // JSON 파일로 저장
    this.saveResults();
  }

  // 결과 저장
  saveResults() {
    const fs = require('fs');
    const filename = `test-results-${new Date().toISOString().split('T')[0]}-${Date.now()}.json`;
    
    const report = {
      summary: {
        totalTests: this.results.length,
        passed: this.results.filter(r => r.status === 'PASS').length,
        failed: this.results.filter(r => r.status === 'FAIL').length,
        partial: this.results.filter(r => r.status === 'PARTIAL').length,
        criticalIssues: this.results.filter(r => r.priority === 'P0').length,
        executionTime: `${((this.endTime - this.startTime) / 1000).toFixed(2)}s`,
        timestamp: new Date().toISOString()
      },
      environment: CONFIG,
      results: this.results
    };
    
    fs.writeFileSync(filename, JSON.stringify(report, null, 2));
    console.log(colors.info(`\n📁 결과 저장: ${filename}`));
  }
}

// 실행
if (require.main === module) {
  const validator = new CriticalIssueValidator();
  validator.runAllTests().catch(error => {
    console.error(colors.fail('\n치명적 오류 발생:'), error);
    process.exit(1);
  });
}

module.exports = CriticalIssueValidator;