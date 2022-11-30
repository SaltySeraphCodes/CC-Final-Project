from flask import Flask, render_template, session, request, redirect, url_for
app = Flask(__name__)
app.config['SECRET_KEY'] = 'EataChicken'

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/login',methods=['GET','POST'])
def login():
    return render_template('login.html')

@app.route('/logout')
def logout():
    return redirect(url_for('index'))

app.run(debug=True)