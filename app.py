from flask import Flask, render_template, request, redirect, session, url_for
from pymongo import MongoClient
from config import MONGO_URI, SECRET_KEY
from bson.objectid import ObjectId


app = Flask(__name__)
app.secret_key = SECRET_KEY


client = MongoClient(MONGO_URI)
db = client['auction_db']
hosts_col = db['hosts']
users_col = db['users']

if hosts_col.count_documents({}) == 0:
    hosts_col.insert_many([
        {"host_name": "Team 1 Host", "username": "host1", "password": "123"},
        {"host_name": "Team 2 Host", "username": "host2", "password": "123"},
        {"host_name": "Team 3 Host", "username": "host3", "password": "123"},
    ])

print("HOSTS:", list(hosts_col.find()))

@app.route('/')
def index():
    return render_template('index.html')


# ---------------- HOST LOGIN -----------------
@app.route('/host-login', methods=['GET','POST'])
def host_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        host = hosts_col.find_one({'username':username,'password':password})
        if host:
            session['host_id'] = str(host['_id'])
            return redirect('/host-dashboard')
    return render_template('host_login.html')


@app.route('/host-dashboard')
def host_dashboard():
    if 'host_id' not in session:
        return redirect('/host-login')
    host = hosts_col.find_one({'_id':ObjectId(session['host_id'])})
    return render_template('host_dashboard.html', host=host)

# ---------------- USER REGISTER -----------------
@app.route('/user-login', methods=['GET','POST'])
def user_login():
    hosts = list(hosts_col.find())
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        team = request.form['team']
        host_id = request.form.get('host')
        if not host_id:
            return "Host not selected", 400

        host = hosts_col.find_one({'_id':ObjectId(host_id)})


        user_data = {
            'user_id': 'U'+str(users_col.count_documents({})+1).zfill(3),
            'username': username,
            'password': password,
            'selected_team': team,
            'selected_host_id': str(host['_id']),
            'selected_host_name': host['host_name']
        }
        users_col.insert_one(user_data)


        # Auto map into host.members
        hosts_col.update_one(
            {'_id':ObjectId(host_id)},
            {'$set':{f"members.{username}":{
                'user_id': user_data['user_id'],
                'team': team
            }}}
        )
        return redirect('/')
    return render_template('user_login.html', hosts=hosts)


if __name__ == '__main__':
    app.run(debug=True)