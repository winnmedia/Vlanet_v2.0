#!/usr/bin/env node

/**
 * VideoPlanet 사용자 여정 통합 테스트
 * - 회원가입 → 로그인 → 프로젝트 생성 → 피드백 테스트
 */

const API_URL = process.env.API_URL || 'http://localhost:8000';
const FRONTEND_URL = process.env.FRONTEND_URL || 'http://localhost:3000';

// 색상 코드
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m'
};

// 테스트 유틸리티
function log(message, type = 'info') {
  const prefix = {
    'info': `${colors.blue}ℹ${colors.reset}`,
    'success': `${colors.green}✓${colors.reset}`,
    'error': `${colors.red}✗${colors.reset}`,
    'warning': `${colors.yellow}⚠${colors.reset}`,
    'test': `${colors.cyan}🧪${colors.reset}`
  };
  console.log(`${prefix[type] || prefix.info} ${message}`);
}

function generateTestUser() {
  const timestamp = Date.now();
  return {
    email: `test${timestamp}@videoplanet.com`,
    password: 'Test1234!@',
    name: `테스트유저${timestamp}`,
    company: 'VideoPlanet Test',
    phone: '010-1234-5678'
  };
}

async function makeRequest(endpoint, options = {}) {
  const url = `${API_URL}${endpoint}`;
  const defaultHeaders = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  };

  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        ...defaultHeaders,
        ...options.headers
      }
    });

    const data = await response.text();
    let jsonData;
    
    try {
      jsonData = JSON.parse(data);
    } catch {
      jsonData = data;
    }

    return {
      ok: response.ok,
      status: response.status,
      data: jsonData,
      headers: response.headers
    };
  } catch (error) {
    return {
      ok: false,
      status: 0,
      error: error.message
    };
  }
}

// 테스트 시나리오
async function testHealthCheck() {
  log('서버 상태 확인 중...', 'test');
  
  const response = await makeRequest('/api/health/', {
    method: 'GET'
  });

  if (response.ok) {
    log('✅ 서버가 정상적으로 응답합니다', 'success');
    return true;
  } else {
    log(`❌ 서버 응답 실패: ${response.status} - ${JSON.stringify(response.data)}`, 'error');
    return false;
  }
}

async function testUserRegistration(userData) {
  log('회원가입 테스트 시작...', 'test');
  
  const response = await makeRequest('/api/users/register/', {
    method: 'POST',
    body: JSON.stringify({
      username: userData.email,
      email: userData.email,
      password: userData.password,
      nickname: userData.name,
      company: userData.company,
      phone_number: userData.phone
    })
  });

  if (response.ok) {
    log(`✅ 회원가입 성공: ${userData.email}`, 'success');
    return response.data;
  } else {
    log(`❌ 회원가입 실패: ${response.status} - ${JSON.stringify(response.data)}`, 'error');
    return null;
  }
}

async function testUserLogin(userData) {
  log('로그인 테스트 시작...', 'test');
  
  const response = await makeRequest('/api/users/login/', {
    method: 'POST',
    body: JSON.stringify({
      username: userData.email,
      password: userData.password
    })
  });

  if (response.ok && response.data.access) {
    log('✅ 로그인 성공, JWT 토큰 획득', 'success');
    return {
      access: response.data.access,
      refresh: response.data.refresh,
      user: response.data.user
    };
  } else {
    log(`❌ 로그인 실패: ${response.status} - ${JSON.stringify(response.data)}`, 'error');
    return null;
  }
}

async function testProjectCreation(authToken) {
  log('프로젝트 생성 테스트 시작...', 'test');
  
  const projectData = {
    name: `테스트 프로젝트 ${Date.now()}`,
    description: '자동 테스트로 생성된 프로젝트입니다',
    start_date: new Date().toISOString().split('T')[0],
    end_date: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    status: 'planning'
  };

  const response = await makeRequest('/api/projects/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${authToken}`
    },
    body: JSON.stringify(projectData)
  });

  if (response.ok) {
    log(`✅ 프로젝트 생성 성공: ${response.data.name}`, 'success');
    return response.data;
  } else {
    log(`❌ 프로젝트 생성 실패: ${response.status} - ${JSON.stringify(response.data)}`, 'error');
    return null;
  }
}

