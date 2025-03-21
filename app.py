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
from flask import send_from_directory

@app.route('/google33e5aa107a02cac2.html')
def google_verification():
    return send_from_directory('static', 'google33e5aa107a02cac2.html')
from flask import Response
from datetime import datetime

@app.route('/sitemap.xml')
def sitemap():
    urls = URL.query.all()  # Get all shortened URLs from the database
    xml = """<?xml version="1.0" encoding="UTF-8"?>
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
        <url><loc>https://flask-url-shortener-g0em.onrender.com/</loc></url>
    """
    for url in urls:
        xml += f"""
        <url>
            <loc>https://flask-url-shortener-g0em.onrender.com/{url.short_url}</loc>
            <lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod>
            <changefreq>daily</changefreq>
            <priority>0.8</priority>
        </url>
        """
    xml += "</urlset>"
    return Response(xml, mimetype='application/xml')
qr_pages = [
    {"short_url": "google-qr", "original_url": "https://www.google.com"},
    {"short_url": "facebook-qr", "original_url": "https://www.facebook.com"},
    {"short_url": "instagram-qr", "original_url": "https://www.instagram.com"}
]

@app.route('/qr_sitemap.xml')
def qr_sitemap():
    xml = """<?xml version="1.0" encoding="UTF-8"?>
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    """
    for page in qr_pages:
        xml += f"""
        <url>
            <loc>https://flask-url-shortener-g0em.onrender.com/{page['short_url']}</loc>
            <changefreq>monthly</changefreq>
            <priority>0.6</priority>
        </url>
        """
    xml += "</urlset>"
    return Response(xml, mimetype='application/xml')
