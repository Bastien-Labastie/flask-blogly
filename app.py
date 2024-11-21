from flask import Flask, request, redirect, render_template, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Post, Tag


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
    tags = Tag.query.all()
    return render_template('posts/new-post.html', user=user, tags=tags)

@app.route('/users<int:user_id>/posts/new', methods=["POST"])
def posts_new(user_id):
    """Handle form submission for creating a new posts."""

    user = User.query.get_or_404(user_id)
    tags_ids = [int(num) for num in request.form.getlist("tags")]
    tags = Tag.query.filter(Tag.id.in_(tags_ids)).all()
    new_post = Post(title=request.form['title'], content=request['content'], user=user, tags=tags)

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
    tags = Tag.query.all()
    return render_template('posts/edit.html', post=post, tags=tags)


@app.route('/posts/<int:post_id>/edit', methods=["POST"])
def update_posts(post_id):
    """Handle form submission to editing a post."""

    
    post = Post.query.get_or_404(post_id)
    post.title = request.form['title']
    post.content = request.form['content']

    tag_ids = [int(num) for num in request.form.getlist("tags")]
    post.tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()

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


# Tags routes


@app.route('/tags')
def tags_list():
    """Show a page with info about all tags."""

    tag = Tag.query.all()
    return render_template('tags/list.html', tag=tag)


@app.route('/tags/<int:tag_id>')
def tag_info(tag_id):
    """Show detail about a tag."""
    tag = Tag.query.get_or_404(tag_id)
    return render_template('tags/tag-info.html', tag=tag)



@app.route('/tags/new')
def tags_form():
    """Shows a form to add a new tag."""

    posts = Post.query.all()
    return render_template('tags/new-tag.html', posts=posts)

@app.route('/tags/new', methods=['POST'])
def tags_new():
    """Handle new tag form submission."""

    post_ids = [int(num) for num in request.form.getlist("posts")]
    posts = Post.queryfilter(Post.id.in_(post_ids)).all()
    new_tag = Tag(name=request.form['name'], posts=posts)


    with app.app_context():

        db.session.add(new_tag)
        db.session.commit()
        
    flash(f"Tag '{new_tag.name}' has been added.")

    return redirect ("/tags")

@app.route('/tags/<int:tag_id>/edit')
def tag_edit_form(tag_id):
    """Show edit form for a tag."""
    tag = Tag.query.get_or_404(tag_id)
    posts = Post.query.all()
    return render_template('tags/edit.html', tag=tag, posts=posts)


@app.route('/tags/<int:tag_id>/edit', methods=["POST"])
def tag_edit(tag_id):
    """Process edit form, edit tag, and redirects to the tag list."""

    tag = Tag.query.get_or_404(tag_id)
    tag.name = request.form['name']
    post_ids = [int(num) for num in request.form.getlist("posts")]
    tag.posts = Post.query.filter(Post.id.in_(post_ids)).all()

    with app.app_context():

        db.session.add(tag)
        db.session.commit()
    
    flash(f"Tag '{tag.name}' has been edited.")

    return redirect("/tags")

@app.route('/tags/<int:tag_id>/delete', methods=["POST"])
def tag_delete(tag_id):
    """Delete a tag."""

    tag = Tag.query.get_or_404(tag_id)

    with app.app_context():

        db.session.delete(tag)
        db.session.commit()

    flash(f"Tag '{tag.name}' has been deleted.")

    return redirect("/tags")
    