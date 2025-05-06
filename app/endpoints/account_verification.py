import os
from flask import Blueprint, request, jsonify
import smtplib
from email.mime.text import MIMEText
import random
from datetime import datetime, timedelta

verify_api = Blueprint('verify_api', __name__)

verification_codes = {}


@verify_api.route('/api/send-verification-code/', methods=['POST'])
def send_verification_code():
    def generate_verification_code():
        """Генерация 4-значного кода подтверждения"""
        return str(random.randint(1000, 9999))

    # Конфигурация SMTP Яндекс
    YANDEX_SMTP_SERVER = 'smtp.yandex.ru'
    YANDEX_SMTP_PORT = 465
    YANDEX_EMAIL = os.environ["SMTP_EMAIL"]  # Ваш яндекс email
    YANDEX_PASSWORD = os.environ["SMTP_PASSWORD"]  # Пароль или app-specific пароль
    """Отправка кода подтверждения на email"""
    email = request.json.get('email')

    if not email:
        return jsonify({'error': 'Email is required'}), 400

    verification_code = generate_verification_code()
    expires_at = datetime.now() + timedelta(minutes=15)  # Код действителен 15 минут

    verification_codes[email] = {
        'code': verification_code,
        'expires_at': expires_at
    }
    try:
        # Создаем сообщение
        msg = MIMEText(f'Ваш код подтверждения: {verification_code}')
        msg['Subject'] = 'Код подтверждения'
        msg['From'] = f'Your App Name <{YANDEX_EMAIL}>'
        msg['To'] = email

        # Отправляем email через SMTP Яндекс
        with smtplib.SMTP_SSL(YANDEX_SMTP_SERVER, YANDEX_SMTP_PORT) as server:
            server.login(YANDEX_EMAIL, YANDEX_PASSWORD)
            server.sendmail(YANDEX_EMAIL, [email], msg.as_string())

        return jsonify({
            'success': True,
            'message': 'Verification code sent'
        })

    except Exception as e:
        print(f'Error sending email: {e}')
        return jsonify({
            'error': 'Failed to send verification code'
        }), 500


@verify_api.route('/api/verify-code', methods=['POST'])
def verify_code():
    """Проверка кода подтверждения"""
    email = request.json.get('email')
    code = request.json.get('code')

    if not email or not code:
        return jsonify({'error': 'Email and code are required'}), 400

    stored_code = verification_codes.get(email)

    if not stored_code:
        return jsonify({'error': 'No verification code found for this email'}), 400

    if datetime.now() > stored_code['expires_at']:
        del verification_codes[email]  # Удаляем просроченный код
        return jsonify({'error': 'Verification code has expired'}), 400

    if stored_code['code'] != code:
        return jsonify({'error': 'Invalid verification code'}), 400

    # Код верный - подтверждаем email
    del verification_codes[email]

    return jsonify({
        'success': True,
        'message': 'Email successfully verified'
    })
