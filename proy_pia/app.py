from flask import Flask, request, render_template, redirect, url_for, session
from wtforms import Form, StringField, PasswordField, validators, SubmitField, IntegerField, SelectField
import sqlite3
import os

app = Flask(__name__)

con = sqlite3.connect('password.db', check_same_thread=False)
cur = con.cursor()

class RegistrationForm(Form):
  username = StringField('Username', [validators.length(min=4, max=25)])
  password = PasswordField('New Password',[
    validators.DataRequired(),
    validators.EqualTo('confirm', message='Passwords must match')
  ])
  confirm = PasswordField('Repeat Password')
  submit = SubmitField('Aceptar', render_kw={"class": "btn btn-success text-white w-100 mt-4 fw-semibold shadow-sm"})

class LoginForm(Form):
  user = StringField('User', [
    validators.length(min=4, max=25)
  ])
  pwd = PasswordField('pwd', [
    validators.DataRequired()
  ])
  sub = SubmitField('Log in')

class MetricForm(Form):
  kilos = IntegerField(label="Ingresa tu peso en kilogramos")
  altura = IntegerField(label="Ingresa tu altura en centimetros")
  edad = IntegerField(label="Ingresa tu edad en años")
  sexo = SelectField('Sexo', choices=[("M"), ("F")])
  submit = SubmitField('Aceptar')

@app.route('/', methods=['GET', 'POST'])
def home():
  session.clear()
  return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
  form = RegistrationForm(request.form)
  if request.method == 'POST' and form.validate():
    data = [form.username.data, form.password.data]
    try:
      con.execute("INSERT INTO users (username, password) VALUES (?, ?)", data)
      con.commit()
    except sqlite3.IntegrityError:
      return redirect(url_for('register'))
    return redirect(url_for('login'))
  return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
  form = LoginForm(request.form)
  if request.method == 'POST' and form.validate():
    username = form.user.data
    password = form.pwd.data
    user = con.execute('SELECT * FROM users WHERE username = ?', (username, )).fetchone()
    if user is not None and password == user[2]:
      session['user_id'] = user[0]
      return redirect(url_for('dashboard'))
    else:
      return render_template('login.html', form=form)
  return render_template('login.html', form=form)

@app.route('/dashboard', methods=["GET", "POST"])
def dashboard():
  if 'user_id' in session:
    user = con.execute('SELECT * FROM users WHERE user_id = ?', (session['user_id'], )).fetchone()
    msg = 'Bienvenido '+user[1]
    metrics = con.execute('SELECT * FROM metric WHERE user_id = ?', (session['user_id'], )).fetchone()
    if metrics == None:
      return redirect(url_for('info'))
    return render_template('dashboard.html', username=user[1], msg=msg, metrics=metrics)
  return redirect(url_for('login'))

@app.route('/dashboard/info', methods=["GET", "POST"])
def info():
  if 'user_id' in session:
    form = MetricForm(request.form)
    if request.method == "POST" and form.validate():
      data = [session['user_id'], form.altura.data, form.edad.data, form.sexo.data, form.kilos.data]
      try:
        con.execute("INSERT INTO metric (user_id, altura, edad, sexo, kilos) VALUES (?, ?, ?, ?, ?)", data)
        con.commit()
      except sqlite3.IntegrityError:
        print("Error")
        return redirect(url_for('info'))
      return redirect(url_for('dashboard'))
    return render_template('info.html', form=form)
  return redirect(url_for('login'))


if __name__ == '__main__':
  app.secret_key = os.urandom(16)
  app.run(debug=True)