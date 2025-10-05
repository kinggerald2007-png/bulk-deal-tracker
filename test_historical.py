"""
Test script to fetch last week's data from NSE and BSE
"""

import os
import sys
from datetime import datetime, timedelta

# Import from main.py
from main import NSEDataFetcher, BSEDataFetcher, DatabaseManager, EmailReporter

def test_historical_data():
    """Fetch data from the past 7 days"""
    
    print("=" * 70)
    print("TESTING: Fetching Last Week's Data")
    print("=" * 70)
    
    nse_fetcher = NSEDataFetcher()
    bse_fetcher = BSEDataFetcher()
    
    # Get dates for last 7 days (excluding today)
    dates_to_test = []
    for i in range(1, 8):  # Last 7 days
        date = datetime.now() - timedelta(days=i)
        dates_to_test.append(date)
    
    all_data = {
        'nse_bulk': [],
        'nse_block': [],
        'bse_bulk': [],
        'bse_block': []
    }
    
    # Try each date
    for date in dates_to_test:
        # NSE format: DD-MM-YYYY
        nse_date = date.strftime('%d-%m-%Y')
        # BSE format: DD/MM/YYYY
        bse_date = date.strftime('%d/%m/%Y')
        
        print(f"\nTrying date: {date.strftime('%d %B %Y')}")
        print("-" * 50)
        
        # Fetch NSE bulk deals
        print("Fetching NSE bulk deals...")
        nse_bulk = nse_fetcher.fetch_bulk_deals(nse_date)
        if nse_bulk is not None and not nse_bulk.empty:
            print(f"  Found {len(nse_bulk)} NSE bulk deals")
            all_data['nse_bulk'].append(nse_bulk)
        else:
            print("  No NSE bulk deals found")
        
        # Fetch NSE block deals
        print("Fetching NSE block deals...")
        nse_block = nse_fetcher.fetch_block_deals(nse_date)
        if nse_block is not None and not nse_block.empty:
            print(f"  Found {len(nse_block)} NSE block deals")
            all_data['nse_block'].append(nse_block)
        else:
            print("  No NSE block deals found")
        
        # Fetch BSE bulk deals
        print("Fetching BSE bulk deals...")
        bse_bulk = bse_fetcher.fetch_bulk_deals(bse_date)
        if bse_bulk is not None and not bse_bulk.empty:
            print(f"  Found {len(bse_bulk)} BSE bulk deals")
            all_data['bse_bulk'].append(bse_bulk)
        else:
            print("  No BSE bulk deals found")
        
        # Fetch BSE block deals
        print("Fetching BSE block deals...")
        bse_block = bse_fetcher.fetch_block_deals(bse_date)
        if bse_block is not None and not bse_block.empty:
            print(f"  Found {len(bse_block)} BSE block deals")
            all_data['bse_block'].append(bse_block)
        else:
            print("  No BSE block deals found")
    
    # Combine all dataframes
    import pandas as pd
    
    combined_data = {}
    for key in all_data:
        if all_data[key]:
            combined_data[key] = pd.concat(all_data[key], ignore_index=True)
        else:
            combined_data[key] = None
    
    # Print summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    total_deals = 0
    for key, df in combined_data.items():
        count = len(df) if df is not None else 0
        total_deals += count
        print(f"{key:20s}: {count:4d} deals")
    
    print(f"{'TOTAL':20s}: {total_deals:4d} deals")