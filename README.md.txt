# AI-Driven Digital Eye Strain Monitoring System

## Overview

The AI-Driven Digital Eye Strain Monitoring System is a real-time computer vision-based application designed to monitor factors associated with digital eye strain during prolonged screen usage.

The system uses a webcam to analyze facial landmarks, blinking behavior, head posture, viewing distance, and screen usage duration. It provides real-time alerts and recommendations to encourage healthier screen usage.

## Features

- Real-time webcam monitoring
- Facial landmark detection
- Eye blink detection using Eye Aspect Ratio (EAR)
- Blink count monitoring
- Head pose and face direction estimation
- Viewing distance estimation
- Screen usage time monitoring
- Real-time eye strain alerts
- 20-20-20 break reminders
- Voice alerts
- CSV-based monitoring reports
- Streamlit dashboard
- Blink trend visualization

## Technologies Used

- Python
- OpenCV
- MediaPipe
- NumPy
- Pandas
- Streamlit
- pyttsx3
- CSV

## System Workflow

```text
Webcam Input
     ↓
Frame Capture
     ↓
Face & Facial Landmark Detection
     ↓
Blink Detection / EAR Calculation
     ↓
Head Pose Estimation
     ↓
Viewing Distance Estimation
     ↓
Screen Time Monitoring
     ↓
Eye Strain Analysis
     ↓
Real-Time Alerts
     ↓
CSV Report & Streamlit Dashboard