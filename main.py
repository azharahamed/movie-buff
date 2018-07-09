from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy
from config import username, password, host, port, database, app_secret_key
from datetime import datetime

connection_string = f'mysql+pymysql://{username}:{password}@{host}:{port}/{database}'
app = Flask(__name__)
app.config['DEBUG'] = False
app.config['ENV'] = 'development'
app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = connection_string
db = SQLAlchemy(app)
db_session = db.session
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
  movies = Movies.query.all()
  return render_template('index.html', movies = movies)

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