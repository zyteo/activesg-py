import os
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS
from urllib.parse import quote_plus # For URL encoding query parameters

app = Flask(__name__)

# Configure CORS to allow requests from any origin for now.
# In a production environment, you should restrict this to your frontend's domain:
# CORS(app, origins=["https://asgfilter.vercel.app"])
CORS(app, origins="*")

# Define common browser headers to mimic a Mozilla browser.
# This can help bypass some bot detection mechanisms.
BROWSER_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
    # You might want to add 'Referer' if specific to ActiveSG or 'Origin'
    # 'Referer': 'https://activesg.gov.sg/',
    # 'Origin': 'https://activesg.gov.sg',
}

# Base URL for the ActiveSG API
ACTIVESG_BASE_URL = "https://activesg.gov.sg/api/trpc"

@app.route("/", methods=["GET"])
def home():
    """
    Root endpoint to confirm the Flask server is running.
    """
    return "Flask server is running!"

@app.route("/api/venues", methods=["GET"])
async def get_venues():
    """
    Proxies the request to the ActiveSG API for programme venues.
    """
    try:
        url = f"{ACTIVESG_BASE_URL}/programme.getProgrammeVenues?input=%7B%22json%22%3Anull%2C%22meta%22%3A%7B%22values%22%3A%5B%22undefined%22%5D%7D%7D"
        # Make the request with browser-like headers
        response = requests.get(url, headers=BROWSER_HEADERS)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        return jsonify(data), 200
    except requests.exceptions.RequestException as e:
        # Catch requests library specific errors (e.g., network issues, HTTP errors)
        app.logger.error(f"Error fetching /api/venues: {e}")
        return jsonify({"error": "Failed to fetch venues data.", "details": str(e)}), 500
    except ValueError as e:
        # Catch JSON decoding errors
        app.logger.error(f"Error decoding JSON for /api/venues: {e}")
        return jsonify({"error": "Failed to parse API response for venues.", "details": str(e)}), 500
    except Exception as e:
        # Catch any other unexpected errors
        app.logger.error(f"An unexpected error occurred for /api/venues: {e}")
        return jsonify({"error": "An unexpected server error occurred for venues.", "details": str(e)}), 500


@app.route("/api/sportslist", methods=["GET"])
async def get_sportslist():
    """
    Proxies the request to the ActiveSG API for the list of activities/sports.
    """
    try:
        url = f"{ACTIVESG_BASE_URL}/activity.listForProgrammes?input=%7B%22json%22%3Anull%2C%22meta%22%3A%7B%22values%22%3A%5B%22undefined%22%5D%7D%7D"
        response = requests.get(url, headers=BROWSER_HEADERS)
        response.raise_for_status()
        data = response.json()
        return jsonify(data), 200
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error fetching /api/sportslist: {e}")
        return jsonify({"error": "Failed to fetch sports list data.", "details": str(e)}), 500
    except ValueError as e:
        app.logger.error(f"Error decoding JSON for /api/sportslist: {e}")
        return jsonify({"error": "Failed to parse API response for sports list.", "details": str(e)}), 500
    except Exception as e:
        app.logger.error(f"An unexpected error occurred for /api/sportslist: {e}")
        return jsonify({"error": "An unexpected server error occurred for sports list.", "details": str(e)}), 500


@app.route("/api/activity", methods=["GET"])
async def get_activity():
    """
    Proxies the request to the ActiveSG API for program activities,
    filtering by sport query parameter.
    """
    sport = request.args.get("sport")
    if not sport:
        return jsonify({"error": "Sport query parameter is required."}), 400

    try:
        # URL-encode the sport parameter to ensure valid URL construction
        encoded_sport = quote_plus(sport)
        url = f"{ACTIVESG_BASE_URL}/programme.listV2?input=%7B%22json%22%3A%7B%22searchQuery%22%3A%22{encoded_sport}%22%2C%22venueId%22%3Anull%2C%22minAgeFilter%22%3Anull%2C%22maxAgeFilter%22%3Anull%2C%22sexFilter%22%3Anull%2C%22postalCode%22%3Anull%2C%22firstSessionFromDate%22%3Anull%2C%22lastSessionTillDate%22%3Anull%2C%22limit%22%3A10%2C%22cursor%22%3Anull%7D%2C%22meta%22%3A%7B%22values%22%3A%7B%22cursor%22%3A%5B%22undefined%22%5D%7D%7D%7D"
        response = requests.get(url, headers=BROWSER_HEADERS)
        response.raise_for_status()
        data = response.json()
        return jsonify(data), 200
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error fetching /api/activity for sport '{sport}': {e}")
        return jsonify({"error": "Failed to fetch activity data.", "details": str(e)}), 500
    except ValueError as e:
        app.logger.error(f"Error decoding JSON for /api/activity: {e}")
        return jsonify({"error": "Failed to parse API response for activity.", "details": str(e)}), 500
    except Exception as e:
        app.logger.error(f"An unexpected error occurred for /api/activity: {e}")
        return jsonify({"error": "An unexpected server error occurred for activity.", "details": str(e)}), 500


@app.route("/api/capacity", methods=["GET"])
async def get_capacity():
    """
    Proxies the request to the ActiveSG API for facility capacities.
    """
    try:
        url = f"{ACTIVESG_BASE_URL}/pass.getFacilityCapacities?input=%7B%22json%22%3Anull%2C%22meta%22%3A%7B%22values%22%3A%5B%22undefined%22%5D%7D%7D"
        response = requests.get(url, headers=BROWSER_HEADERS)
        response.raise_for_status()
        data = response.json()
        return jsonify(data), 200
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error fetching /api/capacity: {e}")
        return jsonify({"error": "Failed to fetch capacity data.", "details": str(e)}), 500
    except ValueError as e:
        app.logger.error(f"Error decoding JSON for /api/capacity: {e}")
        return jsonify({"error": "Failed to parse API response for capacity.", "details": str(e)}), 500
    except Exception as e:
        app.logger.error(f"An unexpected error occurred for /api/capacity: {e}")
        return jsonify({"error": "An unexpected server error occurred for capacity.", "details": str(e)}), 500


# Entry point for the Flask application
if __name__ == "__main__":
    # Get the PORT from environment variables (e.g., set by Render) or default to 5000
    port = int(os.environ.get("PORT", 5000))
    # In a production environment, use a WSGI server like Gunicorn or uWSGI.
    # app.run(host="0.0.0.0", port=port, debug=False)
    # For local development, you can use debug=True
    app.run(host="0.0.0.0", port=port, debug=True)
