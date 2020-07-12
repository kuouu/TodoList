import secrets
from flask import render_template, url_for, flash, redirect, request, abort
from todos import app, db, bcrypt
from todos.models import Todo, User
from flask_login import login_user, current_user, logout_user, login_required
from todos.forms import LoginForm, RegistrationForm

@app.route("/", methods=['GET', 'POST'])
@app.route("/home", methods=['GET', 'POST'])
@login_required
def home():
    todolist = Todo.query.filter_by(user_id=current_user.id).all()
    return render_template('home.html', todolist=todolist)

@app.route("/delete/<int:todo_id>", methods=['POST'])
@login_required
def delete(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    db.session.delete(todo)
    db.session.commit()
    flash('Delete successfully!', 'success')
    return redirect(url_for('home'))

@app.route("/edit/<int:todo_id>", methods=['GET', 'POST'])
@login_required
def edit(todo_id):
    todoedit = Todo.query.get_or_404(todo_id)
    todoedit.title = request.form['title']
    todoedit.content = request.form['content']
    db.session.commit()
    
    flash('Edit successfully!', 'success')

    return redirect(url_for('home'))

@app.route("/new", methods=['GET', 'POST'])
@login_required
def new():
    todo = Todo(title=request.form['title'], content=request.form['content'], author=current_user)
    db.session.add(todo)
    db.session.commit()
    flash('Create successfully!', 'success')
    return redirect(url_for('home'))

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', form=form)

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))