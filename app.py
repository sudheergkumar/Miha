from flask import Flask, request, jsonify, Markup
import json
from geopy.geocoders import Nominatim
import requests
from rapidfuzz import process
import mysql.connector
from textblob import TextBlob
from transformers import pipeline

app = Flask(__name__)
nlp_pipeline = pipeline("text-generation", model="gpt2")

# Routes for rendering HTML content directly
@app.route('/')
def home():
    return "Welcome to the Home Page!"

@app.route('/about')
def about():
    return "About Us: This is a healthcare chatbot application."

@app.route('/services')
def services():
    return "Our Services: We provide information on hospitals, pharmacies, and medicines."

@app.route('/contact')
def contact():
    return "Contact Us: Reach out via email at support@example.com."

@app.route('/chatbot')
def chatbot():
    return "Chatbot: Type your queries to get assistance."

@app.route('/login')
def login():
    return "Login: Enter your credentials to access your account."

db_config_store1 = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Alex@69420.com',
    'database': 'Apollo'
}

db_config_store2 = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Alex@69420.com',
    'database': 'Aster'
}

# Route to handle chatbot queries
@app.route('/get_response', methods=['POST'])
def get_response():
    data = request.json
    query = data['query']
    print("Received query:", query)

    # Correct spelling mistakes in the query
    corrected_query = str(TextBlob(query).correct())
    print("Corrected query:", corrected_query)

    response = handle_query(corrected_query)
    print("Sending response:", response)
    return jsonify(response)

# Function to handle chatbot queries
def handle_query(query):
    query = query.lower()

    if "hospital" in query or "doctor" in query or "clinic" in query:
        return get_google_maps_link("hospital")
    elif "pharmacy" in query or "drugstore" in query or "chemist" in query:
        return get_google_maps_link("pharmacy")
    elif "availability" in query or "stock" in query or "have" in query and "medicine" in query:
        return check_medicine_availability(query)
    elif "information" in query or "info" in query or "detail" in query and "about" in query:
        disease = query.split("about")[-1].strip()
        return get_disease_info(disease)
    else:
        # Use NLP model to generate a response for other queries
        nlp_response = nlp_pipeline(query, max_length=50, num_return_sequences=1)[0]['generated_text']
        return {"response": Markup(nlp_response)}

# Function to get Google Maps link for nearest places
def get_google_maps_link(place_type):
    location = "Hyderabad"  # Replace with dynamic location based on user input or query
    if place_type == "hospital":
        query_term = "hospitals"
    elif place_type == "pharmacy":
        query_term = "pharmacies"
    else:
        query_term = "places"

    google_maps_url = f"https://www.google.com/maps/search/{query_term}/@{location}"
    link_text = f"Click <a href='{google_maps_url}' target='_blank'>here</a> to find the nearest {place_type}s on Google Maps."
    return {"response": Markup(link_text)}

# Function to check medicine availability
def check_medicine_availability(query):
    name = query.split("availability of")[-1].strip()
    availability_info = get_availability_from_stores(name)
    return {"response": Markup(f"Medicine availability: {availability_info}")}

# Function to get availability from multiple stores
def get_availability_from_stores(name):
    stores = [db_config_store1, db_config_store2]
    availability = []

    for store in stores:
        conn = mysql.connector.connect(**store)
        cursor = conn.cursor()
        cursor.execute("SELECT store_name, quantity FROM medicines WHERE name = %s", (name,))
        results = cursor.fetchall()
        conn.close()

        for result in results:
            store_name, quantity = result
            availability.append(f"{store_name} has {quantity} units of {name}")

    return "; ".join(availability)

# Function to get information about a disease
def get_disease_info(name):
    try:
        with open('diseases.json', 'r') as file:
            diseases = json.load(file)
            for disease in diseases:
                if disease['name'].lower() == name.lower():
                    return {"response": Markup(f"{disease['name']}: {disease['description']} Symptoms: {disease['symptoms']} Treatment: {disease['treatment']}")}
        return {"response": "Sorry, I couldn't find information about that disease."}
    except Exception as e:
        print(f"Error fetching disease info: {e}")
        return {"response": "Error fetching disease information."}

if __name__ == '__main__':
    app.run(debug=True)
