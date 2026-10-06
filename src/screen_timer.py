import time


def get_elapsed_seconds(start_time):
    return int(time.time() - start_time)


def format_elapsed(elapsed_seconds):
    hours = elapsed_seconds // 3600
    minutes = (elapsed_seconds % 3600) // 60
    seconds = elapsed_seconds % 60
    return f"{hours:02}:{minutes:02}:{seconds:02}"


def should_take_break(elapsed_seconds, threshold_minutes=20):
    return elapsed_seconds >= threshold_minutes * 60