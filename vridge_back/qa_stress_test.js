/**
 * K6 Stress Test for VideoPlanet Django Integration
 * 
 * This test gradually increases load to find breaking points
 * and measure system performance under stress.
 * 
 * Installation: 
 *   brew install k6 (macOS)
 *   or download from https://k6.io
 * 
 * Usage:
 *   k6 run qa_stress_test.js
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');
const successRate = new Rate('success');

// Test configuration
export let options = {
    stages: [
        // Warm-up
        { duration: '30s', target: 10 },   // Ramp up to 10 users
        
        // Normal load
        { duration: '1m', target: 50 },    // Ramp up to 50 users
        { duration: '2m', target: 50 },    // Stay at 50 users
        
        // Stress test
        { duration: '1m', target: 100 },   // Ramp up to 100 users
        { duration: '2m', target: 100 },   // Stay at 100 users
        
        // Spike test
        { duration: '30s', target: 200 },  // Spike to 200 users
        { duration: '1m', target: 200 },   // Stay at 200 users
        
        // Recovery
        { duration: '1m', target: 50 },    // Scale down to 50 users
        { duration: '1m', target: 0 },     // Scale down to 0
    ],
    
    thresholds: {
        'http_req_duration': ['p(95)<2000'],  // 95% of requests should be below 2s
        'http_req_duration': ['p(99)<3000'],  // 99% of requests should be below 3s
        'errors': ['rate<0.1'],                // Error rate should be below 10%
        'success': ['rate>0.9'],               // Success rate should be above 90%
        'http_req_failed': ['rate<0.1'],      // HTTP failure rate below 10%
    },
    
    // Extended metrics collection
    ext: {
        loadimpact: {
            projectID: 'videoplanet-django',
            name: 'Django Integration Stress Test',
        },
    },
};

const BASE_URL = __ENV.BASE_URL || 'https://videoplanet.up.railway.app';

// Test scenarios
const scenarios = [
    { name: 'health_check', endpoint: '/health', weight: 40 },
    { name: 'ready_check', endpoint: '/ready', weight: 10 },
    { name: 'api_health', endpoint: '/api/health/', weight: 30 },
    { name: 'api_projects', endpoint: '/api/projects/', weight: 20 },
];

// Helper function to select scenario based on weight
function selectScenario() {
    const totalWeight = scenarios.reduce((sum, s) => sum + s.weight, 0);
    let random = Math.random() * totalWeight;
    
    for (let scenario of scenarios) {
        random -= scenario.weight;
        if (random <= 0) {
            return scenario;
        }
    }
    return scenarios[0];
}

export default function() {
    // Select a scenario based on weight
    const scenario = selectScenario();
    
    // Set up request parameters
    const params = {
        headers: {
            'Accept': 'application/json',
            'User-Agent': 'k6-stress-test/1.0',
        },
        timeout: '10s',
        tags: {
            scenario: scenario.name,
        },
    };
    
    // Add CORS test headers occasionally
    if (Math.random() < 0.1) {  // 10% of requests
        params.headers['Origin'] = 'https://vlanet.net';
    }
    
    // Make the request
    const response = http.get(`${BASE_URL}${scenario.endpoint}`, params);
    
    // Validate response
    const checks = {
        'status is 200 or 401': (r) => r.status === 200 || r.status === 401,
        'response time < 500ms': (r) => r.timings.duration < 500,
        'response time < 1000ms': (r) => r.timings.duration < 1000,
        'response time < 2000ms': (r) => r.timings.duration < 2000,
        'has response body': (r) => r.body && r.body.length > 0,
    };
    
    // Special checks for health endpoints
    if (scenario.name === 'health_check') {
        checks['health check OK'] = (r) => r.status === 200;
    }
    
    if (scenario.name === 'ready_check') {
        checks['Django ready'] = (r) => r.status === 200 || r.status === 503;
    }
    
    // Record results
    const success = check(response, checks);
    successRate.add(success);
    errorRate.add(!success);
    
    // Log errors for debugging
    if (!success || response.status >= 500) {
        console.error(`Error in ${scenario.name}: Status ${response.status}, Duration ${response.timings.duration}ms`);
    }
    
    // Think time between requests (simulate real user behavior)
    sleep(Math.random() * 2 + 1);  // 1-3 seconds
}

// Handle test lifecycle
export function setup() {
    console.log('Starting stress test...');
    console.log(`Target URL: ${BASE_URL}`);
    
    // Verify system is accessible
    const response = http.get(`${BASE_URL}/health`);
    if (response.status !== 200) {
        throw new Error(`System not accessible. Health check returned ${response.status}`);
    }
    
    return { startTime: new Date().toISOString() };
}

export function teardown(data) {
    console.log('Stress test completed.');
    console.log(`Started at: ${data.startTime}`);
    console.log(`Ended at: ${new Date().toISOString()}`);
}

// Custom summary generation
export function handleSummary(data) {
    const summary = {
        timestamp: new Date().toISOString(),
        url: BASE_URL,
        metrics: {},
        thresholds: {},
        scenarios: {},
    };
    
    // Extract key metrics
    if (data.metrics) {
        summary.metrics = {
            requests: {
                total: data.metrics.http_reqs?.values?.count || 0,
                rate: data.metrics.http_reqs?.values?.rate || 0,
            },
            duration: {
                avg: data.metrics.http_req_duration?.values?.avg || 0,
                p95: data.metrics.http_req_duration?.values?.['p(95)'] || 0,
                p99: data.metrics.http_req_duration?.values?.['p(99)'] || 0,
                max: data.metrics.http_req_duration?.values?.max || 0,
            },
            errors: {
                rate: data.metrics.errors?.values?.rate || 0,
                count: data.metrics.http_req_failed?.values?.passes || 0,
            },
            success: {
                rate: data.metrics.success?.values?.rate || 0,
            },
        };
    }
    
    // Check thresholds
    for (let [name, threshold] of Object.entries(options.thresholds)) {
        summary.thresholds[name] = data.metrics[name]?.thresholds || {};
    }
    
    // Generate console output
    console.log('\n' + '='.repeat(60));
    console.log('STRESS TEST SUMMARY');
    console.log('='.repeat(60));
    console.log(`Total Requests: ${summary.metrics.requests.total}`);
    console.log(`Request Rate: ${summary.metrics.requests.rate.toFixed(2)} req/s`);
    console.log(`Average Duration: ${summary.metrics.duration.avg.toFixed(2)}ms`);
    console.log(`P95 Duration: ${summary.metrics.duration.p95.toFixed(2)}ms`);
    console.log(`P99 Duration: ${summary.metrics.duration.p99.toFixed(2)}ms`);
    console.log(`Max Duration: ${summary.metrics.duration.max.toFixed(2)}ms`);
    console.log(`Error Rate: ${(summary.metrics.errors.rate * 100).toFixed(2)}%`);
    console.log(`Success Rate: ${(summary.metrics.success.rate * 100).toFixed(2)}%`);
    
    // Determine overall result
    const passed = Object.values(summary.thresholds).every(t => t.ok !== false);
    
    if (passed) {
        console.log('\n✅ All thresholds passed!');
    } else {
        console.log('\n❌ Some thresholds failed!');
        for (let [name, result] of Object.entries(summary.thresholds)) {
            if (result.ok === false) {
                console.log(`  - ${name}: FAILED`);
            }
        }
    }
    
    console.log('='.repeat(60));
    
    // Save detailed results
    return {
        'qa_stress_test_summary.json': JSON.stringify(summary, null, 2),
        'stdout': textSummary(data, { indent: ' ', enableColors: true }),
    };
}

// Helper for text summary (if k6/summary is available)
function textSummary(data, options) {
    try {
        const { textSummary } = require('https://jslib.k6.io/k6-summary/0.0.1/index.js');
        return textSummary(data, options);
    } catch (e) {
        return JSON.stringify(data, null, 2);
    }
}