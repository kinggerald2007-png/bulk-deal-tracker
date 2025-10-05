"""
Fetch NSE Bulk/Block Deals using direct CSV download
"""

import requests
import pandas as pd
from datetime import datetime
import time
from io import StringIO

class NSECSVFetcher:
    """Fetch NSE data using CSV download endpoints"""
    
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.nseindia.com/report-detail/display-bulk-and-block-deals'
        }
        self._get_cookies()
    
    def _get_cookies(self):
        """Visit main page to get cookies"""
        try:
            self.session.get('https://www.nseindia.com', headers=self.headers, timeout=10)
            time.sleep(1)
            # Visit the deals page
            self.session.get('https://www.nseindia.com/report-detail/display-bulk-and-block-deals', 
                           headers=self.headers, timeout=10)
            time.sleep(1)
            print("Cookies obtained")
        except Exception as e:
            print(f"Error getting cookies: {e}")
    
    def fetch_bulk_deals_csv(self, from_date=None, to_date=None):
        """
        Fetch bulk deals CSV
        Dates in format: DD-MM-YYYY
        """
        try:
            if from_date is None:
                from_date = (datetime.now()).strftime('%d-%m-%Y')
            if to_date is None:
                to_date = (datetime.now()).strftime('%d-%m-%Y')
            
            # CSV download URL with date parameters
            url = f"https://www.nseindia.com/api/historical/bulk-deals?from={from_date}&to={to_date}&csv=true"
            
            print(f"Fetching bulk deals from {from_date} to {to_date}...")
            
            response = self.session.get(url, headers=self.headers, timeout=20)
            response.raise_for_status()
            
            # Try to parse as CSV
            try:
                df = pd.read_csv(StringIO(response.text))
                if not df.empty:
                    df['fetch_date'] = datetime.now().date()
                    df['source'] = 'NSE'
                    print(f"SUCCESS! Found {len(df)} bulk deals")
                    return df
                else:
                    print("No data available for these dates")
                    return None
            except:
                print("Could not parse CSV response")
                return None
                
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def fetch_block_deals_csv(self, from_date=None, to_date=None):
        """
        Fetch block deals CSV
        Dates in format: DD-MM-YYYY
        """
        try:
            if from_date is None:
                from_date = (datetime.now()).strftime('%d-%m-%Y')
            if to_date is None:
                to_date = (datetime.now()).strftime('%d-%m-%Y')
            
            url = f"https://www.nseindia.com/api/historical/block-deals?from={from_date}&to={to_date}&csv=true"
            
            print(f"Fetching block deals from {from_date} to {to_date}...")
            
            response = self.session.get(url, headers=self.headers, timeout=20)
            response.raise_for_status()
            
            try:
                df = pd.read_csv(StringIO(response.text))
                if not df.empty:
                    df['fetch_date'] = datetime.now().date()
                    df['source'] = 'NSE'
                    print(f"SUCCESS! Found {len(df)} block deals")
                    return df
                else:
                    print("No data available for these dates")
                    return None
            except:
                print("Could not parse CSV response")
                return None
                
        except Exception as e:
            print(f"Error: {e}")
            return None


def test_last_week():
    """Test fetching last week's data"""
    print("=" * 60)
    print("TESTING: Last Week's NSE Data (CSV Method)")
    print("=" * 60)
    
    fetcher = NSECSVFetcher()
    
    # Last week's dates (as shown on NSE website: 28-Sep to 05-Oct)
    from_date = "28-09-2025"  
    to_date = "05-10-2025"
    
    print(f"\nFetching data from {from_date} to {to_date}\n")
    print("-" * 60)
    
    # Bulk deals
    print("\n1. BULK DEALS:")
    bulk = fetcher.fetch_bulk_deals_csv(from_date, to_date)
    if bulk is not None:
        print(f"\nFirst few records:")
        print(bulk.head(10))
        bulk.to_csv('NSE_Bulk_LastWeek.csv', index=False)
        print(f"\nSaved to: NSE_Bulk_LastWeek.csv")
    
    time.sleep(2)  # Be polite to the server
    
    # Block deals
    print("\n2. BLOCK DEALS:")
    block = fetcher.fetch_block_deals_csv(from_date, to_date)
    if block is not None:
        print(f"\nFirst few records:")
        print(block.head(10))
        block.to_csv('NSE_Block_LastWeek.csv', index=False)
        print(f"\nSaved to: NSE_Block_LastWeek.csv")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    test_last_week()