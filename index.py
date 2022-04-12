from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date

app = Flask(__name__)
# tells app where database is located
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)  # initialize database


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # this is so the user can't put in a blank
    content = db.Column(db.String(200), nullable=False)
    due_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    completed = db.Column(db.Integer, default=0)
    data_created = db.Column(db.DateTime, default=datetime.utcnow)
    is_complete = db.Column(db.Boolean, default=False)

    def __repr__(self):
        # every time you create a new task, it will return task and the id of the task
        return '<Todo %r>' % self.id


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(200), nullable=False)
    last_name = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        # every time you create a new task, it will return task and the id of the task
        return '<User %r>' % self.id


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
def index():
    tasks = Todo.query.order_by(Todo.data_created).all()
    return render_template('index.html', tasks=tasks)


@app.route('/task/add', methods=['POST'])
def addTask():
    task_content = request.form['content']
    task_due_date = request.form['due_date']
    datetime_object = datetime.fromisoformat(task_due_date)
    print(datetime_object)
    new_task = Todo(content=task_content, due_date=datetime_object)

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


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/signup')
def signup():
    return render_template('signup.html')


if __name__ == '__main__':
    app.run(debug=True)
