"""
NSE/BSE Bulk and Block Deals Daily Automation Script - WORKING VERSION
Using nsepython library for NSE data
Repository: https://github.com/kinggerald2007-png/bulk-deal-tracker-cloud
"""

import os
import sys
import logging
from datetime import datetime
from typing import Dict, List, Optional
import traceback

import pandas as pd
from nsepython import get_bulkdeals, get_blockdeals
from supabase import create_client, Client
import yagmail

# ============================================================================
# CONFIGURATION
# ============================================================================

class Config:
    """Configuration class"""
    
    # Supabase Configuration
    SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://tyibyuwusjpogfknameh.supabase.co')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR5aWJ5dXd1c2pwb2dma25hbWVoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk1NDgxMDMsImV4cCI6MjA3NTEyNDEwM30.xS8SYGmUYKIG41IfnpwDkrkkPeDttADY6qSf3MRPvx8')
    
    # Email Configuration
    EMAIL_USER = os.getenv('EMAIL_USER', 'king.gerald2007@gmail.com')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', 'osms grsv iorx hjan')
    EMAIL_TO = os.getenv('EMAIL_TO', 'king.gerald2007@gmail.com').split(',')
    
    # Database Table Names
    TABLE_NSE_BULK = "nse_bulk_deals"
    TABLE_NSE_BLOCK = "nse_block_deals"
    TABLE_BSE_BULK = "bse_bulk_deals"
    TABLE_BSE_BLOCK = "bse_block_deals"
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')


# ============================================================================
# LOGGING SETUP
# ============================================================================

