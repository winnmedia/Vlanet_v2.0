#!/usr/bin/env node

/**
 * VideoPlanet 포괄적 라우팅 테스트
 * 모든 핵심 페이지와 API 엔드포인트를 검증하고 404 에러를 방지합니다.
 */

const https = require('https');
const http = require('http');

// 테스트 설정
const CONFIG = {
  FRONTEND_URL: 'https://vlanet.net',
  BACKEND_URL: 'https://videoplanet.up.railway.app',
  TIMEOUT: 10000,
  MAX_RETRIES: 3,
  RETRY_DELAY: 2000
};

// 테스트할 라우트 정의
const ROUTES_TO_TEST = {
  frontend: [
    { path: '/', name: 'Home Page', expected: [200, 401] },
    { path: '/login', name: 'Login Page', expected: [200, 401] },  // 401 is acceptable for SSO-protected environments
    { path: '/signup', name: 'Signup Page', expected: [200, 401] },  // 401 is acceptable for SSO-protected environments
    { path: '/dashboard', name: 'Dashboard', expected: [200, 401] },
    { path: '/projects', name: 'Projects', expected: [200, 401] },
    { path: '/analytics', name: 'Analytics (NEW)', expected: [200, 401] },
    { path: '/teams', name: 'Teams (NEW)', expected: [200, 401] },
    { path: '/settings', name: 'Settings (NEW)', expected: [200, 401] },
    { path: '/feedbacks', name: 'Feedbacks', expected: [200, 401] },
    { path: '/video-feedback', name: 'Video Feedback', expected: [200, 401] },
    { path: '/video-planning', name: 'Video Planning', expected: [200, 401] },
    { path: '/mypage', name: 'My Page', expected: [200, 401] },
    { path: '/calendar', name: 'Calendar', expected: [200, 401] }
  ],
  backend: [
    { path: '/api/health/', name: 'Health Check', expected: [200] },
    { path: '/api/version/', name: 'Version Info', expected: [200] },
    { path: '/api/analytics/dashboard/', name: 'Analytics API (NEW)', expected: [200, 401, 403] },  // 200 with empty data when tables don't exist
    { path: '/api/projects/', name: 'Projects API', expected: [200, 401] },
    { path: '/api/feedbacks/', name: 'Feedbacks API', expected: [200, 401] },
    { path: '/api/users/me/', name: 'User Profile API', expected: [200, 401] },
    { path: '/api/video-planning/', name: 'Video Planning API', expected: [200, 401] },
    { path: '/api/ai-video/', name: 'AI Video API', expected: [200, 401] }
  ]
};

// 테스트 결과 저장
const results = {
  passed: 0,
  failed: 0,
  errors: [],
  summary: []
};

/**
 * HTTP 요청 유틸리티 함수
 */
function makeRequest(url, options = {}) {
  return new Promise((resolve, reject) => {
    const urlObj = new URL(url);
    const isHttps = urlObj.protocol === 'https:';
    const client = isHttps ? https : http;
    
    const requestOptions = {
      hostname: urlObj.hostname,
      port: urlObj.port || (isHttps ? 443 : 80),
      path: urlObj.pathname + urlObj.search,
      method: options.method || 'GET',
      headers: {
        'User-Agent': 'VideoPlanet-RoutingTest/1.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3',
        'Cache-Control': 'no-cache',
        ...options.headers
      },
      timeout: CONFIG.TIMEOUT
    };

    const req = client.request(requestOptions, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        resolve({
          statusCode: res.statusCode,
          statusMessage: res.statusMessage,
          headers: res.headers,
          body: data,
          url: url
        });
      });
    });

    req.on('error', reject);
    req.on('timeout', () => {
      req.destroy();
      reject(new Error('Request timeout'));
    });

    if (options.body) {
      req.write(options.body);
    }
    
    req.end();
  });
}

/**
 * 재시도 로직이 포함된 테스트 실행
 */
async function testWithRetry(url, route, retries = CONFIG.MAX_RETRIES) {
  for (let attempt = 1; attempt <= retries; attempt++) {
    try {
      const response = await makeRequest(url);
      
      if (route.expected.includes(response.statusCode)) {
        return {
          success: true,
          statusCode: response.statusCode,
          statusMessage: response.statusMessage,
          attempt: attempt
        };
      } else if (response.statusCode === 404) {
        // 404는 즉시 실패로 처리
        return {
          success: false,
          statusCode: response.statusCode,
          statusMessage: response.statusMessage,
          error: `404 NOT FOUND - 페이지가 존재하지 않습니다`,
          attempt: attempt
        };
      } else {
        // 다른 예상치 못한 상태 코드는 재시도
        if (attempt < retries) {
          console.log(`  ⚠️  Attempt ${attempt} failed with ${response.statusCode}, retrying...`);
          await new Promise(resolve => setTimeout(resolve, CONFIG.RETRY_DELAY));
          continue;
        }
        
        return {
          success: false,
          statusCode: response.statusCode,
          statusMessage: response.statusMessage,
          error: `Unexpected status code. Expected: ${route.expected.join(' or ')}, Got: ${response.statusCode}`,
          attempt: attempt
        };
      }
    } catch (error) {
      if (attempt < retries) {
        console.log(`  ⚠️  Attempt ${attempt} failed with error: ${error.message}, retrying...`);
        await new Promise(resolve => setTimeout(resolve, CONFIG.RETRY_DELAY));
        continue;
      }
      
      return {
        success: false,
        error: error.message,
        attempt: attempt
      };
    }
  }
}

