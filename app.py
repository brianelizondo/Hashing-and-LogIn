""" Flask app for Feedback """
from flask import Flask, request, render_template, redirect, flash, session
from models import db, connect_db, User
from forms import AddUserForm, LoginForm

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
        db.session.commit()
        
        flash(f"The user was added", 'success')
        return redirect("/secret")
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
            return redirect('/secret')
        else:
            flash(f"Invalid username/password", 'danger')
    
    return render_template('login.html', form=form)


@app.route('/secret')
def secrect_page():
    """
    Return the text "You made it!"
    """
    if "user_username" not in session:
        flash("You must be logged in to view!", 'danger')
        return redirect('/')
    else:
        return render_template('secret.html')


@app.route('/logout')
def logout():
    """
    Clear any information from the session and redirect to "/"
    """
    session.pop('user_username')
    return redirect('/')