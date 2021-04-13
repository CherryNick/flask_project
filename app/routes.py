from flask import render_template, flash, redirect, url_for, request
from app.forms import LoginForm, RegistrationForm, EditProfileForm
from app import app, db
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Post, Profile
from werkzeug.urls import url_parse


@app.route('/')
@login_required
def index():
    if current_user:
        user = current_user
        posts = [
            {
                'author': {'username': 'John'},
                'body': 'beautiful day in Portland!'
            },
            {
                'author': {'username': 'Peter'},
                'body': 'Hi there!'
            }
        ]
    return render_template('index.html', title='Homepage', posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('Already signed in')
        return redirect(url_for('index'))

    form = LoginForm()

    # submit validation

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        # flash message if success validation
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))

        login_user(user, remember=form.remember_me.data)

        # flash(f'Login requested for user {form.username.data}, remember_me={form.remember_me.data}')

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

    # submit validation

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


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    profile = user.profile.first()
    posts = user.posts.all()
    return render_template('profile.html', user=user, profile=profile, posts=posts)


@app.route('/user/<username>/edit', methods=['GET', 'POST'])
@login_required
def edit_profile(username):
    
    form = EditProfileForm()

    if current_user.profile.first():
        profile = current_user.profile.first()
        if form.validate_on_submit():
            profile.update_info(gender=form.gender.data,
                                info=form.info.data,
                                photo='1',
                                date_of_birth=form.date_of_birth.data)

            db.session.add(profile)
            db.session.commit()

            flash('Saved')
            return redirect(url_for('user', username=current_user.username))
    else:
        profile = Profile(user_id=current_user.id,
                          gender=form.gender.data,
                          info=form.info.data,
                          date_of_birth=form.date_of_birth.data)
        if form.validate_on_submit():

            db.session.add(profile)
            db.session.commit()

            flash('Saved')
            return redirect(url_for('user', username=current_user.username))


    return render_template('edit_profile.html', user=current_user, profile=profile, form=form)
