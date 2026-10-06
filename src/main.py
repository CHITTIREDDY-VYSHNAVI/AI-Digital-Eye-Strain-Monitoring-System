import time

import cv2

from alerts import AlertManager
from blink_detection import get_ear, update_blink_counter
from distance_estimation import estimate_distance
from face_detection import create_landmarker, detect_face
from head_pose import get_head_pose
from screen_timer import format_elapsed, get_elapsed_seconds, should_take_break
from utils import save_log


LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]


def main():
    landmarker = create_landmarker("face_landmarker.task")
    alert_manager = AlertManager()
    cap = cv2.VideoCapture(0)

    blink_count = 0
    blink_flag = False
    start_time = time.time()
    last_alert_time = 0
    last_log_time = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        result, (h, w) = detect_face(frame, landmarker)

        status = "Analyzing..."
        eye_ear = 0.0
        distance_cm = 0.0
        pose = "STRAIGHT"

        if result.face_landmarks:
            face = result.face_landmarks[0]

            eye_ear, left_eye, right_eye = get_ear(face, w, h)
            blink_flag, blink_increment = update_blink_counter(eye_ear, blink_flag)
            blink_count += blink_increment

            pose, dx, dy = get_head_pose(face, w, h)
            distance_cm = estimate_distance(face, w, h)
            elapsed_seconds = get_elapsed_seconds(start_time)

            if eye_ear < 0.18:
                status = "HIGH STRAIN"
            elif distance_cm < 45:
                status = "MOVE AWAY"
            elif should_take_break(elapsed_seconds, threshold_minutes=20):
                status = "TAKE BREAK"
            else:
                status = "NORMAL"

            if time.time() - last_alert_time > 10:
                last_alert_time = alert_manager.maybe_alert(
                    status=status,
                    distance_cm=distance_cm,
                    elapsed_seconds=elapsed_seconds,
                    last_alert_time=last_alert_time,
                )

            current_time = time.time()
            if current_time - last_log_time > 2:
                save_log(blink_count, distance_cm, eye_ear, status)
                last_log_time = current_time

            cv2.putText(frame, f"Blink: {blink_count}", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"EAR: {eye_ear:.2f}", (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            cv2.putText(frame, f"Distance: {distance_cm:.1f} cm", (30, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, f"Pose: {pose}", (30, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)
            cv2.putText(frame, f"Status: {status}", (30, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            cv2.putText(frame, f"Screen Time: {format_elapsed(elapsed_seconds)}", (30, 220), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        cv2.imshow("AI Eye Strain System", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()