from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

load_dotenv() # Load your .env file

app = Flask(__name__)
app.secret_key = "supersecretkey" # Required for flash messages

# --- DATABASE CONFIG (Same as before) ---
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_name = os.getenv('DB_NAME')

app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}?ssl_verify_cert=true&ssl_verify_identity=true"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- MODELS ---
class Tutor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(100), nullable=False)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    time = db.Column(db.String(20), nullable=False)
    tutor_id = db.Column(db.Integer, db.ForeignKey('tutor.id'))

# --- ROUTES ---

@app.route('/')
def home():
    # Fetch tutors from DB to populate the dropdown
    all_tutors = Tutor.query.all()
    return render_template('home.html', tutors=all_tutors)

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/book')
def book():
    # Fetch the data needed for this page
    # Use SQLAlchemy queries to get tutors and bookings
    all_tutors = Tutor.query.all()
    all_bookings = Booking.query.all()
    
    return render_template('book.html', tutors=all_tutors, bookings=all_bookings)

@app.route('/book', methods=['POST'])
def book_session():
    # Get data from the form
    name = request.form.get('student_name')
    email = request.form.get('email')
    tutor = request.form.get('tutor_id')
    date = request.form.get('date')
    time = request.form.get('time')

    # Save to Database
    new_booking = Booking(
        student_name=name, email=email, tutor_id=tutor, date=date, time=time
    )
    db.session.add(new_booking)
    db.session.commit()

    # Show success message
    flash('✅ Booking Confirmed Successfully!', 'success')
    return redirect(url_for('home'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Create a dummy tutor if none exist so the dropdown isn't empty
        if not Tutor.query.first():
            db.session.add(Tutor(name="Dr. Smith", subject="Maths"))
            db.session.add(Tutor(name="Ms. Jones", subject="English"))
            db.session.commit()
            
    app.run(debug=True, port=5000)