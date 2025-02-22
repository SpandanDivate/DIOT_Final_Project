# 🚀 CDAC ACTS, DIOT Final Project - Life Sync: Where Time Meets Intelligence  

"Life Sync is an intelligent scheduling system that seamlessly integrates with Google Calendar, real-time location tracking, weather data, and travel time estimation. By dynamically adjusting alarms based on external factors, it ensures you wake up at the perfect time, optimizing your daily routine with smart automation. No more guessing—just sync, wake, and arrive on time!"

## **Problem Statement**  
Traditional alarm clocks operate on fixed schedules and do not account for external factors like **traffic conditions** or **weather changes**. Users often have to manually adjust their alarms based on estimated travel time, which may not always be accurate. This can result in **missed appointments** or **unnecessary early departures**.  

## **Objectives of the Project**  
The **IoT Smart Alarm Clock** aims to solve these issues by integrating multiple data sources to dynamically adjust alarm times.  

### ✅ **Key Objectives:**  
- **Google Calendar Integration:** Automatically fetch upcoming events, including time and location.  
- **Real-Time Location Tracking:** Determine the user's current position using GPS or network-based location services.  
- **Weather-Based Adjustments:** Fetch weather data and modify the alarm time to compensate for delays caused by adverse conditions.  
- **Travel Time Estimation:** Use Google Maps API to calculate travel duration and adjust the alarm accordingly.  
- **User Interface:** Implement a touchscreen interface for displaying event details, current time, and alarm notifications.  
- **Data Logging:** Store event details, adjusted alarm times, and travel data in Firebase for future reference.  

---

## **🛠 Hardware Components**  
- 🖥 **Raspberry Pi 3 Model B+**  
- 📟 **3.5-inch TFT Touchscreen Display**  
- 🔔 **Active Buzzer (for alarm notifications)**  
- 🌐 **Internet Connectivity (Wi-Fi)**  

## **📌 Software & APIs Used**  
- 🐍 **Python** (Programming Language)  
- 📅 **Google Calendar API** (Event Scheduling)  
- 📍 **Google Geolocation API** (User Location)  
- 🗺 **Google Maps API** (Travel Time Estimation)  
- ☁️ **OpenWeather API** (Weather Data)  
- 🔥 **Firebase Realtime Database** (Log Storage)  
- 🎮 **Pygame** (Touchscreen UI for Raspberry Pi)  

---

## **⚙️ Working Process**  
1️⃣ **Event Retrieval:** Fetch upcoming events from **Google Calendar**, extracting event time and location.  
2️⃣ **User Location Tracking:** Determine the current location using **Google Geolocation API**.  
3️⃣ **Weather Data Fetching:** Retrieve real-time **weather conditions** using **OpenWeather API**.  
4️⃣ **Travel Time Calculation:** Estimate travel duration with **Google Maps API**.  
5️⃣ **Alarm Time Adjustment:** Dynamically modify the alarm time based on travel time, weather conditions, and additional delays.  
6️⃣ **Notification Update:** Update the adjusted alarm time as a **Google Calendar notification**.  
7️⃣ **User Interface Display:** Show event details, time, and adjusted alarm on the **Raspberry Pi touchscreen**.  
8️⃣ **Buzzer Activation:** Trigger an **alarm sound** at the adjusted time.  
9️⃣ **Data Logging:** Store event details, travel durations, and adjustments in **Firebase**.  

---

## **🔄 Flow Chart**  
![image](https://github.com/user-attachments/assets/790ff24d-3c37-4a6d-8b45-bb29d3097799)  

---

## **🏆 Conclusion**  
The **IoT Smart Alarm Clock** successfully integrates **Google Calendar, real-time location tracking, weather conditions, and travel time estimation** to create an **intelligent alarm system**. The system ensures users receive **timely notifications** for scheduled events while dynamically adjusting alarms based on **external factors** like **traffic delays** and **weather conditions**. This enhances **productivity, time management, and punctuality**.  

---

## **💡 Future Enhancements**  
- 🧠 **AI-based Smart Predictions** for better wake-up recommendations.  
- 🎙 **Voice Control** integration with **Google Assistant or Alexa**.  
- 📱 **Mobile App Support** for remote notifications.  
- 🏙 **Public Transport Integration** for smarter travel time adjustments.  
- ⏳ **Sleep Tracking** for optimizing wake-up phases.  


