from pathlib import Path

import cv2
import mediapipe as mp


def create_landmarker(model_path="face_landmarker.task"):
    base_dir = Path(__file__).resolve().parent
    model_path = Path(model_path)
    if not model_path.is_absolute():
        model_path = base_dir / model_path

    BaseOptions = mp.tasks.BaseOptions
    FaceLandmarker = mp.tasks.vision.FaceLandmarker
    FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
    VisionRunningMode = mp.tasks.vision.RunningMode

    options = FaceLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=str(model_path)),
        running_mode=VisionRunningMode.IMAGE,
        num_faces=1,
    )

    return FaceLandmarker.create_from_options(options)


def detect_face(frame, landmarker):
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
    result = landmarker.detect(mp_image)
    return result, frame.shape[:2]