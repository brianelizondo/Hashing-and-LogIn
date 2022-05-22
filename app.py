""" Flask app for Feedback """
from flask import Flask, request, render_template, redirect, flash, session
from psycopg2 import IntegrityError
from models import Feedback, db, connect_db, User
from forms import AddUserForm, LoginForm, FeedbackForm

app = Flask(__name__)
app.config['SECRET_KEY'] = "abcd1234"
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///feedback_test"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)
# db.create_all()

@app.errorhandler(404)
def page_not_found(e):
    """
    Custom 404 Error Page
    """
    return render_template('404.html'), 404


@app.route('/')
def homepage():
    """
    Redirect to /register
    """
    return redirect('/register')


@app.route('/register', methods=["GET", "POST"])
def register_form():
    """
    Show a form that when submitted will register/create a user. 
    This form should accept a username, password, email, first_name, and last_name.
    Make sure you are using WTForms and that your password input hides the characters that the user is typing!
    
    Process the registration form by adding a new user. Then redirect to "/secret"
    """
    form = AddUserForm()
    if form.validate_on_submit():
        username = form.username.data.lower()
        password = form.password.data
        email = form.email.data.lower()
        first_name = form.first_name.data.lower()
        last_name = form.last_name.data.lower()

        new_user = User.register(username=username, password=password, email=email, first_name=first_name, last_name=last_name)
        db.session.add(new_user)
        try:
            db.session.commit()
        except IntegrityError:
            flash(f'The username has been taken. Please pick another', 'danger')
            return render_template('register.html', form=form)
        
        session['user_username'] = new_user.username
        flash(f'Welcome! Successfully created your Account!', 'success')
        return redirect(f'/users/{ new_user.username }')
    else:
        return render_template('register.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login_form():
    """
    Show a form that when submitted will login a user. This form should accept a username and a password.
    Make sure you are using WTForms and that your password input hides the characters that the user is typing!

    Process the login form, ensuring the user is authenticated and going to "/secret if" so.
    """
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data.lower()
        password = form.password.data

        login_user = User.authenticate(username, password)
        
        if login_user:
            session['user_username'] = login_user.username
            return redirect(f'/users/{ login_user.username }')
        else:
            flash(f"Invalid username/password", 'danger')
    
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    """
    Clear any information from the session and redirect to "/"
    """
    session.pop('user_username')
    return redirect('/')


@app.route('/users/<username>')
def user_profile(username):
    """
    Display a template the shows information about that user (everything except for their password)
    You should ensure that only logged in users can access this page.
    """
    if "user_username" not in session:
        flash("You must be logged in to view!", 'danger')
        return redirect('/login')
    else:
        user = User.query.filter_by(username=username).first()
        feedbacks = user.feedbacks
        return render_template('user_profile.html', user=user, feedbacks=feedbacks)


@app.route('/users/<username>/delete', methods=["GET", "POST"])
def delete_user(username):
    """
    Remove the user from the database and make sure to also delete all of their feedback. Clear any user information in the session and redirect to '/'
    Make sure that only the user who is logged in can see this form
    """
    if "user_username" not in session:
        flash("You must be logged in to view!", 'danger')
        return redirect('/login')
    else:
        User.query.filter_by(username=username).delete()
        db.session.commit()
        session.pop('user_username')
        flash('The user was successfully deleted', 'success')
        return redirect('/')


@app.route('/users/<username>/feedback/add', methods=["GET", "POST"])
def create_feedback(username):
    """
    Display a form to add feedback 
    Make sure that only the user who is logged in can see this form
    Add a new piece of feedback and redirect to /users/<username>
    """
    if "user_username" not in session:
        flash("You must be logged in to view!", 'danger')
        return redirect('/login')
    else:
        form = FeedbackForm() 
        if form.validate_on_submit():
            title = form.title.data
            content = form.content.data

            new_feedback = Feedback(title=title, content=content, username=session['user_username'])
            db.session.add(new_feedback)
            db.session.commit()
            flash(f'The feedback was added successfully', 'success')
            return redirect(f'/users/{ new_feedback.username }')
        else:
            user = User.query.filter_by(username=username).first()
            return render_template('feedback_add.html', form=form, user=user)


@app.route('/feedback/<int:feedback_id>/update', methods=["GET", "POST"])
def update_feedback(feedback_id):
    """
    Display a form to edit feedback 
    Make sure that only the user who is logged in can see this form
    Update a specific piece of feedback and redirect to /users/<username>
    """
    if "user_username" not in session:
        flash("You must be logged in to view!", 'danger')
        return redirect('/login')
    else:
        feedback = Feedback.query.get_or_404(feedback_id)
        form = FeedbackForm(obj=feedback) 
        if form.validate_on_submit():
            feedback.title = form.title.data
            feedback.content = form.content.data
            db.session.commit()
            flash(f'The feedback was updated successfully!', 'success')
            return redirect(f'/users/{feedback.username}')

        else:
            user = User.query.filter_by(username=feedback.username).first()
            return render_template('feedback_edit.html', form=form, user=user)


@app.route('/feedback/<int:feedback_id>/delete', methods=["GET", "POST"])
def delete_feedback(feedback_id):
    """
    Delete a specific piece of feedback and redirect to /users/<username>
    Make sure that only the user who is logged in can see this form
    """
    Feedback.query.filter_by(id=feedback_id).delete()
    db.session.commit()
    flash('The feedback was successfully deleted', 'success')
    return redirect(f"/users/{session['user_username']}")