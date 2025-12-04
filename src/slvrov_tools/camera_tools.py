# SLVROV Dec 2025

import cv2  # type: ignore
from pathlib import Path  


def save_pictures(cv2_capture: cv2.VideoCapture, path: Path | str=Path("images/img"), count: int=1) -> None:
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

    if type(path) == str and type(path) != Path: path = Path(path)
    else: raise Exception(f"Argument 'path' must be of type Path or str, not {type(path)}")

    directory = path.parent
    directory.mkdir(parents=True, exist_ok=True)

    for i in range(count):
        imgpath = path.with_name(f"{path.name}{i + 1}.jpg")
        ret, frame = cv2_capture.read()

        if not ret: raise Exception(f"Error capturing frame {i + 1}")
        cv2.imwrite(str(imgpath), frame)