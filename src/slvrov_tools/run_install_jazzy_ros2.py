from pathlib import Path
from .misc_tools import safe_run


def main():
    script = Path(__file__).parent / "install_ros2_jazzy.bash"
    
    run_bash_script = ["sudo", "bash", str(script)]
    safe_run(run_bash_script, f"Problem running {script}")


if __name__ == "__main__":
    main()
