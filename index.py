from flask import Flask, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date

app = Flask(__name__)
# tells app where database is located
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)  # initialize database


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # this is so the user can't put in a blank
    content = db.Column(db.string(200), nullable=False)
    completed = db.Column(db.Integer, default=0)
    data_created = db.Column(db.DateTime, default=datetime.utcnow)
    # data_due = db.Column(db.DateTime, default=date.)

    def __repr__(self):
        # every time you create a new task, it will return task and the id of the task
        return '<Task %r>' % self.id


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
