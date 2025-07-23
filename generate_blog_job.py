#!/usr/bin/env python3
"""
Scheduled job script for generating daily AI blogs on Render
This script will be called by Render's cron job service every 24 hours
"""

import os
import sys
import json
from datetime import datetime

# Add the main directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import from main.py
try:
    from main import generate_blogs, load_blog_history, save_blog_history
    print("✅ Successfully imported blog generation functions")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def main():
    """Main function to generate daily blog"""
    print(f"🚀 Starting scheduled blog generation job at {datetime.now()}")
    
    try:
        # Load existing blog history
        global blog_cards
        blog_cards = load_blog_history()
        print(f"📚 Loaded {len(blog_cards)} existing blogs")
        
        # Generate new blog
        generate_blogs()
        
        print(f"✅ Blog generation job completed successfully at {datetime.now()}")
        
    except Exception as e:
        print(f"❌ Error in scheduled blog generation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
