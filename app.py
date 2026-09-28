from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Application, Review
from datetime import datetime
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super_secret_key_2026'
## если PostgreSQL настроен то пиши --->  app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://exam:exam123@localhost:5432/passazhiram'     в ковычках мы пишем postgresql://пользователь:пароль@хост:порт/имя_бд
## если PostgreSQL не настроен, то пиши --->  app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlire:///app.db'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()
    if not User.query.filter_by(login='Admin26').first():
        admin = User(
            login='Admin26',
            password_hash=generate_password_hash('Demo20'),
            fio='Администратор Системы',
            birth_date=datetime(1990, 1, 1),
            phone='+79876543210',
            email='admin@passazhiram.ru',
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()

@app.route('/')
def index():
    return render_template('index.html')


## === ЗДЕСЬ БУДУТ ИЗМЕНЕНИЯ ДАЛЬШЕ ===
@app.route('/register')
def registr():
    if request.method == 'POST':
        login = request.form.get('login', '').strip()
        password = request.form.get('password', '').strip()
        fio = request.form.get('fio', '').strip()
        birth_date = request.form.get('birth_date', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()

        if not re.match(r'^[a-zA-Z0-9]{6,}$', login):
            flash('Логин долен содержать только латинские буквы и цифры, минимум 6 символов', 'danger')
            return redirect(url_for('register'))

        if len(password) < 8:
            flash('Пароль должен быть не менее 8 символов', 'danger')
            return redirect(url_for('register'))

        if User.query.filter_by(login=login).first():
            flash('Пользователь с таким логином уже существует', 'danger')
            return redirect(url_for('register'))

        new_user = User(
            login=login,
            password_hash=generate_password_hash(password),
            fio=fio,
            birth_date=datetime.strptime(birth_date, '%Y-%m-%d').date(),
            phone=phone,
            email=email,
            role='user'
        )

        db.session.add(new_user)
        db.session.commit()

        flash('Регистрация успешна! Теперь вы можете войти.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

## === Дальше пиши роут с login ===

##=== Вот здесь я остановился, потом продолжи здесь!!!!!!! ===


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)