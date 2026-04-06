import os
import sqlite3
import pandas as pd
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

from ai_engine import extract_text_from_pdf, analyze_resume

load_dotenv()
app = Flask(__name__)

app.secret_key = os.getenv('SECRET_KEY', 'nexus_ai_recruit_2026_key')
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            firstname TEXT,
            email TEXT UNIQUE,
            password TEXT
        )
    ''')
    cursor.execute("INSERT OR IGNORE INTO users (firstname, email, password) VALUES (?, ?, ?)", 
                   ('Admin', 'admin@test.com', '12345'))
    conn.commit()
    conn.close()

init_db()

def load_categories():
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        dataset_path = os.path.join(base_dir, 'UpdatedResumeDataSet.csv')
        if os.path.exists(dataset_path):
            df = pd.read_csv(dataset_path)
            return df['Category'].unique().tolist()
    except:
        pass
    return ["Data Science", "Web Designing", "Java Developer", "HR", "Testing", "Blockchain"]

categories = load_categories()

@app.route('/')
def home():
    if 'user' not in session:
        return render_template('auth.html')
    return render_template('index.html', user=session['user'])

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT firstname FROM users WHERE email=? AND password=?", (email, password))
    user = cursor.fetchone()
    conn.close()
    if user:
        session['user'] = user[0]
        return redirect(url_for('home'))
    return "Invalid Credentials! <a href='/'>Try Again</a>"

@app.route('/signup', methods=['POST'])
def signup():
    fname = request.form.get('firstname')
    email = request.form.get('email')
    password = request.form.get('password')
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (firstname, email, password) VALUES (?, ?, ?)", (fname, email, password))
        conn.commit()
        conn.close()
        session['user'] = fname
        return redirect(url_for('home'))
    except:
        return "Signup Failed! <a href='/'>Try Again</a>"

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    file = request.files.get('resume')
    jd = request.form.get('job_description', '')
    if file and jd:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        try:
            resume_text = extract_text_from_pdf(filepath)
            score, role, gaps, questions = analyze_resume(resume_text, jd, categories)
            
            session['report_data'] = {
                "score": score,
                "role": role,
                "gaps": gaps,
                "questions": questions
            }
            return jsonify({"status": "Success", "redirect": url_for('display_report')})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    return jsonify({"error": "Missing input"}), 400

@app.route('/report')
def display_report():
    if 'report_data' not in session:
        return redirect(url_for('home'))
    data = session['report_data']
    return render_template('report.html', data=data, user=session['user'])

@app.route('/analytics')
def display_analytics():
    if 'report_data' not in session:
        return redirect(url_for('home'))
    data = session['report_data']
    return render_template('analytics.html', data=data, user=session['user'])

if __name__ == '__main__':
    app.run(debug=True)