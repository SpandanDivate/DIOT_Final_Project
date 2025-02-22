# Add your "token.json" and "credential.json" in current directory to run this program. 
import pygame
import time
import threading
import requests
import RPi.GPIO as GPIO
from datetime import datetime, timezone, timedelta
from dateutil import parser
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import firebase_admin
from firebase_admin import credentials, db
import os

last_logged_event = None
buzzer_dismissed = False

# Firebase Initialization
FIREBASE_KEY_PATH = "firebase-key.json"
if not os.path.exists(FIREBASE_KEY_PATH):
    raise FileNotFoundError(f"Firebase key file '{FIREBASE_KEY_PATH}' not found!")

cred = credentials.Certificate(FIREBASE_KEY_PATH)
firebase_admin.initialize_app(cred, {"databaseURL": "https://iotsmartalarm-default-rtdb.firebaseio.com/"})
logs_ref = db.reference("alarm_logs")

# Google API Setup
TOKEN_PATH = "token.json"
SCOPES = ["https://www.googleapis.com/auth/calendar"]

if not os.path.exists(TOKEN_PATH):
    raise FileNotFoundError(f"Google API token file '{TOKEN_PATH}' not found!")

creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
service = build("calendar", "v3", credentials=creds)

# Pygame Setup
SCREEN_WIDTH, SCREEN_HEIGHT = 480, 320
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("IoT Smart Alarm Clock")

background = pygame.image.load("sky_background.jpeg")
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))

WHITE, BLACK, RED, BLUE, PURPLE, MAROON = (255, 255, 255), (0, 0, 0), (200, 0, 0), (0, 0, 255), (128, 0, 128), (128, 0, 0)
clock_font, event_font, button_font = pygame.font.Font(None, 80), pygame.font.Font(None, 30), pygame.font.Font(None, 40)

button_w, button_h = 160, 50
corner_radius = 20

# Buzzer Setup
BUZZER_PIN = 16
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

button_x, button_y, button_w, button_h = 150, 220, 180, 60

buzzer_active = False
buzzer_thread = None

# Function to fetch next event and alarm time
def get_next_event():
    global last_logged_event, buzzer_dismissed
    try:
        now = datetime.now(timezone.utc).isoformat()
        events_result = service.events().list(
            calendarId="primary", timeMin=now, maxResults=1, singleEvents=True, orderBy="startTime"
        ).execute()

        events = events_result.get("items", [])
        if not events:
            return "No upcoming events", None, None

        event = events[0]
        event_id, event_name = event["id"], event["summary"]
        event_start_str = event["start"].get("dateTime", event["start"].get("date"))
        event_end_str = event["end"].get("dateTime", event["end"].get("date"))

        event_start = parser.parse(event_start_str).strftime("%Y-%m-%d %H:%M")
        event_end = parser.parse(event_end_str).strftime("%H:%M")
        event_time = f"{event_start} - {event_end}"

        notification_minutes = event.get("reminders", {}).get("overrides", [{"minutes": 10}])[0]["minutes"]
        adjusted_alarm_time = parser.parse(event_start_str) - timedelta(minutes=notification_minutes)
        adjusted_alarm_str = adjusted_alarm_time.strftime("%Y-%m-%d %H:%M")

        # Reset dismiss flag if it's a new event
        if last_logged_event != event_id:
            buzzer_dismissed = False  # Reset flag when a new event is scheduled
            logs_ref.push({
                "event_id": event_id, "event_name": event_name, "event_time": event_time,
                "adjusted_alarm_time": adjusted_alarm_str, "status": "Scheduled",
                "timestamp": datetime.now().isoformat()
            })
            last_logged_event = event_id

        return event_name, event_time, adjusted_alarm_str

    except Exception as e:
        print(f"Error fetching event: {e}")
        return None, None, None

# Function to check if alarm should trigger
def check_alarm(adjusted_alarm_time):
    global buzzer_dismissed
    if adjusted_alarm_time is None or buzzer_dismissed:
        return False  # Prevent re-trigger after dismissal

    try:
        alarm_datetime = datetime.strptime(adjusted_alarm_time, "%Y-%m-%d %H:%M")
        return datetime.now() >= alarm_datetime
    except ValueError:
        return False

