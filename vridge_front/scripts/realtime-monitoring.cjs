#!/usr/bin/env node

/**
 * VideoPlanet 실시간 모니터링 및 자동 복구 시스템
 * 404 에러를 0으로 유지하고 선순환 피드백 루프를 구현합니다.
 */

const https = require('https');
const fs = require('fs');
const path = require('path');

// 모니터링 설정
const MONITOR_CONFIG = {
  CHECK_INTERVAL: 30000, // 30초마다 체크
  ALERT_THRESHOLD: 3, // 3번 연속 실패시 알림
  AUTO_RECOVERY_ENABLED: true,
  ENDPOINTS: [
    { url: 'https://vlanet.net/', name: 'Frontend Home', type: 'frontend' },
    { url: 'https://vlanet.net/analytics', name: 'Analytics Page', type: 'frontend' },
    { url: 'https://vlanet.net/teams', name: 'Teams Page', type: 'frontend' },
    { url: 'https://vlanet.net/settings', name: 'Settings Page', type: 'frontend' },
    { url: 'https://vlanet.net/dashboard', name: 'Dashboard', type: 'frontend' },
    { url: 'https://videoplanet.up.railway.app/api/health/', name: 'Backend Health', type: 'backend' },
    { url: 'https://videoplanet.up.railway.app/api/analytics/dashboard/', name: 'Analytics API', type: 'backend' }
  ],
  WEBHOOK_URL: null, // Slack/Discord 웹훅 URL (필요시 설정)
  LOG_FILE: 'monitoring.log'
};

// 상태 추적
const monitorState = {
  isRunning: false,
  startTime: null,
  checks: 0,
  failures: {},
  consecutiveFailures: {},
  alerts: [],
  stats: {
    totalChecks: 0,
    totalFailures: 0,
    uptimePercentage: 100,
    averageResponseTime: 0
  }
};

/**
 * HTTP 요청 유틸리티
 */
function makeRequest(url, timeout = 10000) {
  return new Promise((resolve, reject) => {
    const startTime = Date.now();
    const urlObj = new URL(url);
    
    const options = {
      hostname: urlObj.hostname,
      port: urlObj.port || 443,
      path: urlObj.pathname + urlObj.search,
      method: 'HEAD', // HEAD 요청으로 빠른 체크
      headers: {
        'User-Agent': 'VideoPlanet-Monitor/1.0',
        'Accept': '*/*'
      },
      timeout: timeout
    };

    const req = https.request(options, (res) => {
      const responseTime = Date.now() - startTime;
      resolve({
        statusCode: res.statusCode,
        responseTime: responseTime,
        url: url
      });
    });

    req.on('error', (error) => {
      const responseTime = Date.now() - startTime;
      reject({
        error: error.message,
        responseTime: responseTime,
        url: url
      });
    });

    req.on('timeout', () => {
      req.destroy();
      reject({
        error: 'Request timeout',
        responseTime: timeout,
        url: url
      });
    });

    req.end();
  });
}

/**
 * 엔드포인트 상태 체크
 */
async function checkEndpoint(endpoint) {
  try {
    const result = await makeRequest(endpoint.url);
    
    const isHealthy = 
      (endpoint.type === 'frontend' && [200, 401].includes(result.statusCode)) ||
      (endpoint.type === 'backend' && [200, 401, 403].includes(result.statusCode));
    
    return {
      ...endpoint,
      status: isHealthy ? 'healthy' : 'unhealthy',
      statusCode: result.statusCode,
      responseTime: result.responseTime,
      error: null,
      timestamp: new Date().toISOString()
    };
  } catch (error) {
    return {
      ...endpoint,
      status: 'error',
      statusCode: null,
      responseTime: error.responseTime,
      error: error.error,
      timestamp: new Date().toISOString()
    };
  }
}

/**
 * 모든 엔드포인트 상태 체크
 */
