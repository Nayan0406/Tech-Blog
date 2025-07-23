import os
import json
import time
import threading
import requests
from string import Template
from datetime import datetime
from slugify import slugify
from flask import Flask, render_template, send_from_directory, request, redirect, url_for, session, jsonify
import openai
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# ========== CONFIG ========== #

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
OPENROUTER_KEY = os.getenv("OPENROUTER_KEY")

TEMPLATE_PATH = "templates/blog_template.html"
OUTPUT_DIR = "blog_output"
HISTORY_FILE = "blog_history.json"
ADMIN_INPUT_FILE = "admin_input.json"

TODAY = datetime.now().strftime("%Y-%m-%d")
SECRET_KEY = "supersecretkey"
ADMIN_PASSWORD = "admin123"

# OpenAI client setup for older version (0.28.1)
if OPENROUTER_KEY:
    openai.api_key = OPENROUTER_KEY
    openai.api_base = "https://openrouter.ai/api/v1"
    print("✅ OpenAI client configured")
    client = openai  # Use the module directly
else:
    print("⚠️ OPENROUTER_KEY not found")
    client = None

# MongoDB setup
MONGO_URI = os.getenv("MONGO_URI")
mongo_client = None
db = None
mongo_collection = None

if MONGO_URI:
    try:
        mongo_client = MongoClient(MONGO_URI)
        db = mongo_client["test"]         
        mongo_collection = db["blogs"]
        print("✅ MongoDB connection established")
    except Exception as e:
        print(f"⚠️ MongoDB connection failed: {e}")
        mongo_collection = None
else:
    print("⚠️ MONGO_URI not found in environment variables")
    mongo_collection = None

app = Flask(__name__)
app.secret_key = SECRET_KEY
blog_cards = []
CORS(app)

# ========== UTILS ========== #
import random

def fetch_tech_news():
    # First try to get AI-specific news
    ai_keywords = ["ai", "artificial intelligence", "machine learning", "deep learning", "neural network", "openai", "chatgpt", "llm", "generative ai"]
    
    for _ in range(3):  # try 3 random pages for AI news first
        page = random.randint(1, 3)
        # Search specifically for AI-related news
        url = f"https://newsapi.org/v2/everything?q=artificial+intelligence+OR+AI+OR+machine+learning&language=en&sortBy=publishedAt&pageSize=5&page={page}&apiKey={NEWSAPI_KEY}"
        res = requests.get(url)
        if res.status_code == 200:
            articles = res.json().get("articles", [])
            # Filter for AI-specific content
            ai_filtered = [
                article for article in articles
                if any(kw in article.get("title", "").lower() + " " + article.get("description", "").lower() 
                      for kw in ai_keywords)
            ]
            if ai_filtered:
                print(f"✅ Found {len(ai_filtered)} AI-related articles")
                return ai_filtered[:1]  # return the most recent AI article
    
    # Fallback: if no AI articles found, try general tech with AI preference
    for _ in range(2):
        page = random.randint(1, 5)
        url = f"https://newsapi.org/v2/everything?q=technology&language=en&sortBy=publishedAt&pageSize=5&page={page}&apiKey={NEWSAPI_KEY}"
        res = requests.get(url)
        if res.status_code == 200:
            articles = res.json().get("articles", [])
            # Prioritize AI articles, then other tech
            ai_articles = [
                article for article in articles
                if any(kw in article.get("title", "").lower() + " " + article.get("description", "").lower()
                      for kw in ai_keywords)
            ]
            if ai_articles:
                print(f"✅ Found {len(ai_articles)} AI articles in general tech search")
                return ai_articles[:1]
            
            # If no AI, then other tech
            tech_filtered = [
                article for article in articles
                if any(kw in article.get("title", "").lower() for kw in [
                    "technology", "robot", "software", "nvidia", "startup",
                    "chip", "cloud", "data", "cyber", "processor", "quantum"
                ])
            ]
            if tech_filtered:
                print(f"ℹ️ No AI articles found, using general tech: {len(tech_filtered)} articles")
                return tech_filtered[:1]
    
    print("❌ No suitable articles found")
    return []


def fetch_image(query):
    headers = {"Authorization": PEXELS_API_KEY}
    params = {"query": query, "per_page": 1}
    res = requests.get("https://api.pexels.com/v1/search", headers=headers, params=params)
    if res.status_code == 200:
        data = res.json()
        return data['photos'][0]['src']['medium'] if data['photos'] else ""
    return ""

