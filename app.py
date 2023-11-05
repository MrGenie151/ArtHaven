import sqlite3
from flask import Flask, render_template, request, g, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import time
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

UPLOAD_FOLDER = '/static/image'

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

DATABASE = 'social_media.db'

# HELPER FUNCTIONS
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def check_password(saved_password, entered_password):
    return check_password_hash(saved_password, entered_password)

# MAIN SITE STUFF
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/content-rules")
def contentrules():
    return render_template("content-rules.html")

@app.route('/post', methods=['GET', 'POST'])
def post():
    if not "user_id" in session:
        return redirect("/register")

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        dataURL = request.form['dataURL']
        db = get_db()
        cursor = db.cursor()
        cursor.execute('INSERT INTO posts (content,authorid,title,imageData,postdate) VALUES (?,?,?,?,?)', (content,session["user_id"],title,dataURL,time.time()))
        db.commit()
        return redirect("/")
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM posts')
    posts = cursor.fetchall()
    return render_template('posts.html', posts=posts)

@app.route("/browse")
def browse():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM posts ORDER BY id DESC limit 50")
    posts = cursor.fetchall()
    return render_template("browse.html",posts=posts)

@app.route("/post/<post_id>")
def post_page(post_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT content, authorid, title, imageData, postdate, id, username FROM posts INNER JOIN users ON posts.authorid = users.userid WHERE id = ?",(post_id,))
    post = cursor.fetchone()
    #print(post)
    #cursor.execute("SELECT userid, username FROM users WHERE userid = ?",(post[1],))
    #author = cursor.fetchone()
    cursor.execute("SELECT commentid, comment_content, postdate, authorid, username FROM comments INNER JOIN users ON comments.authorid = users.userid WHERE postid = ? ORDER BY commentid DESC",(post_id,))
    comments = cursor.fetchall()

    if post:
        #title, content, authorid, imageData = post
        date = datetime.fromtimestamp(post[4])

        return render_template("post.html", post=post,postdate=date.strftime("%d-%m-%y"),comments=comments)
    
    return render_template("error.html")

@app.route("/users/<user_id>")
def user_page(user_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT username, userid, description, joindate FROM users WHERE userid = ?",(user_id,))
    user = cursor.fetchone()

    cursor.execute("SELECT * FROM posts WHERE authorid = ? ORDER BY id DESC limit 50",(user_id,))
    posts = cursor.fetchall()
    #print(post)

    if user:
        #title, content, authorid, imageData = post
        date = datetime.fromtimestamp(user[3])

        return render_template("user.html", user=user, joindate=date.strftime("%d-%m-%y"), posts=posts)
    
    return render_template("error.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        # Hash the password securely
        hashed_password = generate_password_hash(password)

        # Store the user's information in the 'users' table
        db = get_db()
        cursor = db.cursor()
        cursor.execute('INSERT INTO users (username, email, password_hash, description, joindate) VALUES (?, ?, ?, ?, ?)',
                       (username, email, hashed_password, "User has no description.",time.time()))
        db.commit()

        # Redirect to a new page or perform additional actions
        # (e.g., a 'Thank you for registering' page or login page)
        return render_template('register_success.html')
    return render_template('registration.html')  # Replace with your registration form template

@app.route('/login',methods=["GET","POST"])
def login():
    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]

        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT userid, username, password_hash, ismoderator FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        if user:
            user_id, saved_username, saved_password, ismoderator = user

            if check_password(saved_password, password):
                session["user_id"] = user_id
                if ismoderator and ismoderator > 0:
                    session["moderator"] = True
                return redirect("/")
        
        return "Invalid username or password. Please try again."
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop('user_id',default=None)
    session.pop('moderator',default=None)
    return redirect("/")

@app.route("/comment/<post_id>", methods=['POST'])
def comment(post_id):
    comment_content = request.form["comment-box"]
    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO comments (postid, authorid, comment_content, postdate) VALUES (?, ?, ?, ?)",(post_id, session["user_id"], comment_content, time.time()))
    db.commit()
    return redirect("/post/" + str(post_id) + "#comments")

# END OF MAIN SITE STUFF

#API STUFF
@app.route("/api/is_logged_in")
def is_logged_in():
    if 'user_id' in session:
        return { "response" : True, "userid" : session["user_id"]}
    else:
        return { "response" : False}

@app.route("/api/user/<user_id>")
def user_api(user_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT username, description, joindate FROM users WHERE userid = ?",(user_id,))
    user = cursor.fetchone()

    if user:
        username, description, joindate = user

        return {"username" : username, "description" : description, "joindate" : joindate}

    return {"response" : "Error!"}

@app.route("/api/post/<post_id>/delete", methods=['GET'])
def delete_post(post_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM posts WHERE id = ?",(post_id,))
    post = cursor.fetchone()
    if post:
        if session["user_id"] == post[2] or session["moderator"] > 0:
            print("epic")
            cursor.execute("DELETE FROM posts WHERE id = ?",(post_id,))
            db.commit()
            return "Go back to browse idiot"
    return "Friggin heck"

# END OF API STUFF

if __name__ == '__main__':
    app.run(debug=True,port=5100)
