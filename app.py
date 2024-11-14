from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from babel.dates import format_date
import pytz

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Integer, default=0)
    datecreated = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return '<Task %r>' % self.id 

@app.route('/', methods=['POST', 'GET'])
def index():
    error = None
    if request.method == 'POST':
        task_content = request.form['content']
        if not task_content.strip():
            error = 'Task content cannot be empty'
        else:
            new_task = Todo(content=task_content)
            try:
                db.session.add(new_task)
                db.session.commit()
                return redirect('/')
            except:
                error = 'There was an issue adding your task'
    tasks = Todo.query.order_by(Todo.datecreated).all()
    bangkok_tz = pytz.timezone('Asia/Bangkok')
    for task in tasks:
        task.datecreated = task.datecreated.astimezone(bangkok_tz)
        task.datecreated = format_date(task.datecreated, "d MMMM yyyy", locale='th')
    return render_template('index.html', tasks=tasks, error=error)

@app.route('/add', methods=['POST'])
def add_task():
    task_content = request.form['content']
    if not task_content.strip():
        return redirect(url_for('index', error='Task content cannot be empty'))
    new_task = Todo(content=task_content)
    
    try:
        db.session.add(new_task)
        db.session.commit()
        return redirect('/')
    except:
        return redirect(url_for('index', error='There was an issue adding your task'))
    
@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)
    
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting that task'
    
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = Todo.query.get_or_404(id)
    error = None
    
    if request.method == 'POST':
        task_content = request.form['content']
        if not task_content.strip():
            error = 'Task content cannot be empty'
        else:
            task.content = task_content
            try:
                db.session.commit()
                return redirect('/')
            except:
                error = 'There was an issue updating your task'
    return render_template('update.html', task=task, error=error)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)