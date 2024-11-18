import os
os.environ['FLASK_APP'] = 'main:app'
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_caching import Cache


app = Flask(__name__)

# Настройка кэша (Redis как backend для кэша)
app.config['CACHE_TYPE'] = 'redis'
app.config['CACHE_REDIS_HOST'] = os.getenv('REDIS_HOST', 'localhost')
app.config['CACHE_REDIS_PORT'] = 6379
app.config['CACHE_REDIS_DB'] = 0
app.config['CACHE_REDIS_URL'] =f"redis://{app.config['CACHE_REDIS_HOST']}:{app.config['CACHE_REDIS_PORT']}/0"

# Инициализация кэша
cache = Cache(app)

# Конфигурация для подключения к базе данных PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@db:5432/app_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Инициализация SQLAlchemy
db = SQLAlchemy(app)

migrate = Migrate(app, db) # Инициализация Flask-Migrate

# Пример модели для таблицы "User"
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    def __repr__(self):
        return f'<User {self.username}>'
    
# Создание нового пользователя
@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    new_user = User(username=data['username'], email=data['email'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created successfully'})

# Получение всех пользователей
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    users_list = [{'id': user.id, 'username': user.username, 'email': user.email} for user in users]
    return jsonify(users_list)


# Получение пользователя
@app.route('/user/<int:id>')
@cache.cached(timeout=120, key_prefix='user_data')
def get_user(id):
    # Здесь мог бы быть запрос к базе данных
    user_data = {'id': id, 'name': f'User {id}'}
    return jsonify(user_data)

# Обновление пользователя
@app.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    user = User.query.get(id)
    data = request.get_json()
    if not user:
        return jsonify({'message': 'User not found'}), 404
    user.username = data.get('username', user.username)
    user.email = data.get('email', user.email)
    db.session.commit()
    return jsonify({'message': 'User updated successfully'})

# Удаление пользователя
@app.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'})

# Очистка кэша для определенного пользователя
@app.route('/clear_cache/<int:id>')
def clear_user_cache(id):
    cache.delete(f'user_data::{id}')
    return jsonify({'message': f'Cache for user {id} cleared'})

# Главная страница
@app.route('/')
def hello_world():
    return 'Hello, Docker!'

# Пример маршрута с кэшированием
@app.route('/data')
@cache.cached(timeout=60) # Данные будут кэшироваться на 60 секунд
def get_data():
    # Эмуляция долгого запроса (например, к базе данных)
    return jsonify({'data': 'This is some data!'})

if __name__ == '__main__':
    app.run(host='0.0.0.0')