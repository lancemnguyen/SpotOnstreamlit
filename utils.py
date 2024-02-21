import os
from openai import OpenAI
import streamlit as st
import requests
import folium
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
gmaps_api_key = os.getenv("GMAPS_API_KEY")


# Function to get completion from OpenAI
def get_completion(prompt, model="gpt-3.5-turbo"):
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "user", "content": prompt},
        ],
        model=model,
    )
    return chat_completion.choices[0].message.content


# Function to search places using the Google Places API
@st.cache_data
def search_places(query):
    # gmaps_api_key = os.getenv("GMAPS_API_KEY")
    base_url = 'https://maps.googleapis.com/maps/api/place/textsearch/json'
    params = {
        'query': query,
        'key': gmaps_api_key,
    }
    response = requests.get(base_url, params=params)
    data = response.json()

    if 'results' in data:
        results = [
            {
                'name': place['name'],
                'address': place.get('formatted_address', 'N/A'),
                'lat': place['geometry']['location']['lat'],
                'lng': place['geometry']['location']['lng'],
                'place_id': place['place_id'],
                'business_status': place.get('business_status', 'N/A'),
                'price_level': place.get('price_level', 'N/A'),
                'rating': place.get('rating', 'N/A'),
                'types': place.get('types', []),
                'user_ratings_total': place.get('user_ratings_total', 'N/A'),
            }
            for place in data['results']
        ]
        return results
    else:
        return []


# Function to get reviews from the Google Places API (Place Details)
def get_reviews_from_api(place_id):
    # gmaps_api_key = os.getenv("GMAPS_API_KEY")
    details_url = 'https://maps.googleapis.com/maps/api/place/details/json'
    details_params = {
        'place_id': place_id,
        'key': gmaps_api_key,
        'fields': 'reviews',
    }
    response = requests.get(details_url, params=details_params)
    details_data = response.json()

    return details_data.get('result', {}).get('reviews', [])


# Function to create Folium map with markers and set initial bounds
def create_folium_map(places):
    m = folium.Map(location=[places[0]['lat'], places[0]['lng']], zoom_start=12)

    for i, place in enumerate(places, start=1):
        folium.Marker(
            location=[place['lat'], place['lng']],
            popup=f"{i}. {place['name']}",
            tooltip=f"{i}. {place['name']}",
        ).add_to(m)

    # Fit bounds based on the markers
    latitudes = [place['lat'] for place in places]
    longitudes = [place['lng'] for place in places]
    south, west, north, east = min(latitudes), min(longitudes), max(latitudes), max(longitudes)
    m.fit_bounds([[south, west], [north, east]])

    return m


def generate_prompt(selected_place, query):
    if not selected_place:
        return None

    place_name = selected_place.get('name', 'N/A')
    place_address = selected_place.get('address', 'N/A')
    reviews = get_reviews_from_api(selected_place.get('place_id', ''))
    reviews_text = "".join([review.get('text', '') for review in reviews])
    prompt = f"Use the reviews: {reviews_text}, from {place_name} at {place_address}, to answer the given query: {query}."
    response = get_completion(prompt)
    return response
