import csv
from io import StringIO
from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime, date

app = Flask(__name__)
app.config['SECRET_KEY'] = 'fintracker_smart_super_secret_key_999'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expense_tracker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# --- Models ---
class Family(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    monthly_budget = db.Column(db.Float, default=0.0)
    users = db.relationship('User', backref='family', lazy=True)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    family_id = db.Column(db.Integer, db.ForeignKey('family.id'), nullable=True)
    expenses = db.relationship('Expense', backref='owner', lazy=True)
    incomes = db.relationship('Income', backref='owner', lazy=True)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    date = db.Column(db.Date, nullable=False, default=date.today)

class Income(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    source = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Routes ---

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        if User.query.filter_by(email=email).first() or User.query.filter_by(username=username).first():
            flash('Email or Username already exists. Please choose another.', 'danger')
            return redirect(url_for('register'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, email=email, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully! Welcome to FinTracker.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user, remember=True)
            return redirect(url_for('dashboard'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.family_id:
        family_user_ids = [u.id for u in current_user.family.users]
        expenses = Expense.query.filter(Expense.user_id.in_(family_user_ids)).order_by(Expense.date.desc()).all()
        incomes = Income.query.filter(Income.user_id.in_(family_user_ids)).order_by(Income.date.desc()).all()
        budget = current_user.family.monthly_budget
        family_members = current_user.family.users
    else:
        expenses = Expense.query.filter_by(user_id=current_user.id).order_by(Expense.date.desc()).all()
        incomes = Income.query.filter_by(user_id=current_user.id).order_by(Income.date.desc()).all()
        budget = 0
        family_members = [current_user]

    recent_expenses = expenses[:5]
    recent_incomes = incomes[:5]
    
    total_expense = sum([e.amount for e in expenses])
    total_income = sum([i.amount for i in incomes])
    balance = total_income - total_expense

    current_month = date.today().replace(day=1)
    current_month_expense = sum([e.amount for e in expenses if e.date >= current_month])
    
    budget_progress = (current_month_expense / budget * 100) if budget > 0 else 0
    budget_progress = min(budget_progress, 100)

    return render_template('dashboard.html', 
                           expenses=recent_expenses, 
                           incomes=recent_incomes, 
                           total_expense=total_expense, 
                           total_income=total_income, 
                           balance=balance,
                           budget=budget,
                           current_month_expense=current_month_expense,
                           budget_progress=budget_progress,
                           family_members=family_members)

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'create_family':
            name = request.form.get('family_name')
            new_family = Family(name=name)
            db.session.add(new_family)
            db.session.commit()
            current_user.family_id = new_family.id
            db.session.commit()
            flash(f'Family "{name}" created!', 'success')
            
        elif action == 'join_family':
            family_id = request.form.get('family_id')
            family = Family.query.get(family_id)
            if family:
                current_user.family_id = family.id
                db.session.commit()
                flash(f'Joined family "{family.name}"!', 'success')
            else:
                flash('Family ID not found.', 'danger')
                
        elif action == 'set_budget':
            if current_user.family_id:
                budget = request.form.get('budget', type=float)
                current_user.family.monthly_budget = budget
                db.session.commit()
                flash('Budget updated!', 'success')
            else:
                flash('You must be in a family to set a shared budget. Create or join one first.', 'warning')
        
        elif action == 'leave_family':
            current_user.family_id = None
            db.session.commit()
            flash('You have left the family group.', 'info')
            
        return redirect(url_for('settings'))
        
    all_families = Family.query.all()
    return render_template('settings.html', all_families=all_families)

@app.route('/expenses', methods=['GET', 'POST'])
@login_required
def expenses():
    if request.method == 'POST':
        amount = request.form.get('amount')
        category = request.form.get('category')
        description = request.form.get('description')
        date_str = request.form.get('date')
        
        expense_date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else date.today()

        new_expense = Expense(amount=amount, category=category, description=description, date=expense_date, owner=current_user)
        db.session.add(new_expense)
        db.session.commit()
        flash('Expense added successfully!', 'success')
        return redirect(url_for('expenses'))
    
    if current_user.family_id:
        family_user_ids = [u.id for u in current_user.family.users]
        all_expenses = Expense.query.filter(Expense.user_id.in_(family_user_ids)).order_by(Expense.date.desc()).all()
    else:
        all_expenses = Expense.query.filter_by(user_id=current_user.id).order_by(Expense.date.desc()).all()
        
    return render_template('expenses.html', expenses=all_expenses)

@app.route('/delete_expense/<int:expense_id>')
@login_required
def delete_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    # Allow deletion if the user is the owner, OR if they are in the same family
    can_delete = expense.owner == current_user or (current_user.family_id and expense.owner.family_id == current_user.family_id)
    if not can_delete:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('expenses'))
    db.session.delete(expense)
    db.session.commit()
    flash('Expense deleted.', 'success')
    return redirect(url_for('expenses'))

@app.route('/income', methods=['GET', 'POST'])
@login_required
def income():
    if request.method == 'POST':
        amount = request.form.get('amount')
        source = request.form.get('source')
        date_str = request.form.get('date')
        
        income_date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else date.today()

        new_income = Income(amount=amount, source=source, date=income_date, owner=current_user)
        db.session.add(new_income)
        db.session.commit()
        flash('Income added successfully!', 'success')
        return redirect(url_for('income'))
    
    if current_user.family_id:
        family_user_ids = [u.id for u in current_user.family.users]
        all_incomes = Income.query.filter(Income.user_id.in_(family_user_ids)).order_by(Income.date.desc()).all()
    else:
        all_incomes = Income.query.filter_by(user_id=current_user.id).order_by(Income.date.desc()).all()
        
    return render_template('income.html', incomes=all_incomes)

@app.route('/delete_income/<int:income_id>')
@login_required
def delete_income(income_id):
    income = Income.query.get_or_404(income_id)
    can_delete = income.owner == current_user or (current_user.family_id and income.owner.family_id == current_user.family_id)
    if not can_delete:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('income'))
    db.session.delete(income)
    db.session.commit()
    flash('Income deleted.', 'success')
    return redirect(url_for('income'))

@app.route('/api/chart_data')
@login_required
def chart_data():
    if current_user.family_id:
        family_user_ids = [u.id for u in current_user.family.users]
        expenses = Expense.query.filter(Expense.user_id.in_(family_user_ids)).all()
    else:
        expenses = Expense.query.filter_by(user_id=current_user.id).all()
    
    # Category Data
    category_data = {}
    for e in expenses:
        if e.category in category_data:
            category_data[e.category] += e.amount
        else:
            category_data[e.category] = e.amount
            
    # Monthly Data (Current Year)
    current_year = date.today().year
    monthly_data = {month: 0 for month in range(1, 13)}
    
    for e in expenses:
        if e.date.year == current_year:
            monthly_data[e.date.month] += e.amount

    return jsonify({
        'categories': list(category_data.keys()),
        'category_totals': list(category_data.values()),
        'months': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        'monthly_totals': list(monthly_data.values())
    })

@app.route('/export/csv')
@login_required
def export_csv():
    if current_user.family_id:
        family_user_ids = [u.id for u in current_user.family.users]
        expenses = Expense.query.filter(Expense.user_id.in_(family_user_ids)).all()
    else:
        expenses = Expense.query.filter_by(user_id=current_user.id).all()
        
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['Amount', 'Category', 'Description', 'Date'])
    for e in expenses:
        cw.writerow([e.amount, e.category, e.description, e.date])
        
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=fintracker_expenses.csv"
    output.headers["Content-type"] = "text/csv"
    return output

@app.route('/import/csv', methods=['POST'])
@login_required
def import_csv():
    if 'csv_file' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('settings'))
        
    file = request.files['csv_file']
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(url_for('settings'))
        
    if file and file.filename.endswith('.csv'):
        stream = StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_input = csv.reader(stream)
        next(csv_input, None)  # skip header
        for row in csv_input:
            try:
                # row: Amount, Category, Description, Date
                amount = float(row[0])
                category = row[1]
                description = row[2]
                date_str = row[3]
                expense_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                new_expense = Expense(amount=amount, category=category, description=description, date=expense_date, owner=current_user)
                db.session.add(new_expense)
            except Exception as e:
                continue
        db.session.commit()
        flash('CSV imported successfully.', 'success')
    else:
        flash('Invalid file format. Please upload a CSV.', 'danger')
    return redirect(url_for('settings'))

if __name__ == '__main__':
    with app.app_context():
        # Using db.create_all() handles new tables, but won't alter existing ones automatically
        # For our purposes, we will drop the db file in the terminal and recreate it.
        db.create_all()
    app.run(debug=True, port=5000)
