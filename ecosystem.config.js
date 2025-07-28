module.exports = {
  apps: [
    {
      name: 'command-server',
      script: 'command-server/server.js',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      env: {
        NODE_ENV: 'production',
        PORT: 10001
      },
      env_development: {
        NODE_ENV: 'development',
        PORT: 10001
      }
    },
    {
      name: 'web-interface',
      script: 'web-interface/server.js',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '512M',
      env: {
        NODE_ENV: 'production',
        PORT: 3000
      },
      env_development: {
        NODE_ENV: 'development',
        PORT: 3000
      }
    },
    {
      name: 'telegram-bot',
      script: 'telegram-bot/bot.py',
      interpreter: 'python3',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '256M',
      env: {
        PYTHONPATH: './telegram-bot'
      }
    }
  ],

  deploy: {
    production: {
      user: 'node',
      host: 'localhost',
      ref: 'origin/main',
      repo: 'https://github.com/saud552/remote-control-system.git',
      path: '/var/www/production',
      'post-deploy': 'npm install && pm2 reload ecosystem.config.js --env production'
    }
  }
};