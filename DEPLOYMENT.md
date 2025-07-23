# 📖 Tech Blog Auto-Generator - Render Deployment Guide

## 🚀 Automatic AI Blog Generation Setup

This system automatically generates AI-focused tech blogs every 24 hours using Render's scheduled jobs.

### 📋 Deployment Steps:

#### 1. **Environment Variables (Add these in Render Dashboard):**
```
ENVIRONMENT=production
PEXELS_API_KEY=your_pexels_api_key
NEWSAPI_KEY=your_newsapi_key  
OPENROUTER_KEY=your_openrouter_key
MONGO_URI=your_mongodb_connection_string
```

#### 2. **Deploy as Web Service:**
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `python main.py`
- **Environment:** Python 3

#### 3. **Setup Scheduled Job (Cron Job):**
- **Service Type:** Cron Job
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `python generate_blog_job.py`
- **Schedule:** `0 9 * * *` (Daily at 9 AM UTC)

### 🤖 How It Works:

1. **Web Service:** Serves the blog website and admin panel
2. **Scheduled Job:** Runs every 24 hours to fetch AI news and generate blogs
3. **AI Focus:** Prioritizes AI/ML news over general tech news
4. **Smart Timing:** Only generates new blogs after 24 hours have passed

### 🔧 Manual Testing:

You can manually trigger blog generation via API:
```bash
curl -X POST https://your-app-url.onrender.com/api/generate-blog
```

### 📊 Blog Features:

- ✅ **AI-Focused Content:** Prioritizes AI, ML, and tech news
- ✅ **24-Hour Scheduling:** One blog per day automatically
- ✅ **Duplicate Prevention:** Avoids duplicate content
- ✅ **Grammar Checking:** Quality control for generated content
- ✅ **Admin Panel:** Manual blog creation and management
- ✅ **MongoDB Storage:** Blog metadata and history

### 🎯 Schedule Details:

- **Check Frequency:** Every 24 hours (via cron job)
- **Content Priority:** AI > Machine Learning > General Tech
- **Generation Logic:** Only if 24+ hours since last blog
- **Fallback:** General tech news if no AI news available

### 🔍 Monitoring:

Check the Render logs to see:
- Daily blog generation status
- AI news fetching results
- Blog creation success/failure
- API key usage and limits

---

**Important:** Make sure all environment variables are set correctly in your Render dashboard before deployment!
