from flask import Flask, render_template, session, request, redirect, url_for

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ILIKEPIE'

@app.route('/')
def index():
    print(session)
    if 'user' in session:
        return render_template('member.html')
    else:
        return render_template('guest.html')


@app.route('/memberarea')
def memberarea():
    if 'user' in session:
        return render_template('memberarea.html')
    else:
        return redirect(url_for('index'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == "POST":
        session['user'] = {}
        session['user']['name'] = request.form['username']
        session['user']['email'] = request.form['email']
        session['user']['password'] = request.form['password'] #Totally secret and secure
        return redirect(url_for('index'))
    else:
        return render_template('signup.html')


@app.route('/login')
def login():
    return render_template('memberarea.html',com=fake_comments, rcom=real_comments)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

app.run(debug=True)