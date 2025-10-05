-- Supabase Database Schema for NSE/BSE Bulk & Block Deals
-- Run these queries in your Supabase SQL Editor

-- ============================================================================
-- NSE BULK DEALS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS nse_bulk_deals (
    id BIGSERIAL PRIMARY KEY,
    fetch_date DATE NOT NULL,
    source TEXT DEFAULT 'NSE',
    symbol TEXT,
    security_name TEXT,
    client_name TEXT,
    deal_type TEXT,
    quantity NUMERIC,
    trade_price NUMERIC,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_nse_bulk_fetch_date ON nse_bulk_deals(fetch_date DESC);
CREATE INDEX IF NOT EXISTS idx_nse_bulk_symbol ON nse_bulk_deals(symbol);

-- ============================================================================
-- NSE BLOCK DEALS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS nse_block_deals (
    id BIGSERIAL PRIMARY KEY,
    fetch_date DATE NOT NULL,
    source TEXT DEFAULT 'NSE',
    symbol TEXT,
    security_name TEXT,
    client_name TEXT,
    deal_type TEXT,
    quantity NUMERIC,
    trade_price NUMERIC,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_nse_block_fetch_date ON nse_block_deals(fetch_date DESC);
CREATE INDEX IF NOT EXISTS idx_nse_block_symbol ON nse_block_deals(symbol);

-- ============================================================================
-- BSE BULK DEALS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS bse_bulk_deals (
    id BIGSERIAL PRIMARY KEY,
    fetch_date DATE NOT NULL,
    source TEXT DEFAULT 'BSE',
    scrip_code TEXT,
    scrip_name TEXT,
    client_name TEXT,
    deal_type TEXT,
    quantity NUMERIC,
    trade_price NUMERIC,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_bse_bulk_fetch_date ON bse_bulk_deals(fetch_date DESC);
CREATE INDEX IF NOT EXISTS idx_bse_bulk_scrip ON bse_bulk_deals(scrip_code);

-- ============================================================================
-- BSE BLOCK DEALS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS bse_block_deals (
    id BIGSERIAL PRIMARY KEY,
    fetch_date DATE NOT NULL,
    source TEXT DEFAULT 'BSE',
    scrip_code TEXT,
    scrip_name TEXT,
    client_name TEXT,
    deal_type TEXT,
    quantity NUMERIC,
    trade_price NUMERIC,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_bse_block_fetch_date ON bse_block_deals(fetch_date DESC);
CREATE INDEX IF NOT EXISTS idx_bse_block_scrip ON bse_block_deals(scrip_code);

-- ============================================================================
-- ENABLE ROW LEVEL SECURITY (RLS) - Optional but recommended
-- ============================================================================
-- ALTER TABLE nse_bulk_deals ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE nse_block_deals ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE bse_bulk_deals ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE bse_block_deals ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- CREATE POLICIES (if RLS is enabled)
-- ============================================================================
-- Example: Allow service role to do everything
-- CREATE POLICY "Allow service role full access" ON nse_bulk_deals
-- FOR ALL USING (auth.role() = 'service_role');

-- ============================================================================
-- USEFUL QUERIES FOR MONITORING
-- ============================================================================

-- Get today's deals count
-- SELECT 
--     'NSE Bulk' as category, COUNT(*) as count 
-- FROM nse_bulk_deals 
-- WHERE fetch_date = CURRENT_DATE
-- UNION ALL
-- SELECT 
--     'NSE Block' as category, COUNT(*) as count 
-- FROM nse_block_deals 
-- WHERE fetch_date = CURRENT_DATE
-- UNION ALL
-- SELECT 
--     'BSE Bulk' as category, COUNT(*) as count 
-- FROM bse_bulk_deals 
-- WHERE fetch_date = CURRENT_DATE
-- UNION ALL
-- SELECT 
--     'BSE Block' as category, COUNT(*) as count 
-- FROM bse_block_deals 
-- WHERE fetch_date = CURRENT_DATE;