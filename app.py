#!/usr/bin/env python3

import os
import sqlite3
from datetime import datetime, timedelta
from functools import wraps
import secrets
import yaml
import bcrypt

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, g
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Create Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(16))
app.config['DATABASE'] = os.environ.get('DATABASE_PATH', '/config/budget101.db')
app.config['CONFIG_FILE'] = os.environ.get('CONFIG_FILE', '/config/config.yml')

# Rate limiting
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)
limiter.init_app(app)

# Database setup
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """Initialize the database with required tables"""
    with app.app_context():
        db = get_db()
        
        # Users table
        db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                is_admin BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')
        
        # Income table
        db.execute('''
            CREATE TABLE IF NOT EXISTS income (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                amount DECIMAL(10,2) NOT NULL,
                frequency TEXT NOT NULL,
                frequency_day INTEGER,
                earner_name TEXT NOT NULL,
                earner_type TEXT NOT NULL,
                start_date DATE,
                end_date DATE,
                is_active BOOLEAN DEFAULT TRUE,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Bills table
        db.execute('''
            CREATE TABLE IF NOT EXISTS bills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                amount DECIMAL(10,2) NOT NULL,
                due_date DATE NOT NULL,
                category TEXT,
                is_recurring BOOLEAN DEFAULT FALSE,
                recurring_interval TEXT,
                is_paid BOOLEAN DEFAULT FALSE,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Taxes table
        db.execute('''
            CREATE TABLE IF NOT EXISTS taxes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                tax_year INTEGER NOT NULL,
                income DECIMAL(15,2),
                deductions DECIMAL(15,2),
                taxes_owed DECIMAL(15,2),
                taxes_paid DECIMAL(15,2),
                refund_amount DECIMAL(15,2),
                filing_status TEXT,
                filing_date DATE,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Settings table
        db.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                setting_key TEXT NOT NULL,
                setting_value TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                UNIQUE(user_id, setting_key)
            )
        ''')
        
        db.commit()

# Load configuration
def load_config():
    """Load configuration from YAML file"""
    try:
        if os.path.exists(app.config['CONFIG_FILE']):
            with open(app.config['CONFIG_FILE'], 'r') as f:
                return yaml.safe_load(f)
    except Exception as e:
        app.logger.error(f"Error loading config: {e}")
    return {}

# Authentication helpers
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        db = get_db()
        user = db.execute(
            'SELECT is_admin FROM users WHERE id = ?', 
            (session['user_id'],)
        ).fetchone()
        
        if not user or not user['is_admin']:
            flash('Admin access required.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        db = get_db()
        user = db.execute(
            'SELECT * FROM users WHERE username = ?', (username,)
        ).fetchone()
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash']):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['is_admin'] = user['is_admin']
            
            # Update last login
            db.execute(
                'UPDATE users SET last_login = ? WHERE id = ?',
                (datetime.utcnow(), user['id'])
            )
            db.commit()
            
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'error')
    
    return render_template('auth/login.html')

@app.route('/register', methods=['GET', 'POST'])
@limiter.limit("3 per minute")
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        db = get_db()
        
        # Check if user exists
        existing = db.execute(
            'SELECT id FROM users WHERE username = ? OR email = ?',
            (username, email)
        ).fetchone()
        
        if existing:
            flash('Username or email already exists.', 'error')
        else:
            # Hash password
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            # Check if this is the first user (make admin)
            user_count = db.execute('SELECT COUNT(*) as count FROM users').fetchone()['count']
            is_admin = user_count == 0
            
            # Create user
            db.execute(
                'INSERT INTO users (username, email, password_hash, is_admin) VALUES (?, ?, ?, ?)',
                (username, email, password_hash, is_admin)
            )
            db.commit()
            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
    
    return render_template('auth/register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Main routes
@app.route('/')
@login_required
def index():
    return render_template('pages/home.html')

@app.route('/income')
@login_required
def income():
    db = get_db()
    incomes = db.execute(
        'SELECT * FROM income WHERE user_id = ? ORDER BY created_at DESC',
        (session['user_id'],)
    ).fetchall()
    return render_template('pages/income.html', incomes=incomes)

@app.route('/bills')
@login_required
def bills():
    db = get_db()
    bills = db.execute(
        'SELECT * FROM bills WHERE user_id = ? ORDER BY due_date ASC',
        (session['user_id'],)
    ).fetchall()
    return render_template('pages/bills.html', bills=bills)

@app.route('/taxes')
@login_required
def taxes():
    db = get_db()
    taxes = db.execute(
        'SELECT * FROM taxes WHERE user_id = ? ORDER BY tax_year DESC',
        (session['user_id'],)
    ).fetchall()
    return render_template('pages/taxes.html', taxes=taxes)

@app.route('/settings')
@login_required
def settings():
    db = get_db()
    user_settings = db.execute(
        'SELECT setting_key, setting_value FROM settings WHERE user_id = ?',
        (session['user_id'],)
    ).fetchall()
    
    settings_dict = {setting['setting_key']: setting['setting_value'] for setting in user_settings}
    return render_template('pages/settings.html', settings=settings_dict)

# API routes for dynamic content
@app.route('/api/income', methods=['POST'])
@login_required
def add_income():
    data = request.get_json()
    
    db = get_db()
    db.execute(
        'INSERT INTO income (user_id, name, amount, frequency, frequency_day, earner_name, earner_type, start_date, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
        (session['user_id'], data['name'], data['amount'], data['frequency'], 
         data.get('frequency_day'), data['earner_name'], data['earner_type'], 
         data.get('start_date'), data.get('notes'))
    )
    db.commit()
    
    return jsonify({'status': 'success'})

@app.route('/api/bills', methods=['POST'])
@login_required
def add_bill():
    data = request.get_json()
    
    db = get_db()
    db.execute(
        'INSERT INTO bills (user_id, name, amount, due_date, category, is_recurring, notes) VALUES (?, ?, ?, ?, ?, ?, ?)',
        (session['user_id'], data['name'], data['amount'], data['due_date'], 
         data.get('category'), data.get('is_recurring', False), data.get('notes'))
    )
    db.commit()
    
    return jsonify({'status': 'success'})

@app.route('/api/taxes', methods=['POST'])
@login_required
def add_tax_record():
    data = request.get_json()
    
    db = get_db()
    db.execute(
        'INSERT INTO taxes (user_id, tax_year, income, deductions, taxes_owed, taxes_paid, filing_status, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        (session['user_id'], data['tax_year'], data.get('income'), data.get('deductions'),
         data.get('taxes_owed'), data.get('taxes_paid'), data.get('filing_status'), data.get('notes'))
    )
    db.commit()
    
    return jsonify({'status': 'success'})

# Health check endpoint
@app.route('/health')
def health():
    return {'status': 'healthy', 'version': '1.0.0'}, 200

# Database initialization endpoint
@app.route('/init-db')
def init_database():
    """Initialize database tables"""
    try:
        init_db()
        return {"status": "success", "message": "Database initialized successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('errors/500.html'), 500

# Context processors
@app.context_processor
def inject_config():
    config = load_config()
    return dict(
        app_name=config.get('app_name', 'Budget101'),
        app_version=config.get('version', '1.0.0'),
        current_year=datetime.now().year
    )

# Database teardown
@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        db.close()

if __name__ == '__main__':
    # Ensure config directory exists
    os.makedirs('/config', exist_ok=True)
    
    # Initialize database
    init_db()
    
    # Run the app
    app.run(host='0.0.0.0', port=9715, debug=os.environ.get('DEBUG', 'false').lower() == 'true') 