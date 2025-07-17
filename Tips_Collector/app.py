from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from extensions import db
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import csv
from flask import Response
from flask import flash
from weasyprint import HTML
from io import BytesIO
from models.tips import User,Tip
from flask import make_response

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
db.init_app(app)
# --- Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['GET', 'POST'])
def submit_tip():
    if request.method == 'POST':
        text = request.form.get('tip')
        category = request.form.get('category')
        uploaded_file = request.files.get('file')
        latitude=request.form.get('latitude')
        longitude=request.form.get('longitude')

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
            latitude=float(latitude) if latitude else None, # or get from form if using coordinates
            longitude=float(longitude) if longitude else None,
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

from models.tips import User  # make sure you import your User model

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Look up the user from the database
        user = User.query.filter_by(username=username).first()

        # Check if the user exists and password is correct
        if user and user.check_password(password):
            session['admin'] = user.is_admin  # mark as admin only if true
            session['username'] = user.username
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('admin_login.html', error='Invalid credentials')

    return render_template('admin_dashboard.html')


from sqlalchemy import func

@app.route('/admin/dashboard')
def admin_dashboard():
    # Total tips count
    total_tips = Tip.query.count()

    # Group tips by category and get counts
    tips_by_category = (
        db.session.query(Tip.category, func.count(Tip.id))
        .group_by(Tip.category)
        .all()
    )

    # Also fetch all tips to list them
    tips = Tip.query.order_by(Tip.timestamp.desc()).all()

    return render_template(
        'admin_dashboard.html',
        total_tips=total_tips,
        tips_by_category=tips_by_category,
        tips=tips,
    )


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


@app.route('/admin/tips/export/pdf')
def download_tips_pdf():
    tips = Tip.query.order_by(Tip.timestamp.desc()).all()

    # Render HTML template with tips
    rendered = render_template('tips_pdf.html', tips=tips)

    # Create a PDF
    pdf_file = HTML(string=rendered).write_pdf()

    # Send PDF as response
    response = make_response(pdf_file)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=tips.pdf'
    return response

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            return render_template('register.html', error="Passwords do not match")

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return render_template('register.html', error="Username already exists")

        new_user = User(username=username)
        new_user.set_password(password)  # ← important!
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('admin_login'))

    return render_template('register.html')

from flask import render_template, request, redirect, url_for, flash

@app.route('/admin/tips')
def admin_tips():
    search = request.args.get('search')
    if search:
        tips = Tip.query.filter(Tip.text.contains(search)).all()
    else:
        tips = Tip.query.order_by(Tip.timestamp.desc()).all()
    return render_template('admin_tips.html', tips=tips)

@app.route('/admin/tips/delete/<int:tip_id>', methods=['POST'])
def delete_tip(tip_id):
    tip = Tip.query.get_or_404(tip_id)
    db.session.delete(tip)
    db.session.commit()
    flash('Tip deleted successfully', 'success')
    return redirect(url_for('admin_tips'))


# --- Run Server ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)
