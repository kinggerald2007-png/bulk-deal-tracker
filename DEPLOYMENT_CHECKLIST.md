# ✅ Deployment Checklist

Use this checklist to deploy your Bulk Deal Tracker in the correct order.

---

## 🎯 Pre-Deployment (Before Starting)

- [ ] GitHub account ready
- [ ] Repository created: https://github.com/kinggerald2007-png/bulk-deal-tracker-cloud
- [ ] Supabase account created
- [ ] Gmail account accessible (king.gerald2007@gmail.com)
- [ ] Gmail 2FA enabled
- [ ] Gmail App Password generated

---

## 📦 Step 1: Repository Setup (5 minutes)

### Create/Update GitHub Repository

- [ ] Go to https://github.com/kinggerald2007-png/bulk-deal-tracker-cloud
- [ ] If not exists, create new repository (public)
- [ ] Clone repository locally:
  ```bash
  git clone https://github.com/kinggerald2007-png/bulk-deal-tracker-cloud.git
  cd bulk-deal-tracker-cloud
  ```

### Add All Project Files

- [ ] Copy `main.py` to repository
- [ ] Copy `requirements.txt` to repository
- [ ] Copy `supabase_schema.sql` to repository
- [ ] Copy `test_automation.py` to repository
- [ ] Copy `README.md` to repository
- [ ] Copy `QUICKSTART.md` to repository
- [ ] Copy `deploy_aws.md` to repository
- [ ] Copy `PROJECT_SUMMARY.md` to repository
- [ ] Copy `DEPLOYMENT_CHECKLIST.md` (this file)
- [ ] Create `.env.example` file
- [ ] Create `.github/workflows/` directory
- [ ] Copy `daily_deals_workflow.yml` to `.github/workflows/`

### Create .gitignore File

- [ ] Create `.gitignore` with this content:
  ```
  # Environment variables
  .env
  
  # Python
  __pycache__/
  *.py[cod]
  *$py.class
  *.so
  .Python
  venv/
  env/
  
  # CSV files (optional - remove if you want to commit them)
  *.csv
  
  # Logs
  *.log
  
  # IDE
  .vscode/
  .idea/
  *.swp
  *.swo
  
  # OS
  .DS_Store
  Thumbs.db
  ```

### Commit and Push

- [ ] Add all files:
  ```bash
  git add .
  git commit -m "Initial commit: Complete automation system"
  git push origin main
  ```

---

## 🗄️ Step 2: Supabase Setup (5 minutes)

### Access Supabase Project

- [ ] Go to https://tyibyuwusjpogfknameh.supabase.co
- [ ] Login to your account
- [ ] Confirm project is active

### Create Database Tables

- [ ] Click on **SQL Editor** in left sidebar
- [ ] Click **New query**
- [ ] Copy entire contents of `supabase_schema.sql`
- [ ] Paste into SQL editor
- [ ] Click **Run** (or press F5)
- [ ] Verify success message: "Success. No rows returned"

### Verify Tables Created

- [ ] Click on **Table Editor** in left sidebar
- [ ] Confirm these 4 tables exist:
  - [ ] `nse_bulk_deals`
  - [ ] `nse_block_deals`
  - [ ] `bse_bulk_deals`
  - [ ] `bse_block_deals`
- [ ] Click on each table to verify structure

### Test Database Connection (Optional)

- [ ] Run this test query in SQL Editor:
  ```sql
  SELECT table_name 
  FROM information_schema.tables 
  WHERE table_schema = 'public' 
  AND table_name LIKE '%deals';
  ```
- [ ] Should return 4 table names

---

## 🔐 Step 3: GitHub Secrets Setup (5 minutes)

### Navigate to Secrets

- [ ] Go to https://github.com/kinggerald2007-png/bulk-deal-tracker-cloud
- [ ] Click **Settings** tab
- [ ] Click **Secrets and variables** → **Actions**

### Add Secret 1: SUPABASE_URL

- [ ] Click **New repository secret**
- [ ] Name: `SUPABASE_URL`
- [ ] Value: `https://tyibyuwusjpogfknameh.supabase.co`
- [ ] Click **Add secret**

### Add Secret 2: SUPABASE_KEY

