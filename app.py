from flask import Flask, render_template, request, jsonify
import pandas as pd
import pickle
import os
import numpy as np
from datetime import datetime

app = Flask(__name__)

# Load the trained model
def load_model():
    try:
        with open('model.pkl', 'rb') as file:
            model = pickle.load(file)
        return model
    except FileNotFoundError:
        return None

# Load the dataset
def load_data():
    try:
        return pd.read_csv("matches.csv", index_col=0)
    except FileNotFoundError:
        return None

# Home page route
@app.route('/')
def home():
    # Get all teams from the dataset
    data = load_data()
    
    if data is None:
        return render_template('error.html', message="Dataset not found!")
    
    # Extract unique team names
    teams = sorted(data['team'].unique().tolist())
    
    return render_template('index.html', teams=teams)

# Prediction API endpoint
@app.route('/predict', methods=['POST'])
def predict():
    model = load_model()
    data = load_data()
    
    if model is None:
        return jsonify({'error': 'Model not found!'}), 404
    
    if data is None:
        return jsonify({'error': 'Dataset not found!'}), 404
    
    # Get form data
    home_team = request.form.get('home_team')
    away_team = request.form.get('away_team')
    
    if not home_team or not away_team:
        return jsonify({'error': 'Please select both home and away teams'}), 400
    
    if home_team == away_team:
        return jsonify({'error': 'Home and away teams cannot be the same'}), 400
    
    # Process data for prediction
    try:
        # Get the latest data for both teams
        home_data = data[data['team'] == home_team].sort_values('date').tail(5)
        away_data = data[data['team'] == away_team].sort_values('date').tail(5)
        
        # Calculate features
        home_form = calculate_form(home_data)
        away_form = calculate_form(away_data)
        
        # Create prediction features - only include the 7 features expected by the model
        features = np.array([
            home_form['win_rate'], 
            home_form['goals_scored_avg'],
            home_form['goals_conceded_avg'],
            home_form['shots_avg'],
            home_form['shots_on_target_avg'],
            1,  # Is home game (1 for yes)
            0   # Is draw (default to 0)
        ]).reshape(1, -1)
        
        # Make prediction
        prediction = model.predict_proba(features)[0]
        
        # Return prediction results
        return jsonify({
            'home_win_probability': round(prediction[1] * 100, 2),
            'draw_probability': round(prediction[0] * 100, 2),
            'away_win_probability': round((1 - prediction[0] - prediction[1]) * 100, 2),
            'predicted_result': 'Home Win' if prediction[1] > 0.5 else ('Draw' if prediction[0] > 0.33 else 'Away Win'),
            'expected_score': f"{round(home_form['goals_scored_avg'], 1)} - {round(away_form['goals_scored_avg'], 1)}"
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Helper function to calculate team form
def calculate_form(team_data):
    if team_data.empty:
        return {
            'win_rate': 0,
            'goals_scored_avg': 0,
            'goals_conceded_avg': 0,
            'shots_avg': 0,
            'shots_on_target_avg': 0
        }
    
    wins = team_data[team_data['result'] == 'W'].shape[0]
    win_rate = wins / team_data.shape[0]
    
    goals_scored_avg = team_data['gf'].mean()
    goals_conceded_avg = team_data['ga'].mean()
    
    shots_avg = team_data['sh'].mean()
    shots_on_target_avg = team_data['sot'].mean()
    
    return {
        'win_rate': win_rate,
        'goals_scored_avg': goals_scored_avg,
        'goals_conceded_avg': goals_conceded_avg,
        'shots_avg': shots_avg,
        'shots_on_target_avg': shots_on_target_avg
    }

# About page route
@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True) 