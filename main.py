from flask import Flask, request, jsonify
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

PORT = 5000
GEMINI_API_KEY = "AIzaSyD9bY-arTKXudeWCebi587DkZt_-Y2WtvA"
GEMINI_ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

EMAIL_ADDRESS = "uhhfj0345@gmail.com"
EMAIL_PASSWORD = "oliw smeo tpjv ceze"  # App password

@app.route('/', methods=['GET'])
def home():
    return "Hello from SMIT Chatbot Backend (Python)!"

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json()
    intent = req["queryResult"]["intent"]["displayName"]

    if intent == "welcome":
        return make_response("👋 Assalamu Alaikum! Welcome to SMIT 💻\nHow can I assist you today?")

    elif intent == "registration":
        params = req["queryResult"]["parameters"]
        return send_registration_email(params)

    elif intent == "donation":
        params = req["queryResult"]["parameters"]
        return send_donation_email(params)

    else:
        user_message = req["queryResult"]["queryText"]
        return gemini_fallback(user_message)

def send_registration_email(params):
    name = params.get("name")
    cnic = params.get("cnic")
    email = params.get("email")
    phone = params.get("phone")
    address = params.get("address")
    course = params.get("course")

    subject = "🎓 SMIT Course Registration Confirmation"
    html = f"""
        <h2>Thank you, {name}!</h2>
        <p>You have successfully registered for the course: <strong>{course}</strong>.</p>
        <h3>Your Registration Details:</h3>
        <ul>
          <li><b>Name:</b> {name}</li>
          <li><b>CNIC:</b> {cnic}</li>
          <li><b>Email:</b> {email}</li>
          <li><b>Phone:</b> {phone}</li>
          <li><b>Address:</b> {address}</li>
        </ul>
        <p>We will contact you soon with further details.</p>
        <br/>
        <p>Regards,<br/>SMIT Admissions Team</p>
    """
    send_email(email, subject, html)

    return make_response(f"✅ Thank you, dear! Your registration for \"{course}\" has been received. A confirmation email has been sent to {email}.")

def send_donation_email(params):
    name = params.get("name")
    email = params.get("email")
    number = params.get("number")

    subject = "🙏 SMIT Donation Confirmation"
    html = f"""
        <h2>Dear {name},</h2>
        <p>Thank you for your generous donation! 🙏</p>
        <h3>Donation Details:</h3>
        <ul>
          <li><b>Name:</b> {name}</li>
          <li><b>Email:</b> {email}</li>
          <li><b>Amount/Quantity:</b> {number}</li>
        </ul>
        <p>Your support helps us build a better future.</p>
        <br/>
        <p>Warm regards,<br/>SMIT Donations Team</p>
    """
    send_email(email, subject, html)

    return make_response(f"🎁 Thank you, dear, for donating {number}! We’ve sent a confirmation email to {email}.")

def gemini_fallback(user_message):
    payload = {
        "contents": [{
            "parts": [{
                "text": f"You are a helpful assistant for SMIT (Saylani Mass IT Training). Answer this user query politely: {user_message}"
            }]
        }]
    }

    headers = { "Content-Type": "application/json" }

    try:
        response = requests.post(GEMINI_ENDPOINT, json=payload, headers=headers)
        response.raise_for_status()
        gemini_text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
        return make_response(gemini_text)
    except Exception as e:
        print("Gemini Error:", e)
        return make_response("⚠️ Sorry, I'm having trouble understanding that. Please try again later.")

def send_email(to, subject, html_content):
    msg = MIMEMultipart()
    msg["From"] = EMAIL_ADDRESS
    
    # Handle both string and list recipients
    if isinstance(to, list):
        msg["To"] = ", ".join(to)
        recipients = to
    else:
        msg["To"] = to
        recipients = [to]
    
    msg["Subject"] = subject

    msg.attach(MIMEText(html_content, "html"))

    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    server.sendmail(EMAIL_ADDRESS, recipients, msg.as_string())
    server.quit()

def make_response(text):
    return jsonify({
        "fulfillmentText": text
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=True)
