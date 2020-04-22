from flask_restful import abort, Resource
from flask import jsonify

from data import db_session
from data.post import Post
from data.posts_reqparse import parser


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
            only=('id', 'title', 'content', 'user_id', 'is_private'))})

    def delete(self, post_id):
        abort_if_post_not_found(post_id)
        session = db_session.create_session()
        post = session.query(Post).get(post_id)
        session.delete(post)
        session.commit()
        return jsonify({'success': 'OK'})


class PostListResource(Resource):
    def get(self):
        session = db_session.create_session()
        post = session.query(Post).all()
        return jsonify({'post': [item.to_dict(
            only=('id', 'title', 'content', 'user_id', 'is_private')) for item in post]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        post = Post(
            title=args['title'],
            content=args['content'],
            is_private=args['is_private'],
            user_id=args['user_id']
        )
        session.add(post)
        session.commit()
        return jsonify({'success': 'OK'})
