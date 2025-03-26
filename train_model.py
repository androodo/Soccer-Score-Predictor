import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report
import pickle
import os

def load_data():
    """Load and prepare match data for model training"""
    try:
        # Load data
        matches = pd.read_csv("matches.csv", index_col=0)
        
        # Filter to only Premier League matches
        matches = matches[matches['comp'] == 'Premier League']
        
        # Create target variable (win/loss/draw)
        matches['target'] = matches['result'].apply(lambda x: 1 if x == 'W' else (0 if x == 'D' else -1))
        
        # Calculate rolling averages for key stats (last 5 matches per team)
        teams = matches['team'].unique()
        
        # Create empty dataframe for features
        features_df = pd.DataFrame()
        
        for team in teams:
            team_matches = matches[matches['team'] == team].sort_values('date')
            
            # Skip teams with too few matches
            if len(team_matches) < 10:
                continue
                
            # Calculate rolling averages for key stats
            team_matches['win_rate'] = team_matches['result'].apply(lambda x: 1 if x == 'W' else 0).rolling(5).mean()
            team_matches['goals_scored_avg'] = team_matches['gf'].rolling(5).mean()
            team_matches['goals_conceded_avg'] = team_matches['ga'].rolling(5).mean()
            team_matches['shots_avg'] = team_matches['sh'].rolling(5).mean()
            team_matches['shots_on_target_avg'] = team_matches['sot'].rolling(5).mean()
            
            # Drop rows with NaN values (first 5 matches)
            team_matches = team_matches.dropna(subset=['win_rate', 'goals_scored_avg', 'goals_conceded_avg', 
                                                      'shots_avg', 'shots_on_target_avg'])
            
            # Add to features dataframe
            features_df = pd.concat([features_df, team_matches])
        
        # Reset index
        features_df = features_df.reset_index(drop=True)
        
        # Create is_home feature (1 for home, 0 for away)
        features_df['is_home'] = features_df['venue'].apply(lambda x: 1 if x == 'Home' else 0)
        
        # Create is_draw feature (1 for draw, 0 otherwise)
        features_df['is_draw'] = features_df['result'].apply(lambda x: 1 if x == 'D' else 0)
        
        return features_df
    
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def prepare_features(df):
    """Prepare features for model training"""
    # Select features
    features = ['win_rate', 'goals_scored_avg', 'goals_conceded_avg', 'shots_avg', 
                'shots_on_target_avg', 'is_home', 'is_draw']
    
    # Create X (features) and y (target)
    X = df[features]
    y = df['target']
    
    return X, y

def train_model(X, y):
    """Train and evaluate the prediction model"""
    # Split data into train and test sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Create pipeline with scaling and model
    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('model', RandomForestClassifier(n_estimators=100, random_state=42))
    ])
    
    # Train model
    pipeline.fit(X_train, y_train)
    
    # Evaluate model
    y_pred = pipeline.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"Model Accuracy: {accuracy:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    return pipeline

def save_model(model, filename="model.pkl"):
    """Save trained model to disk"""
    with open(filename, 'wb') as f:
        pickle.dump(model, f)
    print(f"Model saved to {filename}")

def main():
    """Main function to train and save model"""
    print("Loading and preparing data...")
    data = load_data()
    
    if data is None:
        print("Failed to load data. Exiting.")
        return
    
    print(f"Data loaded successfully. Shape: {data.shape}")
    
    print("Preparing features...")
    X, y = prepare_features(data)
    
    print("Training model...")
    model = train_model(X, y)
    
    print("Saving model...")
    save_model(model)
    
    print("Model training complete!")

if __name__ == "__main__":
    main() 