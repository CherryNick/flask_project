from flask import render_template, flash, redirect, url_for
from app.forms import LoginForm
from app import app


@app.route('/')
def index():
    user = {'username': 'Nikita'}
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
    return render_template('index.html', title='Homepage', user=user, posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    # submit validation

    if form.validate_on_submit():

        # flash message if success validation

        flash(f'Login requested for user {form.username.data}, remember_me={form.remember_me.data}')
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign in', form=form)