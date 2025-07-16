from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import csv
from flask import Response
from flask import flash


# --- App Configuration ---
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tips.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB
app.secret_key = 'your-secret-key'

# --- Ensure upload folder exists ---
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# --- Initialize DB ---
db = SQLAlchemy(app)

# --- Tip Model ---
class Tip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50))
    filename = db.Column(db.String(100))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# --- Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['GET', 'POST'])
def submit_tip():
    if request.method == 'POST':
        text = request.form.get('tip')
        location = request.form.get('location')
        category = request.form.get('category')
        uploaded_file = request.files.get('file')

        if not text:
            flash("Tip text is required.", "danger")
            return redirect(request.url)

        # handle file upload
        filename = None
        if uploaded_file and uploaded_file.filename:
            filename = secure_filename(uploaded_file.filename)
            uploaded_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        new_tip = Tip(
            text=text,
            category=category,
            filename=filename,
            latitude=None,  # or get from form if using coordinates
            longitude=None,
            timestamp=datetime.now()
        )

        db.session.add(new_tip)
        db.session.commit()
        flash("Tip submitted successfully!", "success")
        return redirect(url_for('index'))  # or your success page

    return render_template('submit_tip.html')

@app.route('/thank-you')
def thank_you():
    return render_template('thank_you.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == '1234':
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('admin_login.html', error='Invalid credentials')
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    tips = Tip.query.order_by(Tip.timestamp.desc()).all()
    return render_template('admin_dashboard.html', tips=tips)

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('admin_login'))

@app.route('/api/tips', methods=['GET'])
def api_get_tips():
    tips = Tip.query.all()
    return jsonify([{
        'text': tip.text,
        'category': tip.category,
        'filename': tip.filename,
        'latitude': tip.latitude,
        'longitude': tip.longitude,
        'timestamp': tip.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    } for tip in tips])



@app.route('/admin/download-tips')
def download_tips():
    from models.tips import Tip
    tips = Tip.query.all()

    def generate():
        data = []
        header = ['ID', 'Text', 'Category', 'Filename', 'Latitude', 'Longitude', 'Timestamp']
        data.append(header)
        for tip in tips:
            row = [
                tip.id,
                tip.text,
                tip.category,
                tip.filename,
                tip.latitude,
                tip.longitude,
                tip.timestamp
            ]
            data.append(row)

        # Convert to CSV lines
        for row in data:
            yield ','.join(str(field) if field is not None else '' for field in row) + '\n'

    return Response(generate(), mimetype='text/csv',
                    headers={"Content-Disposition": "attachment;filename=tips.csv"})

# --- Run Server ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)
