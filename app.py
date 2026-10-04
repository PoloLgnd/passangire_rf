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


### Здесь я начал писать код для щаблонитизатора

# @app.route('/')
# def index():
#     return render_template('home.html')

# @app.route('/hello')
# def index():
#     return render_template('hello.html', name='Маша', age=5)

# @app.route('/shopping')
# def shopping():
#     items = ['Яблоко','Хлеб','Яйца','Молоко']
#     return render_template('shopping.html', items=items)

### Здесь я закончил писать код для щаблонитизатора
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/prof')
def proffff():
    return render_template('profile.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
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
            birth_date=datetime.strptime(birth_date, '%d.%m.%Y').date(),
            phone=phone,
            email=email,
            role='user'
        )

        db.session.add(new_user)
        db.session.commit()

        flash('Регистрация успешна! Теперь вы можете войти.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))

    if request.method == 'POST':
        login_val = request.form.get('login', '').strip()
        password = request.form.get('password', '')

        user = User.query.filter_by(login=login_val).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)

            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)

            if user.role == 'admin':
                return redirect(url_for('admin'))
            return redirect(url_for('profile'))
        else:
            flash('Неверный логин или пароль', 'danger')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы успешно вышли из системы', 'info')
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    user_applications = Application.query.filter_by(user_id=current_user.id).order_by(Application.created_at.desc()).all()

    return render_template('profile.html', applications=user_applications)

@app.route('/application', methods=['GET', 'POST'])
@login_required
def application():
    if request.method == 'POST':
        # Порлучаем данные из формы
        transport_type = request.form.get('transport_type')
        start_date_str = request.form.get('start_date')
        payment_method = request.form.get('payment_method')

        # Проверка (все ли поля заполнены)
        if not transport_type or not start_date_str or not payment_method:
            flash('Пожалуйста, заполните все поля', 'danger')
            return redirect(url_for('application'))

        # Преобразует строку даты в объект Date (Требование задания: ДД.ММ.ГГГГ)
        try:
            # Пытаемся превратить "29.09.2026" в дату
            # Если у нас в форме type="text"
            # state_date = datetime.strptime(start_date_str, '%d.$m.$Y').date()

            # Если у нас в форме type="date"
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                        
        except ValueError:
            # Если формат не верный к примеру 29/09/2026
            flash('Не верный формат даты! Используйте ДД.ММ.ГГГГ', 'danger')
            return redirect(url_for('application'))

        # Создаём новую заявку
        new_application = Application(
            user_id=current_user.id,
            transport_type=transport_type,
            start_date=start_date,
            payment_method=payment_method,
            status='Новая' #по умолчанию
        )

        # Сохраняем в базу данных
        db.session.add(new_application)
        db.session.commit()

        flash('Заявка успешно создана! Ожидайте подтверждения.', 'success')
        return redirect(url_for('profile'))

    # Если метод GET - просто показываем форму
    return render_template('application.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)