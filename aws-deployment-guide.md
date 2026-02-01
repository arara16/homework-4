# AWS Elastic Beanstalk Deployment Guide

## Step 1: Create AWS Account
1. Go to: https://aws.amazon.com/education/awseducate/
2. Sign up with your student email
3. Verify your student status

## Step 2: Install AWS CLI
```bash
# macOS
brew install awscli

# Configure
aws configure
```

## Step 3: Install EB CLI
```bash
pip install awsebcli
```

## Step 4: Deploy to AWS
```bash
# Initialize EB application
eb init homework-4 \
  --platform "Docker running on 64bit Amazon Linux 2"

# Create production environment
eb create production \
  --instance-type t3.micro \
  --min-instances 1 \
  --max-instances 3

# Deploy
eb deploy
```

## Your AWS URLs:
- **Application**: http://homework-4-production.eba-xxxxx.elasticbeanstalk.com
- **Health Check**: http://homework-4-production.eba-xxxxx.elasticbeanstalk.com/api/health
