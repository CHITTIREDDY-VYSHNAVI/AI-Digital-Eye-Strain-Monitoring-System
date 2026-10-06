def eye_aspect_ratio(eye):
    A = ((eye[1][0] - eye[5][0]) ** 2 + (eye[1][1] - eye[5][1]) ** 2) ** 0.5
    B = ((eye[2][0] - eye[4][0]) ** 2 + (eye[2][1] - eye[4][1]) ** 2) ** 0.5
    C = ((eye[0][0] - eye[3][0]) ** 2 + (eye[0][1] - eye[3][1]) ** 2) ** 0.5
    return (A + B) / (2.0 * C)


def get_ear(face, w, h):
    left_eye = [(face[i].x * w, face[i].y * h) for i in [33, 160, 158, 133, 153, 144]]
    right_eye = [(face[i].x * w, face[i].y * h) for i in [362, 385, 387, 263, 373, 380]]
    return (eye_aspect_ratio(left_eye) + eye_aspect_ratio(right_eye)) / 2.0, left_eye, right_eye


def update_blink_counter(ear_value, blink_flag):
    if ear_value < 0.20:
        return True, 0
    if blink_flag:
        return False, 1
    return False, 0