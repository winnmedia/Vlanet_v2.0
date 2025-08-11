import fetch from 'node-fetch';

//  
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
  console.log(`${colors.cyan}${colors.bright}  API ${colors.reset}`);
  
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
      console.log(`${colors.green}  !${colors.reset}`);
      console.log(`  - Access Token: ${data.access ? '' : ''}`);
      console.log(`  - Refresh Token: ${data.refresh ? '' : ''}`);
      console.log(`  - User ID: ${data.user?.id || 'N/A'}`);
      console.log(`  - Email: ${data.user?.email || 'N/A'}`);
      return data.access;
    } else {
      console.log(`${colors.red}  : ${data.message || response.statusText}${colors.reset}`);
      return null;
    }
  } catch (error) {
    console.log(`${colors.red}  : ${error.message}${colors.reset}`);
    return null;
  }
}

async function testProtectedRoute(token) {
  console.log(`\n${colors.cyan}${colors.bright}  API ${colors.reset}`);
  
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
      console.log(`${colors.green}    !${colors.reset}`);
      console.log(`  - ID: ${data.id}`);
      console.log(`  - Email: ${data.email}`);
      console.log(`  - Nickname: ${data.nickname}`);
      return true;
    } else {
      console.log(`${colors.red}    : ${response.statusText}${colors.reset}`);
      return false;
    }
  } catch (error) {
    console.log(`${colors.red}  : ${error.message}${colors.reset}`);
    return false;
  }
}

async function testFrontendAccess() {
  console.log(`\n${colors.cyan}${colors.bright}    ${colors.reset}`);
  
  const pages = [
    { url: '/', name: '' },
    { url: '/login', name: '' },
    { url: '/cmshome', name: '' },
    { url: '/projects', name: '' },
    { url: '/videoplanning', name: ' ' },
    { url: '/schedule', name: '' },
    { url: '/feedback', name: '' },
  ];

  for (const page of pages) {
    try {
      const response = await fetch(`${FRONTEND_URL}${page.url}`, {
        method: 'GET',
        redirect: 'manual'
      });

      if (response.status === 200) {
        console.log(`${colors.green} ${page.name} :  ${colors.reset}`);
      } else if (response.status === 307 || response.status === 302) {
        console.log(`${colors.yellow}↩  ${page.name} :  ( )${colors.reset}`);
      } else {
        console.log(`${colors.red} ${page.name} :  (${response.status})${colors.reset}`);
      }
    } catch (error) {
      console.log(`${colors.red} ${page.name} :   - ${error.message}${colors.reset}`);
    }
  }
}

async function runTests() {
  console.log(`${colors.bright}${colors.blue}

     VideoPlanet        
${colors.reset}\n`);

  // 1.  
  const token = await testLogin();
  
  if (token) {
    // 2.  API 
    await testProtectedRoute(token);
  }
  
  // 3.    
  await testFrontendAccess();

  console.log(`\n${colors.bright}${colors.blue} !${colors.reset}`);
}

runTests();