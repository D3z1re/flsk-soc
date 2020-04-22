from flask import render_template, request, redirect, url_for, flash, Blueprint
from flask_login import login_user, current_user, logout_user, login_required

from data.login import LoginForm
from data.register import RegisterForm

from data import db_session
from data.post import Post
from data.relationship import Relationship
from data.user import User
from data.account import UpdateAccountForm
from data.search import SearchByUsernameForm

from PIL import Image
import os
import secrets


users = Blueprint('users', __name__)


# Функция добавления картинки на аккаунт
def save_picture(picture):
    from main import app
    hex = secrets.token_hex(8)    # Генерирование случайного названия для картинки
    f_name, f_ext = os.path.splitext(picture.filename)
    picture_fn = hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    size = (125, 125)    # Заданный размер изображения
    img = Image.open(picture)
    img.thumbnail(size)    # Сжатие картинки до заданного размера
    img.save(picture_path)    # Сохранение

    return picture_fn


@users.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect('/')
        return render_template('login.html', title='Authorization',
                               message="Login or password are incorrect!",
                               form=form)
    return render_template('login.html', title='Authorization', form=form)


@users.route('/user/<int:id>')
@login_required
def user_page(id):
    session = db_session.create_session()
    user = session.query(User).filter(User.id == id).first()
    following = session.query(User).\
        filter(Relationship.from_user == current_user.id).filter(Relationship.to_user == id).first()
    followers_c = session.query(User).\
        filter(Relationship.to_user == id).filter(Relationship.from_user == User.id).count()
    following_c = session.query(User).\
        filter(Relationship.from_user == id).filter(Relationship.to_user == User.id).count()
    if following or user == current_user:
        posts = session.query(Post).filter(Post.user == user).order_by(Post.created_date.desc())
    else:
        posts = session.query(Post).filter(Post.user == user).filter(Post.is_private != True).order_by(Post.created_date.desc())
    return render_template('user.html', posts=posts, user=user, title=user.username,
                           following=following, followers_c=followers_c, following_c=following_c, posts_c=posts.count())


@users.route('/user/<int:id>/follow')
@login_required
def follow_user(id):
    session = db_session.create_session()
    relation = Relationship(from_user=current_user.id, to_user=id)
    session.add(relation)
    session.commit()
    flash('You has been followed!', 'success')
    return redirect(f'/user/{id}')


@users.route('/following', methods=['GET', 'POST'])
@login_required
def following_users():
    form = SearchByUsernameForm()
    session = db_session.create_session()
    if form.validate_on_submit():
        if form.username.data:
            search = '%{}%'.format(form.username.data)
            users = session.query(User).filter(User.username.like(search)).\
                filter(Relationship.from_user == current_user.id).filter(Relationship.to_user == User.id).all()
            return render_template('following_users.html', title='Following Users', users=users, following_c=len(users),
                                   form=form)
    users = session.query(User).\
        filter(Relationship.from_user == current_user.id).filter(Relationship.to_user == User.id).all()
    return render_template('following_users.html', title='Following Users',
                           users=users, following_c=len(users), form=form)


@users.route('/followers', methods=['GET', 'POST'])
@login_required
def followers():
    form = SearchByUsernameForm()
    session = db_session.create_session()
    if form.validate_on_submit():
        if form.username.data:
            search = '%{}%'.format(form.username.data)
            users = session.query(User).\
                filter(User.username.like(search)).filter(Relationship.to_user == current_user.id).\
                filter(Relationship.from_user == User.id).all()
            return render_template('followers.html', title='Users', form=form, users=users, users_c=len(users))
    users = session.query(User).\
        filter(Relationship.to_user == current_user.id).filter(Relationship.from_user == User.id).all()
    return render_template('followers.html', title='Followers', users=users, followers_c=len(users), form=form)


@users.route('/users', methods=['GET', 'POST'])
def show_users():
    form = SearchByUsernameForm()
    session = db_session.create_session()
    if form.validate_on_submit():
        if form.username.data:
            search = '%{}%'.format(form.username.data)
            users = session.query(User).filter(User.username.like(search)).all()
            return render_template('users.html', title='Users', form=form, users=users, users_c=len(users))
    users = session.query(User).all()
    return render_template('users.html', title='Users', users=users, users_c=len(users), form=form)


@users.route('/search', methods=['GET', 'POST'])
def search_by_username():
    form = SearchByUsernameForm()
    if form.validate_on_submit():
        if form.username.data:
            session = db_session.create_session()
            search = '%{}%'.format(form.username.data)
            users = session.query(User).filter(User.username.like(search)).all()
            print(users)
            return render_template('search.html', title='Search', form=form)
    return render_template('search.html', title='Search', form=form)


@users.route('/user/<int:id>/unfollow')
@login_required
def unfollow_user(id):
    session = db_session.create_session()
    relation = session.query(Relationship).\
        filter(Relationship.from_user == current_user.id).filter(Relationship.to_user == id).first()
    session.delete(relation)
    session.commit()
    flash('You has been unfollowed!', 'success')
    return redirect(f'/user/{id}')


@users.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.confirm_password.data:
            return render_template('register.html', title='Registration', form=form,
                                   message="Password do not match")
        session = db_session.create_session()
        if session.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Registration', form=form,
                                   message="This user already exists")
        user = User(
            username=form.username.data,
            name=form.name.data,
            surname=form.surname.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        flash('Your account has been created!', 'success')
        return redirect('/login')
    return render_template('register.html', title='Register', form=form)


@users.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@users.route('/account', methods=['GET', 'POST'])
@login_required
def my_account():
    form = UpdateAccountForm()
    session = db_session.create_session()
    user = session.query(User).filter(User.id == current_user.id).first()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            user.image_file = picture_file
        user.username = form.username.data
        user.name = form.name.data
        user.surname = form.surname.data
        user.email = form.email.data
        session.commit()
        flash('Your account has been updated!', 'success')
        return redirect('/account')
    elif request.method == 'GET':
        form.username.data = user.username
        form.name.data = user.name
        form.surname.data = user.surname
        form.email.data = user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)