def setup_logging():
    """Configure logging"""
    logging.basicConfig(
        level=getattr(logging, Config.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('deals_automation.log')
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()


# ============================================================================
# DATA FETCHER
# ============================================================================

class NSEDataFetcher:
    """Fetch NSE data using nsepython library"""
    
    def fetch_bulk_deals(self) -> Optional[pd.DataFrame]:
        """Fetch bulk deals from NSE"""
        try:
            logger.info("Fetching NSE bulk deals...")
            df = get_bulkdeals()
            
            if isinstance(df, pd.DataFrame) and not df.empty:
                # Rename columns to match Supabase schema
                column_mapping = {
                    'Date': 'deal_date',
                    'Symbol': 'symbol',
                    'Security Name': 'security_name',
                    'Client Name': 'client_name',
                    'Buy/Sell': 'buy_sell',
                    'Quantity Traded': 'quantity_traded',
                    'Trade Price / Wght. Avg. Price': 'trade_price',
                    'Remarks': 'remarks'
                }
                df = df.rename(columns=column_mapping)
                
                df['fetch_date'] = datetime.now().date()
                df['source'] = 'NSE'
                df['deal_category'] = 'BULK'
                logger.info(f"Fetched {len(df)} NSE bulk deals")
                return df
            else:
                logger.warning("No NSE bulk deals data available")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching NSE bulk deals: {e}")
            logger.error(traceback.format_exc())
            return None
    
    def fetch_block_deals(self) -> Optional[pd.DataFrame]:
        """Fetch block deals from NSE"""
        try:
            logger.info("Fetching NSE block deals...")
            df = get_blockdeals()
            
            if isinstance(df, pd.DataFrame) and not df.empty:
                # Rename columns to match Supabase schema
                column_mapping = {
                    'Date': 'deal_date',
                    'Symbol': 'symbol',
                    'Security Name': 'security_name',
                    'Client Name': 'client_name',
                    'Buy/Sell': 'buy_sell',
                    'Quantity Traded': 'quantity_traded',
                    'Trade Price / Wght. Avg. Price': 'trade_price'
                }
                df = df.rename(columns=column_mapping)
                
                df['fetch_date'] = datetime.now().date()
                df['source'] = 'NSE'
                df['deal_category'] = 'BLOCK'
                logger.info(f"Fetched {len(df)} NSE block deals")
                return df
            else:
                logger.warning("No NSE block deals data available")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching NSE block deals: {e}")
            logger.error(traceback.format_exc())
            return None


# ============================================================================
# DATABASE MANAGER
# ============================================================================

class DatabaseManager:
    """Handles Supabase database operations"""
    
    def __init__(self):
        if not Config.SUPABASE_URL or not Config.SUPABASE_KEY:
            raise ValueError("Supabase credentials not configured")
        
        try:
            self.client: Client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
            logger.info("Supabase client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            raise
    
    def store_data(self, df: pd.DataFrame, table_name: str) -> bool:
        """Store DataFrame to Supabase table"""
        try:
            if df is None or df.empty:
                logger.warning(f"No data to store in {table_name}")
                return False
            
            # Convert DataFrame to list of dicts
            records = df.to_dict('records')
            
            # Clean NaN values and convert dates to strings
            for record in records:
                for key, value in record.items():
                    if pd.isna(value):
                        record[key] = None
                    elif hasattr(value, 'item'):
                        record[key] = value.item()
                    # Convert date objects to ISO format strings
                    elif isinstance(value, (datetime, pd.Timestamp)):
                        record[key] = value.date().isoformat()
                    elif hasattr(value, 'isoformat'):  # datetime.date objects
                        record[key] = value.isoformat()
            
            # Insert data in batches
            batch_size = 100
            total_inserted = 0
            
            for i in range(0, len(records), batch_size):
                batch = records[i:i + batch_size]
                try:
                    response = self.client.table(table_name).insert(batch).execute()
                    total_inserted += len(batch)
                    logger.info(f"Inserted batch of {len(batch)} records into {table_name}")
                except Exception as e:
                    logger.error(f"Error inserting batch into {table_name}: {e}")
            
            logger.info(f"Successfully stored {total_inserted}/{len(records)} records in {table_name}")
            return total_inserted > 0
            
        except Exception as e:
            logger.error(f"Error storing data in {table_name}: {e}")
            logger.error(traceback.format_exc())
            return False
    
    def get_today_summary(self) -> Dict[str, int]:
        """Get summary of today's deals from database"""
        summary = {}
        today = datetime.now().date().isoformat()
        
        tables = [
            Config.TABLE_NSE_BULK,
            Config.TABLE_NSE_BLOCK,
            Config.TABLE_BSE_BULK,
            Config.TABLE_BSE_BLOCK
        ]
        
        for table in tables:
            try:
                response = self.client.table(table)\
                    .select("*", count="exact")\
                    .eq("fetch_date", today)\
                    .execute()
                
                summary[table] = response.count if hasattr(response, 'count') else len(response.data)
                logger.info(f"Found {summary[table]} records in {table} for today")
                
            except Exception as e:
                logger.error(f"Error getting summary for {table}: {e}")
                summary[table] = 0
        
        return summary


# ============================================================================
# EMAIL REPORTER
# ============================================================================

class EmailReporter:
    """Handles email report generation and sending"""
    
    def __init__(self):
        if not Config.EMAIL_USER or not Config.EMAIL_PASSWORD:
            raise ValueError("Email credentials not configured")
        
        try:
            self.yag = yagmail.SMTP(Config.EMAIL_USER, Config.EMAIL_PASSWORD)
            logger.info("Email client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize email client: {e}")
            raise
    
    def send_report(self, summary: Dict[str, int], csv_files: List[str]):
        """Send daily email report"""
        try:
            today_str = datetime.now().strftime('%d %B %Y')
            subject = f"Daily Bulk & Block Deals Report - {today_str}"
            
            body = self._create_email_body(summary)
            
            attachments = csv_files if csv_files else None
            
            self.yag.send(
                to=Config.EMAIL_TO,
                subject=subject,
                contents=body,
                attachments=attachments
            )
            
            logger.info(f"Email report sent successfully to {Config.EMAIL_TO}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email report: {e}")
            logger.error(traceback.format_exc())
            return False
    
    def _create_email_body(self, summary: Dict[str, int]) -> str:
        """Create HTML email body"""
        total_deals = sum(summary.values())
        today_str = datetime.now().strftime('%d %B %Y, %I:%M %p IST')
        
        html = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f5f5f5;
                    margin: 0;
                    padding: 20px;
                }}
                .container {{
                    max-width: 800px;
                    margin: 0 auto;
                    background-color: white;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    overflow: hidden;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                }}
                .content {{
                    padding: 30px;
                }}
                .summary {{
                    background-color: #f8f9fa;
                    border-left: 4px solid #667eea;
                    padding: 20px;
                    margin: 20px 0;
                    border-radius: 5px;
                }}
                table {{
                    border-collapse: collapse;
                    width: 100%;
                    margin: 20px 0;
                }}
                th, td {{
                    padding: 15px;
                    text-align: left;
                    border-bottom: 1px solid #e0e0e0;
                }}
                th {{
                    background-color: #667eea;
                    color: white;
                    font-weight: 600;
                }}
                .total-row {{
                    font-weight: bold;
                    background-color: #f0f0f0;
                }}
                .footer {{
                    background-color: #f8f9fa;
                    padding: 20px;
                    text-align: center;
                    color: #666;
                    font-size: 13px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Daily Bulk & Block Deals Report</h1>
                    <p>Generated on: {today_str}</p>
                </div>
                
                <div class="content">
                    <div class="summary">
                        <h2>Total Deals Today: {total_deals}</h2>
                    </div>
                    
                    <table>
                        <thead>
                            <tr>
                                <th>Exchange</th>
                                <th>Deal Type</th>
                                <th>Count</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td><strong>NSE</strong></td>
                                <td>Bulk Deals</td>
                                <td>{summary.get(Config.TABLE_NSE_BULK, 0)}</td>
                            </tr>
                            <tr>
                                <td><strong>NSE</strong></td>
                                <td>Block Deals</td>
                                <td>{summary.get(Config.TABLE_NSE_BLOCK, 0)}</td>
                            </tr>
                            <tr>
                                <td><strong>BSE</strong></td>
                                <td>Bulk Deals</td>
                                <td>{summary.get(Config.TABLE_BSE_BULK, 0)}</td>
                            </tr>
                            <tr>
                                <td><strong>BSE</strong></td>
                                <td>Block Deals</td>
                                <td>{summary.get(Config.TABLE_BSE_BLOCK, 0)}</td>
                            </tr>
                            <tr class="total-row">
                                <td colspan="2">TOTAL</td>
                                <td>{total_deals}</td>
                            </tr>
                        </tbody>
                    </table>
                    
                    <p>CSV files are attached to this email for your reference.</p>
                </div>
                
                <div class="footer">
                    <p><strong>Bulk Deal Tracker Cloud</strong></p>
                    <p>Automated Reporting System</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html


# ============================================================================
# MAIN ORCHESTRATOR
# ============================================================================

class DealsAutomation:
    """Main orchestrator"""
    
    def __init__(self):
        self.nse_fetcher = NSEDataFetcher()
        self.db_manager = DatabaseManager()
        self.email_reporter = EmailReporter()
        self.csv_files = []
    
    def fetch_all_data(self) -> Dict[str, pd.DataFrame]:
        """Fetch all deals data"""
        data = {}
        
        logger.info("Fetching data from NSE...")
        data['nse_bulk'] = self.nse_fetcher.fetch_bulk_deals()
        data['nse_block'] = self.nse_fetcher.fetch_block_deals()
        
        # BSE data - placeholder for now (can add later)
        data['bse_bulk'] = None
        data['bse_block'] = None
        
        return data
    
    def save_to_csv(self, data: Dict[str, pd.DataFrame]) -> List[str]:
        """Save DataFrames to CSV files"""
        csv_files = []
        timestamp = datetime.now().strftime('%Y%m%d')
        
        mapping = {
            'nse_bulk': f'NSE_Bulk_Deals_{timestamp}.csv',
            'nse_block': f'NSE_Block_Deals_{timestamp}.csv',
        }
        
        for key, filename in mapping.items():
            df = data.get(key)
            if df is not None and not df.empty:
                try:
                    df.to_csv(filename, index=False)
                    csv_files.append(filename)
                    logger.info(f"Saved {filename} ({len(df)} records)")
                except Exception as e:
                    logger.error(f"Failed to save {filename}: {e}")
        
        return csv_files
    
    def store_all_data(self, data: Dict[str, pd.DataFrame]) -> bool:
        """Store all data to Supabase"""
        success_count = 0
        
        mapping = {
            'nse_bulk': Config.TABLE_NSE_BULK,
            'nse_block': Config.TABLE_NSE_BLOCK,
        }
        
        for key, table_name in mapping.items():
            df = data.get(key)
            if self.db_manager.store_data(df, table_name):
                success_count += 1
        
        return success_count > 0
    
    def run(self):
        """Main execution method"""
        try:
            logger.info("=" * 70)
            logger.info("STARTING DAILY BULK & BLOCK DEALS AUTOMATION")
            logger.info("=" * 70)
            logger.info(f"Execution Time: {datetime.now().strftime('%d %B %Y, %I:%M:%S %p IST')}")
            
            # Fetch data
            logger.info("\n[STEP 1/5] Fetching data...")
            data = self.fetch_all_data()
            
            # Save to CSV
            logger.info("\n[STEP 2/5] Saving to CSV...")
            self.csv_files = self.save_to_csv(data)
            
            # Store in Supabase
            logger.info("\n[STEP 3/5] Storing in Supabase...")
            self.store_all_data(data)
            
            # Get summary
            logger.info("\n[STEP 4/5] Getting summary...")
            summary = self.db_manager.get_today_summary()
            
            # Send email
            logger.info("\n[STEP 5/5] Sending email...")
            self.email_reporter.send_report(summary, self.csv_files)
            
            logger.info("\n" + "=" * 70)
            logger.info("AUTOMATION COMPLETED SUCCESSFULLY!")
            logger.info(f"Total Deals Processed: {sum(summary.values())}")
            logger.info(f"CSV Files Generated: {len(self.csv_files)}")
            logger.info("=" * 70)
            
        except Exception as e:
            logger.error(f"Fatal error: {e}")
            logger.error(traceback.format_exc())
            sys.exit(1)


# ============================================================================
# ENTRY POINT
# ============================================================================

def main():
    """Entry point"""
    try:
        automation = DealsAutomation()
        automation.run()
    except Exception as e:
        logger.error(f"Failed to initialize: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()