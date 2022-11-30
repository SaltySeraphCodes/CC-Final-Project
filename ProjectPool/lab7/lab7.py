from flask import Flask, render_template, g, flash, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import Email, Length, InputRequired, EqualTo


import db # if error, right-click parent directory "mark directory as" "sources root"

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Funny'


@app.before_request
def before_request():
    db.open_db_connection()


@app.teardown_request
def teardown_request(exception):
    db.close_db_connection()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/accounts')
def all_accounts():

    g.cursor.execute('SELECT * FROM account ORDER BY name')
    results = g.cursor.fetchall()

    return render_template('all-accounts.html', accounts=results)


class MemberForm(FlaskForm):
    email = StringField('Email', validators=[Email()])
    first_name = StringField('First Name', validators=[Length(min=1, max=40)])
    last_name = StringField('Last Name', validators=[Length(min=1, max=40)])
    password = PasswordField('New Password', [InputRequired(), EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Password')
    submit = SubmitField('Save Member')


@app.route('/members/create', methods=['GET', 'POST'])
def create_member():

    member_form = MemberForm()

    # The validate_on_submit() method checks for two conditions.
    # 1. If we're handling a GET request, it returns false,
    #    and we fall through to render_template(), which sends the empty form.
    # 2. Otherwise, we're handling a POST request, so it runs the validators on the form,
    #    and returns false if any fail, so we also fall through to render_template()
    #    which renders the form and shows any error messages stored by the validators.
    if member_form.validate_on_submit():
        member = db.find_member(member_form.email.data)

        if member is not None:
            flash("Member {} already exists".format(member_form.email.data))
        else:
            rowcount = db.create_member(member_form.email.data,
                                        member_form.first_name.data,
                                        member_form.last_name.data,
                                        member_form.password.data)

            if rowcount == 1:
                flash("Member {} created".format(member_form.email.data))
                return redirect(url_for('index'))
            else:
                flash("New member not created")

    # We will get here under any of the following conditions:
    # 1. We're handling a GET request, so we render the (empty) form.
    # 2. We're handling a POST request, and some validator failed, so we render the
    #    form with the same values so that the member can try again. The template
    #    will extract and display the error messages stored on the form object
    #    by the validators that failed.
    # 3. The email entered in the form corresponds to an existing member.
    #    The template will render an error message from the flash.
    # 4. Something happened when we tried to update the database (rowcount != 1).
    #    The template will render an error message from the flash.
    return render_template('member-form.html', form=member_form)


app.run(debug=True)