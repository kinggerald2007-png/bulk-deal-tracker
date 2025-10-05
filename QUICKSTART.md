# 🚀 Quick Start Guide

Get your Bulk Deal Tracker running in **under 10 minutes**!

## ⚡ Super Quick Setup

### Step 1: Set Up Supabase (2 minutes)

1. Go to your Supabase project: https://tyibyuwusjpogfknameh.supabase.co
2. Click **SQL Editor** in the left sidebar
3. Copy and paste the entire contents of `supabase_schema.sql`
4. Click **Run** (or press F5)
5. You should see "Success. No rows returned" - that's perfect!

### Step 2: Configure GitHub Secrets (3 minutes)

1. Go to your repository: https://github.com/kinggerald2007-png/bulk-deal-tracker-cloud
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret** and add these **5 secrets**:

```
Name: SUPABASE_URL
Value: https://tyibyuwusjpogfknameh.supabase.co

Name: SUPABASE_KEY
Value: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR5aWJ5dXd1c2pwb2dma25hbWVoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk1NDgxMDMsImV4cCI6MjA3NTEyNDEwM30.xS8SYGmUYKIG41IfnpwDkrkkPeDttADY6qSf3MRPvx8

Name: EMAIL_USER
Value: king.gerald2007@gmail.com

Name: EMAIL_PASSWORD
Value: osms grsv iorx hjan

Name: EMAIL_TO
Value: king.gerald2007@gmail.com
```

### Step 3: Test the Automation (2 minutes)

1. Go to **Actions** tab in your GitHub repository
2. Click on **Daily Bulk & Block Deals Automation** workflow
3. Click **Run workflow** button (on the right)
4. Select branch: `main`
5. Click **Run workflow**
6. Wait 2-5 minutes and check your email! 📧

---

## 📋 Checklist

Before running, make sure:

- [ ] Supabase tables are created
- [ ] All 5 GitHub secrets are added
- [ ] Repository has the workflow file in `.github/workflows/`
- [ ] Workflow is enabled (check Actions tab)

---

## 🔍 Verify Everything is Working

### 1. Check Supabase Tables

Go to your Supabase project and run this query:

```sql
-- Check if tables exist
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name LIKE '%deals';
```

You should see:
- `nse_bulk_deals`
- `nse_block_deals`
- `bse_bulk_deals`
- `bse_block_deals`

### 2. Check GitHub Actions

- Go to **Actions** tab
- You should see your workflow run
- Green checkmark = Success ✅
- Red X = Failed (check logs) ❌

### 3. Check Your Email

You should receive an email with:
- Subject: "📊 Daily Bulk & Block Deals Report - [Today's Date]"
- Beautiful HTML report
- CSV files attached (if deals were found)

---

## 🐛 Troubleshooting

### Problem: Workflow doesn't appear in Actions tab

**Solution:**
```bash
# Make sure the workflow file exists:
# .github/workflows/daily_deals_workflow.yml

# File should start with:
name: Daily Bulk & Block Deals Automation
on:
  schedule:
    - cron: '40 4 * * *'
```

### Problem: Workflow fails with "Error 401"

