#!/usr/bin/env node

import fs from 'fs';
import path from 'path';
import { execSync } from 'child_process';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

class DeploymentValidator {
  constructor() {
    this.errors = [];
    this.warnings = [];
    this.projectRoot = path.resolve(__dirname, '..');
  }

  log(message, type = 'info') {
    const prefix = {
      error: '❌',
      warning: '⚠️',
      success: '✅',
      info: 'ℹ️'
    }[type] || 'ℹ️';
    
    console.log(`${prefix} ${message}`);
  }

  validateVercelConfig() {
    this.log('Validating vercel.json...');
    const vercelConfigPath = path.join(this.projectRoot, 'vercel.json');
    
    if (!fs.existsSync(vercelConfigPath)) {
      this.warnings.push('vercel.json not found - using default settings');
      return;
    }

    try {
      const config = JSON.parse(fs.readFileSync(vercelConfigPath, 'utf8'));
      
      // Node.js 런타임 버전 검증
      if (config.functions?.runtime) {
        const validRuntimes = ['nodejs18.x', 'nodejs20.x'];
        if (!validRuntimes.includes(config.functions.runtime)) {
          this.errors.push(`Invalid runtime: ${config.functions.runtime}. Use nodejs18.x or nodejs20.x`);
        }
      }

      // 리다이렉트 규칙 검증
      if (config.redirects) {
        config.redirects.forEach((redirect, index) => {
          if (!redirect.source || !redirect.destination) {
            this.errors.push(`Invalid redirect at index ${index}`);
          }
        });
      }

      // 헤더 규칙 검증
      if (config.headers) {
        config.headers.forEach((header, index) => {
          if (!header.source || !header.headers) {
            this.errors.push(`Invalid header configuration at index ${index}`);
          }
        });
      }

      // 함수 설정 검증
      if (config.functions) {
        // maxDuration 검증 (Hobby: 10s, Pro: 60s, Enterprise: 900s)
        if (config.functions.maxDuration && config.functions.maxDuration > 10) {
          this.warnings.push(`maxDuration ${config.functions.maxDuration}s requires Pro plan or higher`);
        }
      }

      this.log('vercel.json validation complete', 'success');
    } catch (error) {
      this.errors.push(`Failed to parse vercel.json: ${error.message}`);
    }
  }

  validateEnvironmentVariables() {
    this.log('Checking environment variables...');
    
    const envExamplePath = path.join(this.projectRoot, '.env.example');
    const envProductionPath = path.join(this.projectRoot, '.env.production');
    
    if (!fs.existsSync(envExamplePath)) {
      this.warnings.push('.env.example not found');
      return;
    }

    const requiredVars = fs.readFileSync(envExamplePath, 'utf8')
      .split('\n')
      .filter(line => line && !line.startsWith('#'))
      .map(line => line.split('=')[0].trim())
      .filter(Boolean);

    // 프로덕션 환경변수 확인
    if (fs.existsSync(envProductionPath)) {
      const productionVars = fs.readFileSync(envProductionPath, 'utf8')
        .split('\n')
        .filter(line => line && !line.startsWith('#'))
        .map(line => line.split('=')[0].trim())
        .filter(Boolean);

      const missingVars = requiredVars.filter(v => !productionVars.includes(v));
      
      if (missingVars.length > 0) {
        this.warnings.push(`Missing environment variables in .env.production: ${missingVars.join(', ')}`);
      }
    }

    this.log('Environment variables check complete', 'success');
  }

