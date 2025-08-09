import fetch from 'node-fetch';

const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
  magenta: '\x1b[35m'
};

const API_URL = 'http://localhost:8001';
const FRONTEND_URL = 'http://localhost:3000';

// 테스트 결과 저장
const testResults = {
  passed: 0,
  failed: 0,
  total: 0
};

async function testWithResult(name, testFn) {
  testResults.total++;
  try {
    const result = await testFn();
    if (result) {
      console.log(`${colors.green}✅ ${name}${colors.reset}`);
      testResults.passed++;
      return true;
    } else {
      console.log(`${colors.red}❌ ${name}${colors.reset}`);
      testResults.failed++;
      return false;
    }
  } catch (error) {
    console.log(`${colors.red}❌ ${name}: ${error.message}${colors.reset}`);
    testResults.failed++;
    return false;
  }
}

async function runFinalTests() {
  console.log(`${colors.bright}${colors.blue}
╔════════════════════════════════════════════════╗
║        VideoPlanet 최종 통합 테스트           ║
╚════════════════════════════════════════════════╝${colors.reset}\n`);

  // 1. 백엔드 API 상태 확인
  console.log(`${colors.cyan}${colors.bright}1. 백엔드 API 상태 확인${colors.reset}`);
  
  await testWithResult('백엔드 헬스체크', async () => {
    const response = await fetch(`${API_URL}/api/health/`);
    return response.ok;
  });

  // 2. 프론트엔드 서버 상태 확인
  console.log(`\n${colors.cyan}${colors.bright}2. 프론트엔드 서버 상태${colors.reset}`);
  
  await testWithResult('프론트엔드 서버 응답', async () => {
    const response = await fetch(`${FRONTEND_URL}/`);
    return response.ok;
  });

  // 3. 로그인 테스트
  console.log(`\n${colors.cyan}${colors.bright}3. 사용자 인증 테스트${colors.reset}`);
  
  let authToken = null;
  const loginSuccess = await testWithResult('로그인 API', async () => {
    const response = await fetch(`${API_URL}/api/users/login/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: 'demo@test.com',
        password: 'demo1234'
      })
    });
    
    if (response.ok) {
      const data = await response.json();
      authToken = data.access;
      return !!authToken;
    }
    return false;
  });

  if (loginSuccess && authToken) {
    await testWithResult('사용자 정보 조회', async () => {
      const response = await fetch(`${API_URL}/api/users/me/`, {
        headers: { 'Authorization': `Bearer ${authToken}` }
      });
      return response.ok;
    });
  }

  // 4. 주요 페이지 접근성 테스트
  console.log(`\n${colors.cyan}${colors.bright}4. 페이지 접근성 테스트${colors.reset}`);
  
  const pages = [
    { name: '홈 페이지', url: '/' },
    { name: '로그인 페이지', url: '/login' },
    { name: '대시보드', url: '/cmshome' },
    { name: '프로젝트', url: '/projects' },
    { name: '영상 기획', url: '/videoplanning' },
    { name: '일정관리', url: '/schedule' },
    { name: '피드백', url: '/feedback' },
  ];

  for (const page of pages) {
    await testWithResult(page.name, async () => {
      const response = await fetch(`${FRONTEND_URL}${page.url}`, {
        redirect: 'manual'
      });
      // 200, 307(리다이렉트)는 정상으로 간주
      return response.status === 200 || response.status === 307 || response.status === 302;
    });
  }

  // 5. 프로젝트 API 테스트
  console.log(`\n${colors.cyan}${colors.bright}5. 프로젝트 API 테스트${colors.reset}`);
  
  if (authToken) {
    await testWithResult('프로젝트 목록 조회', async () => {
      const response = await fetch(`${API_URL}/api/projects/`, {
        headers: { 'Authorization': `Bearer ${authToken}` }
      });
      return response.ok;
    });

    await testWithResult('프로젝트 생성 API', async () => {
      const response = await fetch(`${API_URL}/api/projects/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          name: `테스트 프로젝트 ${Date.now()}`,
          description: '자동 테스트로 생성된 프로젝트',
          status: 'planning'
        })
      });
      return response.ok || response.status === 201;
    });
  }

  // 6. 피드백 API 테스트
  console.log(`\n${colors.cyan}${colors.bright}6. 피드백 API 테스트${colors.reset}`);
  
  if (authToken) {
    await testWithResult('피드백 목록 조회', async () => {
      const response = await fetch(`${API_URL}/api/feedbacks/`, {
        headers: { 'Authorization': `Bearer ${authToken}` }
      });
      return response.ok;
    });
  }

  // 최종 결과 출력
  console.log(`\n${colors.bright}${colors.magenta}
╔════════════════════════════════════════════════╗
║                 테스트 결과                    ║
╚════════════════════════════════════════════════╝${colors.reset}`);

  const successRate = Math.round((testResults.passed / testResults.total) * 100);
  const statusColor = successRate === 100 ? colors.green : successRate >= 80 ? colors.yellow : colors.red;
  
  console.log(`
  총 테스트: ${testResults.total}개
  ${colors.green}성공: ${testResults.passed}개${colors.reset}
  ${colors.red}실패: ${testResults.failed}개${colors.reset}
  
  ${statusColor}${colors.bright}성공률: ${successRate}%${colors.reset}
  `);

  if (successRate === 100) {
    console.log(`${colors.green}${colors.bright}🎉 모든 테스트 통과! VideoPlanet이 정상 작동 중입니다.${colors.reset}`);
  } else if (successRate >= 80) {
    console.log(`${colors.yellow}${colors.bright}⚠️ 일부 테스트 실패. 추가 디버깅이 필요합니다.${colors.reset}`);
  } else {
    console.log(`${colors.red}${colors.bright}❌ 많은 테스트가 실패했습니다. 시스템 점검이 필요합니다.${colors.reset}`);
  }
}

// 테스트 실행
runFinalTests().catch(console.error);