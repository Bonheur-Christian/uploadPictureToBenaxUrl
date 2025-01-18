import os
import time
import subprocess
import shutil
import json

# Configuration
WATCH_FOLDER = r"D:\PC\Pictures\Camera Roll"  # Folder to watch for new pictures
UPLOADED_FOLDER = os.path.join(WATCH_FOLDER, "uploaded")  # Folder for successfully uploaded pictures
UPLOAD_URL = "https://projects.benax.rw/f/o/r/e/a/c/h/p/r/o/j/e/c/t/s/4e8d42b606f70fa9d39741a93ed0356c/iot_testing_202501/upload.php"  # Server upload URL

# Ensure the uploaded folder exists
os.makedirs(UPLOADED_FOLDER, exist_ok=True)

def upload_file(file_path):
   
    try:
        # Curl command for file upload
        command = [
            "curl",
            "-X", "POST",
            "-F", f"file=@{file_path}",
            UPLOAD_URL
        ]
        # Execute the curl command and capture the output
        result = subprocess.run(command, capture_output=True, text=True)

        print(f"Raw response for {file_path}: {result.stdout.strip()}")

        # Check curl execution success
        if result.returncode != 0:
            print(f"Error uploading {file_path}: {result.stderr.strip()}")
            return False

        # Parse the server response
        try:
            response = json.loads(result.stdout.strip())
            if response.get("message") == "File uploaded successfully!":
                print(f"Upload successful: {file_path}")
                return True
            else:
                print(f"Failed to upload {file_path}. Server response: {response}")
        except json.JSONDecodeError:
            print(f"Invalid JSON response from server for {file_path}: {result.stdout.strip()}")
    except Exception as e:
        print(f"Exception during upload of {file_path}: {e}")
    return False

def monitor_and_upload():
    #Monitors a folder for new pictures, uploads them to the server, and moves them to the uploaded folder.
    print(f"Starting monitoring for folder: {WATCH_FOLDER}")
    uploaded_files = set()  # Track uploaded files to avoid duplicate uploads

    while True:
        try:
            # List files in the watch folder
            files = [
                f for f in os.listdir(WATCH_FOLDER)
                if os.path.isfile(os.path.join(WATCH_FOLDER, f)) and f not in uploaded_files
            ]

            for file_name in files:
                file_path = os.path.join(WATCH_FOLDER, file_name)
                print(f"Detected new file: {file_path}")

                # Attempt to upload the file
                if upload_file(file_path):
                    # Move file to the uploaded folder on success
                    new_path = os.path.join(UPLOADED_FOLDER, file_name)
                    shutil.move(file_path, new_path)
                    print(f"Moved file to uploaded folder: {new_path}")

                    # Add to uploaded files set
                    uploaded_files.add(file_name)

            # Wait before next iteration
            time.sleep(30)
        except Exception as e:
            print(f"Error during monitoring: {e}")
            time.sleep(30)  # Continue after a brief pause on error

if __name__ == "__main__":
    monitor_and_upload()
