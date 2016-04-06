from flask import Flask, request, redirect, render_template, session, flash
from mysqlconnection import MySQLConnector
import re
from time import gmtime, strftime
strftime('%b %d %y %H:%M', gmtime())
# import uuid
# user_id = uuid.uuid1()

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9\.\+_-]+@[a-zA-Z0-9\._-]+\.[a-zA-Z]*$')
NAME_REGEX = re.compile(r'\d')
PASS_REGEX = re.compile(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$')

app = Flask(__name__)

mysql = MySQLConnector('wall')
app.secret_key = "SecretWall"

@app.route('/')
def index():

	return render_template('index.html', messages = messages)

@app.route('/register', methods=['POST'])
def register():
	if len(request.form['email']) < 1 or len(request.form['first_name']) < 2 or len(request.form['last_name']) < 2:
		flash("All fields must contain at least 2 characters.")
	elif not EMAIL_REGEX.match(request.form['email']):
		flash("Invalid Email Address")
	elif len(request.form['password']) < 8:
		flash("Password must contain at least 8 characters.")
	elif NAME_REGEX.search(request.form['first_name']) or NAME_REGEX.search(request.form['last_name']):
		flash("Name fields cannot contain numbers.")
	elif str(request.form['password']) != str(request.form['confirm_password']):
		flash("Passwords do not match.")
	elif not PASS_REGEX.match(request.form['password']):
		flash("Password must contain at least 1 uppercase letter and 1 number.")
	else:
		flash("Thank you for registering for The Wall.")
		query = "INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES ('{}', '{}', '{}', '{}', NOW(), NOW())".format(request.form['first_name'], request.form['last_name'], request.form['email'], request.form['password'])
		mysql.run_mysql_query(query)

	return redirect ('/')


@app.route('/login', methods=['POST'])
def login():
	# if username doesn't match database, password, etc. do it here
	# put query in else statement
	query = "SELECT * FROM users WHERE email = '{}'".format(request.form['email'])
	userdata = mysql.fetch(query)
	
	if len(userdata) == 0:
		print("No user.")
	else:
		print("There is a user.")

	session['user_id'] = userdata[0]['id']
	session['first_name'] = userdata[0]['first_name']
	session['last_name'] = userdata[0]['last_name']
	session['created_at'] = userdata[0]['created_at']
	
	return redirect('/wall')

@app.route('/messages', methods=['POST'])
def messages():
	query = "INSERT INTO messages (user_id, message, created_at, updated_at) VALUES ('{}', '{}', NOW(), NOW())".format(session['user_id'], request.form['message'])
	mysql.run_mysql_query(query)
	return redirect('/wall')

@app.route('/comments', methods=['POST'])
def comment():
	query = "INSERT INTO comments(message_id, user_id, comment, created_at, updated_at) VALUES ('{}', '{}', '{}', NOW(), NOW())".format(request.form['message_id'], session['user_id'], request.form['comment'])
	mysql.run_mysql_query(query)
	return redirect('/wall')

@app.route('/wall')
def message():
	query = "SELECT comments.comment, comments.created_at, comments.message_id, users.first_name, users.last_name FROM comments JOIN users on users.id = comments.user_id"
	comments = mysql.fetch(query)
	query2 = "SELECT messages.id, messages.message, messages.created_at, users.first_name, users.last_name AS user_id FROM messages JOIN users on messages.user_id = users.id order by created_at desc"
	messages = mysql.fetch(query2)
	try:
		session['user_id']
		print "Hello"
	except:
		print "Hello"

	return render_template('wall.html', messages=messages, comments=comments)
@app.route('/logout')
def logout():
	session.clear()

	return redirect('/')

app.run(debug=True)