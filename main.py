from flask import Flask
from flask_login import LoginManager
from flask_restful import Api

from data import db_session
from data.user import User
from users import users
from posts import posts
from handlers import errors
import users_resources
import post_resources

# Config
app = Flask(__name__)
api = Api(app)
login_manager = LoginManager()
login_manager.login_view = '/login'
login_manager.login_message_category = 'info'
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# Api
# для списка объектов
api.add_resource(users_resources.UsersListResource, '/api/users')
# для одного объекта
api.add_resource(users_resources.UsersResource, '/api/users/<int:user_id>')

# для списка объектов
api.add_resource(post_resources.PostListResource, '/api/posts')
# для одного объекта
api.add_resource(post_resources.PostResource, '/api/posts/<int:post_id>')


def main():
    # Подключение базы данных sqlite3
    db_session.global_init("db/soc.sqlite")
    # подключение блюпринтов
    app.register_blueprint(users)
    app.register_blueprint(posts)
    app.register_blueprint(errors)

    @login_manager.user_loader
    def load_user(user_id):
        session = db_session.create_session()
        return session.query(User).get(user_id)

    app.run()


if __name__ == '__main__':
    main()
