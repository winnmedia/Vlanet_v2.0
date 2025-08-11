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

//   
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
      console.log(`${colors.green} ${name}${colors.reset}`);
      testResults.passed++;
      return true;
    } else {
      console.log(`${colors.red} ${name}${colors.reset}`);
      testResults.failed++;
      return false;
    }
  } catch (error) {
    console.log(`${colors.red} ${name}: ${error.message}${colors.reset}`);
    testResults.failed++;
    return false;
  }
}

async function runFinalTests() {
  console.log(`${colors.bright}${colors.blue}

        VideoPlanet              
${colors.reset}\n`);

  // 1.  API  
  console.log(`${colors.cyan}${colors.bright}1.  API  ${colors.reset}`);
  
  await testWithResult(' ', async () => {
    const response = await fetch(`${API_URL}/api/health/`);
    return response.ok;
  });

  // 2.    
  console.log(`\n${colors.cyan}${colors.bright}2.   ${colors.reset}`);
  
  await testWithResult('  ', async () => {
    const response = await fetch(`${FRONTEND_URL}/`);
    return response.ok;
  });

  // 3.  
  console.log(`\n${colors.cyan}${colors.bright}3.   ${colors.reset}`);
  
  let authToken = null;
  const loginSuccess = await testWithResult(' API', async () => {
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
    await testWithResult('  ', async () => {
      const response = await fetch(`${API_URL}/api/users/me/`, {
        headers: { 'Authorization': `Bearer ${authToken}` }
      });
      return response.ok;
    });
  }

  // 4.    
  console.log(`\n${colors.cyan}${colors.bright}4.   ${colors.reset}`);
  
  const pages = [
    { name: ' ', url: '/' },
    { name: ' ', url: '/login' },
    { name: '', url: '/cmshome' },
    { name: '', url: '/projects' },
    { name: ' ', url: '/videoplanning' },
    { name: '', url: '/schedule' },
    { name: '', url: '/feedback' },
  ];

  for (const page of pages) {
    await testWithResult(page.name, async () => {
      const response = await fetch(`${FRONTEND_URL}${page.url}`, {
        redirect: 'manual'
      });
      // 200, 307()  
      return response.status === 200 || response.status === 307 || response.status === 302;
    });
  }

  // 5.  API 
  console.log(`\n${colors.cyan}${colors.bright}5.  API ${colors.reset}`);
  
  if (authToken) {
    await testWithResult('  ', async () => {
      const response = await fetch(`${API_URL}/api/projects/`, {
        headers: { 'Authorization': `Bearer ${authToken}` }
      });
      return response.ok;
    });

    await testWithResult('  API', async () => {
      const response = await fetch(`${API_URL}/api/projects/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          name: `  ${Date.now()}`,
          description: '   ',
          status: 'planning'
        })
      });
      return response.ok || response.status === 201;
    });
  }

  // 6.  API 
  console.log(`\n${colors.cyan}${colors.bright}6.  API ${colors.reset}`);
  
  if (authToken) {
    await testWithResult('  ', async () => {
      const response = await fetch(`${API_URL}/api/feedbacks/`, {
        headers: { 'Authorization': `Bearer ${authToken}` }
      });
      return response.ok;
    });
  }

  //   
  console.log(`\n${colors.bright}${colors.magenta}

                                      
${colors.reset}`);

  const successRate = Math.round((testResults.passed / testResults.total) * 100);
  const statusColor = successRate === 100 ? colors.green : successRate >= 80 ? colors.yellow : colors.red;
  
  console.log(`
   : ${testResults.total}
  ${colors.green}: ${testResults.passed}${colors.reset}
  ${colors.red}: ${testResults.failed}${colors.reset}
  
  ${statusColor}${colors.bright}: ${successRate}%${colors.reset}
  `);

  if (successRate === 100) {
    console.log(`${colors.green}${colors.bright}   ! VideoPlanet   .${colors.reset}`);
  } else if (successRate >= 80) {
    console.log(`${colors.yellow}${colors.bright}   .   .${colors.reset}`);
  } else {
    console.log(`${colors.red}${colors.bright}   .   .${colors.reset}`);
  }
}

//  
runFinalTests().catch(console.error);