# Buzzer control (Threaded)
def buzzer_loop():
    global buzzer_active
    print("🔔 Alarm Ringing!")
    while buzzer_active:
        GPIO.output(BUZZER_PIN, GPIO.HIGH)
        time.sleep(0.5)
        GPIO.output(BUZZER_PIN, GPIO.LOW)
        time.sleep(0.5)

def trigger_buzzer():
    global buzzer_active, buzzer_thread, last_logged_event, buzzer_dismissed
    if not buzzer_active and not buzzer_dismissed:  # Prevent re-triggering after dismissal
        buzzer_active = True
        buzzer_thread = threading.Thread(target=buzzer_loop, daemon=True)
        buzzer_thread.start()

        logs_ref.push({
            "event_id": last_logged_event,
            "status": "Alarm Triggered",
            "timestamp": datetime.now().isoformat()
        })

def stop_buzzer():
    global buzzer_active, last_logged_event, buzzer_dismissed
    buzzer_active = False
    buzzer_dismissed = True  # Mark as dismissed to prevent retriggering
    GPIO.output(BUZZER_PIN, GPIO.LOW)

    logs_ref.push({
        "event_id": last_logged_event,
        "status": "Alarm Dismissed",
        "timestamp": datetime.now().isoformat()
    })
    print("❌ Alarm Dismissed!")

# UI Drawing
def draw_rounded_rect(surface, color, x, y, w, h, r):
    pygame.draw.rect(surface, color, (x + r, y, w - 2 * r, h))
    pygame.draw.rect(surface, color, (x, y + r, w, h - 2 * r))
    pygame.draw.circle(surface, color, (x + r, y + r), r)
    pygame.draw.circle(surface, color, (x + w - r, y + r), r)
    pygame.draw.circle(surface, color, (x + r, y + h - r), r)
    pygame.draw.circle(surface, color, (x + w - r, y + h - r), r)

# Main Loop
try:
    running = True
    while running:	
        screen.fill(BLACK)
        screen.blit(background, (0, 0))

        current_time = time.strftime("%H:%M:%S", time.localtime())
        event_name, event_time, adjusted_alarm_time = get_next_event()
        clock_surface = clock_font.render(current_time, True, WHITE)
        clock_rect = clock_surface.get_rect(center=(SCREEN_WIDTH // 2, 40))
        text_x = 50
        event_name_surface = event_font.render(f"Next Event: {event_name}", True, PURPLE)
        event_name_rect = event_name_surface.get_rect(topleft=(text_x, 90))
        event_surface = event_font.render(f"Meeting Time: {event_time}", True, MAROON)
        event_rect = event_surface.get_rect(topleft=(text_x, 120))
        alarm_surface = event_font.render(f"Alarm Time: {adjusted_alarm_time}", True, BLUE)
        alarm_rect = alarm_surface.get_rect(topleft=(text_x, 150))
        button_x = (SCREEN_WIDTH - button_w) // 2
        button_y = 190
        screen.blit(clock_surface, clock_rect.topleft)
        screen.blit(event_name_surface, event_name_rect.topleft)
        screen.blit(event_surface, event_rect.topleft)
        screen.blit(alarm_surface, alarm_rect.topleft)
        draw_rounded_rect(screen, RED, button_x, button_y, button_w, button_h, corner_radius)
        button_text = button_font.render("Dismiss", True, WHITE)
        button_text_rect = button_text.get_rect(center=(SCREEN_WIDTH // 2, button_y + button_h // 2))
        screen.blit(button_text, button_text_rect.topleft)

        pygame.display.flip()

        if check_alarm(adjusted_alarm_time):
            trigger_buzzer()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button_x < event.pos[0] < button_x + button_w and button_y < event.pos[1] < button_y + button_h:
                    stop_buzzer()

        time.sleep(1)

finally:
    GPIO.cleanup()
    pygame.quit()
