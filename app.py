from flask import Flask, request
from flask_mail import Mail, Message
from celery import Celery
from datetime import datetime
import logging
import os

app = Flask(__name__)
app.config.from_object('config.Config')
mail = Mail(app)

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

@celery.task
def send_email_task(recipient):
    with app.app_context():
        msg = Message('Hello', recipients=[recipient])
        msg.body = 'This is a test email sent from Flask app using Celery and RabbitMQ'
        mail.send(msg)

@app.route('/')
def index():
    sendmail = request.args.get('sendmail')
    talktome = request.args.get('talktome')

    if sendmail:
        send_email_task.delay(sendmail)
        return f'Email queued to be sent to {sendmail}'

    if talktome:
        log_time()
        return 'Current time logged'

    return 'Welcome to the messaging system!'

def log_time():
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_dir = '/var/log/messaging_system'
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, 'messaging_system.log')
    with open(log_file, 'a') as f:
        f.write(f'{current_time}\n')

if __name__ == '__main__':
    app.run(debug=True)

