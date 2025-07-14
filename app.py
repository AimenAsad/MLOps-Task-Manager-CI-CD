import os
from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'mysecretkey')

# Retrieve credentials and connection info from environment variables
mongo_user = os.environ.get('MONGO_ROOT_USERNAME')
mongo_pass = os.environ.get('MONGO_ROOT_PASSWORD')
mongo_host = os.environ.get('MONGO_HOST', 'mongodb-service')
mongo_db = os.environ.get('MONGO_DB', 'taskdb')

# Construct the MongoDB URI with authentication
if mongo_user and mongo_pass:
    mongo_uri = f"mongodb://{mongo_user}:{mongo_pass}@{mongo_host}:27017/{mongo_db}?authSource=admin"
else:
    mongo_uri = f"mongodb://{mongo_host}:27017/{mongo_db}"

client = MongoClient(mongo_uri)
db = client.get_default_database()
tasks_collection = db.tasks

@app.route('/')
def index():
    tasks = list(tasks_collection.find())
    return render_template('index.html', tasks=tasks)

@app.route('/add', methods=['POST'])
def add_task():
    task_name = request.form.get('task')
    if task_name:
        tasks_collection.insert_one({
            'name': task_name,
            'completed': False
        })
    return redirect(url_for('index'))

@app.route('/complete/<task_id>')
def complete_task(task_id):
    from bson.objectid import ObjectId
    tasks_collection.update_one(
        {'_id': ObjectId(task_id)},
        {'$set': {'completed': True}}
    )
    return redirect(url_for('index'))

@app.route('/delete/<task_id>')
def delete_task(task_id):
    from bson.objectid import ObjectId
    tasks_collection.delete_one({'_id': ObjectId(task_id)})
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
