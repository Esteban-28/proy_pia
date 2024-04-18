from flask import Flask, request, render_template, redirect, url_for, session
from wtforms import Form, StringField, PasswordField, validators, SubmitField
import sqlite3

app = Flask(__name__)

con = sqlite3.connect('password.db', check_same_thread=False)
cur = con.cursor()

class LoginForm(Form):
  user = StringField('User', [
    validators.length(min=4, max=25)
  ])
  pwd = PasswordField('pwd', [
    validators.DataRequired()
  ])
  sub = SubmitField('sub')

@app.route('/login', methods=['GET', 'POST'])
def login():
  form = LoginForm(request.form)
  if request.method == 'POST' and form.validate():
    username = form.user.data
    password = form.pwd.data
    user = con.execute('SELECT * FROM users WHERE username = ?', (username, )).fetchone()

    print(user)
    try:
      if len(user) != 0:
        session['user_id'] = user[0]
        return redirect(url_for('dashboard'))
      else:
        return render_template('login.html', form=form), 300
    except:
      return render_template('login.html', form=form)
  return render_template('login.html', form=form)

login()