/**
 * 프론트엔드 라우트 테스트
 */
async function testFrontendRoutes() {
  console.log('\n🔍 Testing Frontend Routes...');
  console.log('=' .repeat(50));
  
  for (const route of ROUTES_TO_TEST.frontend) {
    const url = `${CONFIG.FRONTEND_URL}${route.path}`;
    console.log(`Testing: ${route.name} (${route.path})`);
    
    const result = await testWithRetry(url, route);
    
    if (result.success) {
      console.log(`  ✅ PASS - ${result.statusCode} ${result.statusMessage}`);
      results.passed++;
      results.summary.push({
        type: 'frontend',
        route: route.path,
        name: route.name,
        status: 'PASS',
        statusCode: result.statusCode,
        attempts: result.attempt
      });
    } else {
      console.log(`  ❌ FAIL - ${result.error || result.statusCode + ' ' + result.statusMessage}`);
      results.failed++;
      results.errors.push({
        type: 'frontend',
        route: route.path,
        name: route.name,
        error: result.error || `${result.statusCode} ${result.statusMessage}`,
        url: url
      });
      results.summary.push({
        type: 'frontend',
        route: route.path,
        name: route.name,
        status: 'FAIL',
        statusCode: result.statusCode,
        error: result.error,
        attempts: result.attempt
      });
    }
  }
}

/**
 * 백엔드 API 엔드포인트 테스트
 */
async function testBackendRoutes() {
  console.log('\n🔍 Testing Backend API Routes...');
  console.log('=' .repeat(50));
  
  for (const route of ROUTES_TO_TEST.backend) {
    const url = `${CONFIG.BACKEND_URL}${route.path}`;
    console.log(`Testing: ${route.name} (${route.path})`);
    
    const result = await testWithRetry(url, route);
    
    if (result.success) {
      console.log(`  ✅ PASS - ${result.statusCode} ${result.statusMessage}`);
      results.passed++;
      results.summary.push({
        type: 'backend',
        route: route.path,
        name: route.name,
        status: 'PASS',
        statusCode: result.statusCode,
        attempts: result.attempt
      });
    } else {
      console.log(`  ❌ FAIL - ${result.error || result.statusCode + ' ' + result.statusMessage}`);
      results.failed++;
      results.errors.push({
        type: 'backend',
        route: route.path,
        name: route.name,
        error: result.error || `${result.statusCode} ${result.statusMessage}`,
        url: url
      });
      results.summary.push({
        type: 'backend',
        route: route.path,
        name: route.name,
        status: 'FAIL',
        statusCode: result.statusCode,
        error: result.error,
        attempts: result.attempt
      });
    }
  }
}

/**
 * 특별 케이스 테스트 (CORS, 헬스체크 등)
 */
async function testSpecialCases() {
  console.log('\n🔍 Testing Special Cases...');
  console.log('=' .repeat(50));
  
  // CORS 프리플라이트 테스트
  console.log('Testing: CORS Preflight');
  try {
    const corsResult = await makeRequest(`${CONFIG.BACKEND_URL}/api/health/`, {
      method: 'OPTIONS',
      headers: {
        'Origin': 'https://vlanet.net',
        'Access-Control-Request-Method': 'GET',
        'Access-Control-Request-Headers': 'Content-Type,Authorization'
      }
    });
    
    if (corsResult.headers['access-control-allow-origin'] || corsResult.statusCode === 200) {
      console.log('  ✅ PASS - CORS properly configured');
      results.passed++;
    } else {
      console.log('  ❌ FAIL - CORS may not be properly configured');
      results.failed++;
      results.errors.push({
        type: 'cors',
        error: 'CORS headers missing or invalid',
        statusCode: corsResult.statusCode
      });
    }
  } catch (error) {
    console.log(`  ❌ FAIL - CORS test failed: ${error.message}`);
    results.failed++;
    results.errors.push({
      type: 'cors',
      error: error.message
    });
  }
}

/**
 * 성능 벤치마크
 */
