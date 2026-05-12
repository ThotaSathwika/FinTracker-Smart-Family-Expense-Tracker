# 💸 FinTracker – Smart Family Expense Tracker

FinTracker is a modern and intelligent family expense tracking web application built using Flask. It enables families to collaboratively manage expenses, income, budgets, and analytics with an elegant glassmorphism UI and interactive dashboards.

---

## 🚀 Features

### 👨‍👩‍👧 Family Expense Management
- Create or join family groups
- Share expenses and income among family members
- Collective financial tracking

### 💰 Expense Tracking
Track expenses across categories:
- 🍔 Food
- 🎬 Entertainment
- ✈️ Travel
- 🏥 Health
- 📚 Education
- 💡 Bills & Utilities
- 🛍️ Shopping
- 📦 Other

### 💵 Income Management
- Add and manage income sources
- Track total earnings
- Monitor family balance

### 📊 Analytics Dashboard
- Monthly expense visualization
- Category-wise spending charts
- Budget usage progress tracking
- Financial summaries

### 🔐 Authentication System
- Secure user registration & login
- Password hashing using Flask-Bcrypt
- Session management with Flask-Login

### 📁 Data Management
- CSV Export functionality
- CSV Import support
- Backup and restore expense records

### 🎨 Modern UI/UX
- Glassmorphism design
- Responsive layout
- Dark futuristic theme
- Interactive charts using Chart.js

---

## 🛠️ Tech Stack

### Backend
- Flask
- Flask-SQLAlchemy
- Flask-Login
- Flask-Bcrypt
- SQLite

### Frontend
- HTML5
- CSS3
- Bootstrap 5
- JavaScript
- Chart.js

---

## 📂 Project Structure

```bash
FinTracker/
│
├── app.py
├── requirements.txt
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
│
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── expenses.html
│   ├── income.html
│   ├── login.html
│   ├── register.html
│   └── settings.html
│
└── expense_tracker.db

⚙️ Installation
1️⃣ Clone Repository
git clone https://github.com/yourusername/FinTracker.git
cd FinTracker

2️⃣ Create Virtual Environment
python -m venv venv

Activate virtual environment:

Windows
venv\Scripts\activate
Mac/Linux
source venv/bin/activate

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Run Application
python app.py

Server runs at:

http://127.0.0.1:5000


📦 Requirements
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-Bcrypt==1.0.1
Flask-Login==0.6.3
Werkzeug==3.0.1

📈 Dashboard Insights

FinTracker provides:

Total Balance
Total Income
Total Expenses
Monthly Budget Progress
Category Distribution
Spending Trends


🔒 Security Features
Password hashing
Session-based authentication
Protected routes
Authorization checks for family data


🌟 Future Enhancements
AI-based expense prediction
OCR receipt scanning
Cloud database support
Mobile app integration
Multi-currency support
Email notifications
Expense reminders


🤝 Contributing

Contributions are welcome!

Fork repository
Create feature branch
Commit changes
Push branch
Open Pull Request

📄 License

This project is licensed under the MIT License.

👩‍💻 Developed By

Thota Sathwika


