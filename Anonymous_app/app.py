from flask import  Flask, render_template, request, redirect, url_for
import json
from datetime import datetime
from flask import session
import os
from werkzeug.utils import secure_filename
from extensions import db
from flask_migrate import Migrate

                  
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tips.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db.init_app(app)

migrate= Migrate(app,db)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['GET', 'POST'])
def submit_tip():
    from models.tip import Tip

    if request.method == 'POST':
        corruption_type = request.form.get('corruption_type')
        location = request.form.get('location')
        date= request.form.get('date')
        people = request.form.get('people')
        tip_category = request.form.get('tip_category')
        text= request.form.get('text')
        file = request.files.get('file')
        filename = None

        # Save file if uploaded
        if file and file.filename:
            filename = secure_filename(file.filename)
            file_path = os.path.join('uploads', filename)
            file.save(file_path)

        # Save to the database
        new_tip = Tip(
            corruption_type=corruption_type,
            location=location,
            date=date,
            people=people,
            tip_category=tip_category,
            text=text,
            file=filename,
            timestamp=datetime.now()
        )
        db.session.add(new_tip)
        db.session.commit()

        return redirect(url_for('thank_you'))

    # GET request - show the form
    return render_template('submit_tip.html')

@app.route('/thank-you')
def thank_you():
    return render_template('thank_you.html')


app.secret_key='your-secret-key' #required for login sessions

@app.route('/admin', methods=['GET','POST'])
def admin_login():
    
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        if username =='admin' and password =='1234':
                    session['admin']=True
        return redirect(url_for('admin_dashboard'))

    else:
        return render_template('admin_login.html', )
    return render_template('admin_login.html')
@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    tips = []
    if os.path.exists('data/tips.json'):
        with open('data/tips.json') as f:
            for line in f:
                tips.append(json.loads(line.strip()))

    return render_template('admin_dashboard.html', tips=tips)


if __name__ == '__main__':
    with app.app_context():
        from extensions import db
        db.create_all()
    app.run(debug=True, port=5001)
