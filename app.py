import os
import time
from flask import Flask, render_template, request, flash, redirect, url_for
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from flask_caching import Cache  # Flask-Cache for caching results
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Load SendGrid API key from environment variable
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')

# Cache configuration
cache = Cache(config={"CACHE_TYPE": "SimpleCache"})
cache.init_app(app)

# Fetch latest TikTok videos
def get_latest_tiktok_videos():
    """Fetch the latest TikTok video embed URLs."""
    retries = 3
    for attempt in range(retries):
        try:
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")  # Disable GPU acceleration
            options.add_argument("--no-sandbox")  # Required for some environments
            options.add_argument("--disable-dev-shm-usage") 
            
            
            
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

            # Open the TikTok channel
            driver.get("https://www.tiktok.com/@sportsqr")
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href*="/video/"]')))

            # Find video elements and extract URLs
            videos = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/video/"]')[:4]
            embed_urls = [video.get_attribute('href') for video in videos]

            # Convert to embed URLs
            embed_urls = [
                f"https://www.tiktok.com/embed/{url.split('/')[-1]}" for url in embed_urls
            ]

            # Generate embed codes
            embeds = [
                f'<iframe src="{url}" width="300" height="500" frameborder="0" allowfullscreen></iframe>'
                for url in embed_urls
            ]

            driver.quit()
            return embeds
        except Exception as e:
            print(f"Error fetching TikTok videos (attempt {attempt + 1}/{retries}): {e}")
            time.sleep(2)  # Wait before retrying
    return []

@cache.cached(timeout=300)  # Cache for 10 minutes
def fetch_and_cache_videos():
    """Fetch and cache the TikTok videos."""
    return get_latest_tiktok_videos()

@app.route("/")
def index():
    # Fetch latest TikTok videos from cache
    latest_videos = fetch_and_cache_videos()
    print(latest_videos)  # Debug: Check embed codes
    return render_template("index.html", latest_videos=latest_videos)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        surname = request.form.get('surname')
        email = request.form.get('email')
        message = request.form.get('message')

        if not all([name, surname, email, message]):
            flash('Lütfen tüm alanları doldurun.', 'error')
            return redirect(url_for('contact'))

        # Create the email content
        subject = f"Yeni İletişim Mesajı: {name} {surname}"
        body = f"Ad: {name}\nSoyad: {surname}\nE-posta: {email}\nMesaj: {message}"

        # Send email using SendGrid
        try:
            mail = Mail(
                from_email='info@sportsqr.com.tr',
                to_emails='info@sportsqr.com.tr',
                subject=subject,
                plain_text_content=body
            )
            sg = SendGridAPIClient(SENDGRID_API_KEY)
            response = sg.send(mail)
            flash('Mesajınız başarıyla gönderildi.', 'success')
        except Exception as e:
            flash('Mesaj gönderilirken bir hata oluştu.', 'error')
            print(f"Error: {e}")

        return redirect(url_for('index'))  # Redirect to home page

    return render_template('contact.html')


if __name__ == "__main__":
    app.run(debug=True)
