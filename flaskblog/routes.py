import secrets
import os
from flask import render_template, url_for, flash, redirect, request, abort
from flaskblog import app, db, bcrypt
from flaskblog.forms import RegistrationForm, LoginForm, AccountUpdate, PostForm
from flaskblog.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
from PIL import Image


@app.route("/")
@app.route("/home")
def home():
    next_page = request.args.get('page', 1, int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=next_page, per_page=5)
    return render_template('home.html', posts=posts)


@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user_info = User(username=form.username.data, password=hashed_password, email=form.email.data)
        db.session.add(new_user_info)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            else:
                return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_pictures(form_picture):
    random_hex = secrets.token_hex(8)
    f_name, f_ext = os.path.split(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn


@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    form = AccountUpdate()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_pictures(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash("Your account has been updated! ", "success")
        return redirect(url_for('account'))

    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email

    image_file = url_for('static', filename=f'profile_pics/{current_user.image_file}')
    return render_template('account.html', image_file=image_file, form=form)


@app.route("/post/new", methods=["GET", "POST"])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash("You have created new post successfully!", "success")
        return redirect(url_for("home"))
    return render_template('create_post.html', form=form)


@app.route('/edit_post/<int:post_id>', methods=["GET", "POST"])
@login_required
def edit_post(post_id):
    form = PostForm()
    post = Post.query.get(post_id)
    if current_user == post.author:
        if form.validate_on_submit():
            post.title = form.title.data
            post.content = form.content.data
            db.session.commit()
            flash("You have edited your post successfully!", "success")
            return redirect(url_for("home"))
        elif request.method == "GET":
            form.title.data = post.title
            form.content.data = post.content
    else:
        return abort(403)
    return render_template('create_post.html', form=form)


@app.route('/post/<int:post_id>', methods=["GET", "POST"])
def post(post_id):
    post = Post.query.get(post_id)
    if current_user != post.author:
       return abort(403)
    return render_template('post.html', post=post)


@app.route('/delete_post/<int:post_id>', methods=["POST"])
def delete_post(post_id):
    post_to_delete = Post.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    flash("You have successfully deleted your post!", "success")
    return redirect(url_for('home'))


@app.route('/user/<string:name>')

def user_posts(name):
    next_page = request.args.get('page', 1, int)
    user = User.query.filter_by(username=name).first()
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(page=next_page, per_page=5)
    return render_template('user.html',posts=posts,user=user)




@app.route("/about")
def about():
    return render_template('about.html')
