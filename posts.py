from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, BlogPost
from forms import BlogPostForm

# Blueprint Setup
posts_bp = Blueprint('posts', __name__)

# View All Posts
@posts_bp.route('/posts')
def view_posts():
    posts = BlogPost.query.order_by(BlogPost.pub_date.desc()).all()
    return render_template('index.html', posts=posts)

# View Single Post
@posts_bp.route('/post/<int:post_id>')
def view_post(post_id):
    post = BlogPost.query.get_or_404(post_id)
    return render_template('post.html', post=post)

# Create New Post
@posts_bp.route('/post/new', methods=['GET', 'POST'])
@login_required
def create_post():
    form = BlogPostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            content=form.content.data,
            author=current_user
        )
        db.session.add(new_post)
        db.session.commit()
        flash('Post created successfully!', 'success')
        return redirect(url_for('posts.view_posts'))
    return render_template('create_post.html', form=form)

# Edit Post
@posts_bp.route('/post/edit/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = BlogPost.query.get_or_404(post_id)
    if post.author != current_user:
        flash('You are not authorized to edit this post.', 'danger')
        return redirect(url_for('posts.view_posts'))
    
    form = BlogPostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Post updated successfully!', 'success')
        return redirect(url_for('posts.view_post', post_id=post.id))
    
    form.title.data = post.title
    form.content.data = post.content
    return render_template('edit_post.html', form=form)

# Delete Post
@posts_bp.route('/post/delete/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    post = BlogPost.query.get_or_404(post_id)
    if post.author != current_user:
        flash('You are not authorized to delete this post.', 'danger')
        return redirect(url_for('posts.view_posts'))
    
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted successfully!', 'success')
    return redirect(url_for('posts.view_posts'))