  validatePackageJson() {
    this.log('Validating package.json...');
    
    const packageJsonPath = path.join(this.projectRoot, 'package.json');
    const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));

    // Next.js 버전 확인
    const nextVersion = packageJson.dependencies?.next;
    if (nextVersion) {
      const majorVersion = parseInt(nextVersion.match(/\d+/)?.[0] || '0');
      if (majorVersion < 13) {
        this.warnings.push(`Next.js version ${nextVersion} is outdated. Consider upgrading to 13+ for better Vercel support`);
      }
    }

    // 필수 스크립트 확인
    const requiredScripts = ['build', 'start'];
    const missingScripts = requiredScripts.filter(script => !packageJson.scripts?.[script]);
    
    if (missingScripts.length > 0) {
      this.errors.push(`Missing required scripts: ${missingScripts.join(', ')}`);
    }

    // Node 엔진 버전 확인
    if (packageJson.engines?.node) {
      const nodeVersion = packageJson.engines.node;
      if (!nodeVersion.includes('18') && !nodeVersion.includes('20')) {
        this.warnings.push(`Node version ${nodeVersion} specified. Vercel works best with Node 18 or 20`);
      }
    }

    this.log('package.json validation complete', 'success');
  }

  checkBuildErrors() {
    this.log('Running build test...');
    
    try {
      execSync('npm run build', { 
        cwd: this.projectRoot,
        stdio: 'pipe'
      });
      this.log('Build successful', 'success');
    } catch (error) {
      this.errors.push('Build failed. Check build errors above');
      
      // 일반적인 Next.js 15 오류 패턴 검사
      const output = error.stdout?.toString() || error.stderr?.toString() || '';
      
      if (output.includes('currentUser is not defined')) {
        this.errors.push('ReferenceError: Make sure all variables are properly defined in server/client components');
      }
      
      if (output.includes('use client')) {
        this.errors.push('Missing "use client" directive in client components');
      }
      
      if (output.includes('Module not found')) {
        this.errors.push('Missing dependencies. Run "npm install" to fix');
      }
    }
  }

  checkTypeErrors() {
    this.log('Running type check...');
    
    try {
      execSync('npx tsc --noEmit', { 
        cwd: this.projectRoot,
        stdio: 'pipe'
      });
      this.log('No TypeScript errors found', 'success');
    } catch (error) {
      this.warnings.push('TypeScript errors found. Fix them for better stability');
    }
  }

  checkLintErrors() {
    this.log('Running lint check...');
    
    try {
      execSync('npm run lint', { 
        cwd: this.projectRoot,
        stdio: 'pipe'
      });
      this.log('No lint errors found', 'success');
    } catch (error) {
      this.warnings.push('Lint errors found. Consider fixing them');
    }
  }

  validateNextConfig() {
    this.log('Validating next.config.js...');
    
    const nextConfigPath = path.join(this.projectRoot, 'next.config.js');
    
    if (!fs.existsSync(nextConfigPath)) {
      this.warnings.push('next.config.js not found - using default configuration');
      return;
    }

    const configContent = fs.readFileSync(nextConfigPath, 'utf8');
    
    // 위험한 설정 패턴 검사
    if (configContent.includes('experimental:')) {
      this.warnings.push('Experimental features detected in next.config.js - may cause instability');
    }
    
    if (configContent.includes('serverActions: true') && !configContent.includes('use server')) {
      this.warnings.push('Server Actions enabled but no "use server" directives found');
    }

    this.log('next.config.js validation complete', 'success');
  }

  checkCommonIssues() {
    this.log('Checking for common issues...');
    
    // app 디렉토리 구조 확인
    const appDir = path.join(this.projectRoot, 'app');
    const srcAppDir = path.join(this.projectRoot, 'src/app');
    const pagesDir = path.join(this.projectRoot, 'pages');
    const srcPagesDir = path.join(this.projectRoot, 'src/pages');
    
    const hasAppDir = fs.existsSync(appDir) || fs.existsSync(srcAppDir);
    const hasPagesDir = fs.existsSync(pagesDir) || fs.existsSync(srcPagesDir);
    
    if (hasAppDir && hasPagesDir) {
      this.warnings.push('Both app/ and pages/ directories found. This may cause routing conflicts');
    }

    // public 디렉토리 확인
    const publicDir = path.join(this.projectRoot, 'public');
    if (!fs.existsSync(publicDir)) {
      this.warnings.push('public/ directory not found');
    }

    // .vercelignore 확인
    const vercelIgnorePath = path.join(this.projectRoot, '.vercelignore');
    if (!fs.existsSync(vercelIgnorePath)) {
      this.warnings.push('.vercelignore not found - all files will be uploaded to Vercel');
    }

    this.log('Common issues check complete', 'success');
  }

  generateReport() {
    console.log('\n' + '='.repeat(50));
    console.log('DEPLOYMENT VALIDATION REPORT');
    console.log('='.repeat(50) + '\n');

    if (this.errors.length === 0 && this.warnings.length === 0) {
      this.log('All checks passed! Ready for deployment', 'success');
      return true;
    }

    if (this.errors.length > 0) {
      console.log('\n❌ ERRORS (Must fix before deployment):');
      this.errors.forEach(error => console.log(`  - ${error}`));
    }

    if (this.warnings.length > 0) {
      console.log('\n⚠️  WARNINGS (Should review):');
      this.warnings.forEach(warning => console.log(`  - ${warning}`));
    }

    console.log('\n' + '='.repeat(50));
    
    if (this.errors.length > 0) {
      this.log('Deployment validation FAILED', 'error');
      return false;
    } else {
      this.log('Deployment validation PASSED with warnings', 'warning');
      return true;
    }
  }

  async run() {
    console.log('🚀 Starting Vercel deployment validation...\n');
    
    this.validateVercelConfig();
    this.validateEnvironmentVariables();
    this.validatePackageJson();
    this.validateNextConfig();
    this.checkCommonIssues();
    
    // 빌드 테스트는 시간이 걸리므로 선택적으로 실행
    if (process.argv.includes('--with-build')) {
      this.checkBuildErrors();
    } else {
      this.log('Skipping build test (use --with-build to include)', 'info');
    }
    
    if (process.argv.includes('--strict')) {
      this.checkTypeErrors();
      this.checkLintErrors();
    }
    
    const success = this.generateReport();
    
    if (!success && !process.argv.includes('--force')) {
      process.exit(1);
    }
  }
}

// 실행
const validator = new DeploymentValidator();
validator.run().catch(error => {
  console.error('Validation failed:', error);
  process.exit(1);
});