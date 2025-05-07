from flask import Blueprint, render_template


index = Blueprint('index', __name__)


@index.route('/')
def landing_page():
    return render_template('rhea/public/index.html')
