# Quick Setup Guide for Investor Monitoring

Your `monitored_investors` table is already set up! Here's how to use it.

## Table Structure

Your table has these columns:
- `investor_name` - Full name in CAPS (e.g., "RAKESH JHUNJHUNWALA")
- `display_name` - Friendly name for emails (e.g., "Rakesh Jhunjhunwala")
- `is_active` - TRUE/FALSE to enable/disable monitoring
- `category` - Type of investor (e.g., "IND", "MUT", "FII")
- `priority` - Number (higher = shown first in alerts)
- `notes` - Your personal notes

## Managing Your Investors

### Activate an Investor for Monitoring

```sql
UPDATE monitored_investors 
SET is_active = TRUE 
WHERE investor_name = 'RAKESH JHUNJHUNWALA';
```

### Deactivate an Investor

```sql
UPDATE monitored_investors 
SET is_active = FALSE 
WHERE investor_name = 'MOTILAL OSWAL MUTUAL FUND';
```

### Add New Investor

```sql
INSERT INTO monitored_investors (investor_name, display_name, is_active, category, priority, notes)
VALUES 
('AKASH BHANSHALI', 'Akash Bhanshali', TRUE, 'IND', 5, 'Smallcap specialist'),
('SANJAY DANGI', 'Sanjay Dangi', TRUE, 'IND', 4, 'Value investor');
```

### View Active Investors

```sql
SELECT investor_name, display_name, category, priority 
FROM monitored_investors 
WHERE is_active = TRUE 
ORDER BY priority DESC;
```

### Set Priority (Higher = More Important)

```sql
UPDATE monitored_investors 
SET priority = 10 
WHERE investor_name = 'RAKESH JHUNJHUNWALA';
```

## Current Active Investors

Looking at your table, you have these investors set to TRUE:
1. RAKESH JHUNJHUNWALA (Priority: IND)
2. VIJAY KEDIA (Priority: IND)
3. DOLLY KHANNA (Priority: IND)
4. ASHISH KACHOLIA (Priority: IND)
5. RADHAKISHAN DAMANI (Priority: IND)
6. PORINJU VELIYATH (Priority: IND)
7. RAMESH DAMANI (Priority: IND)
8. MOHNISH PABRAI (Priority: IND)
9. ASHISH DHAWAN (Priority: IND)
10. NEMISH SHAH (Priority: IND)

And more...

## Test the System

Run locally:
```bash
python main.py
```

Check your email for alerts!

## Priority System

The `priority` column controls alert order:
- **10** = VIP investors (shown first)
- **5** = Important investors
- **1** = Regular monitoring

Higher priority deals appear first in your email alerts.

## Categories

Common categories:
- **IND** = Individual investor
- **MUT** = Mutual fund
- **FII** = Foreign institutional investor
- **DII** = Domestic institutional investor

## Tips

1. Start with 5-10 active investors
2. Use priority to focus on your favorites
3. Add notes to remember why you're tracking them
4. Review and update your list monthly

That's it! The system is ready to use with your existing table.