- [ ] Click **New repository secret**
- [ ] Name: `SUPABASE_KEY`
- [ ] Value: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR5aWJ5dXd1c2pwb2dma25hbWVoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk1NDgxMDMsImV4cCI6MjA3NTEyNDEwM30.xS8SYGmUYKIG41IfnpwDkrkkPeDttADY6qSf3MRPvx8`
- [ ] Click **Add secret**

### Add Secret 3: EMAIL_USER

- [ ] Click **New repository secret**
- [ ] Name: `EMAIL_USER`
- [ ] Value: `king.gerald2007@gmail.com`
- [ ] Click **Add secret**

### Add Secret 4: EMAIL_PASSWORD

- [ ] Click **New repository secret**
- [ ] Name: `EMAIL_PASSWORD`
- [ ] Value: `osms grsv iorx hjan`
- [ ] Click **Add secret**

### Add Secret 5: EMAIL_TO

- [ ] Click **New repository secret**
- [ ] Name: `EMAIL_TO`
- [ ] Value: `king.gerald2007@gmail.com`
- [ ] (For multiple recipients: `email1@gmail.com,email2@gmail.com`)
- [ ] Click **Add secret**

### Verify All Secrets

- [ ] Go back to Secrets page
- [ ] Confirm all 5 secrets are listed:
  - [ ] SUPABASE_URL
  - [ ] SUPABASE_KEY
  - [ ] EMAIL_USER
  - [ ] EMAIL_PASSWORD
  - [ ] EMAIL_TO

---

## 🧪 Step 4: Local Testing (Optional, 10 minutes)

### Install Dependencies Locally

- [ ] Open terminal in project directory
- [ ] Create virtual environment:
  ```bash
  python -m venv venv
  source venv/bin/activate  # On Windows: venv\Scripts\activate
  ```
- [ ] Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```

### Run Test Script

- [ ] Run the test script:
  ```bash
  python test_automation.py
  ```
- [ ] Check all tests pass (green checkmarks)
- [ ] Fix any issues found

### Run Main Script (Optional)

- [ ] Run the main automation:
  ```bash
  python main.py
  ```
- [ ] Wait for completion (2-5 minutes)
- [ ] Check for errors in console
- [ ] Verify CSV files generated
- [ ] Check email inbox for report
- [ ] Verify data in Supabase

---

## 🚀 Step 5: Deploy to GitHub Actions (5 minutes)

### Verify Workflow File

- [ ] Check `.github/workflows/daily_deals_workflow.yml` exists
- [ ] Verify cron schedule: `40 4 * * *` (10:10 AM IST)
- [ ] Confirm all steps are present

### Enable GitHub Actions

- [ ] Go to repository **Actions** tab
- [ ] If prompted, click **"I understand my workflows, go ahead and enable them"**
- [ ] Verify workflow appears: "Daily Bulk & Block Deals Automation"

### Manual Test Run

- [ ] Click on **Daily Bulk & Block Deals Automation** workflow
- [ ] Click **Run workflow** button (top right)
- [ ] Select branch: `main`
- [ ] Click **Run workflow**
- [ ] Wait for workflow to start

### Monitor Execution

- [ ] Click on the running workflow
- [ ] Click on **fetch-and-report** job
- [ ] Watch logs in real-time
- [ ] Wait for completion (2-5 minutes)

### Verify Success

- [ ] Check for green checkmark ✅
- [ ] Review logs for errors
- [ ] Check email inbox
- [ ] Verify CSV files in artifacts
- [ ] Check Supabase data

---

## ✅ Step 6: Verification (5 minutes)

### Check Email

- [ ] Open Gmail inbox
- [ ] Find email with subject: "📊 Daily Bulk & Block Deals Report - [Date]"
- [ ] Verify HTML formatting looks good
- [ ] Check CSV attachments exist
- [ ] Verify summary statistics

### Check Supabase Data

- [ ] Go to Supabase project
- [ ] Click **Table Editor**
- [ ] Check each table for today's data:
  ```sql
  SELECT * FROM nse_bulk_deals WHERE fetch_date = CURRENT_DATE;
  SELECT * FROM nse_block_deals WHERE fetch_date = CURRENT_DATE;
  SELECT * FROM bse_bulk_deals WHERE fetch_date = CURRENT_DATE;
  SELECT * FROM bse_block_deals WHERE fetch_date = CURRENT_DATE;
  ```
- [ ] Verify `fetch_date` is today
- [ ] Verify `source` is correct (NSE/BSE)

### Check GitHub Actions

- [ ] Go to repository **Actions** tab
- [ ] Verify workflow completed successfully
- [ ] Download and review logs artifact
- [ ] Download CSV files artifact (if available)

