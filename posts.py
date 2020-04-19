from flask import render_template, request, redirect, flash, Blueprint
from flask_login import current_user, login_required
from flask_restful import abort

from data import db_session
from data.post import Post, PostForm
from data.user import User
from data.relationship import Relationship
from data.search import SearchByTitleForm


posts = Blueprint('posts', __name__)


@posts.route('/add_post', methods=['GET', 'POST'])
@login_required
def add_post():
    form = PostForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        post = Post()
        post.title = form.title.data
        post.content = form.content.data
        post.is_private = form.is_private.data
        current_user.posts.append(post)
        session.merge(current_user)
        session.commit()
        flash('Your post has ben created!', 'success')
        return redirect('/')
    return render_template('edit_post.html', title='Add post',
                           form=form)


@posts.route('/post/<int:id>')
def show_post(id):
    session = db_session.create_session()
    post = session.query(Post).filter(Post.id == id).first()
    return render_template('post.html', title=post.title, post=post)


@posts.route("/", methods=['GET', 'POST'])
def index():
    form = SearchByTitleForm()
    session = db_session.create_session()
    if form.validate_on_submit():
        if form.title.data:
            search = '%{}%'.format(form.title.data)
            if current_user.is_authenticated:
                following = [i[0] for i in session.query(User.id).
                             filter(Relationship.from_user == current_user.id).
                             filter(Relationship.to_user == User.id).all()]
                posts = session.query(Post).filter(Post.title.like(search)).\
                    filter((Post.user_id.in_(following) & (Post.is_private == True)) | (Post.user_id == current_user.id) |
                           (Post.is_private != True)).order_by(Post.created_date.desc())
            else:
                posts = session.query(Post).\
                    filter(Post.title.like(search)).filter(Post.is_private != True).order_by(Post.created_date.desc())
            return render_template("index.html", posts=posts, title='Feed', form=form)
    if current_user.is_authenticated:
        following = [i[0] for i in session.query(User.id).
            filter(Relationship.from_user == current_user.id).
            filter(Relationship.to_user == User.id).all()]
        posts = session.query(Post).filter((Post.user_id.in_(following) & (Post.is_private == True)) | (Post.user_id == current_user.id) | (Post.is_private != True)).order_by(
            Post.created_date.desc())
    else:
        posts = session.query(Post).filter(Post.is_private != True).order_by(
            Post.created_date.desc())
    return render_template("index.html", posts=posts, title='Feed', form=form)


@posts.route('/f', methods=['GET', 'POST'])
@login_required
def following_posts():
    form = SearchByTitleForm()
    session = db_session.create_session()
    if form.validate_on_submit():
        if form.title.data:
            search = '%{}%'.format(form.title.data)
            following = [i[0] for i in session.query(User.id).
                filter(Relationship.from_user == current_user.id).
                filter(Relationship.to_user == User.id).all()]
            posts = session.query(Post).filter(Post.title.like(search)).\
                filter(Post.user_id.in_(following)).order_by(Post.created_date.desc())
            return render_template('following_posts.html', title='Following Posts', posts=posts, form=form)
    following = [i[0] for i in session.query(User.id).
                 filter(Relationship.from_user == current_user.id).
                 filter(Relationship.to_user == User.id).all()]
    posts = session.query(Post).filter(Post.user_id.in_(following)).order_by(Post.created_date.desc())
    return render_template('following_posts.html', title='Following Posts', posts=posts, form=form)


@posts.route('/post/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    form = PostForm()
    if request.method == "GET":
        session = db_session.create_session()
        post = session.query(Post).filter(Post.id == id,
                                          Post.user == current_user).first()
        if post:
            form.title.data = post.title
            form.content.data = post.content
            form.is_private.data = post.is_private
        else:
            abort(404)
    if form.validate_on_submit():
        session = db_session.create_session()
        post = session.query(Post).filter(Post.id == id,
                                          Post.user == current_user).first()
        if post:
            post.title = form.title.data
            post.content = form.content.data
            post.is_private = form.is_private.data
            session.commit()
            flash('Your post has been updated!', 'success')
            return redirect(f'/post/{post.id}')
        else:
            abort(404)
    return render_template('edit_post.html', title='Update post',
                           form=form)


@posts.route('/post/<int:id>/delete', methods=['GET', 'POST'])
@login_required
def post_delete(id):
    session = db_session.create_session()
    post = session.query(Post).filter(Post.id == id,
                                      Post.user == current_user).first()
    if post:
        session.delete(post)
        session.commit()
        flash('Your post has been deleted!', 'success')
    else:
        abort(404)
    return redirect('/')
