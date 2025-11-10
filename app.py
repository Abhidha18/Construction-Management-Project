"""
Flask Application for Construction Project Management System

This application manages projects, appointments, reminders, partners, and team members
for a construction company. It includes user authentication with secure password hashing.
"""

import os
import binascii
import hashlib
import sqlite3
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session

# ============================================================================
# APPLICATION INITIALIZATION
# ============================================================================

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your_super_secret_key_change_this_later')


# ============================================================================
# UTILITY FUNCTIONS - PASSWORD HASHING
# ============================================================================

def hash_password(password: str, salt_hex: str | None = None) -> tuple[str, str]:
    """
    Hash a password with a salt using PBKDF2.
    
    Args:
        password: Plain text password to hash
        salt_hex: Optional hexadecimal salt string. If None, a new salt is generated.
    
    Returns:
        Tuple of (salt_hex, password_hash) as hexadecimal strings
    """
    if salt_hex is None:
        salt = os.urandom(16)
    else:
        salt = binascii.unhexlify(salt_hex)
    
    dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100_000)
    return binascii.hexlify(salt).decode('ascii'), binascii.hexlify(dk).decode('ascii')


# ============================================================================
# DATABASE MANAGEMENT
# ============================================================================

def get_db_connection() -> sqlite3.Connection:
    """
    Establish a connection to the SQLite database.
    
    Returns:
        SQLite connection object with row_factory set to Row
    """
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

def setup_database() -> None:
    """
    Initialize the database and create all required tables.
    
    Creates tables for: users, projects, appointments, reminders, partners, team_members
    """
    conn = get_db_connection()
    
    # Users table for authentication
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            salt TEXT NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    
    # Projects table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            engineer TEXT,
            contractor TEXT,
            start_date TEXT,
            due_date TEXT,
            contact TEXT,
            drive_link TEXT,
            status TEXT NOT NULL DEFAULT 'ongoing'
        )
    ''')
    
    # Appointments table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            appt_date TEXT NOT NULL,
            appt_time TEXT NOT NULL,
            attendees TEXT
        )
    ''')
    
    # Reminders table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            done INTEGER NOT NULL DEFAULT 0
        )
    ''')
    
    # Partners table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS partners (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT,
            contact_person TEXT,
            contact_email TEXT,
            contact_phone TEXT
        )
    ''')
    
    # Team members table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS team_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            role TEXT NOT NULL,
            email TEXT,
            phone TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database and all tables created successfully.")


# ============================================================================
# AUTHENTICATION & AUTHORIZATION
# ============================================================================

def login_required(f):
    """
    Decorator to protect routes that require user authentication.
    
    Args:
        f: The route function to protect
    
    Returns:
        Decorated function that checks for authentication
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# ============================================================================
# AUTHENTICATION ROUTES
# ============================================================================

@app.route('/', methods=['GET', 'POST'])
def login():
    """
    Handle user login.
    
    GET: Display login form
    POST: Authenticate user and create session
    """
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Please enter both username and password.', 'warning')
            return render_template('login.html')
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if user:
            salt_hex, stored_hash = user['salt'], user['password_hash']
            _, try_hash = hash_password(password, salt_hex)
            
            if try_hash == stored_hash:
                session['username'] = user['username']
                flash(f'Welcome, {session["username"]}!', 'success')
                return redirect(url_for('dashboard'))
        
        flash('Invalid username or password.', 'danger')
    
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handle new user registration.
    
    GET: Display registration form
    POST: Create new user account
    """
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Please enter both username and password.', 'warning')
            return render_template('register.html')
        
        salt_hex, pwd_hash = hash_password(password)
        
        try:
            conn = get_db_connection()
            conn.execute(
                'INSERT INTO users (username, salt, password_hash) VALUES (?, ?, ?)',
                (username, salt_hex, pwd_hash)
            )
            conn.commit()
            conn.close()
            
            flash(f'User "{username}" registered successfully. Please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists. Please choose another.', 'danger')
            return render_template('register.html')
    
    return render_template('register.html')


