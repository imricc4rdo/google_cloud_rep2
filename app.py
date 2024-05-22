from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
from transformers import pipeline
import random
from datetime import datetime
from playlist import *

classifier = pipeline("text-classification", model="SamLowe/roberta-base-go_emotions", top_k=None)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///responses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Response(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    time = db.Column(db.String(80), nullable = False)
    rand_playlist = db.Column(db.Integer, nullable = False)    
    evaluation = db.Column(db.Integer, nullable = False)


@app.route("/")
def index():
    global prob
    prob = random.random()
    global model_output_random
    model_output_random = random_playlist(20)
    return render_template("index.html")


@app.route("/submit", methods = ["POST"])
def submit():
    song = request.form['song']
    artist = request.form['artist']
    n_songs = int(request.form['nsongs'])
    descr = request.form['descr']
    
    global rand_playlist
    
    if prob > 0.5: # Return random playlist
        print('RANDOM')
        rand_playlist = 1
        model_output = model_output_random[:n_songs]
    else: # Return model playlist
        print('MODEL')
        rand_playlist = 0
        sentiments = classifier(descr)
        model_output = model_playlist(song, artist, n_songs, sentiments)

    return render_template('recommendations.html', model_output = model_output, descr = descr)

  
@app.route("/evaluation", methods = ["POST"])
def evaluation():
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    evaluation = int(request.form['evaluation'])
    response = Response(time = time, rand_playlist = rand_playlist, evaluation = evaluation)
    db.session.add(response)
    db.session.commit()
    return render_template('thankyou.html')
 

@app.route('/results')
def results():
    responses = Response.query.all()
    total_responses = len(responses)
    
    return render_template('results.html', responses = responses, total_responses = total_responses)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug = True)