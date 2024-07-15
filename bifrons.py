
import os
import subprocess
import sys
import logging

debug = True
SCRIPTS_DIR = "scripts"

if not os.path.exists("log"):
    os.makedirs("log")
logging.basicConfig(filename='log/bifrons.log', level=logging.INFO, format='%(asctime)s - %(message)s')

def create_new_script(directory, command):
    if not os.path.exists(directory):
        os.makedirs(directory)
    script_path = os.path.join(directory, "script.sh")
    with open(script_path, 'w') as f:
        f.write(f"#!/bin/bash\n{command}\n")
    os.chmod(script_path, 0o755)
    if debug:
        logging.info(f"Created script at {script_path} with command: {command}")
    run_script(directory)

def run_script(directory):
    script_path = os.path.join(directory, "script.sh")
    log_path = os.path.join(directory, "output.log")
    
    if not os.path.exists(script_path):
        logging.error(f"Script {script_path} does not exist.")
        return

    prev_log_path = os.path.join(directory, "prev_output.log")
    current_log_path = os.path.join(directory, "current_output.log")

    with open(current_log_path, 'w') as current_log_file:
        process = subprocess.Popen(script_path, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        for stdout_line in iter(process.stdout.readline, ""):
            line = f"STDOUT: {stdout_line}"
            current_log_file.write(line)
            print(line, end="")
        for stderr_line in iter(process.stderr.readline, ""):
            line = f"STDERR: {stderr_line}"
            current_log_file.write(line)
            print(line, end="")
        process.stdout.close()
        process.stderr.close()
        process.wait()

    if debug:
        logging.info(f"Ran script at {script_path}")

    check_output_changes(directory, current_log_path, prev_log_path)

def check_output_changes(directory, current_log_path, prev_log_path):
    prev_log = ""
    if os.path.exists(prev_log_path):
        with open(prev_log_path, 'r') as f:
            prev_log = f.read().strip()

    with open(current_log_path, 'r') as f:
        current_log = f.read().strip()

    if current_log != prev_log:
        logging.info(f"Output changed for script in {directory}")
        os.replace(current_log_path, prev_log_path)
    else:
        os.remove(current_log_path)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: your_script new <directory> <command> | your_script run <directory>")
        sys.exit(1)

    if not os.path.exists(SCRIPTS_DIR):
        os.makedirs(SCRIPTS_DIR)

    action = sys.argv[1]
    directory = os.path.join(SCRIPTS_DIR, sys.argv[2])

    if action == "new":
        if len(sys.argv) < 4:
            print("Usage: your_script new <directory> <command>")
            sys.exit(1)
        command = ' '.join(sys.argv[3:])
        create_new_script(directory, command)
    elif action == "run":
        run_script(directory)
    else:
        print("Invalid action. Use 'new' to create a new script or 'run' to execute an existing script.")
        sys.exit(1)

