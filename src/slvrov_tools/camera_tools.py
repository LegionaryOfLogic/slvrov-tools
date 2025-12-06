# SLVROV Dec 2025

import cv2  # type: ignore
import subprocess
from .misc_tools import get_os
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


def gst_install() -> None:
    if get_os() == "Darwin":
        print("Installing gstreamer on MacOS using homebrew...")

        command = ["brew", 
             "install", 
             "gstreamer"]
        
    else:
        print("Installing gstreamer on Linux using sudo apt install...")

        command = ["sudo", 
             "apt", 
             "install", 
             "gstreamer1.0-tools", 
             "gstreamer1.0-plugins-base", 
             "gstreamer1.0-plugins-good", 
             "gstreamer1.0-plugins-bad", 
             "gstreamer1.0-plugins-ugly", 
             "gstreamer1.0-libav", 
             "v4l-utils"]
        
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as error:
        print(f"Error running install command: {error}")
        

def gst_stream(ip: str, port: int, device: int, wxh: str, framerate: str) -> None:
    width, height = wxh.split('x')

    if get_os() == "Darwin": 
        print(f"Streaming on MacOs to {ip} at port {port}...")

        command = ["gst-launch-1.0", 
             "avfvideosrc", 
             f"device-index={device}", 
             "!", "video/x-raw,", 
             f"width={width},", 
             f"height={height},", 
             f"framerate={framerate}", 
             "!", "jpegenc", 
             "!", 
             "rtpjpegpay", 
             "!", 
             "udpsink", 
             f"host={ip}", 
             f"port={port}", 
             "sync=false"]

    else:
        print(f"Streaming on Linux to {ip} at port {port}...")

        command = ["gst-launch-1.0",          
            "v4l2src", 
            f"device=/dev/video{device}", 
            "!", 
            f"image/jpeg,width={wxh.width},height={wxh.height},framerate={framerate}", 
            "!", 
            "rtpjpegpay", 
            "!", 
            "udpsink", 
            f"host={ip}", 
            f"port={port}"
            "sync=false"]
        
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as error:
        print(f"Error running stream command: {error}")


def gst_recieve(port: int):
    if get_os() == "Darwin":
        print(f"MacOS recieving stream on port {port}...")

        command = ['gst-launch-1.0', 
             'udpsrc', 
             f'port={port}', 
             'caps="application/x-rtp,media=video,encoding-name=JPEG,payload=26"', 
             '!', 
             'rtpjpegdepay', 
             '!', 
             'jpegdec', 
             '!', 
             'autovideosink', 
             'sync=false']

    else:
        print(f"Linux recieving stream on port {port}...")

        command = ["gst-launch-1.0", 
             "udpsrc", 
             "port={port}", 
             "caps='application/x-rtp, encoding-name=JPEG, payload=26'", 
             "rtpjpegdepay", 
             "!", 
             "jpegdec", 
             "!", 
             "autovideosink", 
             "sync=false"]
        
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as error:
        print(f"Error running recieve command: {error}")