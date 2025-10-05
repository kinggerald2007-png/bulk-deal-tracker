"""
NSE/BSE Bulk and Block Deals Daily Automation Script
WITH BSE SUPPORT AND INVESTOR MONITORING ALERTS
Repository: https://github.com/kinggerald2007-png/bulk-deal-tracker-cloud
"""

import os
import sys
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
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
    EMAIL_USER = os.getenv('EMAIL_USER', 'king.gerald2007@gmail.com')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', 'osms grsv iorx hjan')
    EMAIL_TO = os.getenv('EMAIL_TO', 'king.gerald2007@gmail.com,mahesh22an@gmail.com').split(',')
    
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
# BSE DATA FETCHER
# ============================================================================

class BSEDataFetcher:
    """Fetch BSE bulk and block deals data"""
    
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
            
            # Try to get the main table - BSE might have multiple tables
            df = None
            for i, table in enumerate(tables):
                logger.info(f"Table {i} shape: {table.shape}, columns: {table.columns.tolist()}")
                # Look for table with proper structure (multiple columns)
                if len(table.columns) > 3:
                    df = table
                    logger.info(f"Using table {i} for bulk deals")
                    break
            
            if df is None or df.empty:
                logger.warning("No valid BSE bulk deals table found")
                return None
            
            df = self._clean_bulk_deals_data(df)
            
            logger.info(f"Fetched {len(df)} BSE bulk deals")
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
            
            df = tables[0]
            
            if df.empty:
                logger.warning("BSE block deals table is empty")
                return None
            
            df = self._clean_block_deals_data(df)
            
            logger.info(f"Fetched {len(df)} BSE block deals")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching BSE block deals: {e}")
            logger.error(traceback.format_exc())
            return None
    
    def _clean_bulk_deals_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize bulk deals data"""
        
        # First, let's see what columns we actually have
        logger.info(f"BSE bulk deals columns: {df.columns.tolist()}")
        
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
        
        # Ensure client_name exists
        if 'client_name' not in df.columns:
            logger.warning("client_name column not found in BSE bulk deals, adding empty column")
            df['client_name'] = ''
        
        # Parse deal_date if it exists
        if 'deal_date' in df.columns:
            df['deal_date'] = pd.to_datetime(df['deal_date'], format='%d/%m/%Y', errors='coerce').dt.date
        else:
            df['deal_date'] = datetime.now().date()
        
        df['fetch_date'] = datetime.now().date()
        df['source'] = 'BSE'
        df['deal_category'] = 'BULK'
        
        # Clean buy_sell - convert B/S to BUY/SELL
        if 'buy_sell' in df.columns:
            df['buy_sell'] = df['buy_sell'].str.upper().replace({'B': 'BUY', 'S': 'SELL'})
        
        # Clean quantity - remove commas
        if 'quantity_traded' in df.columns:
            df['quantity_traded'] = df['quantity_traded'].astype(str).str.replace(',', '')
            df['quantity_traded'] = pd.to_numeric(df['quantity_traded'], errors='coerce')
        
        # Clean price
        if 'trade_price' in df.columns:
            df['trade_price'] = pd.to_numeric(df['trade_price'], errors='coerce')
        
        return df
    
    def _clean_block_deals_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize block deals data"""
        
        # First, let's see what columns we actually have
        logger.info(f"BSE block deals columns: {df.columns.tolist()}")
        
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
        
        # Ensure client_name exists
        if 'client_name' not in df.columns:
            logger.warning("client_name column not found in BSE block deals, adding empty column")
            df['client_name'] = ''
        
        # Parse deal_date if it exists
        if 'deal_date' in df.columns:
            df['deal_date'] = pd.to_datetime(df['deal_date'], format='%d/%m/%Y', errors='coerce').dt.date
        else:
            df['deal_date'] = datetime.now().date()
        
        df['fetch_date'] = datetime.now().date()
        df['source'] = 'BSE'
        df['deal_category'] = 'BLOCK'
        
        # Clean buy_sell - convert B/S to BUY/SELL
        if 'buy_sell' in df.columns:
            df['buy_sell'] = df['buy_sell'].str.upper().replace({'B': 'BUY', 'S': 'SELL'})
        
        # Clean quantity - remove commas
        if 'quantity_traded' in df.columns:
            df['quantity_traded'] = df['quantity_traded'].astype(str).str.replace(',', '')
            df['quantity_traded'] = pd.to_numeric(df['quantity_traded'], errors='coerce')
        
        # Clean price
        if 'trade_price' in df.columns:
            df['trade_price'] = pd.to_numeric(df['trade_price'], errors='coerce')
        
        return df


