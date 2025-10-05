"""
Working NSEPython test - FIXED VERSION
"""
from nsepython import get_bulkdeals, get_blockdeals
import pandas as pd
from datetime import datetime

print("=" * 60)
print("NSE Bulk & Block Deals - Working Version")
print("=" * 60)

# Test Bulk Deals
print("\n1. Fetching Bulk Deals...")
try:
    bulk_data = get_bulkdeals()
    
    # Check if it's a DataFrame and not empty
    if isinstance(bulk_data, pd.DataFrame) and not bulk_data.empty:
        print(f"SUCCESS! Found {len(bulk_data)} bulk deals")
        
        # Add metadata
        bulk_data['fetch_date'] = datetime.now().date()
        bulk_data['source'] = 'NSE'
        bulk_data['deal_category'] = 'BULK'
        
        print("\nSample data:")
        print(bulk_data.head(10))
        
        print("\nColumns:", bulk_data.columns.tolist())
        
        # Save to CSV
        filename = f'NSE_Bulk_Deals_{datetime.now().strftime("%Y%m%d")}.csv'
        bulk_data.to_csv(filename, index=False)
        print(f"\nSaved to: {filename}")
    else:
        print("No bulk deals data available")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

# Test Block Deals
print("\n2. Fetching Block Deals...")
try:
    block_data = get_blockdeals()
    
    # Check if it's a DataFrame and not empty
    if isinstance(block_data, pd.DataFrame) and not block_data.empty:
        print(f"SUCCESS! Found {len(block_data)} block deals")
        
        # Add metadata
        block_data['fetch_date'] = datetime.now().date()
        block_data['source'] = 'NSE'
        block_data['deal_category'] = 'BLOCK'
        
        print("\nSample data:")
        print(block_data.head(10))
        
        print("\nColumns:", block_data.columns.tolist())
        
        # Save to CSV
        filename = f'NSE_Block_Deals_{datetime.now().strftime("%Y%m%d")}.csv'
        block_data.to_csv(filename, index=False)
        print(f"\nSaved to: {filename}")
    else:
        print("No block deals data available")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Test completed!")
print("=" * 60)