#!/usr/bin/env node

const https = require('https');
const fs = require('fs');
const path = require('path');

class DeploymentMonitor {
  constructor(config = {}) {
    this.projectId = config.projectId || process.env.VERCEL_PROJECT_ID;
    this.token = config.token || process.env.VERCEL_TOKEN;
    this.webhookUrl = config.webhookUrl || process.env.SLACK_WEBHOOK_URL;
    this.logFile = path.join(__dirname, '..', 'deployment-logs.json');
    this.metrics = {
      totalDeployments: 0,
      successfulDeployments: 0,
      failedDeployments: 0,
      averageBuildTime: 0,
      lastDeployment: null,
      commonErrors: {}
    };
    
    this.loadMetrics();
  }

  loadMetrics() {
    if (fs.existsSync(this.logFile)) {
      try {
        this.metrics = JSON.parse(fs.readFileSync(this.logFile, 'utf8'));
      } catch (error) {
        console.error('Failed to load metrics:', error);
      }
    }
  }

  saveMetrics() {
    fs.writeFileSync(this.logFile, JSON.stringify(this.metrics, null, 2));
  }

  async fetchDeployments() {
    return new Promise((resolve, reject) => {
      const options = {
        hostname: 'api.vercel.com',
        path: `/v6/deployments?projectId=${this.projectId}&limit=10`,
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${this.token}`,
          'Content-Type': 'application/json'
        }
      };

      https.request(options, (res) => {
        let data = '';
        res.on('data', chunk => data += chunk);
        res.on('end', () => {
          try {
            resolve(JSON.parse(data));
          } catch (error) {
            reject(error);
          }
        });
      }).on('error', reject).end();
    });
  }

  analyzeDeployment(deployment) {
    const analysis = {
      id: deployment.id,
      url: deployment.url,
      state: deployment.state,
      created: new Date(deployment.created),
      building: deployment.building,
      error: deployment.error,
      buildTime: deployment.building ? 
        (Date.now() - deployment.created) / 1000 : 
        deployment.buildingAt ? 
          (deployment.ready - deployment.buildingAt) / 1000 : 
          null
    };

    //   
    this.metrics.totalDeployments++;
    
    if (deployment.state === 'READY') {
      this.metrics.successfulDeployments++;
    } else if (deployment.state === 'ERROR' || deployment.state === 'CANCELED') {
      this.metrics.failedDeployments++;
      
      //  
      if (deployment.error) {
        const errorType = this.categorizeError(deployment.error);
        this.metrics.commonErrors[errorType] = 
          (this.metrics.commonErrors[errorType] || 0) + 1;
      }
    }

    //    
    if (analysis.buildTime) {
      const prevAvg = this.metrics.averageBuildTime || 0;
      const prevCount = this.metrics.successfulDeployments - 1;
      this.metrics.averageBuildTime = 
        (prevAvg * prevCount + analysis.buildTime) / this.metrics.successfulDeployments;
    }

    this.metrics.lastDeployment = analysis;
    
    return analysis;
  }

  categorizeError(error) {
    const errorMessage = error.message || error.toString();
    
    if (errorMessage.includes('currentUser is not defined')) {
      return 'UNDEFINED_VARIABLE';
    } else if (errorMessage.includes('Module not found')) {
      return 'MODULE_NOT_FOUND';
    } else if (errorMessage.includes('use client')) {
      return 'CLIENT_DIRECTIVE_MISSING';
    } else if (errorMessage.includes('Function Runtimes')) {
      return 'INVALID_RUNTIME';
    } else if (errorMessage.includes('Build failed')) {
      return 'BUILD_FAILED';
    } else if (errorMessage.includes('timeout')) {
      return 'TIMEOUT';
    } else {
      return 'OTHER';
    }
  }

  async sendNotification(message, type = 'info') {
    if (!this.webhookUrl) {
      console.log(`[${type.toUpperCase()}] ${message}`);
      return;
    }

    const emoji = {
      error: '',
      warning: '',
      success: '',
      info: 'ℹ'
    }[type] || 'ℹ';

    const payload = {
      text: `${emoji} Vercel Deployment Monitor`,
      blocks: [
        {
          type: 'section',
          text: {
            type: 'mrkdwn',
            text: message
          }
        }
      ]
    };

    // Slack webhook 
    try {
      await this.sendWebhook(payload);
    } catch (error) {
      console.error('Failed to send notification:', error);
    }
  }

  async sendWebhook(payload) {
    return new Promise((resolve, reject) => {
      const url = new URL(this.webhookUrl);
      const options = {
        hostname: url.hostname,
        path: url.pathname,
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      };

      const req = https.request(options, (res) => {
        res.on('data', () => {});
        res.on('end', resolve);
      });

      req.on('error', reject);
      req.write(JSON.stringify(payload));
      req.end();
    });
  }

  generateReport() {
    const successRate = this.metrics.totalDeployments > 0 ?
      (this.metrics.successfulDeployments / this.metrics.totalDeployments * 100).toFixed(2) :
      0;

    let report = ` *Deployment Statistics*\n`;
    report += `• Total Deployments: ${this.metrics.totalDeployments}\n`;
    report += `• Success Rate: ${successRate}%\n`;
    report += `• Average Build Time: ${this.metrics.averageBuildTime.toFixed(2)}s\n`;
    
    if (Object.keys(this.metrics.commonErrors).length > 0) {
      report += `\n*Common Errors:*\n`;
      for (const [error, count] of Object.entries(this.metrics.commonErrors)) {
        report += `• ${error}: ${count} occurrences\n`;
      }
    }

    if (this.metrics.lastDeployment) {
      const last = this.metrics.lastDeployment;
      report += `\n*Last Deployment:*\n`;
      report += `• Status: ${last.state}\n`;
      report += `• Time: ${last.created}\n`;
      report += `• URL: https://${last.url}\n`;
    }

    return report;
  }

  async checkHealth(url) {
    return new Promise((resolve) => {
      https.get(url, (res) => {
        resolve({
          statusCode: res.statusCode,
          healthy: res.statusCode >= 200 && res.statusCode < 400
        });
      }).on('error', (error) => {
        resolve({
          statusCode: 0,
          healthy: false,
          error: error.message
        });
      });
    });
  }

  async monitor() {
    console.log(' Starting deployment monitoring...');
    
    try {
      const response = await this.fetchDeployments();
      const deployments = response.deployments || [];
      
      for (const deployment of deployments) {
        const analysis = this.analyzeDeployment(deployment);
        
        //   
        if (deployment.state === 'ERROR') {
          await this.sendNotification(
            ` Deployment failed!\n` +
            `ID: ${deployment.id}\n` +
            `Error: ${deployment.error?.message || 'Unknown error'}\n` +
            `Time: ${new Date(deployment.created).toISOString()}`,
            'error'
          );
        }
        
        //   
        if (deployment.state === 'READY' && deployment.url) {
          const health = await this.checkHealth(`https://${deployment.url}`);
          
          if (!health.healthy) {
            await this.sendNotification(
              ` Deployment succeeded but site is not responding properly!\n` +
              `URL: https://${deployment.url}\n` +
              `Status Code: ${health.statusCode}\n` +
              `Error: ${health.error || 'None'}`,
              'warning'
            );
          }
        }
      }
      
      //  
      this.saveMetrics();
      
      //  
      if (this.metrics.totalDeployments % 10 === 0 && this.metrics.totalDeployments > 0) {
        await this.sendNotification(this.generateReport(), 'info');
      }
      
      //    
      const successRate = this.metrics.successfulDeployments / this.metrics.totalDeployments;
      if (successRate < 0.8 && this.metrics.totalDeployments > 5) {
        await this.sendNotification(
          ` Low deployment success rate: ${(successRate * 100).toFixed(2)}%\n` +
          `Consider reviewing common errors and deployment configuration.`,
          'warning'
        );
      }
      
    } catch (error) {
      console.error('Monitoring error:', error);
      await this.sendNotification(
        ` Monitoring system error: ${error.message}`,
        'error'
      );
    }
  }

  async runContinuous(interval = 300000) { // 5
    await this.monitor();
    setInterval(() => this.monitor(), interval);
  }

  printReport() {
    console.log('\n' + '='.repeat(50));
    console.log('DEPLOYMENT METRICS REPORT');
    console.log('='.repeat(50));
    console.log(this.generateReport().replace(/\*/g, '').replace(/•/g, '-'));
    console.log('='.repeat(50) + '\n');
  }
}

// CLI 
if (require.main === module) {
  const monitor = new DeploymentMonitor();
  
  const command = process.argv[2];
  
  switch (command) {
    case 'watch':
      monitor.runContinuous();
      break;
    case 'report':
      monitor.printReport();
      break;
    case 'check':
    default:
      monitor.monitor().then(() => {
        monitor.printReport();
      });
  }
}

module.exports = DeploymentMonitor;