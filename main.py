"""
NSE/BSE Bulk and Block Deals Daily Automation Script
WITH PROPER BSE HANDLING AND INVESTOR MONITORING

CRITICAL FIXES:
1. BSE public website does NOT provide client names in bulk/block deals
2. Only NSE data includes client information for monitoring
3. Added comprehensive logging to identify data issues
4. Handles missing columns gracefully
5. Fixed column name handling (trailing spaces)

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
import requests

# ============================================================================
# CONFIGURATION
# ============================================================================

class Config:
    """Configuration class"""
    
    # Supabase Configuration
    SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://tyibyuwusjpogfknameh.supabase.co')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR5aWJ5dXd1c2pwb2dma25hbWVoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk1NDgxMDMsImV4cCI6MjA3NTEyNDEwM30.xS8SYGmUYKIG41IfnpwDkrkkPeDttADY6qSf3MRPvx8')
    
    # Email Configuration
    EMAIL_USER = os.getenv('EMAIL_USER', 'quantkingdaily@gmail.com')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', 'tsxa oiiy mztw artq')
    EMAIL_TO = os.getenv('EMAIL_TO', 'king.gerald2007@gmail.com,mahesh22an@gmail.com').split(',')
    
    # Telegram Configuration
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8272854685:AAEYFdXp0TRXpiMLaE1-7AYoyTNjE_vuvOI')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '1524238363')
    
    # Database Table Names
    TABLE_NSE_BULK = "nse_bulk_deals"
    TABLE_NSE_BLOCK = "nse_block_deals"
    TABLE_BSE_BULK = "bse_bulk_deals"
    TABLE_BSE_BLOCK = "bse_block_deals"
    TABLE_MONITORED = "monitored_investors"
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')


# ============================================================================
# LOGGING SETUP
# ============================================================================

def setup_logging():
    """Configure logging with UTF-8 encoding for Windows"""
    # Create handlers with UTF-8 encoding
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.INFO)
    
    file_handler = logging.FileHandler('deals_automation.log', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stream_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    # Get logger and add handlers
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
    
    return logger

logger = setup_logging()


# ============================================================================
# BSE DATA FETCHER
# ============================================================================

class BSEDataFetcher:
    """Fetch BSE bulk and block deals data
    
    NOTE: BSE public website does NOT include client names in bulk/block deals.
    We fetch the data for completeness but cannot monitor specific investors.
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
    
    def fetch_bulk_deals(self) -> Optional[pd.DataFrame]:
        """Fetch bulk deals from BSE"""
        try:
            logger.info("Fetching BSE bulk deals...")
            url = "https://www.bseindia.com/markets/equity/EQReports/bulk_deals.aspx?expandable=3"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            tables = pd.read_html(response.content)
            
            if not tables or len(tables) == 0:
                logger.warning("No BSE bulk deals data found")
                return None
            
            df = None
            for i, table in enumerate(tables):
                logger.debug(f"Table {i} shape: {table.shape}, columns: {table.columns.tolist()}")
                if len(table.columns) >= 3:
                    df = table
                    logger.info(f"Using table {i} for BSE bulk deals")
                    break
            
            if df is None or df.empty:
                logger.warning("No valid BSE bulk deals table found")
                return None
            
            df = self._clean_bulk_deals_data(df)
            
            if df is not None and not df.empty:
                logger.info(f"✓ Fetched {len(df)} BSE bulk deals")
                logger.info(f"  Columns: {df.columns.tolist()}")
            else:
                logger.warning("BSE bulk deals cleaning resulted in empty DataFrame")
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching BSE bulk deals: {e}")
            logger.error(traceback.format_exc())
            return None
    
    def fetch_block_deals(self) -> Optional[pd.DataFrame]:
        """Fetch block deals from BSE"""
        try:
            logger.info("Fetching BSE block deals...")
            url = "https://www.bseindia.com/markets/equity/EQReports/block_deals.aspx?expandable=3"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            tables = pd.read_html(response.content)
            
            if not tables or len(tables) == 0:
                logger.warning("No BSE block deals data found")
                return None
            
            df = None
            for i, table in enumerate(tables):
                logger.debug(f"Table {i} shape: {table.shape}, columns: {table.columns.tolist()}")
                if len(table.columns) >= 3:
                    df = table
                    logger.info(f"Using table {i} for BSE block deals")
                    break
            
            if df is None or df.empty:
                logger.warning("No valid BSE block deals table found")
                return None
            
            df = self._clean_block_deals_data(df)
            
            if df is not None and not df.empty:
                logger.info(f"✓ Fetched {len(df)} BSE block deals")
                logger.info(f"  Columns: {df.columns.tolist()}")
            else:
                logger.warning("BSE block deals cleaning resulted in empty DataFrame")
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching BSE block deals: {e}")
            logger.error(traceback.format_exc())
            return None
    
    def _clean_bulk_deals_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize bulk deals data"""
        logger.debug(f"BSE bulk deals raw columns: {df.columns.tolist()}")
        
        # Strip spaces from column names
        df.columns = df.columns.str.strip()
        
        # Map columns
        column_mapping = {
            'Deal Date': 'deal_date',
            'Security Code': 'scrip_code',
            'Security Name': 'scrip_name',
            'Client Name': 'client_name',
            'Deal Type *': 'buy_sell',
            'Deal Type': 'buy_sell',
            'Quantity': 'quantity_traded',
            'Price **': 'trade_price',
            'Price': 'trade_price',
            'Trade Price': 'trade_price'  # Fix for BSE block deals
        }
        
        existing_cols = {k: v for k, v in column_mapping.items() if k in df.columns}
        df = df.rename(columns=existing_cols)
        
        logger.info(f"BSE bulk deals mapped columns: {df.columns.tolist()}")
        
        # BSE does NOT provide client_name - add empty column
        if 'client_name' not in df.columns:
            logger.warning("⚠️  BSE bulk deals do NOT include client names (this is normal)")
            logger.warning("    Investor monitoring will only work for NSE data")
            df['client_name'] = ''
        
        # Parse date and filter to today only
        if 'deal_date' in df.columns:
            df['deal_date'] = pd.to_datetime(df['deal_date'], format='%d/%m/%Y', errors='coerce').dt.date
            
            # Verify and filter to today's data
            unique_dates = df['deal_date'].unique()
            logger.info(f"  BSE bulk data dates: {unique_dates}")
            
            today = datetime.now().date()
            today_deals = df[df['deal_date'] == today]
            old_deals = df[df['deal_date'] != today]
            
            if len(old_deals) > 0:
                logger.warning(f"  ⚠️  Found {len(old_deals)} BSE bulk deals from other dates - filtering to today only")
                df = today_deals
        else:
            df['deal_date'] = datetime.now().date()
        
        # Add metadata
        df['fetch_date'] = datetime.now().date()
        df['source'] = 'BSE'
        df['deal_category'] = 'BULK'
        
        # Normalize buy/sell
        if 'buy_sell' in df.columns:
            df['buy_sell'] = df['buy_sell'].astype(str).str.upper().str.strip()
            df['buy_sell'] = df['buy_sell'].replace({'B': 'BUY', 'S': 'SELL'})
        
        # Clean quantity
        if 'quantity_traded' in df.columns:
            df['quantity_traded'] = df['quantity_traded'].astype(str).str.replace(',', '').str.replace(' ', '')
            df['quantity_traded'] = pd.to_numeric(df['quantity_traded'], errors='coerce')
        
        # Clean price
        if 'trade_price' in df.columns:
            df['trade_price'] = df['trade_price'].astype(str).str.replace(',', '').str.replace(' ', '')
            df['trade_price'] = pd.to_numeric(df['trade_price'], errors='coerce')
        
        logger.info(f"✓ Processed {len(df)} BSE bulk deals for TODAY")
        return df
    
    def _clean_block_deals_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize block deals data"""
        logger.debug(f"BSE block deals raw columns: {df.columns.tolist()}")
        
        # Strip spaces from column names
        df.columns = df.columns.str.strip()
        
        column_mapping = {
            'Deal Date': 'deal_date',
            'Security Code': 'scrip_code',
            'Security Name': 'scrip_name',
            'Client Name': 'client_name',
            'Deal Type *': 'buy_sell',
            'Deal Type': 'buy_sell',
            'Quantity': 'quantity_traded',
            'Price **': 'trade_price',
            'Price': 'trade_price'
        }
        
        existing_cols = {k: v for k, v in column_mapping.items() if k in df.columns}
        df = df.rename(columns=existing_cols)
        
        logger.info(f"BSE block deals mapped columns: {df.columns.tolist()}")
        
        # BSE does NOT provide client_name
        if 'client_name' not in df.columns:
            logger.warning("⚠️  BSE block deals do NOT include client names (this is normal)")
            logger.warning("    Investor monitoring will only work for NSE data")
            df['client_name'] = ''
        
        # Parse date and filter to today only
        if 'deal_date' in df.columns:
            df['deal_date'] = pd.to_datetime(df['deal_date'], format='%d/%m/%Y', errors='coerce').dt.date
            
            # Verify and filter to today's data
            unique_dates = df['deal_date'].unique()
            logger.info(f"  BSE block data dates: {unique_dates}")
            
            today = datetime.now().date()
            today_deals = df[df['deal_date'] == today]
            old_deals = df[df['deal_date'] != today]
            
            if len(old_deals) > 0:
                logger.warning(f"  ⚠️  Found {len(old_deals)} BSE block deals from other dates - filtering to today only")
                df = today_deals
        else:
            df['deal_date'] = datetime.now().date()
        
        df['fetch_date'] = datetime.now().date()
        df['source'] = 'BSE'
        df['deal_category'] = 'BLOCK'
        
        if 'buy_sell' in df.columns:
            df['buy_sell'] = df['buy_sell'].astype(str).str.upper().str.strip()
            df['buy_sell'] = df['buy_sell'].replace({'B': 'BUY', 'S': 'SELL'})
        
        if 'quantity_traded' in df.columns:
            df['quantity_traded'] = df['quantity_traded'].astype(str).str.replace(',', '').str.replace(' ', '')
            df['quantity_traded'] = pd.to_numeric(df['quantity_traded'], errors='coerce')
        
        if 'trade_price' in df.columns:
            df['trade_price'] = df['trade_price'].astype(str).str.replace(',', '').str.replace(' ', '')
            df['trade_price'] = pd.to_numeric(df['trade_price'], errors='coerce')
        
        logger.info(f"✓ Processed {len(df)} BSE block deals for TODAY")
        return df