**Solution:** 
- Double-check your Supabase credentials
- Make sure you copied the ENTIRE API key (it's very long!)
- Verify the URL doesn't have trailing slashes

### Problem: No email received

**Solution:**
- Check spam/junk folder
- Verify Gmail app password is correct (no spaces)
- Check GitHub Actions logs for email errors
- Test with: `echo "Test" | mail -s "Test" king.gerald2007@gmail.com`

### Problem: "No data available"

**Solution:**
- NSE/BSE might not have published data yet (they publish after market close)
- Try running after 5:30 PM IST
- Check if it's a trading holiday
- Verify NSE website is accessible: https://www.nseindia.com/report-detail/display-bulk-and-block-deals

---

## 🎯 Next Steps

Once everything is working:

### 1. Enable Daily Automation

The workflow is already scheduled for **10:10 AM IST daily**. No action needed!

To change the time:
```yaml
# Edit .github/workflows/daily_deals_workflow.yml
schedule:
  - cron: '40 4 * * *'  # Current: 10:10 AM IST
  # Change to your preferred time (in UTC)
```

### 2. Add More Email Recipients

Update the `EMAIL_TO` secret:
```
EMAIL_TO: email1@gmail.com,email2@gmail.com,email3@gmail.com
```

### 3. Test Locally (Optional)

```bash
# Clone the repository
git clone https://github.com/kinggerald2007-png/bulk-deal-tracker-cloud.git
cd bulk-deal-tracker-cloud

# Install dependencies
pip install -r requirements.txt

# Run the script
python main.py

# Check output
ls -l *.csv
cat deals_automation.log
```

### 4. Monitor Performance

**View logs:**
- Go to Actions → Select a workflow run → Click on job → Expand steps

**Download artifacts:**
- Go to Actions → Select a workflow run → Scroll to bottom → Download artifacts

**Check database:**
```sql
-- Total deals today
SELECT COUNT(*) as total_deals
FROM (
    SELECT * FROM nse_bulk_deals WHERE fetch_date = CURRENT_DATE
    UNION ALL
    SELECT * FROM nse_block_deals WHERE fetch_date = CURRENT_DATE
    UNION ALL
    SELECT * FROM bse_bulk_deals WHERE fetch_date = CURRENT_DATE
    UNION ALL
    SELECT * FROM bse_block_deals WHERE fetch_date = CURRENT_DATE
) combined;
```

---

## 📊 Sample Output

### Email Report Preview

```
📊 Daily Bulk & Block Deals Report
Generated on: 04 October 2025, 10:15 AM IST

Total Deals Today: 47

┌──────────┬─────────────┬───────┐
│ Exchange │ Deal Type   │ Count │
├──────────┼─────────────┼───────┤
│ NSE      │ Bulk Deals  │   12  │
│ NSE      │ Block Deals │    8  │
│ BSE      │ Bulk Deals  │   15  │
│ BSE      │ Block Deals │   12  │
├──────────┴─────────────┼───────┤
│ TOTAL                  │   47  │
└────────────────────────┴───────┘

📎 CSV files attached
```

### CSV Files Generated

- `NSE_Bulk_Deals_20251004.csv`
- `NSE_Block_Deals_20251004.csv`
- `BSE_Bulk_Deals_20251004.csv`
- `BSE_Block_Deals_20251004.csv`

---

## 💡 Pro Tips

### Tip 1: Run Manually Anytime

You can trigger the automation manually:
1. Go to Actions tab
2. Select the workflow
3. Click "Run workflow"
4. Wait for email

### Tip 2: Check Logs Without Email

Download logs from GitHub Actions artifacts (retained for 30 days)

### Tip 3: Pause Automation

To temporarily stop daily runs:
1. Go to Actions tab
2. Select the workflow
3. Click "..." → Disable workflow

### Tip 4: Get Historical Data

Modify the script to fetch past dates:

```python
# In main.py, modify fetch methods:
nse_fetcher.fetch_bulk_deals(date='01-10-2025')  # DD-MM-YYYY
bse_fetcher.fetch_bulk_deals(date='01/10/2025')  # DD/MM/YYYY
```

### Tip 5: Add Slack/Discord Notifications

Replace `yagmail` with webhook-based notifications for team collaboration.

---

## 🎓 Understanding the Schedule

**Cron Expression**: `40 4 * * *`

```
┌───────────── minute (0 - 59)        → 40
│ ┌───────────── hour (0 - 23)         → 4 (UTC)
│ │ ┌───────────── day of month (1-31) → *
│ │ │ ┌───────────── month (1 - 12)    → *
│ │ │ │ ┌───────────── day of week (0-6)→ *
│ │ │ │ │
* * * * *
```

**Why 4:40 UTC?**
- IST = UTC + 5:30
- 10:10 AM IST = 4:40 AM UTC
- Markets close at ~3:30 PM, data published by 5-6 PM
- 10:10 AM next day = safe time to fetch previous day's data

---

## 📞 Need Help?

### Quick Checks:

1. **Tables not created?**
   - Re-run `supabase_schema.sql`
   - Check for SQL errors

2. **Secrets not working?**
   - Delete and re-add them
   - Copy-paste carefully (no extra spaces!)

3. **Workflow not running?**
   - Check if repository is public
   - Enable Actions in repository settings

4. **Still stuck?**
   - Open an issue on GitHub
   - Include error logs
   - Mention what step failed

---

## ✅ Success Indicators

You'll know everything is working when:

1. ✅ Supabase shows 4 tables created
2. ✅ GitHub Actions shows green checkmark
3. ✅ Email arrives with today's report
4. ✅ CSV files are generated
5. ✅ Database contains today's data

---

## 🚀 You're All Set!

Your automation will now run **daily at 10:10 AM IST** automatically!

**What happens daily:**
1. GitHub Actions triggers at 10:10 AM IST
2. Script fetches deals from NSE and BSE
3. Data saved to CSV files
4. Data stored in Supabase
5. Email report sent to you
6. Logs saved for 30 days

**No manual intervention needed!** 🎉

---

## 📈 What's Next?

Explore advanced features:
- Deploy to AWS Lambda (see `deploy_aws.md`)
- Create a dashboard with Supabase + Next.js
- Add WhatsApp notifications
- Build a mobile app
- Analyze trends with Python/Pandas
- Set up alerts for large deals

**Happy Trading! 📊📈**