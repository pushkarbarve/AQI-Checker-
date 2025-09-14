from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

API_KEY = os.getenv("AQICN")
API_URL_FEED = "https://api.waqi.info/feed/{city}/?token={token}"
API_URL_SEARCH = "https://api.waqi.info/search/?keyword={keyword}&token={token}"


# ----------------- ROUTE 1: Homepage -----------------
@app.route('/')
def home():
    return render_template("temp.html")


# ----------------- ROUTE 2: Get AQI for a station -----------------
@app.route('/api/aqi', methods=['POST'])
def get_air_quality():
    data = request.get_json()
    if not data or 'city' not in data:
        return jsonify({'error': 'City name is required.'}), 400

    city_name = data['city']
    try:
        response = requests.get(API_URL_FEED.format(city=city_name, token=API_KEY))
        response.raise_for_status()
        api_data = response.json()
        if api_data.get('status') == 'ok':
            return jsonify(api_data['data'])
        else:
            return jsonify({'error': api_data.get('data', 'Unknown station')}), 404
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Failed to connect to the AQI service: {e}'}), 503
    except Exception as e:
        return jsonify({'error': f'An unexpected error occurred: {e}'}), 500


# ----------------- ROUTE 3: Suggest stations for a city -----------------
@app.route('/api/suggest', methods=['POST'])
def suggest_stations():
    data = request.get_json()
    if not data or 'city' not in data:
        return jsonify({'error': 'City name is required.'}), 400

    city_to_check = data['city']
    try:
        response = requests.get(API_URL_SEARCH.format(keyword=city_to_check, token=API_KEY))
        response.raise_for_status()
        api_data = response.json()

        if api_data.get('status') == 'ok':
            stations = []
            for s in api_data.get("data", []):
                stations.append({
                    "station_name": s["station"]["name"],
                    "geo": s["station"]["geo"],
                    "aqi": s.get("aqi", "-")
                })
            return jsonify(stations)
        else:
            return jsonify({'error': 'No stations found'}), 404

    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Failed to connect to the AQI service: {e}'}), 503
    except Exception as e:
        return jsonify({'error': f'An unexpected error occurred: {e}'}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
