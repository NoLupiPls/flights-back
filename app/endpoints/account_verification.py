import os
import socket
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Blueprint, request, jsonify, current_app
import random
from datetime import datetime, timedelta
from app.data import db_session
from app.data.users import User
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

verify_api = Blueprint('verify_api', __name__)


def send_email(to_email, verification_code):
    """
    Отправляет email с кодом подтверждения через Яндекс.Почту
    """
    # Получаем учетные данные из переменных окружения
    smtp_user = os.environ.get('YANDEX_EMAIL')
    smtp_password = os.environ.get('YANDEX_PASSWORD')
    
    if not smtp_user or not smtp_password:
        print("WARNING: YANDEX_EMAIL или YANDEX_PASSWORD не настроены. Письмо не отправлено!")
        return False
    
    # Настройки SMTP-сервера Яндекс
    smtp_server = "smtp.yandex.ru"
    smtp_port = 465  # SSL порт
    
    # Создаем сообщение
    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = to_email
    msg['Subject'] = "Код подтверждения для вашего аккаунта"
    
    # Формируем HTML-тело письма
    html = f"""
    <html>
    <body>
        <h2>Код подтверждения</h2>
        <p>Здравствуйте!</p>
        <p>Ваш код подтверждения: <strong style="font-size: 18px;">{verification_code}</strong></p>
        <p>Этот код действителен в течение 15 минут.</p>
        <p>Если вы не запрашивали этот код, просто проигнорируйте это письмо.</p>
        <p>С уважением,<br>Команда Flights App</p>
    </body>
    </html>
    """
    
    # Прикрепляем HTML-содержимое
    msg.attach(MIMEText(html, 'html'))
    
    try:
        # Устанавливаем соединение с SMTP-сервером
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.login(smtp_user, smtp_password)
        
        # Отправляем письмо
        server.send_message(msg)
        server.quit()
        
        print(f"Email с кодом подтверждения успешно отправлен на {to_email}")
        return True
    
    except Exception as e:
        print(f"Ошибка при отправке email: {e}")
        return False


@verify_api.route('/api/send-verification-code/', methods=['POST'])
def send_verification_code():
    def generate_verification_code():
        """Генерация 4-значного кода подтверждения"""
        return str(random.randint(1000, 9999))

    # Получаем email и uuid из запроса
    email = request.json.get('email')
    user_uuid = request.json.get('uuid')
    
    # Проверяем наличие обязательных полей
    if not email:
        return jsonify({'error': 'Email is required'}), 400
    if not user_uuid:
        return jsonify({'error': 'User UUID is required'}), 400

    # Инициализируем соединение с БД
    base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    db_dir = os.path.join(base_dir, 'db')
    os.makedirs(db_dir, exist_ok=True)  # Создаем директорию, если она не существует
    db_path = os.path.join(db_dir, 'flights_db.db')
    db_session.global_init(db_path)
    db_sess = db_session.create_session()
    
    # Ищем пользователя по UUID
    user = db_sess.query(User).filter(User.uuid == user_uuid).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
        
    # Проверяем, что email совпадает с указанным при регистрации
    if user.email != email:
        return jsonify({'error': 'Email does not match the one registered with this UUID'}), 400
        
    # Генерируем код и устанавливаем время истечения
    verification_code = generate_verification_code()
    expires_at = datetime.now() + timedelta(minutes=15)  # Код действителен 15 минут
    
    # Сохраняем код в базу данных
    user.verification_code = verification_code
    user.verification_code_expires = expires_at
    db_sess.commit()
    
    # Отправляем код на email
    email_sent = send_email(email, verification_code)
    
    # Выводим код и UUID в консоль (для отладки)
    print(f"\n=== VERIFICATION CODE FOR {email} (UUID: {user_uuid}): {verification_code} ===\n")
    
    response = {
        'success': True,
        'message': 'Verification code generated' + (' and sent to your email' if email_sent else ''),
        'uuid': user_uuid
    }
    
    # Для режима разработки или если отправка не удалась, возвращаем код в ответе
    if not email_sent or os.environ.get('FLASK_ENV') == 'development':
        response['code'] = verification_code
    
    return jsonify(response)


@verify_api.route('/api/verify-code', methods=['POST'])
def verify_code():
    """Проверка кода подтверждения"""
    email = request.json.get('email')
    code = request.json.get('code')
    user_uuid = request.json.get('uuid')

    # Проверяем наличие обязательных полей
    if not email or not code:
        return jsonify({'error': 'Email and code are required'}), 400
    if not user_uuid:
        return jsonify({'error': 'User UUID is required'}), 400

    # Инициализируем соединение с БД
    base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    db_dir = os.path.join(base_dir, 'db')
    os.makedirs(db_dir, exist_ok=True)
    db_path = os.path.join(db_dir, 'flights_db.db')
    db_session.global_init(db_path)
    db_sess = db_session.create_session()
    
    # Ищем пользователя по UUID
    user = db_sess.query(User).filter(User.uuid == user_uuid).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
        
    # Проверяем, что email совпадает с указанным при регистрации
    if user.email != email:
        return jsonify({'error': 'Email does not match the one registered with this UUID'}), 400
    
    # Проверяем наличие активного кода верификации
    if not user.verification_code or not user.verification_code_expires:
        return jsonify({'error': 'No verification code found for this user'}), 400

    # Проверяем срок действия кода
    if datetime.now() > user.verification_code_expires:
        # Очищаем просроченный код
        user.verification_code = None
        user.verification_code_expires = None
        db_sess.commit()
        return jsonify({'error': 'Verification code has expired'}), 400

    # Проверяем код
    if user.verification_code != code:
        return jsonify({'error': 'Invalid verification code'}), 400

    # Код верный - подтверждаем email, очищаем код верификации и устанавливаем флаг verified
    user.verification_code = None
    user.verification_code_expires = None
    user.verified = True
    db_sess.commit()

    return jsonify({
        'success': True,
        'message': 'Email successfully verified',
        'uuid': user_uuid
    })
