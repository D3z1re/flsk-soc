from flask_restful import abort, Resource
from flask import jsonify
from werkzeug.security import generate_password_hash

from data import db_session
from data.user import User
from data.post import Post
from data.users_reqparse import parser


def abort_if_user_not_found(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        abort(404, message=f"User {user_id} not found")


def set_password(password):
    return generate_password_hash(password)


class UsersResource(Resource):
    def get(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        return jsonify({'user': user.to_dict(
            only=('id', 'name', 'surname', 'username', 'email'))})

    def delete(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        posts = session.query(Post).filter(Post.user_id == user.id).all()
        for post in posts:
            session.delete(post)
        session.delete(user)
        session.commit()
        return jsonify({'success': 'OK'})


class UsersListResource(Resource):
    def get(self):
        session = db_session.create_session()
        user = session.query(User).all()
        return jsonify({'user': [item.to_dict(
            only=('id', 'name', 'username', 'surname', 'email')) for item in user]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        user = User(name=args['name'],
                    username=args['username'],
                    surname=args['surname'],
                    email=args['email'],
                    hashed_password=set_password(args['hashed_password']))
        user.set_password(args['password'])
        session.add(user)
        session.commit()
        return jsonify({'success': 'OK'})