### Check CSV Files (if saved locally)

- [ ] Verify files exist in project directory
- [ ] Open each CSV and check data:
  - [ ] `NSE_Bulk_Deals_[DATE].csv`
  - [ ] `NSE_Block_Deals_[DATE].csv`
  - [ ] `BSE_Bulk_Deals_[DATE].csv`
  - [ ] `BSE_Block_Deals_[DATE].csv`

---

## 📅 Step 7: Schedule Verification (2 minutes)

### Confirm Schedule

- [ ] Workflow is set to run at **10:10 AM IST daily**
- [ ] Cron expression: `40 4 * * *` (UTC)
- [ ] Manual trigger is enabled for testing

### Set Reminder

- [ ] Set reminder to check email tomorrow at 10:15 AM IST
- [ ] Mark calendar to review first automated run

### First Automated Run

- [ ] **Tomorrow at 10:10 AM IST**, workflow will run automatically
- [ ] No action needed from you
- [ ] Email will arrive automatically
- [ ] Data will be stored automatically

---

## 🎉 Step 8: Post-Deployment (Optional)

### Documentation

- [ ] Update README with any custom changes
- [ ] Document any issues encountered
- [ ] Note any exchange-specific quirks

### Optimization

- [ ] Review execution time
- [ ] Check memory usage
- [ ] Optimize queries if needed

### Monitoring Setup

- [ ] Set up email filters for reports
- [ ] Create folder in Gmail: "Bulk Deal Reports"
- [ ] Set up rules for automatic organization

### Backup

- [ ] Export Supabase data periodically
- [ ] Keep copies of CSV files
- [ ] Backup GitHub repository

---

## 🔒 Security Checklist

- [ ] Never commit `.env` file
- [ ] GitHub secrets are properly configured
- [ ] Email app password is secure
- [ ] Supabase API key is not exposed
- [ ] Repository is public (or Actions enabled for private)
- [ ] No sensitive data in commit history
- [ ] `.gitignore` includes sensitive files

---

## 🐛 Troubleshooting Reference

### If Workflow Fails:

1. **Check logs in GitHub Actions**
   - [ ] Go to Actions → Failed run → Click job
   - [ ] Review error messages

2. **Verify secrets**
   - [ ] Settings → Secrets → Check all 5 secrets exist
   - [ ] Recreate if suspicious of typos

3. **Check Supabase**
   - [ ] Verify tables exist
   - [ ] Check API key is valid
   - [ ] Review Supabase logs

4. **Test locally**
   - [ ] Run `python test_automation.py`
   - [ ] Run `python main.py`
   - [ ] Fix issues found

### If Email Not Received:

- [ ] Check spam/junk folder
- [ ] Verify EMAIL_PASSWORD is correct app password
- [ ] Test Gmail login manually
- [ ] Generate new app password if needed

### If No Data in Supabase:

- [ ] Check if trading day (not weekend/holiday)
- [ ] Verify NSE/BSE websites are accessible
- [ ] Run after 5:30 PM IST when data is published
- [ ] Check GitHub Actions logs for errors

---

## 📊 Success Criteria

Your deployment is successful when:

- [  ] ✅ All files committed to GitHub
- [ ] ✅ Supabase tables created
- [ ] ✅ GitHub secrets configured
- [ ] ✅ Workflow runs successfully
- [ ] ✅ Email report received
- [ ] ✅ CSV files generated
- [ ] ✅ Data in Supabase
- [ ] ✅ No errors in logs
- [ ] ✅ Schedule is active
- [ ] ✅ System runs automatically

---

## 🎯 Next Scheduled Run

**Tomorrow at 10:10 AM IST**

The system will automatically:
1. Fetch data from NSE and BSE
2. Store in Supabase database
3. Generate CSV files
4. Send email report to king.gerald2007@gmail.com
5. Upload logs to GitHub

**No action required from you!** 🎉

---

## 📞 Need Help?

If you encounter issues:

1. **Review logs** - Check GitHub Actions logs
2. **Check documentation** - Read README.md and QUICKSTART.md
3. **Run tests** - Execute test_automation.py
4. **Open issue** - Create GitHub issue with error details
5. **Email support** - Contact king.gerald2007@gmail.com

---

**Congratulations! Your Bulk Deal Tracker is now deployed and running! 🚀**

---

_Last updated: October 2025_
_Version: 1.0.0_