def generate_blog_from_title(title, description):
    # Check if it's AI-related content to customize the prompt
    text_to_check = (title + " " + description).lower()
    ai_keywords = ["ai", "artificial intelligence", "machine learning", "deep learning", 
                  "neural", "openai", "chatgpt", "llm", "generative", "gpt"]
    is_ai_content = any(keyword in text_to_check for keyword in ai_keywords)
    
    if is_ai_content:
        prompt = f"""
        Write a comprehensive, engaging blog post about this AI/technology development:

        Headline: "{title}"
        Summary: "{description}"

        Structure it in 4-5 detailed paragraphs:
        1. Introduction - Hook the reader with the significance of this AI development
        2. Technical Background - Explain the technology and its context in simple terms
        3. Impact Analysis - How this affects the industry, users, or society
        4. Expert Perspective - Analysis of implications and future potential
        5. Conclusion - What this means for the future of AI and technology

        Focus on:
        - Making complex AI concepts accessible to general readers
        - Highlighting real-world applications and benefits
        - Discussing both opportunities and challenges
        - Using engaging, journalistic writing style
        
        Write like a professional tech journalist who specializes in AI. Be informative yet accessible.
        """
    else:
        prompt = f"""
        Write a detailed, natural-sounding tech blog post based on the following headline and summary:

        Headline: "{title}"
        Summary: "{description}"

        Structure it in 4 paragraphs:
        1. Intro with context and hook
        2. Background or event details
        3. Insights, reactions or expert view
        4. Conclusion with reflection or future outlook

        Write like a human professional journalist in your own words. Avoid generic language or clichés.
        """
    
    try:
        # Debug: Check client type
        print(f"DEBUG: Generating {'AI-focused' if is_ai_content else 'general tech'} blog")
        
        if client is None:
            return "<p>Error: OpenAI client not configured</p>"
        
        # Use the older OpenAI API format (v0.28.1)
        response = openai.ChatCompletion.create(
            model="meta-llama/llama-3-70b-instruct",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            top_p=0.95,
            max_tokens=1500 if is_ai_content else 1000,
        )
        blog = response.choices[0].message.content.strip()
        formatted_blog = "".join(f"<p>{para.strip()}</p>" for para in blog.split("\n\n") if para.strip())
        print(f"✅ {'AI-focused' if is_ai_content else 'Tech'} blog generated successfully")
        return formatted_blog
    except Exception as e:
        print(f"DEBUG: Error details - {type(e)}: {e}")
        return f"<p>Error generating blog: {e}</p>"

def check_grammar_with_languagetool(text):
    try:
        res = requests.post(
            "https://api.languagetool.org/v2/check",
            data={
                "text": text,
                "language": "en-US"
            }
        )
        result = res.json()
        matches = result.get("matches", [])
        # We'll allow minor issues but skip if too many
        if len(matches) > 15:
            print("❌ Grammar check failed: too many issues.")
            return False
        print(f"✅ Grammar check passed with {len(matches)} minor alerts.")
        return True
    except Exception as e:
        print(f"⚠️ Grammar check error: {e}")
        return True  # Don't block blog in case API fails

# ========== BACKGROUND GENERATION ========== #
def load_blog_history():
    """Load blog history from MongoDB first, then fallback to local file"""
    if mongo_collection is not None:
        try:
            # Load from MongoDB
            blogs = list(mongo_collection.find().sort("timestamp", -1))
            if blogs:
                print(f"📚 Loaded {len(blogs)} blogs from MongoDB")
                return blogs
        except Exception as e:
            print(f"⚠️ MongoDB load failed: {e}")
    
    # Fallback to local file
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                local_blogs = json.load(f)
                print(f"📚 Loaded {len(local_blogs)} blogs from local file")
                return local_blogs
        except Exception as e:
            print(f"⚠️ Local file load failed: {e}")
    
    return []

def save_blog_history():
    """Save blog history to both MongoDB and local file"""
    global blog_cards
    
    # Save to MongoDB first
    if mongo_collection is not None:
        try:
            # Clear existing blogs and insert new ones
            mongo_collection.delete_many({})
            if blog_cards:
                # Add MongoDB ObjectId for each blog
                blogs_to_save = []
                for blog in blog_cards:
                    blog_copy = blog.copy()
                    if "_id" not in blog_copy:
                        blog_copy["_id"] = slugify(blog_copy["title"] + "-" + blog_copy["date"])
                    blogs_to_save.append(blog_copy)
                
                mongo_collection.insert_many(blogs_to_save)
                print(f"✅ Saved {len(blogs_to_save)} blogs to MongoDB")
        except Exception as e:
            print(f"⚠️ MongoDB save failed: {e}")
    
    # Also save to local file as backup
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(blog_cards, f, indent=2)
        print(f"✅ Saved {len(blog_cards)} blogs to local file")
    except Exception as e:
        print(f"⚠️ Local file save failed: {e}")

