from flask import render_template, flash, redirect, url_for, request
from app.forms import LoginForm, RegistrationForm
from app import app, db
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User
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
        user = User(username=form.username.data, email=form.email.data)
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
