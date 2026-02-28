from flask import Flask, request, jsonify
from flask_cors import CORS
import re

app = Flask(__name__)
CORS(app)

# List of common place indicators
place_indicators = [
    'City', 'Town', 'Village', 'State', 'Country', 'Province', 'Region',
    'Street', 'Avenue', 'Road', 'Boulevard', 'Lane', 'Drive', 'Place',
    'Square', 'Park', 'Garden', 'Forest', 'River', 'Lake', 'Ocean', 'Sea',
    'Mountain', 'Valley', 'Island', 'Peninsula', 'Gulf', 'Bay',
    'Airport', 'Station', 'University', 'College', 'School', 'Hospital',
    'Hotel', 'Restaurant', 'Cafe', 'Museum', 'Theater', 'Stadium',
    'Bridge', 'Tower', 'Castle', 'Palace', 'Temple', 'Church', 'Mosque',
    'Continent', 'District', 'Zone', 'Neighborhood'
]

# List of common place names (add more as needed)
common_places = [
    'New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia',
    'San Antonio', 'San Diego', 'Dallas', 'San Jose', 'London', 'Paris', 'Tokyo',
    'Delhi', 'Shanghai', 'São Paulo', 'Mexico City', 'Cairo', 'Mumbai', 'Beijing',
    'Dhaka', 'Osaka', 'Karachi', 'Istanbul', 'United States', 'China', 'India',
    'Indonesia', 'Pakistan', 'Brazil', 'Nigeria', 'Bangladesh', 'Russia', 'Japan'
]

def extract_entities(text):
    # Pattern for names (two capitalized words)
    name_pattern = r'\b[A-Z][a-z]+ [A-Z][a-z]+\b'
    
    # Pattern for places (capitalized word followed by a place indicator)
    place_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:' + '|'.join(place_indicators) + r')\b'
    
    # Find names and places using patterns
    names = list(set(re.findall(name_pattern, text)))
    places = list(set(re.findall(place_pattern, text)))
    
    # Add common places if they are in the text
    for place in common_places:
        if place in text and place not in places:
            places.append(place)
    
    return {
        'names': sorted(names),
        'places': sorted(places)
    }

@app.route('/api/detect-entities', methods=['POST'])
def detect_entities():
    data = request.json
    text = data.get('text', '')
    
    entities = extract_entities(text)
    
    return jsonify({'entities': entities})

if __name__ == '__main__':
    app.run(debug=True)