#!/usr/bin/env node

/**
 * VideoPlanet    
 * -  →  →   →  
 */

const API_URL = process.env.API_URL || 'http://localhost:8000';
const FRONTEND_URL = process.env.FRONTEND_URL || 'http://localhost:3000';

//  
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m'
};

//  
function log(message, type = 'info') {
  const prefix = {
    'info': `${colors.blue}ℹ${colors.reset}`,
    'success': `${colors.green}${colors.reset}`,
    'error': `${colors.red}${colors.reset}`,
    'warning': `${colors.yellow}${colors.reset}`,
    'test': `${colors.cyan}${colors.reset}`
  };
  console.log(`${prefix[type] || prefix.info} ${message}`);
}

function generateTestUser() {
  const timestamp = Date.now();
  return {
    email: `test${timestamp}@videoplanet.com`,
    password: 'Test1234!@',
    name: `${timestamp}`,
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

//  
async function testHealthCheck() {
  log('   ...', 'test');
  
  const response = await makeRequest('/api/health/', {
    method: 'GET'
  });

  if (response.ok) {
    log('   ', 'success');
    return true;
  } else {
    log(`   : ${response.status} - ${JSON.stringify(response.data)}`, 'error');
    return false;
  }
}

async function testUserRegistration(userData) {
  log('  ...', 'test');
  
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
    log(`  : ${userData.email}`, 'success');
    return response.data;
  } else {
    log(`  : ${response.status} - ${JSON.stringify(response.data)}`, 'error');
    return null;
  }
}

async function testUserLogin(userData) {
  log('  ...', 'test');
  
  const response = await makeRequest('/api/users/login/', {
    method: 'POST',
    body: JSON.stringify({
      username: userData.email,
      password: userData.password
    })
  });

  if (response.ok && response.data.access) {
    log('  , JWT  ', 'success');
    return {
      access: response.data.access,
      refresh: response.data.refresh,
      user: response.data.user
    };
  } else {
    log(`  : ${response.status} - ${JSON.stringify(response.data)}`, 'error');
    return null;
  }
}

async function testProjectCreation(authToken) {
  log('   ...', 'test');
  
  const projectData = {
    name: `  ${Date.now()}`,
    description: '   ',
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
    log(`   : ${response.data.name}`, 'success');
    return response.data;
  } else {
    log(`   : ${response.status} - ${JSON.stringify(response.data)}`, 'error');
    return null;
  }
}

async function testProjectList(authToken) {
  log('   ...', 'test');
  
  const response = await makeRequest('/api/projects/', {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${authToken}`
    }
  });

  if (response.ok) {
    const count = Array.isArray(response.data) ? response.data.length : 
                  response.data.results ? response.data.results.length : 0;
    log(`    : ${count} `, 'success');
    return response.data;
  } else {
    log(`    : ${response.status}`, 'error');
    return null;
  }
}

async function testFeedbackCreation(authToken, projectId) {
  log('   ...', 'test');
  
  const feedbackData = {
    project: projectId,
    content: ' .    !',
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
    log('   ', 'success');
    return response.data;
  } else {
    log(`   : ${response.status} - ${JSON.stringify(response.data)}`, 'error');
    return null;
  }
}

//   
async function runFullUserJourney() {
  console.log('\n' + '='.repeat(60));
  console.log(`${colors.bright} VideoPlanet    ${colors.reset}`);
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

  // 1.   
  results.total++;
  const serverHealthy = await testHealthCheck();
  if (serverHealthy) {
    results.passed++;
  } else {
    results.failed++;
    log('    ', 'error');
    return results;
  }
  console.log();

  // 2.  
  const testUser = generateTestUser();
  results.total++;
  const registrationResult = await testUserRegistration(testUser);
  if (registrationResult) {
    results.passed++;
  } else {
    results.failed++;
  }
  console.log();

  // 3.  
  results.total++;
  const loginResult = await testUserLogin(testUser);
  if (loginResult) {
    results.passed++;
  } else {
    results.failed++;
    log('    ', 'warning');
    results.skipped += 3;
    return results;
  }
  console.log();

  // 4.   
  results.total++;
  const project = await testProjectCreation(loginResult.access);
  if (project) {
    results.passed++;
  } else {
    results.failed++;
  }
  console.log();

  // 5.    
  results.total++;
  const projectList = await testProjectList(loginResult.access);
  if (projectList) {
    results.passed++;
  } else {
    results.failed++;
  }
  console.log();

  // 6.   
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
    log('    ', 'warning');
  }

  //   
  console.log('\n' + '='.repeat(60));
  console.log(`${colors.bright}   ${colors.reset}`);
  console.log('='.repeat(60));
  
  const successRate = results.total > 0 ? 
    Math.round((results.passed / results.total) * 100) : 0;
  
  console.log(`${colors.green} : ${results.passed}${colors.reset}`);
  console.log(`${colors.red} : ${results.failed}${colors.reset}`);
  console.log(`${colors.yellow}⏭  : ${results.skipped}${colors.reset}`);
  console.log(`${colors.blue} : ${results.total}${colors.reset}`);
  console.log(`${colors.cyan} : ${successRate}%${colors.reset}`);
  
  if (successRate === 100) {
    console.log(`\n${colors.green}${colors.bright}    !${colors.reset}`);
  } else if (successRate >= 80) {
    console.log(`\n${colors.yellow}      .${colors.reset}`);
  } else {
    console.log(`\n${colors.red}   .   .${colors.reset}`);
  }

  return results;
}

//  
runFullUserJourney()
  .then(results => {
    process.exit(results.failed > 0 ? 1 : 0);
  })
  .catch(error => {
    log(`    : ${error.message}`, 'error');
    process.exit(1);
  });