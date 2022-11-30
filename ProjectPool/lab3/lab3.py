from flask import Flask, render_template
from math import *

app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template('hello.html')


@app.route('/name')
def hello_name():
    return render_template('hello-name.html', name ='Jimmy')


@app.route('/comments')
def comments():
    fake_comments = []
    fake_comments.append("hello")
    fake_comments.append("die")
    fake_comments.append("please die")

    real_comments = []
    real_comments.append({"name": "Mom", "says": "This was horrible"})
    real_comments.append({"name": "Dad","says": "I've seen better"})
    real_comments.append({"name": "Uncle", "says": "I cant wait to see you again ( ͡° ͜ʖ ͡°)"})
    return render_template('comments.html',com=fake_comments, rcom=real_comments)



if __name__ == '__main__':
    app.run(debug=True)