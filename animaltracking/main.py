import argparse
import getpass
from tqdm import tqdm
import requests
import zipfile
import math
import os


# Global vars
detections = []
events = []
receivers = []
counter = 0


def parse_receiver(csv_model, csv_serial):
    model_split = csv_model.split("-")
    return f"{model_split[0] if any(char.isdigit() for char in model_split[1]) else csv_model}-{csv_serial}"


def parse_csv(file):
    global detections, events
    detection_csv_ids = ["DET"]
    lines = file.split("\n")
    for line in lines:
        l = line.split(",")
        if len(l) < 6:
            continue
        if l[0] in detection_csv_ids:
            record = {
                "timestamp": f"{l[1]}.000" if "." not in l[1] else l[1],
                "timestamp_corrected": f"{l[2]}.000" if "." not in l[2] else l[2],
                "receiverName": parse_receiver(l[5], l[6]),
                "transmitterId": l[8]
            }
            detections.append(record)
        elif "DIAG" in l[0] and "_DESC" not in l[0]:
            record = {
                "eventDetail": line
            }
            events.append(record)


def extract_csv_from_zip(zip_file):
    with zipfile.ZipFile(zip_file, 'r') as archive:
        for entry in archive.infolist():
            if entry.filename.endswith('.csv'):
                global counter
                counter += 1
                with archive.open(entry.filename) as csv_file:
                    parse_csv(csv_file.read().decode('utf-8'))


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', help='Path to file', required=True)
    parser.add_argument('-H', '--host', help='Hostname', required=True)
    args = parser.parse_args()
    host = args.host
    if host == "localhost":
        port = 5000
        protocol = "http"
    else:
        port = 443
        protocol = "https"

    print("+------------------------------+")
    print("+  AODN Fathom Zip Upload Tool +")
    print("+------------------------------+")

    if os.path.basename(args.file).endswith('.zip'):
        print("\n==========Authenticating========")
        username = input("Enter your username: ")
        password = getpass.getpass(prompt="Enter your password: ")

        url = f"{protocol}://{host}:{port}/api/auth/signin"
        payload = {
            "username": username,
            "password": password
        }
        response = requests.post(url, json=payload)

        if response.status_code == 200:
            print("Successful login!")

            print("\n==========Loading===============")
            extract_csv_from_zip(args.file)
            print("File:", os.path.basename(args.file))
            print("Total CSV files:", counter)
            print("Total detections:", len(detections))
            print("Total events:", len(events))
            receivers = list(set(record['receiverName'] for record in detections))
            print("Total receivers:", len(receivers))

            # Begin upload
            begin_body = {
                "fileName": os.path.basename(args.file),
                "receivers": receivers
            }
            headers = {
                "Authorization": "Bearer " + response.json()["accessToken"]
            }
            begin_data = requests.post(f"{protocol}://{host}:{port}/api/fathom/upload/begin", json=begin_body, headers=headers)
            if begin_data.status_code == 200:

                print("\n==========Uploading=============")
                # Payload upload
                chunkSize = 77
                chunks = math.ceil(max(len(detections), len(events)) / chunkSize)

                runningTotal = {
                    "newDetections": 0,
                    "newEvents": 0,
                    "duplicateEvents": 0,
                    "duplicateDetections": 0
                }

                for i in tqdm(range(chunks)):
                    sliceLow = i * chunkSize
                    sliceHigh = i * chunkSize + chunkSize
                    detectionsChunk = detections[sliceLow:sliceHigh]
                    eventsChunk = events[sliceLow:sliceHigh]
                    payload = {
                        "fileId": begin_data.json()["fileId"],
                        "fileName": begin_data.json()["fileName"],
                        "detections": detectionsChunk,
                        "events": eventsChunk
                    }
                    res = requests.post(f"{protocol}://{host}:{port}/api/fathom/upload/payload", json=payload, headers=headers)
                    runningTotal["newDetections"] += res.json()["newDetections"]
                    runningTotal["newEvents"] += res.json()["newEvents"]
                    runningTotal["duplicateDetections"] += res.json()["duplicateDetections"]
                    runningTotal["duplicateEvents"] += res.json()["duplicateEvents"]
                # End upload
                print("\n==========Results===============")
                end_body = {
                    "fileId": begin_data.json()["fileId"],
                    "fileName": begin_data.json()["fileName"],
                    "synchronous": True
                }
                end_data = requests.post(f"{protocol}://{host}:{port}/api/fathom/upload/end", json=end_body, headers=headers)
                print("New detections added:", end_data.json()["detectionsAdded"])
                print("Duplicated detections:", runningTotal["duplicateDetections"])
                print("New events added:", end_data.json()["eventsAdded"])
                print("Duplicated events:", runningTotal["duplicateEvents"])
            else:
                print("\n==========Results===============")
                print(begin_data.json()["errors"][0])
                exit(1)
        else:
            print("\n==========Results===============")
            print("Login failed")
            print(response.json()["errors"][0])
            exit(1)
    else:
        print("File must be a zip file")
        exit(1)
