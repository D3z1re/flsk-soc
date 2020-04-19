from flask_restful import reqparse, abort, Resource
from flask import jsonify

from data import db_session
from data.post import Post


def abort_if_post_not_found(post_id):
    session = db_session.create_session()
    post = session.query(Post).get(post_id)
    if not post:
        abort(404, message=f"Post {post_id} not found")


class PostResource(Resource):
    def get(self, post_id):
        abort_if_post_not_found(post_id)
        session = db_session.create_session()
        post = session.query(Post).get(post_id)
        return jsonify({'post': post.to_dict(
            only=('title', 'content', 'user_id', 'is_private'))})

    def delete(self, post_id):
        abort_if_post_not_found(post_id)
        session = db_session.create_session()
        post = session.query(Post).get(post_id)
        session.delete(post)
        session.commit()
        return jsonify({'success': 'OK'})


parser = reqparse.RequestParser()
parser.add_argument('title', required=True)
parser.add_argument('content', required=True)
parser.add_argument('is_private', required=True)
parser.add_argument('user_id', required=True, type=int)


class PostListResource(Resource):
    def get(self):
        session = db_session.create_session()
        post = session.query(Post).all()
        return jsonify({'post': [item.to_dict(
            only=('title', 'content', 'user_id', 'is_private')) for item in post]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        post = Post(
            title=args['title'],
            content=args['content'],
            user_id=args['user_id'],
            is_private=args['is_private']
        )
        session.add(post)
        session.commit()
        return jsonify({'success': 'OK'})
