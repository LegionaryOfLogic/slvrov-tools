# SLVROV Jan 2025

import cv2
import pathlib
import time


def cv2_cam(camera_index: int=0) -> cv2.VideoCapture:
    cam = cv2.VideoCapture(camera_index)
    if not cam.isOpened(): raise Exception("Camera not opened")

    return cam


def warm_up_camera(cv2_capture: cv2.VideoCapture, count: int = 5, wait: int=0.1) -> None:
    for _ in range(count):
        ret, frame = cv2_capture.read()
        if not ret: print("Warning: Could not read frame during warmup.")
        time.sleep(wait)


def save_pictures(cv2_capture: cv2.VideoCapture, path: pathlib.PosixPath | str=pathlib.Path("images/img"), count: int=1) -> None:
    """Capture and save a specified number of images from a VideoCapture source.

    Args:
        cv2_capture (cv2.VideoCapture): 
            An active OpenCV video capture object from which frames will be read.
        path (Path | str, optional): 
            Base file path (without index or extension) where images will be saved.
            For example, Path("images/img") will generate files like img1.jpg, img2.jpg, etc.
            The parent directory is created if it does not already exist.
        count (int, optional): 
            Number of images to capture and save. Defaults to 1.

    Raises:
        Exception: If 'path' argument type is invalid
        Exception: If a frame cannot be captured from the video source.

    Code adapted from Tommy Fydrich
    """

    if type(path) == str: path = pathlib.Path(path)

    directory = path.parent
    directory.mkdir(parents=True, exist_ok=True)

    for i in range(count):
        imgpath = path.with_name(f"{path.name}{i + 1}.jpg")
        ret, frame = cv2_capture.read()

        if not ret: raise Exception(f"Error capturing frame {i + 1}")
        cv2.imwrite(str(imgpath), frame)