from flask import render_template, flash, redirect, url_for, request
from app.forms import LoginForm, RegistrationForm, EditProfileForm, CreatePost
from app import app, db
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Post, Profile
from werkzeug.urls import url_parse
from app.utils import upload_media


@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if current_user:
        user = current_user
        posts = user.followed_posts()

    post_form = CreatePost()

    if post_form.validate_on_submit():
        media_id = upload_media(post_form)

        post = Post(body=post_form.text.data,
                    photo_id=media_id,
                    user_id=current_user.id)

        db.session.add(post)
        db.session.commit()

        return redirect(url_for('index'))

    return render_template('index.html', title='Homepage', posts=posts, post_form=post_form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('Already signed in')
        return redirect(url_for('index'))

    form = LoginForm()

    if form.validate_on_submit():

        user = User.query.filter_by(username=form.username.data.title()).first()

        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))

        login_user(user, remember=form.remember_me.data)

        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)

    return render_template('login.html', title='Sign in', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash('Already signed in')
        return redirect(url_for('index'))

    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(username=form.username.data.strip().title(), email=form.email.data.strip().lower())
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        flash('Success! Now you can sign in')
        return redirect(url_for('login'))

    return render_template('registration.html', title='Sign up', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    profile = user.profile
    post_form = CreatePost()

    if post_form.validate_on_submit():
        media_id = upload_media(post_form)

        post = Post(body=post_form.text.data,
                    photo_id=media_id,
                    user_id=current_user.id)

        db.session.add(post)
        db.session.commit()

        return redirect(url_for('user', username=username))

    posts = user.posts.all()

    return render_template('profile.html', user=user, profile=profile, posts=posts, post_form=post_form)


@app.route('/user/<username>/edit', methods=['GET', 'POST'])
@login_required
def edit_profile(username):
    form = EditProfileForm()

    if form.validate_on_submit():

        media_id = upload_media(form)

        if current_user.profile:
            profile = current_user.profile
            profile.update_info(gender=form.gender.data,
                                info=form.info.data,
                                photo=media_id,
                                date_of_birth=form.date_of_birth.data)
        else:
            profile = Profile(user_id=current_user.id,
                              gender=form.gender.data,
                              photo_id=media_id,
                              info=form.info.data,
                              date_of_birth=form.date_of_birth.data)

        db.session.add(profile)
        db.session.commit()

        flash('Saved')
        return redirect(url_for('user', username=current_user.username))

    return render_template('edit_profile.html', user=current_user, form=form)


@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first_or_404()
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('index'))
    current_user.follow(user)
    db.session.commit()
    return redirect(url_for('user', username=username))


@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first_or_404()
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('index'))
    current_user.unfollow(user)
    db.session.commit()
    return redirect(url_for('user', username=username))


@app.errorhandler(404)
def error404(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def error500(error):
    db.session.rollback()
    return render_template('500.html'), 500
