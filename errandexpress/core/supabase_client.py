# core/supabase_client.py
import os
import logging

logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Make Supabase optional - don't crash if credentials are not set
if SUPABASE_URL and SUPABASE_KEY:
    try:
        from supabase import create_client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("✅ Supabase client initialized successfully")
    except Exception as e:
        supabase = None
        logger.warning(f"⚠️ Supabase client initialization failed: {e}")
        logger.warning("Supabase features will be disabled")
else:
    supabase = None
    logger.info("ℹ️ Supabase credentials not set - Supabase features disabled")

