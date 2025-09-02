/** @type {import('next').NextConfig} */
const nextConfig = {
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    unoptimized: true,
  },
  async rewrites() {
    return [
      {
        source: '/agent-status',
        destination: 'http://localhost:8000/agent-status',
      },
      {
        source: '/connection-info',
        destination: 'http://localhost:8000/connection-info',
      },
      {
        source: '/connect-obd',
        destination: 'http://localhost:8000/connect-obd',
      },
      {
        source: '/disconnect-obd',
        destination: 'http://localhost:8000/disconnect-obd',
      },
      {
        source: '/diagnose',
        destination: 'http://localhost:8000/diagnose',
      },
    ]
  },
}

export default nextConfig