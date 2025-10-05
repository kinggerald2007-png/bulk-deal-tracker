from datetime import datetime, timedelta
from main import NSEDataFetcher, BSEDataFetcher

print("Testing NSE/BSE data fetch...")
print("=" * 50)

nse = NSEDataFetcher()
bse = BSEDataFetcher()

# Try October 3, 2024 (Thursday - likely a trading day)
test_date_nse = "03-10-2024"
test_date_bse = "03/10/2024"

print(f"\nTesting date: 03 October 2024")
print("-" * 50)

print("\n1. NSE Bulk Deals:")
result = nse.fetch_bulk_deals(test_date_nse)
if result is not None:
    print(f"   SUCCESS! Found {len(result)} deals")
    print(result.head())
else:
    print("   No data found")

print("\n2. NSE Block Deals:")
result = nse.fetch_block_deals(test_date_nse)
if result is not None:
    print(f"   SUCCESS! Found {len(result)} deals")
    print(result.head())
else:
    print("   No data found")

print("\n3. BSE Bulk Deals:")
result = bse.fetch_bulk_deals(test_date_bse)
if result is not None:
    print(f"   SUCCESS! Found {len(result)} deals")
    print(result.head())
else:
    print("   No data found")

print("\n4. BSE Block Deals:")
result = bse.fetch_block_deals(test_date_bse)
if result is not None:
    print(f"   SUCCESS! Found {len(result)} deals")
    print(result.head())
else:
    print("   No data found")

print("\n" + "=" * 50)
print("Test completed!")