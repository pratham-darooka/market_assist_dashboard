from loguru import logger
import subprocess
import sys
import os
import threading

def run_subprocess(command):
    process = subprocess.Popen(args=command)
    logger.info(f"Started subprocess {command} with PID {process.pid}")

def trigger_update_jobs():
    sys.path.append(os.path.join(os.getcwd()))

    commands = [
        ["python", "jobs/update_indices.py"],
        ["python", "jobs/update_stocks.py"],
        ["python", "jobs/update_mc.py"]
    ]

    threads = []
    for command in commands:
        thread = threading.Thread(target=run_subprocess, args=(command,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()


if __name__ == "__main__":
    trigger_update_jobs()