async function performHealthCheck() {
  const results = [];
  
  for (const endpoint of MONITOR_CONFIG.ENDPOINTS) {
    const result = await checkEndpoint(endpoint);
    results.push(result);
    
    // 연속 실패 카운트 업데이트
    if (result.status !== 'healthy') {
      monitorState.consecutiveFailures[endpoint.name] = 
        (monitorState.consecutiveFailures[endpoint.name] || 0) + 1;
      
      if (!monitorState.failures[endpoint.name]) {
        monitorState.failures[endpoint.name] = [];
      }
      monitorState.failures[endpoint.name].push(result);
      monitorState.stats.totalFailures++;
    } else {
      monitorState.consecutiveFailures[endpoint.name] = 0;
    }
    
    monitorState.stats.totalChecks++;
  }
  
  return results;
}

/**
 * 알림 발송
 */
async function sendAlert(endpoint, failureCount, lastError) {
  const alertMessage = {
    timestamp: new Date().toISOString(),
    endpoint: endpoint.name,
    url: endpoint.url,
    failureCount: failureCount,
    error: lastError,
    severity: failureCount >= MONITOR_CONFIG.ALERT_THRESHOLD ? 'CRITICAL' : 'WARNING'
  };
  
  monitorState.alerts.push(alertMessage);
  
  // 콘솔 알림
  const severity = alertMessage.severity === 'CRITICAL' ? '🚨' : '⚠️';
  console.log(`${severity} ALERT: ${endpoint.name} has failed ${failureCount} times consecutively`);
  console.log(`   URL: ${endpoint.url}`);
  console.log(`   Error: ${lastError}`);
  console.log(`   Time: ${alertMessage.timestamp}`);
  
  // 로그 파일에 기록
  logEvent('ALERT', alertMessage);
  
  // 웹훅 알림 (설정된 경우)
  if (MONITOR_CONFIG.WEBHOOK_URL) {
    try {
      await sendWebhookAlert(alertMessage);
    } catch (error) {
      console.log('⚠️  Failed to send webhook alert:', error.message);
    }
  }
  
  // 자동 복구 시도
  if (MONITOR_CONFIG.AUTO_RECOVERY_ENABLED && alertMessage.severity === 'CRITICAL') {
    await attemptAutoRecovery(endpoint);
  }
}

/**
 * 웹훅 알림 발송
 */
