# 📰 Tech Blog Generator with AI

This Flask-based project automatically generates daily tech blogs using the OpenAI API and real-time news sources. It also features an admin panel to submit manual news for blog generation and displays all blogs with dynamic frontend updates.

---

## 🚀 Features

- 🔁 **Auto-generate tech blogs every 24 hours**
- ✍️ **Admin panel** for manual news input
- 🧠 Powered by **OpenAI** for intelligent content creation
- 📸 Integrated with relevant tech images
- ✅ Prevents duplicate blog generation
- ⚡ Real-time UI updates on the homepage
- 📚 Blog history tracking and HTML output generation

---

## 🧩 Tech Stack

- **Flask** (backend)
- **HTML/CSS** (frontend)
- **OpenAI API** (blog generation)
- **Requests** (fetch external news)
- **Slugify** (clean blog filenames)

---

## 🛠️ Installation

1. **Clone the repository:**
   ```bash
   git clone <repo_url>
   cd Tech_blogs
   ```

2. **Create and activate a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set your OpenAI API key** inside `main.py`:
   ```python
   openai.api_key = "YOUR_API_KEY"
   ```

---

## 🧪 Running the App

```bash
python main.py
```

The server will start at `http://localhost:5000`.

---

## 📁 Folder Structure

```
Tech_blogs/
├── main.py
├── admin_input.json
├── blog_history.json
├── blog_output/             ← Generated blog HTML files
├── static/style.css
├── templates/
│   ├── index.html
│   ├── admin.html
│   ├── login.html
│   ├── blog_template.html
│   └── edit_blog.html
```

---

## 👤 Admin Panel

- Accessible via `/admin`
- Requires a basic login (you can customize it)
- Admin can:
  - Submit manual tech news
  - Edit or delete blogs

---

## 📌 To-Do / Improvements

- Add database support (SQLite or MongoDB)
- Add email/WhatsApp notifications
- Deploy to Render, Railway, or Heroku
- Add filtering and sorting on homepage

---

## 📄 License

MIT License – free to use and modify.