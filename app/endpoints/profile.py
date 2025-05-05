from flask import request, Blueprint
from app.data import db_session
import uuid
import os
from flask_login import login_required, current_user


profile_api = Blueprint('profile_api', __name__)

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@login_required
@profile_api.route('/upload_avatar', methods=['POST'])
def upload_avatar():
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
