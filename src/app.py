import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
import pandas as pd
import os
import csv
import time
import threading
from math import sqrt
import pyttsx3

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Eye Strain Monitoring System",
    layout="wide"
)

st.title("👁 AI-Driven Digital Eye Strain Monitoring System")

st.markdown("---")

# ============================================================
# MODEL PATH
# ============================================================

BASE_DIR = os.path.dirname(__file__)
MODEL_PATH = os.path.join(BASE_DIR, "face_landmarker.task")

if not os.path.exists(MODEL_PATH):
    st.error("face_landmarker.task not found inside src folder.")
    st.stop()

# ============================================================
# MEDIAPIPE SETUP
# ============================================================

BaseOptions = mp.tasks.BaseOptions
FaceLandmarker = mp.tasks.vision.FaceLandmarker
FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

options = FaceLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=MODEL_PATH),
    running_mode=VisionRunningMode.IMAGE,
    num_faces=1
)

landmarker = FaceLandmarker.create_from_options(options)

# ============================================================
# LANDMARKS
# ============================================================

LEFT_EYE = [33,160,158,133,153,144]
RIGHT_EYE = [362,385,387,263,373,380]

LEFT_FACE = 234
RIGHT_FACE = 454

# ============================================================
# SESSION STATE
# ============================================================

if "blink_count" not in st.session_state:
    st.session_state.blink_count = 0

if "blink_flag" not in st.session_state:
    st.session_state.blink_flag = False

if "blink_history" not in st.session_state:
    st.session_state.blink_history = []

if "time_history" not in st.session_state:
    st.session_state.time_history = []

if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()

if "last_alert_time" not in st.session_state:
    st.session_state.last_alert_time = 0

if "alert_message" not in st.session_state:
    st.session_state.alert_message = "No alert"

# ============================================================
# ALERT ENGINE
# ============================================================

engine = pyttsx3.init()
engine.setProperty("rate", 150)
engine.setProperty("volume", 1.0)
speech_lock = threading.Lock()


def speak(message):
    if not speech_lock.acquire(blocking=False):
        return

    try:
        engine.say(message)
        engine.runAndWait()
    except RuntimeError as error:
        if "run loop already started" not in str(error):
            raise
        engine.stop()
    finally:
        speech_lock.release()

# ============================================================
# EAR FUNCTION
# ============================================================

def distance(p1, p2):
    return sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

def calculate_ear(points):

    A = distance(points[1], points[5])
    B = distance(points[2], points[4])
    C = distance(points[0], points[3])

    if C == 0:
        return 0

    return (A + B) / (2 * C)

# ============================================================
# SAVE CSV
# ============================================================

CSV_FILE = os.path.join(BASE_DIR, "eye_strain_report.csv")

def save_report(blinks, ear, distance_cm, status):

    file_exists = os.path.exists(CSV_FILE)

    with open(CSV_FILE, "a", newline="", encoding="utf-8") as file:

        writer = csv.writer(file)

        if not file_exists:
            writer.writerow([
                "Time",
                "Blink Count",
                "EAR",
                "Distance(cm)",
                "Status"
            ])

        writer.writerow([
            time.strftime("%H:%M:%S"),
            blinks,
            round(ear,3),
            round(distance_cm,1),
            status
        ])

# ============================================================
# STREAMLIT PLACEHOLDERS
# ============================================================

frame_placeholder = st.empty()

metric1, metric2, metric3, metric4 = st.columns(4)

graph_placeholder = st.empty()

download_placeholder = st.empty()

st.sidebar.header("Dashboard")

status_box = st.sidebar.empty()

blink_box = st.sidebar.empty()

distance_box = st.sidebar.empty()

ear_box = st.sidebar.empty()

time_box = st.sidebar.empty()

alert_box = st.sidebar.empty()

# ============================================================
# CSV DOWNLOAD BUTTON
# ============================================================

if os.path.exists(CSV_FILE):
    with open(CSV_FILE, "rb") as file:
        download_button = st.sidebar.download_button(
            label="Download CSV Report",
            data=file,
            file_name="eye_strain_report.csv",
            mime="text/csv"
        )

# ============================================================
# CAMERA
# ============================================================

run = st.button("▶ Start Camera")

