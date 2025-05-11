from flask import Blueprint, flash
from flask_login import login_user, logout_user, login_required
from app.data.forms.forms import LoginForm
from app.data.users import User

login_bp = Blueprint('login_bp', __name__)


@login_bp.route('/login', methods=['GET', 'POST'])
def login():

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
        else:
            flash('Login unsuccessful. Please check email and password.', 'danger')


@login_bp.route('/logout')
@login_required
def logout():
    logout_user()