def read_admin_input():
    if os.path.exists(ADMIN_INPUT_FILE):
        with open(ADMIN_INPUT_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                if data.get("title") and data.get("description"):
                    return data
            except json.JSONDecodeError:
                return None
    return None

def clear_admin_input():
    with open(ADMIN_INPUT_FILE, "w", encoding="utf-8") as f:
        f.write("{}")

def generate_blogs():
    global blog_cards

    # Ensure blog_cards is loaded
    if not blog_cards:
        blog_cards = load_blog_history()
        print(f"📚 Loaded {len(blog_cards)} existing blogs")

    # ✅ Proper 24-hour check with timestamp
    today_str = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now()
    
    # For production, allow generation if it's a new day or first time
    should_generate = True
    if blog_cards:
        last_blog = blog_cards[0]
        last_blog_date = last_blog.get("date", "")
        
        # If there's already a blog from today, skip (unless in development)
        if last_blog_date == today_str:
            if os.getenv("ENVIRONMENT") == "production":
                print(f"⏰ Blog already exists for today ({today_str}). Skipping...")
                return
            else:
                print("🧪 Development mode: allowing multiple blogs per day...")
        else:
            print(f"✅ Generating new AI-focused blog for {today_str}...")
    else:
        print(f"📝 First blog generation for {today_str}...")
    
    tech_keywords = [
        # AI and ML keywords (high priority)
        "ai", "artificial intelligence", "machine learning", "deep learning", 
        "neural network", "neural", "openai", "chatgpt", "llm", "generative ai",
        "large language model", "gpt", "transformer", "nlp", "computer vision",
        
        # Other tech keywords (lower priority)
        "robot", "cloud", "data", "software", "hardware", "semiconductor", 
        "quantum", "programming", "automation", "cybersecurity", "algorithm", 
        "model", "token", "processor"
    ]

    def is_tech_article(article):
        text = (article.get("title", "") + " " + article.get("description", "")).lower()
        
        # Give higher priority to AI-related articles
        ai_keywords = ["ai", "artificial intelligence", "machine learning", "deep learning", 
                      "neural", "openai", "chatgpt", "llm", "generative", "gpt"]
        
        is_ai_related = any(keyword in text for keyword in ai_keywords)
        is_tech_related = any(keyword in text for keyword in tech_keywords)
        
        if is_ai_related:
            print(f"🤖 AI-related article found: {article.get('title', '')[:50]}...")
            return True
        elif is_tech_related:
            print(f"💻 Tech article found: {article.get('title', '')[:50]}...")
            return True
        
        return False

    admin_data = read_admin_input()
    if admin_data:
        articles = [admin_data]
        print("📝 Admin blog input used")
        clear_admin_input()
    else:
        articles = fetch_tech_news()
        if not articles:
            print("❌ No articles fetched.")
            return
        articles = [a for a in articles if is_tech_article(a)]
        if not articles:
            print("⏭️ No tech articles passed the filter.")
            return

    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        template = Template(f.read())

    existing_files = os.listdir(OUTPUT_DIR)

    for article in articles:
        title = article["title"]
        slug = slugify(title)

        # ✅ Modified duplicate check - only check for exact slug matches, not partial
        exact_slug_exists = any(slug == blog["link"].split("/")[-1].replace(".html", "").rsplit("-", 3)[0] for blog in blog_cards)
        file_exists = any(slug in fname for fname in existing_files)
        
        if exact_slug_exists or file_exists:
            print(f"⏭️ Blog already exists: {title}")
            continue

        description = article.get("description", "")
        image_url = fetch_image(title)
        blog_content = generate_blog_from_title(title, description)

        # ✅ Grammar check
        if not check_grammar_with_languagetool(blog_content):
            print(f"🚫 Blog rejected due to grammar issues: {title}")
            continue

        timestamp = datetime.now().strftime("%H-%M-%S")
        output_filename = f"{slug}-{timestamp}.html"
        output_path = os.path.join(OUTPUT_DIR, output_filename)

        html_content = template.substitute(title=title, content=blog_content)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        # ✅ Store blog with timestamp for better tracking
        blog_cards.insert(0, {
            "title": title,
            "date": today_str,
            "timestamp": current_time.isoformat(),
            "desc": "Click to read original tech blog based on this news.",
            "image_url": image_url,
            "link": f"/blog_output/{output_filename}"
        })

        save_blog_history()
        print(f"✅ Blog generated: {title}")
        
        # ✅ Limit to 50 blogs total
        if len(blog_cards) > 50:
            blog_cards = blog_cards[:50]

# Background threads don't work reliably on Render. Use scheduled jobs instead.
os.makedirs(OUTPUT_DIR, exist_ok=True)
blog_cards = load_blog_history()

# Only generate blog on startup for testing locally
# In production, blogs are generated via scheduled job (generate_blog_job.py)
if os.getenv("ENVIRONMENT") != "production":
    print("🧪 Development mode: generating blog on startup...")
    generate_blogs()
else:
    print("🚀 Production mode: blogs will be generated via scheduled job")
    print(f"📚 Currently have {len(blog_cards)} blogs loaded")

# ========== ROUTES ========== #
@app.route("/")
def index():
    per_page = 5
    page = int(request.args.get("page", 1))
    start = (page - 1) * per_page
    end = start + per_page
    total_pages = (len(blog_cards) + per_page - 1) // per_page

    paginated_blogs = blog_cards[start:end]

    return render_template("index.html", blogs=paginated_blogs, page=page, total_pages=total_pages)


@app.route("/blog_output/<filename>")
def serve_blog(filename):
    return send_from_directory("blog_output", filename)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("password") == ADMIN_PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("admin"))
    return render_template("login.html")

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        if title and description:
            with open(ADMIN_INPUT_FILE, "w", encoding="utf-8") as f:
                json.dump({"title": title, "description": description}, f)
            return redirect(url_for("admin"))
    date_filter = request.args.get("date")
    filtered_blogs = [b for b in blog_cards if b["date"] == date_filter] if date_filter else blog_cards
    return render_template("admin.html",  blogs=filtered_blogs)