if run:

    cap = cv2.VideoCapture(0)

    while cap.isOpened():

        ret, frame = cap.read()

        if not ret:
            st.error("Unable to access webcam.")
            break

        frame = cv2.flip(frame, 1)

        h, w, _ = frame.shape

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb
        )

        result = landmarker.detect(mp_image)

        status = "No Face"

        ear_value = 0

        distance_cm = 0

        alert_message = ""

        elapsed = int(time.time() - st.session_state.start_time)

        if result.face_landmarks:

            status = "Normal"

            face = result.face_landmarks[0]

            # ------------------------------------------------
            # Draw all landmarks
            # ------------------------------------------------

            for lm in face:

                x = int(lm.x * w)
                y = int(lm.y * h)

                cv2.circle(frame,(x,y),1,(0,255,0),-1)

            # ------------------------------------------------
            # Eye landmarks
            # ------------------------------------------------

            left_eye = [(face[i].x*w, face[i].y*h) for i in LEFT_EYE]
            right_eye = [(face[i].x*w, face[i].y*h) for i in RIGHT_EYE]

            left_ear = calculate_ear(left_eye)
            right_ear = calculate_ear(right_eye)

            ear_value = (left_ear + right_ear) / 2

            # ------------------------------------------------
            # Blink Detection
            # ------------------------------------------------

            if ear_value < 0.20:

                st.session_state.blink_flag = True

            else:

                if st.session_state.blink_flag:

                    st.session_state.blink_count += 1

                    st.session_state.blink_flag = False

            # ------------------------------------------------
            # Distance Estimation
            # ------------------------------------------------

            left_face = face[LEFT_FACE]
            right_face = face[RIGHT_FACE]

            face_width = abs(
                (right_face.x*w) -
                (left_face.x*w)
            )

            if face_width > 0:

                distance_cm = (14 * 650) / face_width

            # ------------------------------------------------
            # Head Position
            # ------------------------------------------------

            nose = face[1]

            nose_x = nose.x

            if nose_x < 0.40:

                status = "Looking Left"

            elif nose_x > 0.60:

                status = "Looking Right"

            else:

                status = "Looking Center"

            # ------------------------------------------------
            # Eye Strain Alerts
            # ------------------------------------------------

            if distance_cm < 40:

                status = "Too Close"
                alert_message = "Move away from the screen."

            if ear_value < 0.18:

                status = "Eye Strain"
                alert_message = "Blink more frequently and rest your eyes."

            if elapsed > 20*60:

                status = "Take Break"
                alert_message = "Take a break and follow the 20-20-20 rule."

            if alert_message:
                st.session_state.alert_message = alert_message

                if time.time() - st.session_state.last_alert_time > 5:
                    speak(alert_message)
                    st.session_state.last_alert_time = time.time()

            # ------------------------------------------------
            # Save Graph Data
            # ------------------------------------------------

            st.session_state.blink_history.append(
                st.session_state.blink_count
            )

            st.session_state.time_history.append(
                elapsed
            )

            # ------------------------------------------------
            # Save CSV Every 5 Seconds
            # ------------------------------------------------

            if elapsed % 5 == 0:

                save_report(
                    st.session_state.blink_count,
                    ear_value,
                    distance_cm,
                    status
                )

        # ------------------------------------------------
        # Draw Information
        # ------------------------------------------------

        cv2.putText(
            frame,
            f"Blinks : {st.session_state.blink_count}",
            (20,40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0,255,0),
            2
        )

        cv2.putText(
            frame,
            f"EAR : {ear_value:.2f}",
            (20,75),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255,255,0),
            2
        )

        cv2.putText(
            frame,
            f"Distance : {distance_cm:.1f} cm",
            (20,110),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255,255,255),
            2
        )

        cv2.putText(
            frame,
            f"Status : {status}",
            (20,145),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0,0,255),
            2
        )

        # ------------------------------------------------
        # Streamlit Image
        # ------------------------------------------------

        frame_placeholder.image(
            cv2.cvtColor(frame,cv2.COLOR_BGR2RGB),
            channels="RGB"
        )

        # ------------------------------------------------
        # Sidebar
        # ------------------------------------------------

        blink_box.metric(
            "Blink Count",
            st.session_state.blink_count
        )

        ear_box.metric(
            "EAR",
            round(ear_value,3)
        )

        distance_box.metric(
            "Distance",
            f"{distance_cm:.1f} cm"
        )

        time_box.metric(
            "Screen Time",
            f"{elapsed} sec"
        )

        status_box.success(status)
        alert_box.warning(st.session_state.alert_message)

    cap.release()

