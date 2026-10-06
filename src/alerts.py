import time

import pyttsx3


class AlertManager:
    def __init__(self, rate=150, volume=1.0):
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", rate)
        self.engine.setProperty("volume", volume)
        self.last_blink_alert = 0
        self.last_distance_alert = 0
        self.last_break_alert = 0

    def speak(self, message):
        self.engine.say(message)
        self.engine.runAndWait()

    def maybe_alert(self, status, distance_cm, elapsed_seconds, last_alert_time, delay=10):
        current_time = time.time()
        if current_time - last_alert_time <= delay:
            return last_alert_time

        if status == "HIGH STRAIN":
            self.speak("Warning! High eye strain detected.")
        elif distance_cm < 45:
            self.speak("Please move away from the screen.")
        elif elapsed_seconds >= 20 * 60:
            self.speak("Please take a break and follow the 20-20-20 rule.")

        return current_time