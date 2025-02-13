from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, BlogPost
from forms import RegistrationForm, LoginForm
from datetime import datetime

# Initialize Flask Application
app = Flask(__name__)
app.config.from_object('config.Config')

# Initialize Extensions
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# User Loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Home Page - List All Posts
@app.route('/')
def home():
    posts = BlogPost.query.order_by(BlogPost.pub_date.desc()).all()
    return render_template('index.html', posts=posts)

# About Page
@app.route('/about')
def about():
    return render_template('about.html')

# Register Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Account created! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('home'))
        flash('Invalid credentials. Please try again.', 'danger')
    return render_template('login.html', form=form)

# Logout Route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

# Create New Post (Only for Logged-in Users)
@app.route('/create', methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        new_post = BlogPost(title=title, content=content, pub_date=datetime.now(), author=current_user)
        db.session.add(new_post)
        db.session.commit()
        flash('New post created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html')

# View Single Post
@app.route('/posts/<int:post_id>')
def view_post(post_id):
    post = BlogPost.query.get_or_404(post_id)
    return render_template('post.html', post=post)

# Edit Post (Only for the Author)
@app.route('/edit/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = BlogPost.query.get_or_404(post_id)
    if post.author != current_user:
        flash('You are not authorized to edit this post.', 'danger')
        return redirect(url_for('home'))
    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content']
        db.session.commit()
        flash('Post updated successfully!', 'success')
        return redirect(url_for('view_post', post_id=post.id))
    return render_template('edit_post.html', post=post)

# Delete Post (Only for the Author)
@app.route('/delete/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    post = BlogPost.query.get_or_404(post_id)
    if post.author != current_user:
        flash('You are not authorized to delete this post.', 'danger')
        return redirect(url_for('home'))
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted successfully!', 'success')
    return redirect(url_for('home'))

# Custom 404 Error Handler
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

# Run the Application
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables if they don't exist
        print("Database tables created successfully.")
    app.run(debug=True, use_reloader=False)
