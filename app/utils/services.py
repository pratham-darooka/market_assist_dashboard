from loguru import logger
import subprocess
import sys
import os

def trigger_update_jobs():
    sys.path.append(os.path.join(os.getcwd()))

    p1 = subprocess.Popen(args=["python", "jobs/update_stocks.py"])
    logger.info(f"triggered stock update services {p1.communicate()}")
    p2 = subprocess.Popen(args=["python", "jobs/update_indices.py"])
    logger.info(f"triggered index update services {p2.communicate()}")
    p3 = subprocess.Popen(args=["python", "jobs/update_mc.py"])
    logger.info(f"triggered mc update services {p3.communicate()}")


if __name__ == "__main__":
    trigger_update_jobs()
