# Tech Blog Generator - Render Deployment Guide

## 🚀 How to Deploy on Render

### Step 1: Deploy the Web Service
1. Connect your GitHub repo to Render
2. Create a new **Web Service**
3. Use these settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`
   - **Environment**: `production`

### Step 2: Set Environment Variables
Add these environment variables in Render dashboard:
```
ENVIRONMENT=production
NEWSAPI_KEY=your_newsapi_key_here
PEXELS_API_KEY=your_pexels_key_here
OPENROUTER_KEY=your_openrouter_key_here
MONGO_URI=your_mongodb_connection_string_here
```

### Step 3: Create Scheduled Job for Daily Blogs
1. In Render dashboard, create a new **Cron Job**
2. Use these settings:
   - **Command**: `python generate_blog_job.py`
   - **Schedule**: `0 9 * * *` (runs daily at 9 AM UTC)
   - **Docker Command**: Leave blank
   - **Region**: Same as your web service

### Step 4: Manual Blog Generation (Optional)
You can also trigger blog generation manually by running the cron job or accessing the admin panel.

## 📁 File Structure
```
├── main.py                 # Main Flask application
├── generate_blog_job.py    # Scheduled job script for daily blogs
├── requirements.txt        # Python dependencies
├── templates/             # HTML templates
├── static/               # CSS files
├── blog_output/          # Generated blog files
└── .env                  # Environment variables (local only)
```

## 🤖 AI Blog Features
- **AI-First**: Prioritizes AI/ML news over general tech
- **24-Hour Schedule**: Generates one new blog every 24 hours
- **Smart Filtering**: Uses keywords to find relevant content
- **Quality Control**: Grammar checking and duplicate prevention
- **Admin Panel**: Manual blog creation and editing

## 🔧 Local Development
For local testing:
```bash
pip install -r requirements.txt
python main.py
```

## 📝 Notes
- Background threads don't work on Render, so we use scheduled jobs
- The web service handles user requests
- The cron job handles automatic blog generation
- All data is stored in MongoDB and local files