async function testProjectList(authToken) {
  log('프로젝트 목록 조회 테스트...', 'test');
  
  const response = await makeRequest('/api/projects/', {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${authToken}`
    }
  });

  if (response.ok) {
    const count = Array.isArray(response.data) ? response.data.length : 
                  response.data.results ? response.data.results.length : 0;
    log(`✅ 프로젝트 목록 조회 성공: ${count}개 프로젝트`, 'success');
    return response.data;
  } else {
    log(`❌ 프로젝트 목록 조회 실패: ${response.status}`, 'error');
    return null;
  }
}

async function testFeedbackCreation(authToken, projectId) {
  log('피드백 생성 테스트 시작...', 'test');
  
  const feedbackData = {
    project: projectId,
    content: '테스트 피드백입니다. 영상 품질이 매우 좋습니다!',
    timestamp: '00:01:30',
    type: 'comment'
  };

  const response = await makeRequest('/api/feedbacks/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${authToken}`
    },
    body: JSON.stringify(feedbackData)
  });

  if (response.ok) {
    log('✅ 피드백 생성 성공', 'success');
    return response.data;
  } else {
    log(`❌ 피드백 생성 실패: ${response.status} - ${JSON.stringify(response.data)}`, 'error');
    return null;
  }
}

// 메인 테스트 실행
async function runFullUserJourney() {
  console.log('\n' + '='.repeat(60));
  console.log(`${colors.bright}📊 VideoPlanet 사용자 여정 통합 테스트${colors.reset}`);
  console.log('='.repeat(60) + '\n');

  log(`API URL: ${API_URL}`, 'info');
  log(`Frontend URL: ${FRONTEND_URL}`, 'info');
  console.log();

  const results = {
    total: 0,
    passed: 0,
    failed: 0,
    skipped: 0
  };

  // 1. 서버 상태 확인
  results.total++;
  const serverHealthy = await testHealthCheck();
  if (serverHealthy) {
    results.passed++;
  } else {
    results.failed++;
    log('서버가 응답하지 않아 테스트를 중단합니다', 'error');
    return results;
  }
  console.log();

  // 2. 회원가입 테스트
  const testUser = generateTestUser();
  results.total++;
  const registrationResult = await testUserRegistration(testUser);
  if (registrationResult) {
    results.passed++;
  } else {
    results.failed++;
  }
  console.log();

  // 3. 로그인 테스트
  results.total++;
  const loginResult = await testUserLogin(testUser);
  if (loginResult) {
    results.passed++;
  } else {
    results.failed++;
    log('로그인 실패로 이후 테스트를 건너뜁니다', 'warning');
    results.skipped += 3;
    return results;
  }
  console.log();

  // 4. 프로젝트 생성 테스트
  results.total++;
  const project = await testProjectCreation(loginResult.access);
  if (project) {
    results.passed++;
  } else {
    results.failed++;
  }
  console.log();

  // 5. 프로젝트 목록 조회 테스트
  results.total++;
  const projectList = await testProjectList(loginResult.access);
  if (projectList) {
    results.passed++;
  } else {
    results.failed++;
  }
  console.log();

  // 6. 피드백 생성 테스트
  if (project) {
    results.total++;
    const feedback = await testFeedbackCreation(loginResult.access, project.id);
    if (feedback) {
      results.passed++;
    } else {
      results.failed++;
    }
  } else {
    results.skipped++;
    log('프로젝트가 없어 피드백 테스트를 건너뜁니다', 'warning');
  }

  // 테스트 결과 요약
  console.log('\n' + '='.repeat(60));
  console.log(`${colors.bright}📈 테스트 결과 요약${colors.reset}`);
  console.log('='.repeat(60));
  
  const successRate = results.total > 0 ? 
    Math.round((results.passed / results.total) * 100) : 0;
  
  console.log(`${colors.green}✅ 성공: ${results.passed}${colors.reset}`);
  console.log(`${colors.red}❌ 실패: ${results.failed}${colors.reset}`);
  console.log(`${colors.yellow}⏭️  건너뜀: ${results.skipped}${colors.reset}`);
  console.log(`${colors.blue}📊 전체: ${results.total}${colors.reset}`);
  console.log(`${colors.cyan}📈 성공률: ${successRate}%${colors.reset}`);
  
  if (successRate === 100) {
    console.log(`\n${colors.green}${colors.bright}🎉 모든 테스트가 성공적으로 통과했습니다!${colors.reset}`);
  } else if (successRate >= 80) {
    console.log(`\n${colors.yellow}⚠️  일부 테스트가 실패했지만 대부분 통과했습니다.${colors.reset}`);
  } else {
    console.log(`\n${colors.red}❌ 테스트 실패율이 높습니다. 시스템 점검이 필요합니다.${colors.reset}`);
  }

  return results;
}

// 테스트 실행
runFullUserJourney()
  .then(results => {
    process.exit(results.failed > 0 ? 1 : 0);
  })
  .catch(error => {
    log(`테스트 실행 중 오류 발생: ${error.message}`, 'error');
    process.exit(1);
  });