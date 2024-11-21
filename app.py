from flask import Flask, redirect, render_template, request
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User

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
    return redirect("/users-list")


@app.route("/users-list")
def show_users():
    users = User.query.order_by(User.first_name, User.last_name).all()
    return render_template('users-list', users=users)

@app.route('/users/new', methods=["GET"])
def new_user_form():
    return render_template('users/new.html')


@app.route("/users/new", methods=["POST"])
def new_user():
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
    user = User.query.get_or_404(user_id)
    return render_template('users/users-show.html', user=user)

    
@app.route('/users/<int:user_id>/edit')
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('users/users-edit.html', user=user)


@app.route('users/<int:user_id>/edit', methods=["POST"])
def user_changed(user_id):
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
    user = User.query.get_or404(user_id)

    with app.app_context():
        db.session.delete(user)
        db.session.commit()

        return redirect("/users")