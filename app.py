from flask import Flask, request, redirect, render_template, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Post


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'supasecret'


toolbar = DebugToolbarExtension(app)

connect_db(app)
with app.app_context():
    db.create_all()


@app.route("/")
def homepage():
    """Redirect users to user page"""

    return redirect("/users-list")


#  Users route




@app.route("/users-list")
def show_users():
    """Shows a list of all users"""
    
    users = User.query.order_by(User.first_name, User.last_name).all()
    return render_template('users-list', users=users)

@app.route('/users/new', methods=["GET"])
def new_user_form():
    """Show the for to create a new users."""

    return render_template('users/new-user.html')


@app.route("/users/new", methods=["POST"])
def new_user():
    """Handling the submission form for creating new user."""

    new_user = User(
        first_name=request.form['first_name'],
        last_name=request.form['last_name'],
        image_url=request.form['image_url'] or None)
    
    with app.app_context():
        db.session.add(new_user)
        db.session.commit()

        return redirect("/users-list")
    
@app.route('/users/<int:user_id>')
def show_user(user_id):
    """Show a page with info on the user"""

    user = User.query.get_or_404(user_id)
    return render_template('users/users-show.html', user=user)

    
@app.route('/users/<int:user_id>/edit')
def edit_user(user_id):
    "Show a form for editing a user. "

    user = User.query.get_or_404(user_id)
    return render_template('users/users-edit.html', user=user)


@app.route('/users/<int:user_id>/edit', methods=["POST"])
def user_changed(user_id):
    "Handling the submission form for making user changes"

    user = User.query.get_or_404(user_id)
    user.first_name = request.form['first_name']
    user.last_name = request.form['last_name']
    user.image_url = request.form['image_url']

    with app.app_context():
        db.session.add(user)
        db.session.commit()

    return redirect("/users")


@app.route('/users/<int:user_id>/delete', methods=["POST"])
def delete_user(user_id):
    """Handling form for deleting a user."""

    user = User.query.get_or404(user_id)

    with app.app_context():
        db.session.delete(user)
        db.session.commit()

    return redirect("/users")
    


# Post route


@app.route('/users/<int:user_id>/posts/new')
def posts_new_form(user_id):
    """Show form to add new post for certain user."""

    user = User.query.get_or_404(user_id)
    return render_template('posts/new-post.html', user=user)

@app.route('/users<int:user_id>/posts/new', methods=["POST"])
def posts_new(user_id):
    """Handle form submission for creating a new posts."""

    user = User.query.get_or_404(user_id)
    new_post = Post(title=request.form['title'], content=request['content'], user=user)

    with app.app_context():
        db.session.add(new_post)
        db.session.commit()

    flash(f"Post '{new_post.title}' added.")

    return redirect(f"/users/{user_id}")


@app.route('/posts/<int:post_id>')
def show_posts(post_id):
    """Show an info page for a post."""

    post = Post.query.get_or_404(post_id)
    return render_template('posts/show.html', post=post)


@app.route('/posts/<int:post_id>/edit')
def edit_posts(post_id):
    """Show a form to edit a post."""

    post = Post.query.get_or_404(post_id)
    return render_template('posts/edit.html', post=post)


@app.route('/posts/<int:post_id>/edit', methods=["POST"])
def update_posts(post_id):
    """Handle form submission to editing a post."""

    
    post = Post.query.get_or_404(post_id)
    post.title = request.form['title']
    post.content = request.form['content']

    with app.app_context():
        db.session.add(post)
        db.session.commit()
    
    flash(f"POST '{post.title}' edited.")
    
    return redirect(f"/users/{post.user_id}")


@app.route('/posts/<int:post_id>/delete', methods=["POST"])
def delete_post(post_id):

    post = Post.query.get_or_404(post_id)

    with app.app_context():
        db.session.delete(post)
        db.session.commit()
    
    flash(f"POST '{post.title}' deleted.")
    
    return redirect(f"/users/{post.user_id}")