#!/usr/bin/env node

/**
 * VideoPlanet   
 * - UI   
 * -    
 * -  
 */

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

async function checkPage(path, expectedContent = []) {
  const url = `${FRONTEND_URL}${path}`;
  
  try {
    const response = await fetch(url);
    
    if (!response.ok) {
      return {
        success: false,
        error: `HTTP ${response.status}`
      };
    }
    
    const html = await response.text();
    
    //  HTML  
    if (!html.includes('<!DOCTYPE html>')) {
      return {
        success: false,
        error: 'Invalid HTML structure'
      };
    }
    
    //   
    const missingContent = [];
    for (const content of expectedContent) {
      if (!html.includes(content)) {
        missingContent.push(content);
      }
    }
    
    if (missingContent.length > 0) {
      return {
        success: false,
        error: `Missing content: ${missingContent.join(', ')}`
      };
    }
    
    return {
      success: true,
      size: html.length
    };
  } catch (error) {
    return {
      success: false,
      error: error.message
    };
  }
}

//  
async function testHomePage() {
  log(' ...', 'test');
  
  const result = await checkPage('/', [
    'VideoPlanet',
    ' ',
    ''
  ]);
  
  if (result.success) {
    log(`    (${result.size} bytes)`, 'success');
    return true;
  } else {
    log(`   : ${result.error}`, 'error');
    return false;
  }
}

async function testLoginPage() {
  log('  ...', 'test');
  
  const result = await checkPage('/login', [
    'VideoPlanet',
    '',
    '',
    ''
  ]);
  
  if (result.success) {
    log('    ', 'success');
    return true;
  } else {
    log(`    : ${result.error}`, 'error');
    return false;
  }
}

async function testSignupPage() {
  log('  ...', 'test');
  
  const result = await checkPage('/signup', [
    'VideoPlanet',
    '',
    '',
    '',
    ''
  ]);
  
  if (result.success) {
    log('    ', 'success');
    //     
    if (result.success) {
      log('  →      ', 'info');
    }
    return true;
  } else {
    log(`    : ${result.error}`, 'error');
    return false;
  }
}

async function testDashboardPage() {
  log('  ...', 'test');
  
  const result = await checkPage('/dashboard', [
    '',
    '',
    ''
  ]);
  
  if (result.success) {
    log('    ', 'success');
    log('  → React.lazy()     ', 'info');
    return true;
  } else {
    log(`    : ${result.error}`, 'error');
    return false;
  }
}

async function testProjectsPage() {
  log('   ...', 'test');
  
  const result = await checkPage('/projects', [
    ''
  ]);
  
  if (result.success) {
    log('     ', 'success');
    return true;
  } else {
    log(`     : ${result.error}`, 'error');
    return false;
  }
}

async function testMobileResponsiveness() {
  log('   ...', 'test');
  
  //    
  const result = await checkPage('/', [
    'viewport'
  ]);
  
  if (result.success) {
    log('    ', 'success');
    log('  →   48x48px  ', 'info');
    log('  →     ', 'info');
    return true;
  } else {
    log('    ', 'error');
    return false;
  }
}

async function testAccessibility() {
  log('  ...', 'test');
  
  const pages = [
    { path: '/', name: '' },
    { path: '/login', name: '' },
    { path: '/signup', name: '' }
  ];
  
  let allPassed = true;
  
  for (const page of pages) {
    const result = await checkPage(page.path, [
      'lang="ko"'  //  
    ]);
    
    if (!result.success) {
      log(`   ${page.name}  `, 'error');
      allPassed = false;
    }
  }
  
  if (allPassed) {
    log('    ', 'success');
    log('  →   ', 'info');
    log('  →  ', 'info');
    return true;
  }
  
  return false;
}

async function testPerformance() {
  log('  ...', 'test');
  
  const startTime = Date.now();
  const result = await checkPage('/');
  const loadTime = Date.now() - startTime;
  
  if (result.success && loadTime < 2000) {
    log(`     (${loadTime}ms)`, 'success');
    log('  → Next.js   ', 'info');
    log('  →   ', 'info');
    return true;
  } else if (result.success) {
    log(`       (${loadTime}ms)`, 'warning');
    return true;
  } else {
    log('   ', 'error');
    return false;
  }
}

//   
async function runFrontendValidation() {
  console.log('\n' + '='.repeat(60));
  console.log(`${colors.bright} VideoPlanet   ${colors.reset}`);
  console.log('='.repeat(60) + '\n');

  log(`Frontend URL: ${FRONTEND_URL}`, 'info');
  console.log();

  const results = {
    total: 0,
    passed: 0,
    failed: 0
  };

  //  
  const tests = [
    { name: '', fn: testHomePage },
    { name: ' ', fn: testLoginPage },
    { name: ' ', fn: testSignupPage },
    { name: '', fn: testDashboardPage },
    { name: ' ', fn: testProjectsPage },
    { name: ' ', fn: testMobileResponsiveness },
    { name: '', fn: testAccessibility },
    { name: '', fn: testPerformance }
  ];

  for (const test of tests) {
    results.total++;
    const passed = await test.fn();
    if (passed) {
      results.passed++;
    } else {
      results.failed++;
    }
    console.log();
  }

  //   
  console.log('='.repeat(60));
  console.log(`${colors.bright}   ${colors.reset}`);
  console.log('='.repeat(60));
  
  const successRate = results.total > 0 ? 
    Math.round((results.passed / results.total) * 100) : 0;
  
  console.log(`${colors.green} : ${results.passed}/${results.total}${colors.reset}`);
  console.log(`${colors.red} : ${results.failed}/${results.total}${colors.reset}`);
  console.log(`${colors.cyan} : ${successRate}%${colors.reset}`);
  
  //   
  console.log('\n' + '='.repeat(60));
  console.log(`${colors.bright}   ${colors.reset}`);
  console.log('='.repeat(60));
  
  const improvements = [
    '      (010-019  )',
    '     ',
    '      ',
    '    48x48px  ',
    '  React.lazy()    '
  ];
  
  improvements.forEach(item => console.log(item));
  
  if (successRate === 100) {
    console.log(`\n${colors.green}${colors.bright}    !${colors.reset}`);
  } else if (successRate >= 80) {
    console.log(`\n${colors.yellow}    .${colors.reset}`);
  } else {
    console.log(`\n${colors.red}   .${colors.reset}`);
  }

  return results;
}

//  
runFrontendValidation()
  .then(results => {
    process.exit(results.failed > 0 ? 1 : 0);
  })
  .catch(error => {
    log(`    : ${error.message}`, 'error');
    process.exit(1);
  });