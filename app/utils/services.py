from loguru import logger
import subprocess
import os
import threading
import sys
import psutil

def is_process_running(script_name):
    """Check if there is any running process that contains the given script name."""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info['cmdline']
            if cmdline and script_name in cmdline:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

def run_subprocess(command):
    process = subprocess.Popen(args=command)
    logger.info(f"Started subprocess {command} with PID {process.pid}")

def trigger_update_jobs():
    if os.getcwd() not in sys.path:
        logger.info(f'Updated sys.path to: {sys.path}')
        sys.path.append(os.getcwd())

    pwd = os.path.join(os.getcwd())
    env = os.environ.copy()

    os.environ['PYTHONPATH'] = pwd if 'PYTHONPATH' not in env else f"{env['PYTHONPATH']}:{pwd}"
    logger.info(f"PYTHONPATH: {os.environ.get('PYTHONPATH')}")

    commands = [
        ["python", "jobs/update_indices.py"],
        ["python", "jobs/update_stocks.py"],
        ["python", "jobs/update_mc.py"]
    ]

    threads = []
    for command in commands:
        script_name = command[-1]  # Extract the script name from the command list
        if not is_process_running(script_name):
            thread = threading.Thread(target=run_subprocess, args=(command,))
            thread.start()
            threads.append(thread)
        else:
            logger.warning(f"Process {script_name} is already running. Skipping.")

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    trigger_update_jobs()