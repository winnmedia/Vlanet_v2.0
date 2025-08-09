import fetch from 'node-fetch';

// 색상 코드
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m'
};

const API_URL = 'http://localhost:8001';
const FRONTEND_URL = 'http://localhost:3000';

async function testLogin() {
  console.log(`${colors.cyan}${colors.bright}📝 로그인 API 테스트${colors.reset}`);
  
  try {
    const response = await fetch(`${API_URL}/api/users/login/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: 'demo@test.com',
        password: 'demo1234'
      })
    });

    const data = await response.json();

    if (response.ok) {
      console.log(`${colors.green}✅ 로그인 성공!${colors.reset}`);
      console.log(`  - Access Token: ${data.access ? '발급됨' : '없음'}`);
      console.log(`  - Refresh Token: ${data.refresh ? '발급됨' : '없음'}`);
      console.log(`  - User ID: ${data.user?.id || 'N/A'}`);
      console.log(`  - Email: ${data.user?.email || 'N/A'}`);
      return data.access;
    } else {
      console.log(`${colors.red}❌ 로그인 실패: ${data.message || response.statusText}${colors.reset}`);
      return null;
    }
  } catch (error) {
    console.log(`${colors.red}❌ 네트워크 오류: ${error.message}${colors.reset}`);
    return null;
  }
}

async function testProtectedRoute(token) {
  console.log(`\n${colors.cyan}${colors.bright}🔒 인증된 API 테스트${colors.reset}`);
  
  try {
    const response = await fetch(`${API_URL}/api/users/me/`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      }
    });

    if (response.ok) {
      const data = await response.json();
      console.log(`${colors.green}✅ 사용자 정보 조회 성공!${colors.reset}`);
      console.log(`  - ID: ${data.id}`);
      console.log(`  - Email: ${data.email}`);
      console.log(`  - Nickname: ${data.nickname}`);
      return true;
    } else {
      console.log(`${colors.red}❌ 사용자 정보 조회 실패: ${response.statusText}${colors.reset}`);
      return false;
    }
  } catch (error) {
    console.log(`${colors.red}❌ 네트워크 오류: ${error.message}${colors.reset}`);
    return false;
  }
}

async function testFrontendAccess() {
  console.log(`\n${colors.cyan}${colors.bright}🌐 프론트엔드 페이지 접근 테스트${colors.reset}`);
  
  const pages = [
    { url: '/', name: '홈' },
    { url: '/login', name: '로그인' },
    { url: '/cmshome', name: '대시보드' },
    { url: '/projects', name: '프로젝트' },
    { url: '/videoplanning', name: '영상 기획' },
    { url: '/schedule', name: '일정관리' },
    { url: '/feedback', name: '피드백' },
  ];

  for (const page of pages) {
    try {
      const response = await fetch(`${FRONTEND_URL}${page.url}`, {
        method: 'GET',
        redirect: 'manual'
      });

      if (response.status === 200) {
        console.log(`${colors.green}✅ ${page.name} 페이지: 접근 가능${colors.reset}`);
      } else if (response.status === 307 || response.status === 302) {
        console.log(`${colors.yellow}↩️  ${page.name} 페이지: 리다이렉트 (인증 필요)${colors.reset}`);
      } else {
        console.log(`${colors.red}❌ ${page.name} 페이지: 오류 (${response.status})${colors.reset}`);
      }
    } catch (error) {
      console.log(`${colors.red}❌ ${page.name} 페이지: 접근 실패 - ${error.message}${colors.reset}`);
    }
  }
}

async function runTests() {
  console.log(`${colors.bright}${colors.blue}
╔════════════════════════════════════════╗
║     VideoPlanet 인증 플로우 테스트     ║
╚════════════════════════════════════════╝${colors.reset}\n`);

  // 1. 로그인 테스트
  const token = await testLogin();
  
  if (token) {
    // 2. 인증된 API 테스트
    await testProtectedRoute(token);
  }
  
  // 3. 프론트엔드 페이지 접근 테스트
  await testFrontendAccess();

  console.log(`\n${colors.bright}${colors.blue}테스트 완료!${colors.reset}`);
}

runTests();