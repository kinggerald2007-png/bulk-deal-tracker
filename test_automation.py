"""
Test Script for Bulk Deal Tracker Automation
Run this to verify your setup before deploying
"""

import os
import sys
from datetime import datetime

def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)

def print_success(text):
    """Print success message"""
    print(f"✅ {text}")

def print_error(text):
    """Print error message"""
    print(f"❌ {text}")

def print_warning(text):
    """Print warning message"""
    print(f"⚠️  {text}")

def test_dependencies():
    """Test if all required packages are installed"""
    print_header("Testing Dependencies")
    
    required_packages = [
        'requests',
        'pandas',
        'supabase',
        'yagmail',
    ]
    
    all_installed = True
    for package in required_packages:
        try:
            __import__(package)
            print_success(f"{package} is installed")
        except ImportError:
            print_error(f"{package} is NOT installed")
            all_installed = False
    
    return all_installed

def test_environment_variables():
    """Test if environment variables are set"""
    print_header("Testing Environment Variables")
    
    required_vars = {
        'SUPABASE_URL': 'https://tyibyuwusjpogfknameh.supabase.co',
        'SUPABASE_KEY': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
        'EMAIL_USER': 'king.gerald2007@gmail.com',
        'EMAIL_PASSWORD': 'osms grsv iorx hjan',
        'EMAIL_TO': 'king.gerald2007@gmail.com',
    }
    
    all_set = True
    for var, expected in required_vars.items():
        value = os.getenv(var)
        if value:
            # Show partial value for security
            if 'PASSWORD' in var or 'KEY' in var:
                display_value = value[:10] + "..." if len(value) > 10 else value
            else:
                display_value = value
            print_success(f"{var} is set: {display_value}")
        else:
            # Use default values from main.py
            if var == 'SUPABASE_URL':
                print_warning(f"{var} not in environment, using default: {expected}")
            elif var == 'SUPABASE_KEY':
                print_warning(f"{var} not in environment, using default: {expected[:20]}...")
            else:
                print_warning(f"{var} not in environment, using default: {expected}")
    
    return all_set

def test_supabase_connection():
    """Test Supabase connection"""
    print_header("Testing Supabase Connection")
    
    try:
        from supabase import create_client
        
        url = os.getenv('SUPABASE_URL', 'https://tyibyuwusjpogfknameh.supabase.co')
        key = os.getenv('SUPABASE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR5aWJ5dXd1c2pwb2dma25hbWVoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk1NDgxMDMsImV4cCI6MjA3NTEyNDEwM30.xS8SYGmUYKIG41IfnpwDkrkkPeDttADY6qSf3MRPvx8')
        
        client = create_client(url, key)
        print_success("Supabase client created successfully")
        
        # Test connection by querying tables
        tables = ['nse_bulk_deals', 'nse_block_deals', 'bse_bulk_deals', 'bse_block_deals']
        for table in tables:
            try:
                response = client.table(table).select("*", count="exact").limit(1).execute()
                print_success(f"Table '{table}' is accessible")
            except Exception as e:
                print_error(f"Table '{table}' is NOT accessible: {str(e)[:50]}...")
                return False
        
        return True
        
    except Exception as e:
        print_error(f"Failed to connect to Supabase: {e}")
        return False

def test_nse_connection():
    """Test NSE website connectivity"""
    print_header("Testing NSE Connection")
    
    try:
        import requests
        
        session = requests.Session()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
        }
        
        # Test main site
        response = session.get('https://www.nseindia.com', headers=headers, timeout=10)
        if response.status_code == 200:
            print_success("NSE website is accessible")
        else:
            print_warning(f"NSE returned status code: {response.status_code}")
        
        # Test deals page
        response = session.get(
            'https://www.nseindia.com/report-detail/display-bulk-and-block-deals',
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            print_success("NSE bulk/block deals page is accessible")
        else:
            print_warning(f"NSE deals page returned status code: {response.status_code}")
        
        return True
        
    except Exception as e:
        print_error(f"Failed to connect to NSE: {e}")
        return False

def test_bse_connection():
    """Test BSE website connectivity"""
    print_header("Testing BSE Connection")
    
    try:
        import requests
        
        session = requests.Session()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        }
        
        # Test main site
        response = session.get('https://www.bseindia.com', headers=headers, timeout=10)
        if response.status_code == 200:
            print_success("BSE website is accessible")
            return True
        else:
            print_warning(f"BSE returned status code: {response.status_code}")
            return False
        
    except Exception as e:
        print_error(f"Failed to connect to BSE: {e}")
        return False

def test_email_configuration():
    """Test email configuration (without sending)"""
    print_header("Testing Email Configuration")
    
    try:
        import yagmail
        
        user = os.getenv('EMAIL_USER', 'king.gerald2007@gmail.com')
        password = os.getenv('EMAIL_PASSWORD', 'osms grsv iorx hjan')
        
        # Just initialize, don't send
        yag = yagmail.SMTP(user, password)
        print_success("Email client initialized successfully")
        print_success(f"Sender: {user}")
        
        return True
        
    except Exception as e:
        print_error(f"Failed to initialize email client: {e}")
        print_warning("Check if Gmail app password is correct")
        return False

def test_csv_writing():
    """Test if CSV files can be written"""
    print_header("Testing CSV Writing")
    
    try:
        import pandas as pd
        
        # Create test data
        test_data = {
            'symbol': ['TEST'],
            'client': ['TEST CLIENT'],
            'quantity': [1000],
            'price': [100.50]
        }
        df = pd.DataFrame(test_data)
        
        # Write test CSV
        test_file = 'test_output.csv'
        df.to_csv(test_file, index=False)
        print_success(f"Test CSV file created: {test_file}")
        
        # Clean up
        os.remove(test_file)
        print_success("Test CSV file deleted")
        
        return True
        
    except Exception as e:
        print_error(f"Failed to write CSV: {e}")
        return False

def run_full_test():
    """Run all tests"""
    print_header("🧪 BULK DEAL TRACKER - SYSTEM TEST")
    print(f"Test started at: {datetime.now().strftime('%d %B %Y, %I:%M:%S %p')}")
    
    results = {
        'Dependencies': test_dependencies(),
        'Environment Variables': test_environment_variables(),
        'Supabase Connection': test_supabase_connection(),
        'NSE Connection': test_nse_connection(),
        'BSE Connection': test_bse_connection(),
        'Email Configuration': test_email_configuration(),
        'CSV Writing': test_csv_writing(),
    }
    
    # Summary
    print_header("📊 TEST SUMMARY")
    
    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)
    failed_tests = total_tests - passed_tests
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:.<50} {status}")
    
    print("\n" + "=" * 70)
    print(f"  Total Tests: {total_tests}")
    print(f"  Passed: {passed_tests}")
    print(f"  Failed: {failed_tests}")
    
    if failed_tests == 0:
        print("\n  🎉 ALL TESTS PASSED! Your setup is ready!")
        print("  ✅ You can now run the main automation script")
        print("  Run: python main.py")
    else:
        print("\n  ⚠️  SOME TESTS FAILED")
        print("  Please fix the issues above before running the automation")
    
    print("=" * 70)
    
    return failed_tests == 0

if __name__ == "__main__":
    try:
        success = run_full_test()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)