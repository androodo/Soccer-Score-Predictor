import os
import requests
import pandas as pd
from urllib.parse import urlparse
from PIL import Image, ImageDraw, ImageFont
import io

# Create the teams directory if it doesn't exist
os.makedirs('static/images/teams', exist_ok=True)

# Define a function to normalize team names
def normalize_team_name(team_name):
    # Convert to lowercase, replace spaces with underscores and remove special characters
    return team_name.lower().replace(' ', '_').replace('-', '_').replace('.', '').replace('&', 'and')

# Premier League team logo URLs
team_logos = {
    'Arsenal': 'https://resources.premierleague.com/premierleague/badges/t3.png',
    'Chelsea': 'https://resources.premierleague.com/premierleague/badges/t8.png',
    'Liverpool': 'https://resources.premierleague.com/premierleague/badges/t14.png',
    'Manchester United': 'https://resources.premierleague.com/premierleague/badges/t1.png',
    'Manchester City': 'https://resources.premierleague.com/premierleague/badges/t43.png',
    'Tottenham Hotspur': 'https://resources.premierleague.com/premierleague/badges/t6.png',
    'Aston Villa': 'https://resources.premierleague.com/premierleague/badges/t7.png',
    'Newcastle United': 'https://resources.premierleague.com/premierleague/badges/t4.png',
    'West Ham United': 'https://resources.premierleague.com/premierleague/badges/t21.png',
    'Bournemouth': 'https://resources.premierleague.com/premierleague/badges/t91.png',
    'Fulham': 'https://resources.premierleague.com/premierleague/badges/t54.png',
    'Wolverhampton Wanderers': 'https://resources.premierleague.com/premierleague/badges/t39.png',
    'Everton': 'https://resources.premierleague.com/premierleague/badges/t11.png',
    'Brentford': 'https://resources.premierleague.com/premierleague/badges/t94.png',
    'Nottingham Forest': 'https://resources.premierleague.com/premierleague/badges/t17.png',
    'Luton Town': 'https://resources.premierleague.com/premierleague/badges/t102.png',
    'Burnley': 'https://resources.premierleague.com/premierleague/badges/t90.png',
    'Sheffield United': 'https://resources.premierleague.com/premierleague/badges/t49.png',
    'Ipswich Town': 'https://resources.premierleague.com/premierleague/badges/t98.png',
    'Leicester City': 'https://resources.premierleague.com/premierleague/badges/t13.png',
    'Southampton': 'https://resources.premierleague.com/premierleague/badges/t20.png',
    'Crystal Palace': 'https://resources.premierleague.com/premierleague/badges/t31.png',
    'Brighton': 'https://resources.premierleague.com/premierleague/badges/t36.png',
    'Brighton and Hove Albion': 'https://resources.premierleague.com/premierleague/badges/t36.png',
    'Leeds United': 'https://resources.premierleague.com/premierleague/badges/t2.png',
    'Watford': 'https://resources.premierleague.com/premierleague/badges/t57.png',
    'Norwich City': 'https://resources.premierleague.com/premierleague/badges/t45.png',
}

# Function to create a placeholder logo
def create_placeholder_logo(team_name, output_path):
    try:
        # Create a 200x200 white image with an initial
        size = (200, 200)
        image = Image.new('RGBA', size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Create a colored circle
        circle_color = get_color_from_name(team_name)
        radius = 90
        center = (size[0] // 2, size[1] // 2)
        draw.ellipse((center[0] - radius, center[1] - radius, 
                      center[0] + radius, center[1] + radius), fill=circle_color)
        
        # Draw the first letter
        letter = team_name[0].upper()
        try:
            # Try to use a standard font
            font = ImageFont.truetype("arial.ttf", 100)
        except:
            # Fallback to default font
            font = ImageFont.load_default()
        
        # Calculate text position to center it
        text_width = draw.textlength(letter, font=font)
        text_height = 100  # Approximate height
        text_position = (center[0] - text_width // 2, center[1] - text_height // 2)
        
        # Draw the text
        draw.text(text_position, letter, fill="white", font=font)
        
        # Save the image
        image.save(output_path, 'PNG')
        print(f"Created placeholder logo for {team_name}")
        return True
    except Exception as e:
        print(f"Error creating placeholder logo for {team_name}: {str(e)}")
        return False

# Get a unique color based on team name
def get_color_from_name(team_name):
    hash_value = 0
    for char in team_name:
        hash_value = ord(char) + ((hash_value << 5) - hash_value)
    
    hue = hash_value % 360
    return f"hsl({hue}, 70%, 50%)"

# Try to load the dataset to get actual team names
try:
    # Load the matches.csv to get actual team names in the dataset
    matches_df = pd.read_csv('matches.csv')
    # Get unique team names
    teams_in_dataset = matches_df['team'].unique()
    print(f'Found {len(teams_in_dataset)} teams in the dataset')
    
    # Check if we have predefined logos for teams in the dataset
    for team in teams_in_dataset:
        normalized_name = normalize_team_name(team)
        output_path = f'static/images/teams/{normalized_name}.png'
        
        # Check if we've already downloaded this logo
        if os.path.exists(output_path):
            print(f'Logo for {team} already exists')
            continue
            
        # Check if we have a predefined logo URL for this team
        found = False
        for known_team, logo_url in team_logos.items():
            if team.lower() == known_team.lower():
                found = True
                try:
                    print(f'Downloading logo for {team}...')
                    response = requests.get(logo_url, stream=True)
                    if response.status_code == 200:
                        with open(output_path, 'wb') as f:
                            for chunk in response.iter_content(1024):
                                f.write(chunk)
                        print(f'Downloaded logo for {team}')
                    else:
                        print(f'Failed to download logo for {team}: HTTP {response.status_code}')
                        # Create a placeholder logo instead
                        create_placeholder_logo(team, output_path)
                except Exception as e:
                    print(f'Error downloading logo for {team}: {str(e)}')
                    # Create a placeholder logo instead
                    create_placeholder_logo(team, output_path)
                break
                
        if not found:
            print(f'No predefined logo URL for {team}, creating placeholder')
            create_placeholder_logo(team, output_path)
    
except Exception as e:
    print(f'Error processing team logos: {str(e)}')
    
print('Done!') 