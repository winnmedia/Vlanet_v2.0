/** @type {import('next').NextConfig} */
const nextConfig = {
  eslint: {
    ignoreDuringBuilds: true,
  },
  
  typescript: {
    ignoreBuildErrors: true,
  },
  
  experimental: {
    optimizePackageImports: ['lucide-react'],
    // Disable Partial Pre-rendering
    ppr: false,
  },
  
  images: {
    domains: [
      'localhost',
      'videoplanet.up.railway.app',
    ],
    formats: ['image/webp', 'image/avif'],
  },

  env: {
    CUSTOM_KEY: process.env.CUSTOM_KEY,
  },

  // Performance optimizations
  compiler: {
    removeConsole: process.env.NODE_ENV === 'production',
  },

  // Security headers
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin',
          },
        ],
      },
    ];
  },

  // Redirects for SEO and UX
  async redirects() {
    return [
      {
        source: '/home',
        destination: '/',
        permanent: true,
      },
    ];
  },
  
  // Bundle analysis
  webpack: (config, { buildId, dev, isServer, defaultLoaders, webpack }) => {
    // Analyze bundle in production
    if (!dev && !isServer && process.env.ANALYZE === 'true') {
      const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer');
      config.plugins.push(
        new BundleAnalyzerPlugin({
          analyzerMode: 'static',
          openAnalyzer: false,
        })
      );
    }

    return config;
  },
};

export default nextConfig;