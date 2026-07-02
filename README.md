# MedCore HMS - Hospital Management System

A comprehensive hospital management system built with **Flask**, **PostgreSQL**, and a premium **dark-themed frontend**.

## 🚀 Tech Stack

| Layer       | Technology                                |
|-------------|-------------------------------------------|
| **Backend** | Flask 3.x, SQLAlchemy, Flask-Migrate      |
| **Database**| PostgreSQL 18                             |
| **Frontend**| HTML5, CSS3 (custom), Vanilla JS          |
| **Auth**    | Flask-Login, Flask-WTF (CSRF)             |
| **Icons**   | Font Awesome 6                            |
| **Fonts**   | Inter (Google Fonts)                      |

## 📁 Project Structure

```
hospital management/
├── app/
│   ├── __init__.py          # App factory + extensions
│   ├── models/              # SQLAlchemy models
│   ├── routes/              # Blueprint routes
│   │   ├── main.py          # Home & dashboard
│   │   └── auth.py          # Login, register, logout
│   ├── templates/           # Jinja2 templates
│   │   ├── base.html        # Layout skeleton
│   │   ├── index.html       # Landing page
│   │   ├── dashboard.html   # Dashboard
│   │   └── auth/            # Auth pages
│   └── static/
│       ├── css/style.css    # Global stylesheet
│       └── js/main.js       # Client-side logic
├── config.py                # Multi-env configuration
├── run.py                   # Entry point
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (not committed)
├── .env.example             # Env template
├── .gitignore
└── README.md
```

## ⚡ Quick Start

### 1. Clone & Enter
```bash
git clone <your-repo-url>
cd "hospital management"
```

### 2. Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # macOS/Linux
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
# Edit .env and set your PostgreSQL password
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/hospital_management_db
```

### 5. Create Database
```bash
psql -U postgres -c "CREATE DATABASE hospital_management_db;"
```

### 6. Run Migrations
```bash
flask db init
flask db migrate -m "initial migration"
flask db upgrade
```

### 7. Start Dev Server
```bash
flask run
# or
python run.py
```

Visit **http://localhost:5000** 🎉

## 📌 Status

- [x] Project structure & configuration
- [x] Flask app factory with extensions
- [x] Auth blueprint (login / register / logout stubs)
- [x] Premium dark-theme UI
- [ ] Database models (schema pending from user)
- [ ] Full CRUD for all modules
- [ ] Role-based access control
- [ ] API endpoints

## 📄 License

MIT