# ============================================================================
# NSE DATA FETCHER
# ============================================================================

class NSEDataFetcher:
    """Fetch NSE data using nsepython library
    
    NOTE: NSE API returns only TODAY's deals by default.
    """
    
    def fetch_bulk_deals(self) -> Optional[pd.DataFrame]:
        """Fetch bulk deals from NSE (today's data only)"""
        try:
            logger.info("Fetching NSE bulk deals...")
            df = get_bulkdeals()
            
            if isinstance(df, pd.DataFrame) and not df.empty:
                # Strip spaces from column names
                df.columns = df.columns.str.strip()
                
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
                
                # Parse deal_date to verify it's today's data
                if 'deal_date' in df.columns:
                    df['deal_date'] = pd.to_datetime(df['deal_date'], format='%d-%b-%Y', errors='coerce').dt.date
                    
                    # Log date range for verification
                    unique_dates = df['deal_date'].unique()
                    logger.info(f"  Data dates: {unique_dates}")
                    
                    today = datetime.now().date()
                    today_deals = df[df['deal_date'] == today]
                    old_deals = df[df['deal_date'] != today]
                    
                    if len(old_deals) > 0:
                        logger.warning(f"  ⚠️  Found {len(old_deals)} deals from other dates - filtering to today only")
                        df = today_deals
                
                df['fetch_date'] = datetime.now().date()
                df['source'] = 'NSE'
                df['deal_category'] = 'BULK'
                
                # Normalize client names for matching
                if 'client_name' in df.columns:
                    df['client_name'] = df['client_name'].astype(str).str.strip().str.upper()
                
                logger.info(f"✓ Fetched {len(df)} NSE bulk deals for TODAY")
                if 'client_name' in df.columns and len(df) > 0:
                    logger.info(f"  Sample clients: {df['client_name'].head(3).tolist()}")
                return df
            else:
                logger.warning("No NSE bulk deals data available for today")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching NSE bulk deals: {e}")
            logger.error(traceback.format_exc())
            return None
    
    def fetch_block_deals(self) -> Optional[pd.DataFrame]:
        """Fetch block deals from NSE (today's data only)"""
        try:
            logger.info("Fetching NSE block deals...")
            df = get_blockdeals()
            
            if isinstance(df, pd.DataFrame) and not df.empty:
                df.columns = df.columns.str.strip()
                
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
                
                # Parse deal_date to verify it's today's data
                if 'deal_date' in df.columns:
                    df['deal_date'] = pd.to_datetime(df['deal_date'], format='%d-%b-%Y', errors='coerce').dt.date
                    
                    # Log date range for verification
                    unique_dates = df['deal_date'].unique()
                    logger.info(f"  Data dates: {unique_dates}")
                    
                    today = datetime.now().date()
                    today_deals = df[df['deal_date'] == today]
                    old_deals = df[df['deal_date'] != today]
                    
                    if len(old_deals) > 0:
                        logger.warning(f"  ⚠️  Found {len(old_deals)} deals from other dates - filtering to today only")
                        df = today_deals
                
                df['fetch_date'] = datetime.now().date()
                df['source'] = 'NSE'
                df['deal_category'] = 'BLOCK'
                
                if 'client_name' in df.columns:
                    df['client_name'] = df['client_name'].astype(str).str.strip().str.upper()
                
                logger.info(f"✓ Fetched {len(df)} NSE block deals for TODAY")
                if 'client_name' in df.columns and len(df) > 0:
                    logger.info(f"  Sample clients: {df['client_name'].head(3).tolist()}")
                return df
            else:
                logger.warning("No NSE block deals data available for today")
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
    
    def get_monitored_investors(self) -> List[Dict[str, str]]:
        """Get list of monitored investors with their details"""
        try:
            response = self.client.table(Config.TABLE_MONITORED)\
                .select("investor_name, display_name, category, priority")\
                .eq("is_active", True)\
                .execute()
            
            investors = []
            for row in response.data:
                investors.append({
                    'name': row['investor_name'].strip().upper(),
                    'display_name': row.get('display_name', row['investor_name']),
                    'category': row.get('category', ''),
                    'priority': row.get('priority', 0)
                })
            
            logger.info(f"✓ Loaded {len(investors)} active monitored investors")
            for inv in investors:
                logger.debug(f"  Monitoring: '{inv['name']}'")
            
            return investors
            
        except Exception as e:
            logger.error(f"Error fetching monitored investors: {e}")
            logger.error(traceback.format_exc())
            return []
    
    def store_data(self, df: pd.DataFrame, table_name: str) -> bool:
        """Store DataFrame to Supabase table"""
        try:
            if df is None or df.empty:
                logger.warning(f"No data to store in {table_name}")
                return False
            
            records = df.to_dict('records')
            
            for record in records:
                for key, value in record.items():
                    if pd.isna(value):
                        record[key] = None
                    elif hasattr(value, 'item'):
                        record[key] = value.item()
                    elif isinstance(value, (datetime, pd.Timestamp)):
                        record[key] = value.date().isoformat()
                    elif hasattr(value, 'isoformat'):
                        record[key] = value.isoformat()
            
            batch_size = 100
            total_inserted = 0
            
            for i in range(0, len(records), batch_size):
                batch = records[i:i + batch_size]
                try:
                    self.client.table(table_name).insert(batch).execute()
                    total_inserted += len(batch)
                    logger.debug(f"Inserted batch of {len(batch)} records into {table_name}")
                except Exception as e:
                    logger.error(f"Error inserting batch into {table_name}: {e}")
            
            logger.info(f"✓ Stored {total_inserted}/{len(records)} records in {table_name}")
            return total_inserted > 0
            
        except Exception as e:
            logger.error(f"Error storing data in {table_name}: {e}")
            logger.error(traceback.format_exc())
            return False
    
    def get_today_summary(self) -> Dict[str, int]:
        """Get summary of today's deals from database"""
        summary = {}
        today = datetime.now().date().isoformat()
        
        tables = [Config.TABLE_NSE_BULK, Config.TABLE_NSE_BLOCK, 
                  Config.TABLE_BSE_BULK, Config.TABLE_BSE_BLOCK]
        
        for table in tables:
            try:
                response = self.client.table(table)\
                    .select("*", count="exact")\
                    .eq("fetch_date", today)\
                    .execute()
                summary[table] = response.count if hasattr(response, 'count') else len(response.data)
            except Exception as e:
                logger.error(f"Error getting summary for {table}: {e}")
                summary[table] = 0
        
        return summary


