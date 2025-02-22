import firebase_admin
from firebase_admin import credentials, db
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from datetime import datetime, timezone, timedelta
import requests

# API Keys (Replace with actual API Key)
GOOGLE_MAPS_API_KEY = "********************************"
OPENWEATHER_API_KEY = "********************************"

# Load Google Calendar Credentials
SCOPES = ["https://www.googleapis.com/auth/calendar"]
creds = Credentials.from_authorized_user_file("token.json", SCOPES)
service = build("calendar", "v3", credentials=creds)

# Load Firebase Credentials for Second Project
cred_travel = credentials.Certificate("travel-firebase-key.json") 
firebase_admin.initialize_app(cred_travel, {
    "databaseURL": "https://travelschedule-453a2-default-rtdb.firebaseio.com/"
}, name="travel_db")

# Reference to the "travel_logs" node in Firebase
travel_logs_ref = db.reference("travel_logs", app=firebase_admin.get_app("travel_db"))

# Step 1: Fetch the Next Event with a Location
def get_next_event():
    now = datetime.now(timezone.utc).isoformat()  # Current time in UTC
    events_result = service.events().list(
        calendarId="primary", timeMin=now, maxResults=1, singleEvents=True, orderBy="startTime"
    ).execute()
    
    events = events_result.get("items", [])
    if not events:
        print("No upcoming events found with a location.")
        return None

    event = events[0]
    event_time = event["start"]["dateTime"]
    destination = event.get("location", None)

    if not destination:
        print("Event has no location.")
        return None
    
    return event, event_time, destination

# Step 2: Get User's Current Location (Geolocation API)
def get_current_location():
    geo_url = f"https://www.googleapis.com/geolocation/v1/geolocate?key={GOOGLE_MAPS_API_KEY}"
    geo_response = requests.post(geo_url)
    geo_data = geo_response.json()

    if "location" in geo_data:
        lat, lng = geo_data["location"]["lat"], geo_data["location"]["lng"]
        return f"{lat},{lng}"
    else:
        print("Error fetching location.")
        return None

# Step 3: Get Weather Data for Current Location
def get_weather(lat, lng):
    weather_url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lng}&appid={OPENWEATHER_API_KEY}&units=metric"
    weather_response = requests.get(weather_url)
    weather_data = weather_response.json()

    if "weather" in weather_data:
        weather_condition = weather_data["weather"][0]["description"]
        temp = weather_data["main"]["temp"]
        return weather_condition, temp
    else:
        print("Error fetching weather data.")
        return None, None

# Step 4: Get Travel Time from Google Maps API
def get_travel_time(origin, destination):
    directions_url = f"https://maps.googleapis.com/maps/api/directions/json?origin={origin}&destination={destination}&key={GOOGLE_MAPS_API_KEY}"
    directions_response = requests.get(directions_url)
    directions_data = directions_response.json()

    if 'routes' in directions_data and len(directions_data['routes']) > 0:
        base_duration = directions_data['routes'][0]['legs'][0]['duration']['text']
        base_duration_seconds = directions_data['routes'][0]['legs'][0]['duration']['value']
        return base_duration, base_duration_seconds
    else:
        print("No route found.")
        return None, None

# Step 5: Adjust ETA Based on Weather
def adjust_travel_time(base_duration_seconds, weather_condition, temp):
    adjustment_factor = 1  # Default (no delay)

    if "rain" in weather_condition or "storm" in weather_condition:
        adjustment_factor = 1.2  # 20% delay
    elif "snow" in weather_condition:
        adjustment_factor = 1.3  # 30% delay
    elif temp > 35:  # Very hot weather
        adjustment_factor = 1.1  # 10% delay

    adjusted_duration_seconds = int(base_duration_seconds * adjustment_factor)
    adjusted_minutes = adjusted_duration_seconds // 60
    return adjusted_minutes

# Step 6: Update Google Calendar Event Notification
def update_event_notification(event, event_time, adjusted_travel_time):
    event_datetime = datetime.fromisoformat(event_time.replace("Z", "+00:00"))  # Convert to datetime
    notification_time = event_datetime - timedelta(minutes=adjusted_travel_time)  # Calculate alarm time

    event["reminders"] = {
        "useDefault": False,
        "overrides": [{"method": "popup", "minutes": adjusted_travel_time}]
    }

    updated_event = service.events().update(calendarId="primary", eventId=event["id"], body=event).execute()

    print(f"Updated event notification: Alarm set for {notification_time.strftime('%Y-%m-%d %H:%M:%S')} UTC")


    # Store Event & Travel Data in Firebase
    travel_logs_ref.push({
        "event_name": event["summary"],
        "event_time": event_time,
        "location": event.get("location", "Unknown"),
        "weather": weather_condition,
        "temperature": temp,
        "base_travel_time": base_duration,
        "adjusted_travel_time": adjusted_travel_time,
        "notification_time": notification_time.strftime('%Y-%m-%d %H:%M:%S UTC'),
        "timestamp": datetime.now().isoformat()
    })
    print("Travel log stored in Firebase")

#   Main program
event_data = get_next_event()
if event_data:
    event, event_time, destination = event_data
    print(f"Next Event: {event['summary']} at {event_time} Location: {destination}")

    origin = get_current_location()

    if origin:
        lat, lng = origin.split(",")
        weather_condition, temp = get_weather(lat, lng)

        if weather_condition:
            print(f"Weather: {weather_condition}, Temperature: {temp}°C")

            base_duration, base_duration_seconds = get_travel_time(origin, destination)

            if base_duration:
                print(f"Base Travel Time: {base_duration}")

                adjusted_travel_time = adjust_travel_time(base_duration_seconds, weather_condition, temp)
                print(f"Adjusted Travel Time (Weather Considered): {adjusted_travel_time} minutes")

                update_event_notification(event, event_time, adjusted_travel_time)