@app.route("/delete/<slug>")
def delete_blog(slug):
    global blog_cards
    filename = next((blog["link"].split("/")[-1] for blog in blog_cards if slug in blog["link"]), None)
    if filename:
        path = os.path.join(OUTPUT_DIR, filename)
        if os.path.exists(path):
            os.remove(path)
        blog_cards = [b for b in blog_cards if slug not in b["link"]]
        save_blog_history()
    return redirect(url_for("admin"))

@app.route("/edit/<slug>", methods=["GET", "POST"])
def edit_blog(slug):
    filename = next((blog["link"].split("/")[-1] for blog in blog_cards if slug in blog["link"]), None)
    if not filename:
        return "Blog not found", 404

    path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(path):
        return "File not found", 404

    if request.method == "POST":
        title = request.form.get("title")
        content = request.form.get("content")
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"<html><head><meta charset='UTF-8'><title>{title}</title><link rel='stylesheet' href='../static/style.css'></head><body><div class='blog-container'><h1>{title}</h1>{content}</div></body></html>")
        for b in blog_cards:
            if slug in b["link"]:
                b["title"] = title
        save_blog_history()
        return redirect(url_for("admin"))

    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()
    title_start = raw.find("<h1>") + 4
    title_end = raw.find("</h1>")
    body_start = raw.find("</h1>") + 5
    title = raw[title_start:title_end]
    content = raw[body_start:].strip().replace("</div></body></html>", "")

    return render_template("edit_blog.html", slug=slug, title=title, content=content)

@app.route("/api/blogs")
def api_blogs():
    if mongo_collection is not None:
        try:
            blogs = list(mongo_collection.find({}, {"_id": 1, "title": 1, "image": 1, "date": 1, "description": 1, "link": 1}))
            # Convert ObjectId to string if needed
            for blog in blogs:
                blog["_id"] = str(blog["_id"])
            return jsonify({"blogs": blogs})
        except Exception as e:
            print(f"❌ MongoDB query failed: {e}")
            return jsonify({"blogs": [], "error": "Database connection failed"})
    else:
        return jsonify({"blogs": [], "error": "Database not configured"})

@app.route("/api/generate-blog", methods=["POST"])
def api_generate_blog():
    """Manual blog generation endpoint for testing"""
    try:
        print("🔧 Manual blog generation triggered via API")
        generate_blogs()
        return jsonify({
            "success": True, 
            "message": "Blog generation completed",
            "total_blogs": len(blog_cards)
        })
    except Exception as e:
        return jsonify({
            "success": False, 
            "error": str(e)
        }), 500

@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True, port=5001)
