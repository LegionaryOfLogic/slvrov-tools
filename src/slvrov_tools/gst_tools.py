# SLVROV Dec 2025

from .misc_tools import get_os, safe_run


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
        
    safe_run(command, "Error running install command")
        

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
            f"image/jpeg,width={width},height={height},framerate={framerate}", 
            "!", 
            "rtpjpegpay", 
            "!", 
            "udpsink", 
            f"host={ip}", 
            f"port={port}",
            "sync=false"]
        
    safe_run(command, "Error running stream command")


def gst_recieve(port: int):
    if get_os() == "Darwin":
        print(f"MacOS recieving stream on port {port}...")

        command = ['gst-launch-1.0', 
             'udpsrc', 
             f'port={port}', 
             'caps=application/x-rtp,media=video,encoding-name=JPEG,payload=26', 
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
                   f"port={port}",
                   "caps=application/x-rtp,encoding-name=JPEG,payload=26",
                   "!",
                   "rtpjpegdepay",
                   "!",
                   "jpegdec",
                   "!",
                   "autovideosink",
                   "sync=false"
]
        
    safe_run(command, "Error running recieve command")