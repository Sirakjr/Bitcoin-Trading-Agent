# 🚀 Deployment Guide

This guide covers deploying the Bitcoin Trading Agent to both local Docker and cloud platforms.

## 🐳 Local Docker Deployment

### Prerequisites
- Docker installed
- Docker Compose installed

### Quick Start
```bash
# 1. Copy environment file
cp env.example .env

# 2. Edit .env with your configuration
nano .env

# 3. Build and run
docker-compose up -d

# 4. View logs
docker-compose logs -f bitcoin-trading-agent
```

### Manual Docker Commands
```bash
# Build image
docker build -t bitcoin-trading-agent .

# Run container
docker run -d \
    --name bitcoin-trading-agent \
    --restart unless-stopped \
    --env-file .env \
    -v "$(pwd)/data:/app/data" \
    bitcoin-trading-agent

# View logs
docker logs -f bitcoin-trading-agent
```

## ☁️ AWS Deployment

## ☁️ AWS Deployment

### 1. EC2 Instance
```bash
# Launch Ubuntu 22.04 LTS instance
# Instance type: t3.micro (free tier) or t3.small
# Security group: Allow SSH (port 22)
```

### 2. Install Docker
```bash
# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt install docker-compose -y

# Add user to docker group
usermod -aG docker $USER
```

### 3. Deploy Application
```bash
# Clone repository
git clone <your-repo-url>
cd bitcoin-trading-agent

# Copy environment file
cp env.example .env

# Edit configuration
nano .env

# Build and run
docker-compose up -d

# Check status
docker-compose ps
```

### 4. Set Up Monitoring
```bash
# View logs
docker-compose logs -f bitcoin-trading-agent

# Check container health
docker ps

# Monitor system resources
htop
```

## 🔧 Environment Configuration

### Required Variables
```env
# Trading Configuration
BUDGET_USD=10000
DCA_AMOUNT_USD=500
DCA_DROP_PERCENT=3.0
MAX_DRAWDOWN_PCT=25.0
TRADING_MODE=hybrid

# Notifications (optional but recommended)
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
GMAIL_USER=your_email@gmail.com
GMAIL_APP_PASSWORD=your_app_password
```

### Optional Variables
```env
# Google Sheets integration
GOOGLE_SHEET_ID=your_sheet_id
GOOGLE_SERVICE_ACCOUNT_JSON_PATH=path/to/service_account.json

# Advanced configuration
DCA_MIN_INTERVAL_HOURS=24
SWING_AMOUNT_USD=500
ENVIRONMENT=production
LOG_LEVEL=INFO
```

## 📊 Monitoring & Maintenance

### Health Checks
```bash
# Container status
docker ps

# Application logs
docker logs bitcoin-trading-agent

# System resources
docker stats bitcoin-trading-agent
```

### Updates
```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose down
docker-compose up -d --build
```

### Backup
```bash
# Backup data directory
tar -czf backup-$(date +%Y%m%d).tar.gz data/

# Backup environment
cp .env backup-env-$(date +%Y%m%d)
```

## 🚨 Troubleshooting

### Common Issues
1. **Container won't start**: Check .env file and logs
2. **Permission errors**: Ensure data directory is writable
3. **Network issues**: Check firewall settings
4. **Memory issues**: Monitor system resources

### Debug Commands
```bash
# Check container logs
docker logs bitcoin-trading-agent

# Enter container
docker exec -it bitcoin-trading-agent bash

# Check environment
docker exec bitcoin-trading-agent env

# Restart container
docker restart bitcoin-trading-agent
```

## 🔒 Security Considerations

1. **Environment Variables**: Never commit .env files
2. **Firewall**: Only open necessary ports
3. **Updates**: Keep system and Docker updated
4. **Monitoring**: Set up alerts for system issues
5. **Backups**: Regular data backups

## 📈 Scaling Considerations

### Vertical Scaling
- Increase droplet/instance size
- Add more memory/CPU

### Horizontal Scaling
- Multiple trading agents
- Load balancer for high availability
- Redis for job queuing

## 🎯 Next Steps

1. **Test locally** with Docker Compose
2. **Deploy to AWS** for production
3. **Set up monitoring** and alerts
4. **Configure backups** and maintenance
5. **Monitor performance** and optimize

---

**Status**: Ready for deployment! 🚀
