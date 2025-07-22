import os
import requests
from string import Template
from datetime import datetime
from slugify import slugify
from openai import OpenAI

# ========== CONFIG ========== #
NEWSAPI_KEY = "a39061e62095496b91b9d896ecfd6677"
PEXELS_API_KEY = "cstlKtCCuZttQQ7ZHaUDDUCaSAame4jTh499GBbJ3N5xgCslsc5lQKFI"
OPENROUTER_KEY = "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"

TEMPLATE_PATH = "templates/blog_template.html"
OUTPUT_DIR = "blog_output"
TODAY = datetime.now().strftime("%Y-%m-%d")

client = OpenAI(
    api_key=OPENROUTER_KEY,
    base_url="https://openrouter.ai/api/v1"
)

# ========== UTILS ========== #
def fetch_tech_news():
    url = f"https://newsapi.org/v2/everything?q=technology&language=en&sortBy=publishedAt&pageSize=1&apiKey={NEWSAPI_KEY}"
    res = requests.get(url)
    if res.status_code == 200:
        return res.json().get("articles", [])[:1]
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
    prompt = f"""
    Write a detailed, natural-sounding tech blog post based on the following headline and summary:

    Headline: "{title}"
    Summary: "{description}"

    Structure it in 4 paragraphs:
    1. Intro with context and hook
    2. Background or event details
    3. Insights, reactions or expert view
    4. Conclusion with reflection or future outlook

    Do NOT copy anything from the web.
    Write like a human professional journalist in your own words. Avoid generic language or clichés.
    Ensure the writing is fully original and passes AI and plagiarism detection.
    """
    try:
        response = client.chat.completions.create(
            model="meta-llama/llama-3-70b-instruct",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            top_p=0.95,
            max_tokens=1000,
        )
        blog = response.choices[0].message.content.strip()
        formatted_blog = "".join(f"<p>{para.strip()}</p>" for para in blog.split("\n\n") if para.strip())
        return formatted_blog
    except Exception as e:
        return f"<p>Error generating blog: {e}</p>"

# ========== MAIN LOGIC ========== #
os.makedirs(OUTPUT_DIR, exist_ok=True)
news_articles = fetch_tech_news()

if not news_articles:
    print("❌ No news articles found. Please check your NewsAPI key or network.")
    exit()

with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
    template = Template(f.read())

for article in news_articles:
    title = article["title"]
    description = article.get("description", "")
    image_url = fetch_image(title)
    blog_content = generate_blog_from_title(title, description)

    slug = slugify(title)
    timestamp = datetime.now().strftime("%H-%M-%S")
    output_filename = f"{slug}-{timestamp}.html"
    output_path = os.path.join(OUTPUT_DIR, output_filename)

    html_content = template.substitute(title=title, content=blog_content)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    # Create blog card HTML
    new_card_html = f"""
    <div class="card">
      <img src="{image_url}" alt="Thumbnail">
      <div class="card-content">
        <h3>{title}</h3>
        <p class="card-date">{TODAY}</p>
        <p class="card-desc">Click to read original tech blog based on this news.</p>
        <a href="blog_output/{output_filename}" class="read-more">Read More</a>
      </div>
    </div>
    """

    # ========== Append or Create index.html ========== #
    if not os.path.exists("index.html"):
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>TechPulse Daily Blog</title>
  <link rel="stylesheet" href="static/style.css">
</head>
<body>
  <div class="container">
    <h1>TechPulse Daily</h1>
    {new_card_html}
  </div>
</body>
</html>
            """)
    else:
        with open("index.html", "r", encoding="utf-8") as f:
            old_content = f.read()

        updated_content = old_content.replace(
            "</div></body></html>",
            new_card_html + "\n</div></body></html>"
        )

        with open("index.html", "w", encoding="utf-8") as f:
            f.write(updated_content)

    print(f"✅ Blog generated: {title}")