# ============================================================================
# NSE DATA FETCHER
# ============================================================================

class NSEDataFetcher:
    """Fetch NSE data using nsepython library"""
    
    def fetch_bulk_deals(self) -> Optional[pd.DataFrame]:
        """Fetch bulk deals from NSE"""
        try:
            logger.info("Fetching NSE bulk deals...")
            df = get_bulkdeals()
            
            if isinstance(df, pd.DataFrame) and not df.empty:
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
                    'name': row['investor_name'].upper(),
                    'display_name': row.get('display_name', row['investor_name']),
                    'category': row.get('category', ''),
                    'priority': row.get('priority', 0)
                })
            
            logger.info(f"Found {len(investors)} active monitored investors")
            return investors
            
        except Exception as e:
            logger.error(f"Error fetching monitored investors: {e}")
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
        
        # Check NSE bulk deals
        if data.get('nse_bulk') is not None:
            df = data['nse_bulk']
            for investor in self.monitored_investors:
                matches = df[df['client_name'].str.upper().str.contains(investor['name'], na=False)]
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
        if data.get('nse_block') is not None:
            df = data['nse_block']
            for investor in self.monitored_investors:
                matches = df[df['client_name'].str.upper().str.contains(investor['name'], na=False)]
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
        
        # Check BSE bulk deals
        if data.get('bse_bulk') is not None:
            df = data['bse_bulk']
            # Safety check - ensure client_name column exists
            if 'client_name' not in df.columns:
                logger.warning("Skipping BSE bulk deals monitoring - client_name column missing")
            else:
                for investor in self.monitored_investors:
                    matches = df[df['client_name'].str.upper().str.contains(investor['name'], na=False)]
                    for _, row in matches.iterrows():
                        monitored_deals.append({
                            'investor': investor['display_name'],
                            'investor_category': investor['category'],
                            'priority': investor['priority'],
                            'deal_type': 'BULK',
                            'source': 'BSE',
                            'date': row.get('deal_date', ''),
                            'symbol': row.get('scrip_code', ''),
                            'security_name': row.get('scrip_name', ''),
                            'action': row.get('buy_sell', ''),
                            'quantity': row.get('quantity_traded', 0),
                            'price': row.get('trade_price', 0),
                            'remarks': ''
                        })
        
        # Check BSE block deals
        if data.get('bse_block') is not None:
            df = data['bse_block']
            # Safety check - ensure client_name column exists
            if 'client_name' not in df.columns:
                logger.warning("Skipping BSE block deals monitoring - client_name column missing")
            else:
                for investor in self.monitored_investors:
                    matches = df[df['client_name'].str.upper().str.contains(investor['name'], na=False)]
                    for _, row in matches.iterrows():
                        monitored_deals.append({
                            'investor': investor['display_name'],
                            'investor_category': investor['category'],
                            'priority': investor['priority'],
                            'deal_type': 'BLOCK',
                            'source': 'BSE',
                            'date': row.get('deal_date', ''),
                            'symbol': row.get('scrip_code', ''),
                            'security_name': row.get('scrip_name', ''),
                            'action': row.get('buy_sell', ''),
                            'quantity': row.get('quantity_traded', 0),
                            'price': row.get('trade_price', 0),
                            'remarks': ''
                        })
        
        # Sort by priority
        monitored_deals.sort(key=lambda x: x['priority'], reverse=True)
        
        if monitored_deals:
            logger.info(f"Found {len(monitored_deals)} deals from monitored investors!")
        else:
            logger.info("No deals from monitored investors today")
        
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
                subject = f"ALERT: Monitored Investor Activity + Daily Report - {today_str}"
            else:
                subject = f"Daily Bulk & Block Deals Report - {today_str}"
            
            body = self._create_email_body(summary, monitored_deals)
            
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
    
    def _create_monitored_deals_html(self, monitored_deals: List[Dict]) -> str:
        """Create HTML for monitored investor deals"""
        if not monitored_deals:
            return ""
        
        html = """
        <div style="background-color: #fff3cd; border-left: 5px solid #ff6b6b; padding: 20px; margin: 20px 0; border-radius: 5px;">
            <h2 style="color: #d32f2f; margin: 0 0 15px 0;">🚨 INVESTOR ALERT!</h2>
            <p style="font-size: 14px; color: #666; margin-bottom: 20px;">
                Your monitored investors have made the following trades:
            </p>
            <table style="width: 100%; border-collapse: collapse; background-color: white;">
                <thead>
                    <tr style="background-color: #d32f2f; color: white;">
                        <th style="padding: 12px; text-align: left;">Investor</th>
                        <th style="padding: 12px; text-align: left;">Stock</th>
                        <th style="padding: 12px; text-align: left;">Action</th>
                        <th style="padding: 12px; text-align: right;">Quantity</th>
                        <th style="padding: 12px; text-align: right;">Price</th>
                        <th style="padding: 12px; text-align: center;">Type</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for deal in monitored_deals:
            action_color = "#4caf50" if deal['action'].upper() == 'BUY' else "#f44336"
            category_badge = f"<br><small style='color: #999;'>{deal['investor_category']}</small>" if deal['investor_category'] else ""
            
            html += f"""
                <tr style="border-bottom: 1px solid #e0e0e0;">
                    <td style="padding: 12px;">
                        <strong>{deal['investor']}</strong>{category_badge}
                    </td>
                    <td style="padding: 12px;">
                        {deal['symbol']}<br>
                        <small style="color: #666;">{deal['security_name'][:40]}...</small>
                    </td>
                    <td style="padding: 12px; color: {action_color}; font-weight: bold;">{deal['action']}</td>
                    <td style="padding: 12px; text-align: right;">{deal['quantity']:,.0f}</td>
                    <td style="padding: 12px; text-align: right;">₹{deal['price']:,.2f}</td>
                    <td style="padding: 12px; text-align: center;">
                        <span style="background-color: #e3f2fd; padding: 4px 8px; border-radius: 3px; font-size: 11px;">
                            {deal['source']} {deal['deal_type']}
                        </span>
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
        total_deals = sum(summary.values())
        today_str = datetime.now().strftime('%d %B %Y, %I:%M %p IST')
        
        monitored_html = self._create_monitored_deals_html(monitored_deals) if monitored_deals else ""
        
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
                    {monitored_html}
                    
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
                    <p>Automated Reporting System with Investor Monitoring</p>
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
    """Main orchestrator with investor monitoring"""
    
    def __init__(self):
        self.nse_fetcher = NSEDataFetcher()
        self.bse_fetcher = BSEDataFetcher()
        self.db_manager = DatabaseManager()
        self.investor_monitor = InvestorMonitor(self.db_manager)
        self.email_reporter = EmailReporter()
        self.csv_files = []
        self.monitored_deals = []
    
    def fetch_all_data(self) -> Dict[str, pd.DataFrame]:
        """Fetch all deals data"""
        data = {}
        
        logger.info("Fetching data from NSE...")
        data['nse_bulk'] = self.nse_fetcher.fetch_bulk_deals()
        data['nse_block'] = self.nse_fetcher.fetch_block_deals()
        
        logger.info("Fetching data from BSE...")
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
            logger.info("WITH BSE SUPPORT AND INVESTOR MONITORING")
            logger.info("=" * 70)
            logger.info(f"Execution Time: {datetime.now().strftime('%d %B %Y, %I:%M:%S %p IST')}")
            
            # Step 1: Load monitored investors
            logger.info("\n[STEP 1/6] Loading monitored investors...")
            self.investor_monitor.load_monitored_investors()
            
            # Step 2: Fetch data
            logger.info("\n[STEP 2/6] Fetching data from NSE and BSE...")
            data = self.fetch_all_data()
            
            # Step 3: Check for monitored investor deals
            logger.info("\n[STEP 3/6] Checking for monitored investor activity...")
            self.monitored_deals = self.investor_monitor.find_monitored_deals(data)
            
            if self.monitored_deals:
                logger.info(f"ALERT: Found {len(self.monitored_deals)} deals from monitored investors!")
            
            # Step 4: Save to CSV
            logger.info("\n[STEP 4/6] Saving to CSV...")
            self.csv_files = self.save_to_csv(data)
            
            # Step 5: Store in Supabase
            logger.info("\n[STEP 5/6] Storing in Supabase...")
            self.store_all_data(data)
            
            # Step 6: Get summary
            logger.info("\n[STEP 6/6] Generating report...")
            summary = self.db_manager.get_today_summary()
            
            # Step 7: Send email with alerts
            logger.info("\nSending email report...")
            self.email_reporter.send_report(summary, self.csv_files, self.monitored_deals)
            
            logger.info("\n" + "=" * 70)
            logger.info("AUTOMATION COMPLETED SUCCESSFULLY!")
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