@app.route('/logout')
@login_required
def logout():
    """Log out the current user and clear session."""
    username = session.get('username', 'User')
    session.pop('username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


# ============================================================================
# DASHBOARD ROUTES
# ============================================================================

@app.route('/dashboard')
@login_required
def dashboard():
    """Display the main dashboard."""
    return render_template('index.html')


# ============================================================================
# PROJECT ROUTES
# ============================================================================

@app.route('/projects')
@login_required
def projects():
    """Display all ongoing projects."""
    conn = get_db_connection()
    ongoing_projects = conn.execute(
        "SELECT * FROM projects WHERE status = 'ongoing' ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return render_template('projects.html', projects=ongoing_projects)


@app.route('/completed_projects')
@login_required
def completed_projects():
    """Display all completed projects."""
    conn = get_db_connection()
    projects = conn.execute(
        "SELECT * FROM projects WHERE status = 'completed' ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return render_template('completed_projects.html', projects=projects)


@app.route('/add_project', methods=['GET', 'POST'])
@login_required
def add_project():
    """
    Add a new project.
    
    GET: Display project creation form
    POST: Save new project to database
    """
    if request.method == 'POST':
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO projects (name, engineer, contractor, start_date, due_date, contact, drive_link)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            request.form.get('proj-name', '').strip(),
            request.form.get('chief-engineer', '').strip(),
            request.form.get('contracted-by', '').strip(),
            request.form.get('start-date', ''),
            request.form.get('due-date', ''),
            request.form.get('contact', '').strip(),
            request.form.get('drive-link', '').strip()
        ))
        conn.commit()
        conn.close()
        
        project_name = request.form.get('proj-name', '').strip()
        flash(f"Project '{project_name}' has been added successfully!", "success")
        return redirect(url_for('projects'))
    
    return render_template('add_project.html')


@app.route('/project/<int:project_id>')
@login_required
def project_details(project_id):
    """Display details for a specific project."""
    conn = get_db_connection()
    project = conn.execute('SELECT * FROM projects WHERE id = ?', (project_id,)).fetchone()
    conn.close()
    
    if not project:
        flash('Project not found.', 'danger')
        return redirect(url_for('projects'))
    
    return render_template('project_details.html', project=project)


@app.route('/complete_project/<int:project_id>', methods=['POST'])
@login_required
def complete_project(project_id):
    """Mark a project as completed."""
    conn = get_db_connection()
    conn.execute("UPDATE projects SET status = 'completed' WHERE id = ?", (project_id,))
    conn.commit()
    conn.close()
    
    flash('Project has been marked as completed.', 'info')
    return redirect(url_for('projects'))


# ============================================================================
# APPOINTMENT ROUTES
# ============================================================================

@app.route('/appointments', methods=['GET', 'POST'])
@login_required
def appointments():
    """
    Manage appointments.
    
    GET: Display all appointments and form to add new one
    POST: Create new appointment
    """
    conn = get_db_connection()
    
    if request.method == 'POST':
        conn.execute('''
            INSERT INTO appointments (title, appt_date, appt_time, attendees)
            VALUES (?, ?, ?, ?)
        ''', (
            request.form.get('title', '').strip(),
            request.form.get('appt_date', ''),
            request.form.get('appt_time', ''),
            request.form.get('attendees', '').strip()
        ))
        conn.commit()
        flash('New appointment scheduled successfully!', 'success')
        conn.close()
        return redirect(url_for('appointments'))
    
    all_appointments = conn.execute(
        'SELECT * FROM appointments ORDER BY appt_date, appt_time'
    ).fetchall()
    conn.close()
    
    return render_template('appointments.html', appointments=all_appointments)


@app.route('/delete_appointment/<int:appt_id>', methods=['POST'])
@login_required
def delete_appointment(appt_id):
    """Delete an appointment."""
    conn = get_db_connection()
    conn.execute('DELETE FROM appointments WHERE id = ?', (appt_id,))
    conn.commit()
    conn.close()
    
    flash('Appointment has been deleted.', 'info')
    return redirect(url_for('appointments'))


# ============================================================================
# REMINDER ROUTES
# ============================================================================

@app.route('/reminders', methods=['GET', 'POST'])
@login_required
def reminders():
    """
    Manage reminders/tasks.
    
    GET: Display all reminders and form to add new one
    POST: Create new reminder
    """
    conn = get_db_connection()
    
    if request.method == 'POST':
        reminder_text = request.form.get('text', '').strip()
        if reminder_text:
            conn.execute('INSERT INTO reminders (text) VALUES (?)', (reminder_text,))
            conn.commit()
            flash('New reminder added!', 'success')
        conn.close()
        return redirect(url_for('reminders'))
    
    all_reminders = conn.execute(
        'SELECT * FROM reminders ORDER BY done, id DESC'
    ).fetchall()
    conn.close()
    
    return render_template('reminders.html', reminders=all_reminders)


@app.route('/toggle_reminder/<int:rem_id>', methods=['POST'])
@login_required
def toggle_reminder(rem_id):
    """Toggle the completion status of a reminder."""
    conn = get_db_connection()
    reminder = conn.execute('SELECT done FROM reminders WHERE id = ?', (rem_id,)).fetchone()
    
    if reminder:
        new_status = 0 if reminder['done'] else 1
        conn.execute('UPDATE reminders SET done = ? WHERE id = ?', (new_status, rem_id))
        conn.commit()
    
    conn.close()
    return redirect(url_for('reminders'))


# ============================================================================
# PARTNER ROUTES
# ============================================================================

@app.route('/partners', methods=['GET', 'POST'])
@login_required
def partners():
    """
    Manage partners.
    
    GET: Display all partners and form to add new one
    POST: Create new partner
    """
    conn = get_db_connection()
    
    if request.method == 'POST':
        conn.execute('''
            INSERT INTO partners (name, type, contact_person, contact_email, contact_phone)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            request.form.get('name', '').strip(),
            request.form.get('type', '').strip(),
            request.form.get('contact_person', '').strip(),
            request.form.get('contact_email', '').strip(),
            request.form.get('contact_phone', '').strip()
        ))
        conn.commit()
        
        partner_name = request.form.get('name', '').strip()
        flash(f'Partner "{partner_name}" added successfully!', 'success')
        conn.close()
        return redirect(url_for('partners'))
    
    all_partners = conn.execute('SELECT * FROM partners ORDER BY name').fetchall()
    conn.close()
    
    return render_template('partners.html', partners=all_partners)


# ============================================================================
# TEAM ROUTES
# ============================================================================

@app.route('/team', methods=['GET', 'POST'])
@login_required
def team():
    """
    Manage team members.
    
    GET: Display all team members and form to add new one
    POST: Create new team member
    """
    conn = get_db_connection()
    
    if request.method == 'POST':
        conn.execute('''
            INSERT INTO team_members (name, role, email, phone)
            VALUES (?, ?, ?, ?)
        ''', (
            request.form.get('name', '').strip(),
            request.form.get('role', '').strip(),
            request.form.get('email', '').strip(),
            request.form.get('phone', '').strip()
        ))
        conn.commit()
        
        member_name = request.form.get('name', '').strip()
        flash(f'Team member "{member_name}" added successfully!', 'success')
        conn.close()
        return redirect(url_for('team'))
    
    team_members = conn.execute('SELECT * FROM team_members ORDER BY name').fetchall()
    conn.close()
    
    return render_template('team.html', team_members=team_members)


# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    # Initialize database if it doesn't exist
    if not os.path.exists('users.db'):
        setup_database()
    
    app.run(debug=True)