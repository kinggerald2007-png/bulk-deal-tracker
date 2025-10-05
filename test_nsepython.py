"""
Test NSEPython library with correct function names
"""
import pandas as pd
from datetime import datetime

# Try importing and check what functions are available
try:
    import nsepython as nse
    print("NSEPython imported successfully")
    print("Available functions:", dir(nse))
except ImportError:
    print("NSEPython not installed. Install with: pip install nsepython")
    exit()

print("=" * 60)
print("Testing NSEPython Library")
print("=" * 60)

# Try different function names for bulk deals
print("\n1. Trying to fetch Bulk Deals...")
try:
    # Try the correct function name
    data = nse.nse_get_bulk_deals()
    if data:
        df = pd.DataFrame(data)
        print(f"SUCCESS! Found {len(df)} bulk deals")
        print(df.head(10))
        df.to_csv('NSE_Bulk_Working.csv', index=False)
    else:
        print("No data returned")
except AttributeError:
    print("Function 'nse_get_bulk_deals' not found, trying alternatives...")
    try:
        data = nse.bulk_deals()
        if data:
            df = pd.DataFrame(data)
            print(f"SUCCESS! Found {len(df)} bulk deals")
            print(df.head(10))
    except:
        print("Could not find working bulk deals function")
except Exception as e:
    print(f"Error: {e}")

# Try block deals
print("\n2. Trying to fetch Block Deals...")
try:
    data = nse.nse_get_block_deals()
    if data:
        df = pd.DataFrame(data)
        print(f"SUCCESS! Found {len(df)} block deals")
        print(df.head(10))
        df.to_csv('NSE_Block_Working.csv', index=False)
    else:
        print("No data returned")
except AttributeError:
    print("Function 'nse_get_block_deals' not found, trying alternatives...")
    try:
        data = nse.block_deals()
        if data:
            df = pd.DataFrame(data)
            print(f"SUCCESS! Found {len(df)} block deals")
            print(df.head(10))
    except:
        print("Could not find working block deals function")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 60)