# AWS Elastic Beanstalk Deployment Guide

## Prerequisites
1. AWS Account (free tier eligible)
2. AWS CLI installed
3. EB CLI installed

## Installation

### 1. Install AWS CLI
```bash
# Windows (using pip)
pip install awscli

# Configure AWS credentials
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Enter region: eu-west-2 (or your preferred region)
# Enter output format: json
```

### 2. Install EB CLI
```bash
pip install awsebcli
```

## Deployment Steps

### 1. Navigate to webapp directory
```bash
cd scorps_fulltime_agent/webapp
```

### 2. Initialize Elastic Beanstalk
```bash
eb init -p python-3.9 scorpions-webapp --region eu-west-2
```

When prompted:
- Select your AWS credentials profile (or use default)
- Do you want to set up SSH? **Yes** (recommended for debugging)

### 3. Create Environment (Free Tier)
```bash
eb create scorpions-env --single --instance-type t2.micro
```

This will:
- Create a t2.micro instance (free tier)
- Use single instance mode (no load balancer = cheaper)
- Deploy your application
- Takes about 5 minutes

### 4. Open Your App
```bash
eb open
```

This opens your deployed app in the browser!

## Useful Commands

### Deploy Updates
```bash
eb deploy
```

### Check Status
```bash
eb status
```

### View Logs
```bash
eb logs
```

### SSH into Instance
```bash
eb ssh
```

### Terminate Environment (Stop Costs)
```bash
eb terminate scorpions-env
```

## Cost Management

### Free Tier (First 12 Months)
- 750 hours/month of t2.micro = FREE
- 5GB storage = FREE
- Your app runs 24/7 for FREE

### After Free Tier
- ~$9-10/month for 24/7 availability
- Or terminate when not needed (football off-season)

## Troubleshooting

### If deployment fails:
```bash
# Check logs
eb logs

# SSH in to debug
eb ssh
```

### If app doesn't start:
- Check that all dependencies are in requirements.txt
- Verify Python version matches (3.9)
- Check logs: `eb logs`

## Environment Variables

To add environment variables:
```bash
eb setenv FLASK_ENV=production
```

## Custom Domain (Optional)

1. Go to AWS Console > Elastic Beanstalk
2. Click your environment
3. Go to Configuration > Load Balancer (if using one)
4. Add your domain in Route 53

## Monitoring

View your app metrics:
```bash
eb console
```

This opens the AWS Console where you can see:
- Request counts
- Response times
- Error rates
- Instance health

## Support

If you need help:
1. Check logs: `eb logs`
2. Check AWS Console for detailed errors
3. Verify all files are committed to git (EB deploys from git)
