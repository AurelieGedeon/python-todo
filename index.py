from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Length, InputRequired, ValidationError, Email
from flask_bcrypt import Bcrypt


app = Flask(__name__)
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)  # initialize database
# tells app where database is located
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SECRET_KEY'] = "thisismysecretkey"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader  # loads user from database
def load_user(user_id):  # user_id is the id of the user
    return User.query.get(int(user_id))  # returns user object


class User(db.Model, UserMixin):
    __table_name__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(30), nullable=False, unique=True)
    todos = db.relationship('Todo', backref='user')

    def __repr__(self):
        # every time you create a new task, it will return task and the id of the task
        return '<User %r>' % self.id


class Todo(db.Model):
    __table_name__ = 'todo'
    id = db.Column(db.Integer, primary_key=True)
    # this is so the user can't put in a blank
    content = db.Column(db.String(200), nullable=False)
    due_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    completed = db.Column(db.Integer, default=0)
    data_created = db.Column(db.DateTime, default=datetime.utcnow)
    is_complete = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        # every time you create a new task, it will return task and the id of the task
        return '<Todo %r>' % self.id


class SignupForm(FlaskForm):
    first_name = StringField('First Name', validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "First Name"})
    last_name = StringField('Last Name', validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Last Name"})
    email = StringField('Email', validators=[InputRequired(), Email(
        message='Invalid email'), Length(max=30)], render_kw={"placeholder": "Email"})
    password = PasswordField('Password', validators=[InputRequired(), Length(
        min=6, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        existing_user = User.query.filter_by(email=email.data).first()
        if existing_user:
            raise ValidationError(
                'Email already in use. Please choose another email.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email(
        message='Invalid email'), Length(max=30)], render_kw={"placeholder": "Email"})
    password = PasswordField('Password', validators=[InputRequired(), Length(
        min=6, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField('Login')

    def validate_email(self, email):
        existing_user = User.query.filter_by(email=email.data).first()
        if not existing_user:
            raise ValidationError('Email does not exist. Please register.')


@app.route('/task/<int:id>/complete', methods=['POST'])
def completeTask(id):
    task_to_complete = Todo.query.get_or_404(id)
    task_to_complete.is_complete = True

    try:
        db.session.commit()
        return redirect('/')
    except:
        return "Unable to complete task"


@app.route('/task/<int:id>/undo', methods=['POST'])
def uncompleteTask(id):
    task_to_complete = Todo.query.get_or_404(id)
    task_to_complete.is_complete = False

    try:
        db.session.commit()
        return redirect('/')
    except:
        return "Unable to complete task"


@app.route('/', methods=['GET'])
@login_required
def index():
    tasks = Todo.query.order_by(Todo.data_created).filter_by(
        user_id=current_user.id).all()
    logged_in_user = User.query.filter_by(id=current_user.id).first()
    return render_template('index.html', tasks=tasks, user=logged_in_user)


@app.route('/task/add', methods=['POST'])
def addTask():
    task_content = request.form['content']
    task_due_date = request.form['due_date']
    datetime_object = datetime.fromisoformat(task_due_date)
    new_task = Todo(content=task_content,
                    due_date=datetime_object, user_id=current_user.id)

    try:
        db.session.add(new_task)
        db.session.commit()
        return redirect('/')
    except:
        return "Unable to add task"


@app.route('/task/<int:id>/delete')
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return "Unable to delete task"


@app.route('/task/<int:id>/update', methods=['GET', 'POST'])
def update(id):
    task = Todo.query.get_or_404(id)
    if request.method == 'POST':
        task.content = request.form['content']

        try:
            db.session.commit()
            return redirect('/')

        except:
            return "Unable to update task"
    else:
        return render_template('update.html', task=task)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # checks if user is in the database
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect('/')
    return render_template('login.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(first_name=form.first_name.data, last_name=form.last_name.data,
                        email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/login')
    return render_template('signup.html', form=form)


@app.route("/oldest")
def todo_oldest():
    tasks = Todo.query.order_by(Todo.data_created).filter_by(
        user_id=current_user.id).all()
    return render_template("index.html", tasks=tasks)


@app.route("/newest")
def todo_newest():
    tasks = Todo.query.order_by(Todo.data_created.desc()).filter_by(
        user_id=current_user.id).all()
    return render_template("index.html", tasks=tasks)


@app.route("/duedate")
def todo_due_date():
    tasks = Todo.query.order_by(Todo.due_date).filter_by(
        user_id=current_user.id).all()
    return render_template("index.html", tasks=tasks)


@app.route("/completed")
def todo_complete():
    tasks = Todo.query.order_by(Todo.is_complete.desc()).filter_by(
        user_id=current_user.id).all()
    return render_template("index.html", tasks=tasks)


@app.route("/notcompleted")
def todo_notcomplete():
    tasks = Todo.query.order_by(Todo.is_complete).filter_by(
        user_id=current_user.id).all()
    return render_template("index.html", tasks=tasks)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect('/login')


if __name__ == '__main__':
    app.run(debug=True)
