import os
from flask import Blueprint, flash, redirect, url_for, render_template, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.data.forms.forms import LoginForm
from app.data.users import User
from app.data import db_session

login_bp = Blueprint('login_bp', __name__)


@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Обработка входа пользователя через форму или API (JSON)
    """
    # Если пользователь уже авторизован
    if current_user.is_authenticated:
        if request.is_json:
            return jsonify({
                'success': True,
                'message': 'Already logged in',
                'user': {
                    'uuid': current_user.uuid,
                    'name': current_user.name,
                    'email': current_user.email,
                    'verified': getattr(current_user, 'verified', False)
                }
            })
        return redirect(url_for('index'))  # Если это не API-запрос
    
    # Для API запросов (JSON)
    if request.is_json:
        data = request.get_json()
        
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({
                'success': False, 
                'message': 'Email and password are required'
            }), 400
        
        # Инициализация базы данных
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db', 'flights_db.db')
        db_session.global_init(db_path)
        db_sess = db_session.create_session()
        
        user = db_sess.query(User).filter(User.email == data['email']).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({
                'success': False, 
                'message': 'Invalid email or password'
            }), 401
        
        remember = data.get('remember', False)
        login_user(user, remember=remember)
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': {
                'uuid': user.uuid,
                'name': user.name,
                'email': user.email,
                'verified': getattr(user, 'verified', False),
                'premium': getattr(user, 'premium', False)
            }
        })
    
    # Для обычных HTML-запросов с формой
    form = LoginForm()
    if form.validate_on_submit():
        # Инициализация базы данных
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db', 'flights_db.db')
        db_session.global_init(db_path)
        db_sess = db_session.create_session()
        
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('index'))
        else:
            flash('Неверный email или пароль', 'danger')
    
    return render_template('login.html', form=form, title='Вход')


@login_bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    """
    Обработка выхода пользователя из системы
    """
    logout_user()
    
    if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'success': True,
            'message': 'Successfully logged out'
        })
    
    return {"success": True, "message": "Successfully logged out"}, 200