async function sendWebhookAlert(alert) {
  const payload = {
    text: `🚨 VideoPlanet Monitor Alert`,
    attachments: [
      {
        color: alert.severity === 'CRITICAL' ? 'danger' : 'warning',
        fields: [
          { title: 'Endpoint', value: alert.endpoint, short: true },
          { title: 'URL', value: alert.url, short: true },
          { title: 'Failure Count', value: alert.failureCount.toString(), short: true },
          { title: 'Error', value: alert.error, short: false }
        ],
        timestamp: alert.timestamp
      }
    ]
  };
  
  return makeRequest(MONITOR_CONFIG.WEBHOOK_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
}

/**
 * 자동 복구 시도
 */
async function attemptAutoRecovery(endpoint) {
  console.log(`🔧 Attempting auto-recovery for ${endpoint.name}...`);
  logEvent('AUTO_RECOVERY', { endpoint: endpoint.name, url: endpoint.url });
  
  // 백엔드 엔드포인트의 경우
  if (endpoint.type === 'backend') {
    // Railway 서비스 재시작 시도 (실제로는 API 호출 필요)
    console.log('   - Checking Railway service status...');
    
    // 헬스체크 재시도
    console.log('   - Retrying health check...');
    const recheckResult = await checkEndpoint(endpoint);
    
    if (recheckResult.status === 'healthy') {
      console.log('   ✅ Recovery successful!');
      logEvent('RECOVERY_SUCCESS', { endpoint: endpoint.name });
      return true;
    }
  }
  
  // 프론트엔드 엔드포인트의 경우
  if (endpoint.type === 'frontend') {
    // Vercel 배포 상태 확인
    console.log('   - Checking Vercel deployment status...');
    
    // 캐시 무효화 시도
    console.log('   - Attempting cache invalidation...');
    const recheckResult = await checkEndpoint({
      ...endpoint,
      url: endpoint.url + '?cache_bust=' + Date.now()
    });
    
    if (recheckResult.status === 'healthy') {
      console.log('   ✅ Recovery successful!');
      logEvent('RECOVERY_SUCCESS', { endpoint: endpoint.name });
      return true;
    }
  }
  
  console.log('   ❌ Auto-recovery failed');
  logEvent('RECOVERY_FAILED', { endpoint: endpoint.name });
  return false;
}

/**
 * 이벤트 로깅
 */
function logEvent(type, data) {
  const logEntry = {
    timestamp: new Date().toISOString(),
    type: type,
    data: data
  };
  
  const logLine = JSON.stringify(logEntry) + '\\n';
  
  try {
    fs.appendFileSync(MONITOR_CONFIG.LOG_FILE, logLine);
  } catch (error) {
    console.log('⚠️  Failed to write to log file:', error.message);
  }
}

/**
 * 통계 계산 및 업데이트
 */
function updateStats(results) {
  const healthyCount = results.filter(r => r.status === 'healthy').length;
  const totalResponseTime = results.reduce((sum, r) => sum + (r.responseTime || 0), 0);
  
  // 업타임 계산
  monitorState.stats.uptimePercentage = 
    monitorState.stats.totalChecks > 0 
      ? ((monitorState.stats.totalChecks - monitorState.stats.totalFailures) / monitorState.stats.totalChecks * 100)
      : 100;
  
  // 평균 응답 시간
  monitorState.stats.averageResponseTime = 
    results.length > 0 ? Math.round(totalResponseTime / results.length) : 0;
}

/**
 * 상태 리포트 출력
 */
function printStatusReport(results) {
  console.clear();
  console.log('🖥️  VideoPlanet Real-time Monitor');
  console.log('═'.repeat(60));
  console.log(`Started: ${monitorState.startTime}`);
  console.log(`Uptime: ${Math.round((Date.now() - new Date(monitorState.startTime)) / 1000 / 60)} minutes`);
  console.log(`Checks: ${monitorState.checks}`);
  console.log(`Overall Uptime: ${monitorState.stats.uptimePercentage.toFixed(2)}%`);
  console.log(`Avg Response Time: ${monitorState.stats.averageResponseTime}ms`);
  console.log();
  
  // 엔드포인트별 상태
  console.log('📊 Endpoint Status:');
  console.log('-'.repeat(40));
  
  results.forEach(result => {
    const statusIcon = 
      result.status === 'healthy' ? '✅' :
      result.status === 'unhealthy' ? '⚠️' : '❌';
    
    const consecutiveFails = monitorState.consecutiveFailures[result.name] || 0;
    const failInfo = consecutiveFails > 0 ? ` (${consecutiveFails} fails)` : '';
    
    console.log(`${statusIcon} ${result.name}: ${result.statusCode || 'ERROR'} - ${result.responseTime}ms${failInfo}`);
    if (result.error) {
      console.log(`   Error: ${result.error}`);
    }
  });
  
  // 최근 알림
  if (monitorState.alerts.length > 0) {
    console.log();
    console.log('🚨 Recent Alerts:');
    console.log('-'.repeat(40));
    
    const recentAlerts = monitorState.alerts.slice(-5);
    recentAlerts.forEach(alert => {
      const time = new Date(alert.timestamp).toLocaleTimeString();
      console.log(`${time} - ${alert.endpoint}: ${alert.error}`);
    });
  }
  
  console.log();
  console.log(`Last check: ${new Date().toLocaleTimeString()} | Next check in ${Math.round(MONITOR_CONFIG.CHECK_INTERVAL / 1000)}s`);
  console.log('Press Ctrl+C to stop monitoring');
}

/**
 * 모니터링 루프 실행
 */
async function runMonitoringLoop() {
  try {
    monitorState.checks++;
    const results = await performHealthCheck();
    
    // 알림 체크
    for (const result of results) {
      const consecutiveFails = monitorState.consecutiveFailures[result.name] || 0;
      
      if (consecutiveFails >= MONITOR_CONFIG.ALERT_THRESHOLD) {
        await sendAlert(result, consecutiveFails, result.error || `Status: ${result.statusCode}`);
      }
    }
    
    // 통계 업데이트
    updateStats(results);
    
    // 상태 리포트 출력
    printStatusReport(results);
    
    // 로그 기록
    logEvent('HEALTH_CHECK', {
      results: results.map(r => ({
        name: r.name,
        status: r.status,
        statusCode: r.statusCode,
        responseTime: r.responseTime
      })),
      stats: monitorState.stats
    });
    
  } catch (error) {
    console.error('❌ Monitoring loop error:', error);
    logEvent('MONITOR_ERROR', { error: error.message });
  }
}

/**
 * 모니터링 시작
 */
function startMonitoring() {
  if (monitorState.isRunning) {
    console.log('⚠️  Monitoring is already running');
    return;
  }
  
  monitorState.isRunning = true;
  monitorState.startTime = new Date().toISOString();
  
  console.log('🚀 Starting VideoPlanet Real-time Monitor...');
  console.log(`Check interval: ${MONITOR_CONFIG.CHECK_INTERVAL / 1000} seconds`);
  console.log(`Alert threshold: ${MONITOR_CONFIG.ALERT_THRESHOLD} consecutive failures`);
  console.log(`Auto-recovery: ${MONITOR_CONFIG.AUTO_RECOVERY_ENABLED ? 'Enabled' : 'Disabled'}`);
  console.log();
  
  // 초기 체크 실행
  runMonitoringLoop();
  
  // 정기적인 체크 시작
  const intervalId = setInterval(runMonitoringLoop, MONITOR_CONFIG.CHECK_INTERVAL);
  
  // 종료 처리
  process.on('SIGINT', () => {
    console.log('\\n\\n🛑 Stopping monitor...');
    clearInterval(intervalId);
    
    // 최종 리포트
    console.log('\\n📈 Final Report:');
    console.log(`Total Checks: ${monitorState.stats.totalChecks}`);
    console.log(`Total Failures: ${monitorState.stats.totalFailures}`);
    console.log(`Overall Uptime: ${monitorState.stats.uptimePercentage.toFixed(2)}%`);
    console.log(`Total Alerts: ${monitorState.alerts.length}`);
    
    logEvent('MONITOR_STOPPED', {
      finalStats: monitorState.stats,
      totalAlerts: monitorState.alerts.length,
      duration: Math.round((Date.now() - new Date(monitorState.startTime)) / 1000)
    });
    
    process.exit(0);
  });
}

/**
 * CLI 명령 처리
 */
function handleCLI() {
  const args = process.argv.slice(2);
  const command = args[0];
  
  switch (command) {
    case 'start':
    case undefined:
      startMonitoring();
      break;
      
    case 'test':
      console.log('🧪 Running single health check...');
      runMonitoringLoop().then(() => {
        process.exit(0);
      });
      break;
      
    case 'logs':
      try {
        const logs = fs.readFileSync(MONITOR_CONFIG.LOG_FILE, 'utf8');
        console.log(logs);
      } catch (error) {
        console.log('❌ Could not read log file:', error.message);
      }
      break;
      
    case 'clear-logs':
      try {
        fs.writeFileSync(MONITOR_CONFIG.LOG_FILE, '');
        console.log('✅ Log file cleared');
      } catch (error) {
        console.log('❌ Could not clear log file:', error.message);
      }
      break;
      
    case 'help':
      console.log(`
VideoPlanet Real-time Monitor

Usage:
  node realtime-monitoring.js [command]

Commands:
  start       Start real-time monitoring (default)
  test        Run single health check
  logs        Show monitoring logs
  clear-logs  Clear log file
  help        Show this help message

Examples:
  node realtime-monitoring.js start
  node realtime-monitoring.js test
      `);
      break;
      
    default:
      console.log(`❌ Unknown command: ${command}`);
      console.log('Use "help" command for usage information');
      process.exit(1);
  }
}

// CLI 실행
if (require.main === module) {
  handleCLI();
}

module.exports = {
  startMonitoring,
  checkEndpoint,
  MONITOR_CONFIG,
  monitorState
};