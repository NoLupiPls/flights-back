from flask import request, Blueprint, jsonify
from app.data import db_session
import uuid
import os
from flask_login import login_required, current_user
from app.data.users import User

profile_api = Blueprint('profile_api', __name__)


@profile_api.route('/api/profile', methods=['GET'])
@login_required
def get_profile():
    """
    Возвращает основные данные профиля текущего пользователя.
    """
    # Инициализируем соединение с БД
    base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    db_dir = os.path.join(base_dir, 'db')
    os.makedirs(db_dir, exist_ok=True)  # Создаем директорию, если она не существует
    db_path = os.path.join(db_dir, 'flights_db.db')
    db_session.global_init(db_path)
    
    # Обновляем данные о пользователе из базы данных
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.uuid == current_user.uuid).first()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
        
    # Возвращаем только нужные поля
    return jsonify({
        'uuid': user.uuid,
        'name': user.name,
        'premium': user.premium or False  # Если premium равен None, вернем False
    }), 200


@profile_api.route('/upload_avatar', methods=['POST'])
@login_required
def upload_avatar():
    def allowed_file(filename):
        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    if not current_user.verified:
        return 'Account is not verified', 401
    pfp_directory = 'static/uploads/user_pfp/'
    if 'avatar' not in request.files:
        return 'No file part', 400

    file = request.files['avatar']
    if file.filename == '':
        return 'No selected file', 400

    if file and allowed_file(file.filename):
        # Генерируем уникальное имя файла с помощью uuid4
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4()}.{ext}"

        # Сохраняем файл
        filepath = os.path.join(pfp_directory, filename)
        file.save(filepath)

        db_sess = db_session.create_session()
        current_user.pfp = filepath
        db_sess.merge(current_user)
        db_sess.commit()

        return f"Avatar uploaded successfully! Filename: {filename}", 200

    return 'Invalid file type', 400