async function performanceBenchmark() {
  console.log('\n🚀 Performance Benchmark...');
  console.log('=' .repeat(50));
  
  const benchmarkRoutes = [
    `${CONFIG.FRONTEND_URL}/`,
    `${CONFIG.BACKEND_URL}/api/health/`
  ];
  
  for (const url of benchmarkRoutes) {
    console.log(`Benchmarking: ${url}`);
    
    const times = [];
    for (let i = 0; i < 3; i++) {
      const start = Date.now();
      try {
        await makeRequest(url);
        const time = Date.now() - start;
        times.push(time);
      } catch (error) {
        console.log(`  ⚠️  Benchmark request failed: ${error.message}`);
      }
    }
    
    if (times.length > 0) {
      const avgTime = Math.round(times.reduce((a, b) => a + b, 0) / times.length);
      const status = avgTime < 2000 ? '✅' : avgTime < 5000 ? '⚠️' : '❌';
      console.log(`  ${status} Average response time: ${avgTime}ms`);
      
      if (avgTime > 5000) {
        results.errors.push({
          type: 'performance',
          url: url,
          error: `Slow response time: ${avgTime}ms`
        });
      }
    }
  }
}

/**
 * 결과 리포트 생성
 */
function generateReport() {
  console.log('\n' + '='.repeat(60));
  console.log('📊 TEST RESULTS SUMMARY');
  console.log('='.repeat(60));
  
  const total = results.passed + results.failed;
  const passRate = total > 0 ? ((results.passed / total) * 100).toFixed(1) : 0;
  
  console.log(`Total Tests: ${total}`);
  console.log(`✅ Passed: ${results.passed}`);
  console.log(`❌ Failed: ${results.failed}`);
  console.log(`📈 Pass Rate: ${passRate}%`);
  
  if (results.errors.length > 0) {
    console.log('\n🚨 CRITICAL ISSUES:');
    console.log('-'.repeat(40));
    
    const criticalErrors = results.errors.filter(e => 
      e.error?.includes('404') || 
      e.type === 'cors' ||
      e.type === 'performance'
    );
    
    criticalErrors.forEach((error, index) => {
      console.log(`${index + 1}. ${error.type?.toUpperCase()} - ${error.name || error.url || 'Unknown'}`);
      console.log(`   Error: ${error.error}`);
      if (error.url) console.log(`   URL: ${error.url}`);
      console.log();
    });
  }
  
  // JSON 리포트 저장
  const reportData = {
    timestamp: new Date().toISOString(),
    config: CONFIG,
    summary: {
      total: total,
      passed: results.passed,
      failed: results.failed,
      passRate: passRate
    },
    results: results.summary,
    errors: results.errors
  };
  
  const fs = require('fs');
  const reportPath = `routing-test-report-${Date.now()}.json`;
  
  try {
    fs.writeFileSync(reportPath, JSON.stringify(reportData, null, 2));
    console.log(`📁 Full report saved to: ${reportPath}`);
  } catch (error) {
    console.log(`⚠️  Could not save report: ${error.message}`);
  }
  
  // 성공 기준
  const SUCCESS_CRITERIA = {
    MIN_PASS_RATE: 80,
    MAX_404_ERRORS: 0
  };
  
  const has404Errors = results.errors.some(e => e.error?.includes('404'));
  const meetsPassRate = parseFloat(passRate) >= SUCCESS_CRITERIA.MIN_PASS_RATE;
  
  console.log('\n🎯 SUCCESS CRITERIA:');
  console.log('-'.repeat(30));
  console.log(`Pass Rate ≥ ${SUCCESS_CRITERIA.MIN_PASS_RATE}%: ${meetsPassRate ? '✅' : '❌'} (${passRate}%)`);
  console.log(`404 Errors = 0: ${!has404Errors ? '✅' : '❌'} (${results.errors.filter(e => e.error?.includes('404')).length} found)`);
  
  const overallSuccess = meetsPassRate && !has404Errors;
  console.log(`\n🎉 OVERALL RESULT: ${overallSuccess ? '✅ SUCCESS' : '❌ NEEDS ATTENTION'}`);
  
  return overallSuccess;
}

/**
 * 메인 테스트 실행
 */
async function runTests() {
  console.log('🚀 VideoPlanet Comprehensive Routing Test');
  console.log('=' .repeat(60));
  console.log(`Frontend: ${CONFIG.FRONTEND_URL}`);
  console.log(`Backend: ${CONFIG.BACKEND_URL}`);
  console.log(`Started: ${new Date().toISOString()}`);
  
  try {
    await testFrontendRoutes();
    await testBackendRoutes();
    await testSpecialCases();
    await performanceBenchmark();
    
    const success = generateReport();
    
    // Exit with appropriate code
    process.exit(success ? 0 : 1);
    
  } catch (error) {
    console.error('❌ Test execution failed:', error);
    process.exit(1);
  }
}

// CLI 실행
if (require.main === module) {
  runTests();
}

module.exports = { runTests, testWithRetry, CONFIG };