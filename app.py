import os
import time
from flask import Flask, render_template, request, flash, redirect, url_for
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Load SendGrid API key from environment variable
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')

# Manually updated TikTok video embed URLs
def get_tiktok_embeds():
    return [
        '<iframe src="https://www.tiktok.com/embed/VIDEO_ID_1" width="300" height="500" frameborder="0" allowfullscreen></iframe>',
        '<iframe src="https://www.tiktok.com/embed/VIDEO_ID_2" width="300" height="500" frameborder="0" allowfullscreen></iframe>',
        '<iframe src="https://www.tiktok.com/embed/VIDEO_ID_3" width="300" height="500" frameborder="0" allowfullscreen></iframe>',
        '<iframe src="https://www.tiktok.com/embed/VIDEO_ID_4" width="300" height="500" frameborder="0" allowfullscreen></iframe>'
    ]

@app.route("/")
def index():
    latest_videos = get_tiktok_embeds()
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

        subject = f"Yeni İletişim Mesajı: {name} {surname}"
        body = f"Ad: {name}\nSoyad: {surname}\nE-posta: {email}\nMesaj: {message}"

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

        return redirect(url_for('index'))

    return render_template('contact.html')

if __name__ == "__main__":
    app.run(debug=True)
