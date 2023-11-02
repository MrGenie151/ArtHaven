import sqlite3
from flask import Flask, render_template, request, g, session, redirect
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'arthavenistheopposite'

DATABASE = 'social_media.db'

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

@app.route("/")
def home():
    return render_template("index.html")

@app.route('/post', methods=['GET', 'POST'])
def post():
    if not session["user_id"]:
        return redirect("/register")

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        dataURL = request.form['dataURL']
        db = get_db()
        cursor = db.cursor()
        cursor.execute('INSERT INTO posts (content,authorid,title,imageData) VALUES (?,?,?,?)', (content,session["user_id"],title,dataURL))
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
    cursor.execute("SELECT content, authorid, title, imageData FROM posts WHERE id = ?",(post_id,))
    post = cursor.fetchone()
    print(post)

    if post:
        title, content, authorid, imageData = post

        return render_template("post.html", post=post)
    
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
        cursor.execute('INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                       (username, email, hashed_password))
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
        cursor.execute('SELECT id, username, password_hash FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        if user:
            user_id, saved_username, saved_password = user

            if check_password(saved_password, password):
                session["user_id"] = user_id
                return redirect("/")
        
        return "Invalid username or password. Please try again."
    return render_template("login.html")

if __name__ == '__main__':
    app.run(debug=True,port=5100)
