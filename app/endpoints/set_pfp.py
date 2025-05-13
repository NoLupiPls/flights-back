from flask import flash, request, Blueprint
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
import os
from app.data import db_session


def get_user_pfp_path(user_id, filename):
    # This creates a path like: uploads/profile_pictures/user_1_profile.jpg
    ext = filename.rsplit('.', 1)[1].lower()
    return os.path.join('static/uploads/user_pfp', f'user_{user_id}_profile.{ext}')


set_pfp = Blueprint('set_pfp', __name__)

@set_pfp.route('/upload_pfp', methods=['GET', 'POST'])
@login_required
def upload_pfp():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')

        file = request.files['file']

        # If user does not select file, browser submits an empty part without filename
        if file.filename == '':
            flash('No selected file')

        if file:
            filename = secure_filename(file.filename)
            filepath = get_user_pfp_path(current_user.get_id(), filename)

            # Delete old profile picture if exists
            if current_user.pfp_filename and os.path.exists(current_user.pfp_filename):
                try:
                    os.remove(current_user.pfp_filename)
                except:
                    pass

            # Save the new file
            file.save(filepath)

            # Update user record
            base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
            db_dir = os.path.join(base_dir, 'db')
            os.makedirs(db_dir, exist_ok=True)  # Создаем директорию, если она не существует
            db_path = os.path.join(db_dir, 'flights_db.db')
            db_session.global_init(db_path)
            db_sess = db_session.create_session()
            db_sess.commit()

            flash('Profile picture updated successfully!')