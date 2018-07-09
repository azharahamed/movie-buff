from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy
from config import username, password, host, port, database, app_secret_key
from datetime import datetime

connection_string = f'mysql+pymysql://{username}:{password}@{host}:{port}/{database}'
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['ENV'] = 'development'
app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = connection_string
db = SQLAlchemy(app)
app.secret_key = app_secret_key

class Movies(db.Model):
  movie_id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(100))
  year = db.Column(db.Integer)
  director_id = db.Column(db.Integer, db.ForeignKey('directors.director_id'), nullable=False)
  viewings = db.relationship('Viewings', backref='movies')

  def __repr__(self):
    return f'<Movie: {self.title}>'

class Directors(db.Model):
  director_id = db.Column(db.Integer, primary_key=True)
  firstname = db.Column(db.String(45))
  lastname = db.Column(db.String(45))
  country = db.Column(db.String(10))
  movies = db.relationship('Movies', backref='directors')

  def __repr__(self):
    return f'<Director: {self.firstname} {self.lastname}>'

class Viewers(db.Model):
  viewer_id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(10))
  password = db.Column(db.String(45))
  firstname = db.Column(db.String(45))
  lastname = db.Column(db.String(45))
  viewings =  db.relationship('Viewings', backref='viewers')

  def __repr__(self):
    return f'<Viewer: {self.firstname} {self.lastname}>'

class Viewings(db.Model):
  viewings_id = db.Column(db.Integer, primary_key=True)
  date_viewed = db.Column(db.DateTime, default=datetime.utcnow)
  movie_id = db.Column(db.Integer, db.ForeignKey('movies.movie_id'), nullable=False)
  viewer_id = db.Column(db.Integer, db.ForeignKey('viewers.viewer_id'), nullable=False)

  def __repr__(self):
    return f'<viewings: {self.viewings_id}>'

@app.route('/')
def index():
  usrmsg = request.args.get('msg')
  movies = Movies.query.all()
  return render_template('index.html', movies = movies,usrmsg = usrmsg )

@app.route('/register', methods = ['POST', 'GET'])
def register():
  if request.method == 'GET':
    errormsg = request.args.get('error')
    return render_template('viewer_registration.html', errormsg = errormsg)

  elif request.method == 'POST':
    print("Inside the register post method")
    req_username = request.form.get('username')
    req_password = request.form.get('password')
    print(f"Req Username - {req_username} | Req Password - {req_password}")
    if req_password and req_username:
      if req_password == request.form.get('verifypassword'):
        existinguser = Viewers.query.filter_by(username = req_username).first()
        if existinguser:
          errormsg = "Username already exists! Please try with a different username"
          return redirect(f'/register?error={errormsg}')
        viewer = Viewers()
        viewer.firstname = request.form.get('firstname')
        viewer.lastname = request.form.get('lastname')
        viewer.username = req_username
        viewer.password = req_password
        db.session.add(viewer)
        db.session.commit()
        usrmessage = "Registration was successfull"
        session[username] = req_username
        return redirect(f'/?msg={usrmessage}')
      else:
        errormsg = "Registration failed - The password and verify password didn't match"
        return redirect(f'/register?error={errormsg}')
    else:
      errormsg = "Registration failed - The username and password are mandotary"
      return redirect(f'/register?error={errormsg}')

@app.route('/login', methods = ['POST', 'GET'])
def login():
  if session.get('username'):
    usrmessage = "Already Logged-in, Please logout before login again"
    return redirect(f'/?msg={usrmessage}')
    
  if request.method == 'GET':
    errormsg = request.args.get('error')
    return render_template('login.html', errormsg = errormsg)
  
  else:
    req_username = request.form.get('username')
    req_password = request.form.get('password')
    print(f"Req Username - {req_username} | Req Password - {req_password}")
    if req_username and req_password:
      viewer = Viewers.query.filter_by(username = req_username).first()
      if viewer:
        if req_password == viewer.password:
          usrmessage = "Login was successfull"
          session['username'] = req_username
          return redirect(f'/?msg={usrmessage}')
    
@app.route('/logout', methods = ['GET'])
def logout():
  if session.get('username'):
    del session['username']
    usrmessage = "Logout Successfull!"
    return redirect(f'/?msg={usrmessage}')
  else:
    usrmessage = "No logged user to logout"
    return redirect(f'/?msg={usrmessage}')

@app.route('/addmovies', methods = ['POST', 'GET'])
def addmovies():
  if not session.get('username'):
    usrmessage = "Please login before Adding movies"
    return redirect(f'/?msg={usrmessage}')
  
  if request.method == 'GET':
    errormsg = request.args.get('error')
    return render_template('addmovies.html', errormsg = errormsg)
  
  else:
    req_movie_title = request.form.get('title')
    req_movie_year = request.form.get('year')
    req_movie_director_f = request.form.get('firstname')
    req_movie_director_l = request.form.get('lastname') 
    req_movie_director_c = request.form.get('country') 

    if req_movie_title and req_movie_year and req_movie_director_f and req_movie_director_l and req_movie_director_c:
      director = Directors()
      director.firstname = req_movie_director_f
      director.lastname = req_movie_director_l
      director.country = req_movie_director_c
      db.session.add(director)
      db.session.flush()
      movie = Movies()
      movie.title = req_movie_title
      movie.year = req_movie_year
      movie.director_id = director.director_id
      db.session.add(movie)
      db.session.commit()
      
      usrmessage = f"You movies '{req_movie_title}' has been added"
      return redirect(f'/?msg={usrmessage}')
    else:
      error = "All the fields are mandatory"
      return redirect(f'/addmovies?error={error}')

def main():
  from sqlalchemy import create_engine, inspect
  from sqlalchemy.exc import OperationalError
    
  try:
      ENGINE = create_engine(connection_string)
      INSPECTOR = inspect(ENGINE)  # used for checking if tables exist on startup
      # check if tables exist - create if they do not
      tables = INSPECTOR.get_table_names()
      if not tables:
          db.create_all()
  except OperationalError:
      print("Operational Error, Turn on MAMP")   

  app.run()

if __name__ == '__main__':
  main()