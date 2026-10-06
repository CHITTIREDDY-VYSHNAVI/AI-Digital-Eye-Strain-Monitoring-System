def get_head_pose(face, w, h):
    nose = face[1]
    left = face[234]
    right = face[454]
    forehead = face[10]
    chin = face[152]

    nose_x = nose.x * w
    nose_y = nose.y * h

    face_center_x = ((left.x * w) + (right.x * w)) / 2
    face_center_y = ((forehead.y * h) + (chin.y * h)) / 2

    dx = nose_x - face_center_x
    dy = nose_y - face_center_y

    if dx > 20:
        direction = "RIGHT"
    elif dx < -20:
        direction = "LEFT"
    elif dy > 25:
        direction = "DOWN"
    elif dy < -25:
        direction = "UP"
    else:
        direction = "STRAIGHT"

    return direction, dx, dy