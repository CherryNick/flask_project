from flask import render_template, flash, redirect, url_for, request
from app.forms import LoginForm, RegistrationForm, EditProfileForm, CreatePost
from app import app, db
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Post, Profile
from werkzeug.urls import url_parse
from app.utils import upload_media


@app.route('/', methods=['GET', 'POST'])
def index():
    if not current_user.is_anonymous:
        user = current_user

        page = request.args.get('page', 1, type=int)
        posts = user.friends_posts().paginate(page, app.config['POST_PER_PAGE'], False)
        next_url = url_for('index', page=posts.next_num) if posts.has_next else None
        prev_url = url_for('index', page=posts.prev_num) if posts.has_prev else None

        post_form = CreatePost()

        if post_form.validate_on_submit():
            media_id = upload_media(post_form)

            post = Post(body=post_form.text.data,
                        photo_id=media_id,
                        user_id=current_user.id)

            db.session.add(post)
            db.session.commit()

            return redirect(url_for('index'))
        return render_template('index.html', title='Homepage', posts=posts.items, post_form=post_form,
                               next_url=next_url, prev_url=prev_url)
    return render_template('index.html', title='Homepage')


@app.route('/explore', methods=['GET', 'POST'])
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(is_deleted=False).order_by(
        Post.timestamp.desc()).paginate(page, app.config['POST_PER_PAGE'], False)
    next_url = url_for('explore', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('explore', page=posts.prev_num) if posts.has_prev else None

    post_form = CreatePost()

    if post_form.validate_on_submit():
        media_id = upload_media(post_form)

        post = Post(body=post_form.text.data,
                    photo_id=media_id,
                    user_id=current_user.id)

        db.session.add(post)
        db.session.commit()

        return redirect(url_for('explore'))

    return render_template('explore.html', title='Explore', posts=posts.items, post_form=post_form,
                           next_url=next_url, prev_url=prev_url)


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

    page = request.args.get('page', 1, type=int)
    posts = user.posts.filter_by(is_deleted=False).order_by(
        Post.timestamp.desc()).paginate(page, app.config['POST_PER_PAGE'], False)
    next_url = url_for('user', username=user.username, page=posts.next_num) if posts.has_next else None
    prev_url = url_for('user', username=user.username, page=posts.prev_num) if posts.has_prev else None

    return render_template('profile.html', user=user, profile=profile, posts=posts.items, post_form=post_form,
                           next_url=next_url, prev_url=prev_url)


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


@app.route('/delete_post/<post_id>')
@login_required
def delete_post(post_id):
    post = Post.query.filter_by(id=post_id).first_or_404()
    if post.author != current_user:
        flash('You are not allowed to do this')
        return redirect(url_for('index'))
    next_page = request.args.get('next')
    post.delete()
    db.session.commit()
    return redirect(request.referrer) if request.referrer else redirect(url_for('index'))
