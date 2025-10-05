# 🚀 AWS Deployment Guide

This guide covers deploying the Bulk Deal Tracker on AWS using multiple approaches.

## 📋 Table of Contents

1. [AWS Lambda + EventBridge (Recommended)](#option-1-aws-lambda--eventbridge)
2. [AWS EC2 + Cron](#option-2-aws-ec2--cron)
3. [AWS ECS Fargate (Advanced)](#option-3-aws-ecs-fargate)

---

## Option 1: AWS Lambda + EventBridge (Recommended)

**Best for**: Serverless, cost-effective, automatic scaling

### Step 1: Prepare Lambda Deployment Package

```bash
# Create a deployment directory
mkdir lambda_deployment
cd lambda_deployment

# Copy your main script
cp ../main.py .
cp ../requirements.txt .

# Install dependencies in the deployment directory
pip install -r requirements.txt -t .

# Create deployment package
zip -r deployment_package.zip .
```

### Step 2: Create Lambda Function

1. **Go to AWS Lambda Console**: https://console.aws.amazon.com/lambda
2. Click **"Create function"**
3. Configure:
   - **Function name**: `bulk-deal-tracker`
   - **Runtime**: Python 3.11
   - **Architecture**: x86_64
   - **Permissions**: Create new role with basic Lambda permissions

4. Click **"Create function"**

### Step 3: Upload Code

```bash
# Upload via AWS CLI (recommended for large packages)
aws lambda update-function-code \
  --function-name bulk-deal-tracker \
  --zip-file fileb://deployment_package.zip
```

Or use the Lambda console:
1. Go to **Code** tab
2. Click **Upload from** → **.zip file**
3. Upload `deployment_package.zip`

### Step 4: Configure Lambda Settings

1. **Memory**: 512 MB (increase if needed)
2. **Timeout**: 10 minutes (600 seconds)
3. **Handler**: `main.lambda_handler`

### Step 5: Add Environment Variables

Go to **Configuration** → **Environment variables** and add:

```
SUPABASE_URL = https://tyibyuwusjpogfknameh.supabase.co
SUPABASE_KEY = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
EMAIL_USER = king.gerald2007@gmail.com
EMAIL_PASSWORD = osms grsv iorx hjan
EMAIL_TO = king.gerald2007@gmail.com
LOG_LEVEL = INFO
```

### Step 6: Modify main.py for Lambda

Add this Lambda handler at the end of `main.py`:

```python
def lambda_handler(event, context):
    """AWS Lambda handler function"""
    import json
    
    try:
        main()
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Automation completed successfully',
                'timestamp': datetime.now().isoformat()
            })
        }
    except Exception as e:
        logger.error(f"Lambda execution failed: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Automation failed',
                'error': str(e)
            })
        }
```

### Step 7: Create EventBridge Rule

1. **Go to Amazon EventBridge**: https://console.aws.amazon.com/events
2. Click **"Create rule"**
3. Configure:
   - **Name**: `daily-bulk-deals-10-10am-ist`
   - **Description**: Triggers bulk deal tracker daily at 10:10 AM IST
   - **Rule type**: Schedule
   - **Schedule pattern**: Cron expression
   - **Cron**: `40 4 * * ? *` (4:40 AM UTC = 10:10 AM IST)

4. **Target**:
   - **Target type**: AWS service
   - **Select target**: Lambda function
   - **Function**: `bulk-deal-tracker`

5. Click **"Create rule"**

### Step 8: Test Lambda Function

```bash
# Test via AWS CLI
aws lambda invoke \
  --function-name bulk-deal-tracker \
  --payload '{}' \
  response.json

# View response
cat response.json
```

Or test in Lambda console:
1. Click **"Test"** tab
2. Create new test event (default template is fine)
3. Click **"Test"**

### Cost Estimate:
- **Lambda**: ~$0.50/month (free tier covers most usage)
- **EventBridge**: Free
- **Total**: ~$0-1/month

---

## Option 2: AWS EC2 + Cron

**Best for**: Traditional server setup, more control

### Step 1: Launch EC2 Instance

1. **Go to EC2 Console**: https://console.aws.amazon.com/ec2
2. Click **"Launch Instance"**
3. Configure:
   - **Name**: `bulk-deal-tracker-server`
   - **AMI**: Ubuntu Server 22.04 LTS (Free tier eligible)
   - **Instance type**: t2.micro (free tier)
   - **Key pair**: Create or select existing
   - **Security group**: Allow SSH (port 22)

4. Click **"Launch instance"**

### Step 2: Connect to EC2

```bash
# SSH into your instance
ssh -i your-key.pem ubuntu@your-ec2-public-ip

# Update system
sudo apt update && sudo apt upgrade -y
```

### Step 3: Install Python and Dependencies

```bash
# Install Python 3.11
sudo apt install python3.11 python3-pip -y

# Install Git
sudo apt install git -y

# Clone repository
git clone https://github.com/kinggerald2007-png/bulk-deal-tracker-cloud.git
cd bulk-deal-tracker-cloud

# Install Python dependencies
pip3 install -r requirements.txt
```

### Step 4: Create Environment Variables

```bash
# Create .env file
nano .env

# Add your credentials (paste and save):
SUPABASE_URL=https://tyibyuwusjpogfknameh.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
EMAIL_USER=king.gerald2007@gmail.com
EMAIL_PASSWORD=osms grsv iorx hjan
EMAIL_TO=king.gerald2007@gmail.com
LOG_LEVEL=INFO
```

Update `main.py` to load from .env:

```python
from dotenv import load_dotenv
load_dotenv()  # Add this at the top of Config class
```

### Step 5: Test Execution

```bash
# Run manually to test
python3 main.py

# Check logs
cat deals_automation.log
```

### Step 6: Set Up Cron Job

```bash
# Edit crontab
crontab -e

# Add this line for 10:10 AM IST daily:
10 10 * * * cd /home/ubuntu/bulk-deal-tracker-cloud && /usr/bin/python3 main.py >> /var/log/deals_automation.log 2>&1

# Save and exit (Ctrl+X, then Y, then Enter)

# Verify cron job
crontab -l
```

### Step 7: Set Up Log Rotation (Optional)

```bash
# Create logrotate config
sudo nano /etc/logrotate.d/deals-tracker

# Add:
/var/log/deals_automation.log {
    daily
    rotate 30
    compress
    missingok
    notifempty
}

# Save and exit
```

### Step 8: Keep Repository Updated

```bash
# Create update script
nano ~/update_tracker.sh

# Add:
#!/bin/bash
cd /home/ubuntu/bulk-deal-tracker-cloud
git pull origin main
pip3 install -r requirements.txt

# Make executable
chmod +x ~/update_tracker.sh

# Run weekly via cron:
0 2 * * 0 /home/ubuntu/update_tracker.sh
```

### Cost Estimate:
- **EC2 t2.micro**: Free tier (750 hrs/month) or ~$8/month
- **EBS Storage**: ~$1/month (8 GB)
- **Total**: ~$0-9/month

---

## Option 3: AWS ECS Fargate (Advanced)

**Best for**: Containerized deployment, better scaling

### Step 1: Create Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY main.py .

# Set environment variables (will be overridden by ECS)
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["python", "main.py"]
```

### Step 2: Build and Push to ECR

```bash
# Create ECR repository
aws ecr create-repository --repository-name bulk-deal-tracker

# Get login command
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Build image
docker build -t bulk-deal-tracker .

# Tag image
docker tag bulk-deal-tracker:latest YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/bulk-deal-tracker:latest

# Push to ECR
docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/bulk-deal-tracker:latest
```

### Step 3: Create ECS Task Definition

1. Go to **ECS Console** → **Task Definitions**
2. Click **"Create new task definition"**
3. Configure:
   - **Family**: `bulk-deal-tracker`
   - **Launch type**: Fargate
   - **CPU**: 0.25 vCPU
   - **Memory**: 0.5 GB
   - **Container**:
     - **Image**: Your ECR image URI
     - **Environment variables**: Add all credentials

### Step 4: Create ECS Cluster

```bash
# Create cluster via CLI
aws ecs create-cluster --cluster-name bulk-deal-tracker-cluster
```

### Step 5: Schedule with EventBridge

1. Create EventBridge rule (same as Lambda)
2. Target: ECS task
3. Select your cluster and task definition

### Cost Estimate:
- **Fargate**: ~$5-10/month
- **ECR Storage**: ~$0.10/month
- **Total**: ~$5-11/month

---

## 🔒 Security Best Practices

### 1. Use AWS Secrets Manager (Recommended)

Instead of environment variables, store secrets securely:

```python
import boto3
from botocore.exceptions import ClientError

def get_secret(secret_name):
    client = boto3.client('secretsmanager', region_name='us-east-1')
    
    try:
        response = client.get_secret_value(SecretId=secret_name)
        return json.loads(response['SecretString'])
    except ClientError as e:
        logger.error(f"Error retrieving secret: {e}")
        raise

# Usage in Config class:
secrets = get_secret('bulk-deal-tracker-secrets')
SUPABASE_KEY = secrets['supabase_key']
EMAIL_PASSWORD = secrets['email_password']
```

### 2. Use IAM Roles

For EC2/Lambda, attach IAM roles with minimal permissions:
- S3 access (if storing files)
- CloudWatch Logs access
- Secrets Manager access

### 3. Enable VPC (Optional)

For EC2/Fargate, deploy in private subnet with NAT Gateway for outbound access.

---

## 📊 Monitoring & Alerts

### CloudWatch Logs

Lambda and ECS automatically send logs to CloudWatch. For EC2:

```bash
# Install CloudWatch agent
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i amazon-cloudwatch-agent.deb

# Configure agent to send logs
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
  -a fetch-config \
  -m ec2 \
  -s \
  -c file:/opt/aws/amazon-cloudwatch-agent/etc/config.json
```

### SNS Alerts

Create SNS topic for failure notifications:

```bash
# Create topic
aws sns create-topic --name bulk-deal-tracker-alerts

# Subscribe email
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:YOUR_ACCOUNT:bulk-deal-tracker-alerts \
  --protocol email \
  --notification-endpoint king.gerald2007@gmail.com
```

---

## 🔄 CI/CD Pipeline (Bonus)

### Using GitHub Actions to Deploy to AWS

Create `.github/workflows/deploy_aws.yml`:

```yaml
name: Deploy to AWS Lambda

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v4
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: us-east-1
    
    - name: Deploy to Lambda
      run: |
        pip install -r requirements.txt -t .
        zip -r deployment.zip .
        aws lambda update-function-code \
          --function-name bulk-deal-tracker \
          --zip-file fileb://deployment.zip
```

---

## 📞 Support

For AWS-specific issues:
- Check CloudWatch Logs for errors
- Review IAM permissions
- Verify network connectivity (Security Groups, NACLs)
- Test locally before deploying

---

**Choose the deployment method that best fits your needs!**

| Method | Cost | Complexity | Scalability | Maintenance |
|--------|------|------------|-------------|-------------|
| Lambda | $ | Low | High | Low |
| EC2 | $$ | Medium | Medium | Medium |
| ECS | $$$ | High | High | Low |

**Recommendation**: Start with **Lambda + EventBridge** for simplicity and cost-effectiveness.