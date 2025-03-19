from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import shortuuid
import qrcode
from io import BytesIO
import base64
import os  # ✅ This should be at the top

# Initialize Flask app
app = Flask(__name__)

# Set up the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Model
class URL(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Unique ID
    original_url = db.Column(db.String(500), nullable=False)  # Long URL
    short_url = db.Column(db.String(10), unique=True, nullable=False)  # Short URL
    clicks = db.Column(db.Integer, default=0)  # Track how many times the link is clicked

# Home Page (where users enter a URL)
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':  # When user submits a URL
        original_url = request.form['url']  # Get the long URL
        short_url = shortuuid.ShortUUID().random(length=6)  # Generate short code

        # Save to database
        new_url = URL(original_url=original_url, short_url=short_url)
        db.session.add(new_url)
        db.session.commit()

        # ✅ Get the Render URL (fallback to local if not available)
        render_url = os.getenv("RENDER_EXTERNAL_URL", "https://flask-url-shortener-g0em.onrender.com")

        # ✅ Generate the QR Code with the correct live link
        qr = qrcode.make(f"{render_url}/{short_url}")

        img_io = BytesIO()
        qr.save(img_io, 'PNG')
        img_io.seek(0)
        qr_base64 = base64.b64encode(img_io.getvalue()).decode()

        return render_template('home.html', short_url=short_url, qr_code=qr_base64, clicks=new_url.clicks)

    return render_template('home.html')

# Redirect the short URL to the original website
@app.route('/<short_url>')
def redirect_url(short_url):
    url_data = URL.query.filter_by(short_url=short_url).first()
    if url_data:
        url_data.clicks += 1  # Increase click count
        db.session.commit()
        return redirect(url_data.original_url)
    return "URL not found", 404

# Run the app
if __name__ == '__main__':
    with app.app_context():  # Ensures database creation inside Flask context
        db.create_all()
    app.run(debug=True)  # Start Flask server