# ============================================================================
# INVESTOR MONITOR
# ============================================================================

class InvestorMonitor:
    """Monitor deals for specific investors"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.monitored_investors = []
    
    def load_monitored_investors(self):
        """Load list of monitored investors"""
        self.monitored_investors = self.db_manager.get_monitored_investors()
        logger.info(f"Loaded {len(self.monitored_investors)} active monitored investors")
    
    def find_monitored_deals(self, data: Dict[str, pd.DataFrame]) -> List[Dict]:
        """Find deals involving monitored investors"""
        monitored_deals = []
        
        if not self.monitored_investors:
            logger.warning("No monitored investors configured")
            return monitored_deals
        
        logger.info("=" * 70)
        logger.info("CHECKING FOR MONITORED INVESTOR ACTIVITY")
        logger.info("=" * 70)
        
        # Check NSE bulk deals
        if data.get('nse_bulk') is not None and not data['nse_bulk'].empty:
            df = data['nse_bulk']
            logger.info(f"\nChecking NSE bulk deals ({len(df)} total deals)...")
            
            if 'client_name' not in df.columns:
                logger.error("❌ NSE bulk deals missing client_name column!")
            else:
                for investor in self.monitored_investors:
                    matches = df[df['client_name'].str.contains(investor['name'], na=False, case=False)]
                    if len(matches) > 0:
                        logger.info(f"  ✓ MATCH: {investor['display_name']} - {len(matches)} deals")
                        for _, row in matches.iterrows():
                            monitored_deals.append({
                                'investor': investor['display_name'],
                                'investor_category': investor['category'],
                                'priority': investor['priority'],
                                'deal_type': 'BULK',
                                'source': 'NSE',
                                'date': row.get('deal_date', ''),
                                'symbol': row.get('symbol', ''),
                                'security_name': row.get('security_name', ''),
                                'action': row.get('buy_sell', ''),
                                'quantity': row.get('quantity_traded', 0),
                                'price': row.get('trade_price', 0),
                                'remarks': row.get('remarks', '')
                            })
        
        # Check NSE block deals
        if data.get('nse_block') is not None and not data['nse_block'].empty:
            df = data['nse_block']
            logger.info(f"\nChecking NSE block deals ({len(df)} total deals)...")
            
            if 'client_name' not in df.columns:
                logger.error("❌ NSE block deals missing client_name column!")
            else:
                for investor in self.monitored_investors:
                    matches = df[df['client_name'].str.contains(investor['name'], na=False, case=False)]
                    if len(matches) > 0:
                        logger.info(f"  ✓ MATCH: {investor['display_name']} - {len(matches)} deals")
                        for _, row in matches.iterrows():
                            monitored_deals.append({
                                'investor': investor['display_name'],
                                'investor_category': investor['category'],
                                'priority': investor['priority'],
                                'deal_type': 'BLOCK',
                                'source': 'NSE',
                                'date': row.get('deal_date', ''),
                                'symbol': row.get('symbol', ''),
                                'security_name': row.get('security_name', ''),
                                'action': row.get('buy_sell', ''),
                                'quantity': row.get('quantity_traded', 0),
                                'price': row.get('trade_price', 0),
                                'remarks': ''
                            })
        
        # BSE deals are skipped for monitoring
        if data.get('bse_bulk') is not None or data.get('bse_block') is not None:
            logger.warning("\n⚠️  BSE deals cannot be monitored (no client names in public data)")
        
        monitored_deals.sort(key=lambda x: x['priority'], reverse=True)
        
        logger.info("\n" + "=" * 70)
        if monitored_deals:
            logger.info(f"✓ FOUND {len(monitored_deals)} DEALS FROM MONITORED INVESTORS!")
        else:
            logger.info("No deals from monitored investors today")
        logger.info("=" * 70 + "\n")
        
        return monitored_deals


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
    
    def send_report(self, summary: Dict[str, int], csv_files: List[str], monitored_deals: List[Dict] = None):
        """Send daily email report with investor alerts"""
        try:
            today_str = datetime.now().strftime('%d %B %Y')
            
            if monitored_deals:
                subject = f"🚨 ALERT: Monitored Investor Activity - {today_str}"
            else:
                subject = f"Daily Bulk & Block Deals Report - {today_str}"
            
            body = self._create_email_body(summary, monitored_deals)
            
            self.yag.send(to=Config.EMAIL_TO, subject=subject, contents=body)
            logger.info(f"✓ Email report sent successfully to {Config.EMAIL_TO}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email report: {e}")
            logger.error(traceback.format_exc())
            return False
    
    def _create_monitored_deals_html(self, monitored_deals: List[Dict]) -> str:
        """Create HTML for monitored investor deals"""
        if not monitored_deals:
            return ""
        
        deal_date_str = datetime.now().strftime('%d %B %Y')
        
        html = f"""
        <div style="background-color: #fff3cd; border-left: 5px solid #ff6b6b; padding: 15px; margin: 0 0 15px 0; border-radius: 5px;">
            <h2 style="color: #d32f2f; margin: 0 0 5px 0; font-size: 18px;">🚨 INVESTOR ALERT!</h2>
            <p style="font-size: 13px; color: #666; margin: 0 0 10px 0;">
                Your monitored investors made <strong>{len(monitored_deals)} trades</strong> on <strong>{deal_date_str}</strong>:
            </p>
            <table style="width: 100%; border-collapse: collapse; background-color: white; margin: 0;">
                <thead>
                    <tr style="background-color: #d32f2f; color: white;">
                        <th style="padding: 8px; text-align: left; font-size: 13px;">Date</th>
                        <th style="padding: 8px; text-align: left; font-size: 13px;">Investor</th>
                        <th style="padding: 8px; text-align: left; font-size: 13px;">Stock</th>
                        <th style="padding: 8px; text-align: left; font-size: 13px;">Action</th>
                        <th style="padding: 8px; text-align: right; font-size: 13px;">Quantity</th>
                        <th style="padding: 8px; text-align: right; font-size: 13px;">Price</th>
                        <th style="padding: 8px; text-align: center; font-size: 13px;">Type</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for deal in monitored_deals:
            action_color = "#4caf50" if deal['action'].upper() == 'BUY' else "#f44336"
            category_badge = f"<br><small style='color: #999; font-size: 11px;'>{deal['investor_category']}</small>" if deal['investor_category'] else ""
            
            # Format date
            deal_date_formatted = deal['date'].strftime('%d-%b') if hasattr(deal['date'], 'strftime') else str(deal['date'])
            
            html += f"""
                <tr style="border-bottom: 1px solid #e0e0e0;">
                    <td style="padding: 8px; font-size: 12px; color: #666;">{deal_date_formatted}</td>
                    <td style="padding: 8px; font-size: 13px;"><strong>{deal['investor']}</strong>{category_badge}</td>
                    <td style="padding: 8px; font-size: 13px;">{deal['symbol']}<br><small style="color: #666; font-size: 11px;">{deal['security_name'][:40]}...</small></td>
                    <td style="padding: 8px; color: {action_color}; font-weight: bold; font-size: 13px;">{deal['action']}</td>
                    <td style="padding: 8px; text-align: right; font-size: 13px;">{deal['quantity']:,.0f}</td>
                    <td style="padding: 8px; text-align: right; font-size: 13px;">₹{deal['price']:,.2f}</td>
                    <td style="padding: 8px; text-align: center; font-size: 11px;">
                        <span style="background-color: #e3f2fd; padding: 3px 6px; border-radius: 3px;">{deal['source']} {deal['deal_type']}</span>
                    </td>
                </tr>
            """
        
        html += """
                </tbody>
            </table>
        </div>
        """
        return html
    
    def _create_email_body(self, summary: Dict[str, int], monitored_deals: List[Dict] = None) -> str:
        """Create HTML email body"""
        today_str = datetime.now().strftime('%d %B %Y, %I:%M %p IST')
        deal_date_str = datetime.now().strftime('%d %B %Y')
        
        monitored_html = self._create_monitored_deals_html(monitored_deals) if monitored_deals else ""
        
        # Create summary table
        total_deals = sum(summary.values())
        summary_html = f"""
        <div style="background-color: #f8f9fa; padding: 15px; margin: 15px 0; border-radius: 5px;">
            <h3 style="margin: 0 0 10px 0; font-size: 16px; color: #333;">📊 Today's Market Activity Summary</h3>
            <p style="margin: 0 0 10px 0; font-size: 13px; color: #666;"><strong>Deal Date:</strong> {deal_date_str}</p>
            <table style="width: 100%; border-collapse: collapse; background-color: white; border-radius: 5px;">
                <thead>
                    <tr style="background-color: #667eea; color: white;">
                        <th style="padding: 10px; text-align: left; font-size: 13px; border-radius: 5px 0 0 0;">Exchange</th>
                        <th style="padding: 10px; text-align: center; font-size: 13px;">Bulk Deals</th>
                        <th style="padding: 10px; text-align: center; font-size: 13px; border-radius: 0 5px 0 0;">Block Deals</th>
                    </tr>
                </thead>
                <tbody>
                    <tr style="border-bottom: 1px solid #e0e0e0;">
                        <td style="padding: 10px; font-size: 13px; font-weight: bold;">NSE</td>
                        <td style="padding: 10px; text-align: center; font-size: 13px;">{summary.get(Config.TABLE_NSE_BULK, 0)}</td>
                        <td style="padding: 10px; text-align: center; font-size: 13px;">{summary.get(Config.TABLE_NSE_BLOCK, 0)}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #e0e0e0;">
                        <td style="padding: 10px; font-size: 13px; font-weight: bold;">BSE</td>
                        <td style="padding: 10px; text-align: center; font-size: 13px;">{summary.get(Config.TABLE_BSE_BULK, 0)}</td>
                        <td style="padding: 10px; text-align: center; font-size: 13px;">{summary.get(Config.TABLE_BSE_BLOCK, 0)}</td>
                    </tr>
                    <tr style="background-color: #f8f9fa; font-weight: bold;">
                        <td style="padding: 10px; font-size: 14px; border-radius: 0 0 0 5px;">Total</td>
                        <td style="padding: 10px; text-align: center; font-size: 14px;">{summary.get(Config.TABLE_NSE_BULK, 0) + summary.get(Config.TABLE_BSE_BULK, 0)}</td>
                        <td style="padding: 10px; text-align: center; font-size: 14px; border-radius: 0 0 5px 0;">{summary.get(Config.TABLE_NSE_BLOCK, 0) + summary.get(Config.TABLE_BSE_BLOCK, 0)}</td>
                    </tr>
                </tbody>
            </table>
            <p style="margin: 10px 0 0 0; font-size: 12px; color: #999; text-align: center;">
                <strong>Grand Total: {total_deals} deals</strong> processed for {deal_date_str}
            </p>
        </div>
        """
        
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #f5f5f5; margin: 0; padding: 5px; }}
                .container {{ max-width: 800px; margin: 0 auto; background-color: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); overflow: hidden; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px; text-align: center; }}
                .header h1 {{ margin: 0; font-size: 20px; }}
                .header p {{ margin: 3px 0 0 0; font-size: 12px; opacity: 0.9; }}
                .content {{ padding: 15px; }}
                .footer {{ background-color: #f8f9fa; padding: 10px; text-align: center; color: #666; font-size: 11px; margin: 0; }}
                .footer p {{ margin: 3px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📈 Daily Bulk & Block Deals Report</h1>
                    <p>Report Generated: {today_str}</p>
                    <p style="font-size: 14px; margin-top: 5px;"><strong>Deal Date: {deal_date_str}</strong></p>
                </div>
                <div class="content">
                    {monitored_html if monitored_html else ''}
                    {summary_html}
                    {'<p style="text-align: center; color: #666; padding: 10px 0; margin: 10px 0 0 0; font-size: 12px; background-color: #fff3cd; border-radius: 5px;">ℹ️ Note: BSE deals do not include client names in public data</p>' if not monitored_html else '<p style="text-align: center; color: #666; padding: 10px 0; margin: 10px 0 0 0; font-size: 12px; background-color: #e8f5e9; border-radius: 5px;">✓ Full report with investor alerts above</p>'}
                </div>
                <div class="footer">
                    <p><strong>Bulk Deal Tracker Cloud</strong></p>
                    <p>Automated Reporting System | NSE + BSE Data | Deal Date: {deal_date_str}</p>
                </div>
            </div>
        </body>
        </html>
        """
        return html


# ============================================================================
# TELEGRAM NOTIFIER
# ============================================================================

class TelegramNotifier:
    """Handles Telegram notifications"""
    
    def __init__(self):
        self.bot_token = Config.TELEGRAM_BOT_TOKEN
        self.chat_id = Config.TELEGRAM_CHAT_ID
        
        if not self.bot_token or not self.chat_id:
            logger.warning("Telegram credentials not configured - notifications disabled")
            self.enabled = False
        else:
            self.enabled = True
            logger.info("Telegram notifier initialized successfully")
    
    def send_message(self, message: str) -> bool:
        """Send a message via Telegram"""
        if not self.enabled:
            logger.info("Telegram notifications disabled - skipping")
            return False
        
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            
            response = requests.post(url, json={
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'Markdown',
                'disable_web_page_preview': True
            }, timeout=10)
            
            if response.status_code == 200:
                logger.info("✓ Telegram notification sent successfully")
                return True
            else:
                logger.error(f"Telegram send failed: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
            return False
    
    def send_daily_summary(self, summary: Dict[str, int], monitored_deals: List[Dict] = None):
        """Send daily summary via Telegram"""
        today_str = datetime.now().strftime('%d %B %Y, %I:%M %p IST')
        
        message = f"*📊 Daily Bulk & Block Deals Report*\n"
        message += f"_{today_str}_\n\n"
        
        if monitored_deals and len(monitored_deals) > 0:
            message += f"*🚨 INVESTOR ALERT!*\n"
            message += f"Found {len(monitored_deals)} deals from monitored investors\n\n"
            
            for deal in monitored_deals[:5]:
                action_emoji = "🟢" if deal['action'].upper() == 'BUY' else "🔴"
                message += f"{action_emoji} *{deal['investor']}*\n"
                message += f"   {deal['action']} {deal['symbol']}\n"
                message += f"   Qty: {deal['quantity']:,.0f} @ ₹{deal['price']:,.2f}\n"
                message += f"   Type: {deal['source']} {deal['deal_type']}\n\n"
            
            if len(monitored_deals) > 5:
                message += f"_...and {len(monitored_deals) - 5} more deals_\n\n"
        else:
            message += "✓ No monitored investor activity today\n\n"
        
        message += f"*Summary:*\n"
        message += f"NSE Bulk: {summary.get(Config.TABLE_NSE_BULK, 0)}\n"
        message += f"NSE Block: {summary.get(Config.TABLE_NSE_BLOCK, 0)}\n"
        message += f"BSE Bulk: {summary.get(Config.TABLE_BSE_BULK, 0)}\n"
        message += f"BSE Block: {summary.get(Config.TABLE_BSE_BLOCK, 0)}\n"
        
        self.send_message(message)


# ============================================================================
# MAIN ORCHESTRATOR
# ============================================================================

class DealsAutomation:
    """Main orchestrator with investor monitoring and notifications"""
    
    def __init__(self):
        self.nse_fetcher = NSEDataFetcher()
        self.bse_fetcher = BSEDataFetcher()
        self.db_manager = DatabaseManager()
        self.investor_monitor = InvestorMonitor(self.db_manager)
        self.email_reporter = EmailReporter()
        self.telegram_notifier = TelegramNotifier()
        self.csv_files = []
        self.monitored_deals = []
    
    def fetch_all_data(self) -> Dict[str, pd.DataFrame]:
        """Fetch all deals data"""
        data = {}
        logger.info("\nFetching data from NSE...")
        data['nse_bulk'] = self.nse_fetcher.fetch_bulk_deals()
        data['nse_block'] = self.nse_fetcher.fetch_block_deals()
        
        logger.info("\nFetching data from BSE...")
        data['bse_bulk'] = self.bse_fetcher.fetch_bulk_deals()
        data['bse_block'] = self.bse_fetcher.fetch_block_deals()
        
        return data
    
    def save_to_csv(self, data: Dict[str, pd.DataFrame]) -> List[str]:
        """Save DataFrames to CSV files"""
        csv_files = []
        timestamp = datetime.now().strftime('%Y%m%d')
        
        mapping = {
            'nse_bulk': f'NSE_Bulk_Deals_{timestamp}.csv',
            'nse_block': f'NSE_Block_Deals_{timestamp}.csv',
            'bse_bulk': f'BSE_Bulk_Deals_{timestamp}.csv',
            'bse_block': f'BSE_Block_Deals_{timestamp}.csv',
        }
        
        for key, filename in mapping.items():
            df = data.get(key)
            if df is not None and not df.empty:
                try:
                    df.to_csv(filename, index=False)
                    csv_files.append(filename)
                    logger.info(f"✓ Saved {filename} ({len(df)} records)")
                except Exception as e:
                    logger.error(f"Failed to save {filename}: {e}")
        
        return csv_files
    
    def store_all_data(self, data: Dict[str, pd.DataFrame]) -> bool:
        """Store all data to Supabase"""
        success_count = 0
        
        mapping = {
            'nse_bulk': Config.TABLE_NSE_BULK,
            'nse_block': Config.TABLE_NSE_BLOCK,
            'bse_bulk': Config.TABLE_BSE_BULK,
            'bse_block': Config.TABLE_BSE_BLOCK,
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
            logger.info("WITH BSE SUPPORT, INVESTOR MONITORING, AND TELEGRAM")
            logger.info("=" * 70)
            logger.info(f"Execution Time: {datetime.now().strftime('%d %B %Y, %I:%M:%S %p IST')}")
            logger.info("=" * 70)
            
            logger.info("\n[STEP 1/7] Loading monitored investors...")
            self.investor_monitor.load_monitored_investors()
            
            logger.info("\n[STEP 2/7] Fetching data from NSE and BSE...")
            data = self.fetch_all_data()
            
            logger.info("\n[STEP 3/7] Checking for monitored investor activity...")
            self.monitored_deals = self.investor_monitor.find_monitored_deals(data)
            
            if self.monitored_deals:
                logger.info(f"\n🚨 ALERT: Found {len(self.monitored_deals)} deals from monitored investors!")
                for deal in self.monitored_deals[:5]:
                    logger.info(f"  - {deal['investor']}: {deal['action']} {deal['symbol']}")
            
            logger.info("\n[STEP 4/7] Saving to CSV...")
            self.csv_files = self.save_to_csv(data)
            
            logger.info("\n[STEP 5/7] Storing in Supabase...")
            self.store_all_data(data)
            
            logger.info("\n[STEP 6/7] Generating report...")
            summary = self.db_manager.get_today_summary()
            
            logger.info("\n[STEP 7/7] Sending notifications...")
            logger.info("Sending email report...")
            self.email_reporter.send_report(summary, self.csv_files, self.monitored_deals)
            
            logger.info("Sending Telegram notification...")
            self.telegram_notifier.send_daily_summary(summary, self.monitored_deals)
            
            logger.info("\n" + "=" * 70)
            logger.info("✓ AUTOMATION COMPLETED SUCCESSFULLY!")
            logger.info("=" * 70)
            logger.info(f"Total Deals Processed: {sum(summary.values())}")
            logger.info(f"  - NSE Bulk: {summary.get(Config.TABLE_NSE_BULK, 0)}")
            logger.info(f"  - NSE Block: {summary.get(Config.TABLE_NSE_BLOCK, 0)}")
            logger.info(f"  - BSE Bulk: {summary.get(Config.TABLE_BSE_BULK, 0)}")
            logger.info(f"  - BSE Block: {summary.get(Config.TABLE_BSE_BLOCK, 0)}")
            logger.info(f"Monitored Investor Alerts: {len(self.monitored_deals)}")
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