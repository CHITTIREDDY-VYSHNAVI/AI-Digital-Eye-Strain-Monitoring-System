KNOWN_FACE_WIDTH = 14.0
FOCAL_LENGTH = 650.0


def estimate_distance(face, w, h, known_face_width=KNOWN_FACE_WIDTH, focal_length=FOCAL_LENGTH):
    left = face[234]
    right = face[454]

    face_width = abs((right.x * w) - (left.x * w))
    if face_width <= 0:
        return 0.0

    return (known_face_width * focal_length) / face_width