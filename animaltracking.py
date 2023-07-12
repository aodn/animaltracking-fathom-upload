import getpass
from sys import exit
from tqdm import tqdm
import requests
import zipfile
import math
import os
import re


class AODNFathomZipUploader:
    def __init__(self):
        self.detections = []
        self.events = []
        self.receivers = []
        self.counter = 0
        self.validFile = False
        self.authenticated = False
        self.file = ""
        self.authToken = ""
        self.host = ""
        self.port = 443
        self.protocol = "https"

    @staticmethod
    def parse_receiver(csv_model, csv_serial):
        model_split = csv_model.split("-")
        return f"{model_split[0] if any(char.isdigit() for char in model_split[1]) else csv_model}-{csv_serial}"

    def parse_csv(self, csv_file):
        detection_csv_ids = ["DET"]
        lines = csv_file.split("\n")
        for line in lines:
            l = line.split(",")
            if len(l) < 6:
                continue
            if l[0] in detection_csv_ids:
                record = {
                    "timestamp": f"{l[1]}.000" if "." not in l[1] else l[1],
                    "timestamp_corrected": f"{l[2]}.000" if "." not in l[2] else l[2],
                    "receiverName": self.parse_receiver(l[5], l[6]),
                    "transmitterId": l[8],
                    "sensorValue": l[14],
                    "sensorUnit": l[15]
                }
                self.detections.append(record)
            elif "DIAG" in l[0] and "_DESC" not in l[0]:
                record = {
                    "eventDetail": line
                }
                self.events.append(record)

    def extract_csv_from_zip(self):
        with zipfile.ZipFile(self.file, 'r') as archive:
            for entry in archive.infolist():
                if entry.filename.endswith('.csv'):
                    self.counter += 1
                    with archive.open(entry.filename) as csv_file:
                        self.parse_csv(csv_file.read().decode('utf-8'))

    def upload(self):

        print("+------------------------------+")
        print("+  AODN Fathom Zip Upload Tool +")
        print("+------------------------------+")

        while self.authenticated is False:
            print("\n==========Authenticating========")
            self.host = input(
                "Press enter if you really want to upload your detections onto the Australian Animal Acoustic "
                "Telemetry Database (animaltracking.aodn.org.au) or q then enter to quit: ")

            if self.host == "q":
                exit()

            if self.host == "localhost":
                self.port = 5000
                self.protocol = "http"
            if self.host == "systest":
                self.host = "animaltracking-systest.aodn.org.au"
            if self.host == "edge":
                self.host = "animaltracking-edge.aodn.org.au"
            if self.host == "":
                self.host = "animaltracking.aodn.org.au"

            username = input("Enter your username: ")
            password = getpass.getpass(prompt="Enter your password: ")

            url = f"{self.protocol}://{self.host}:{self.port}/api/auth/signin"
            payload = {
                "username": username,
                "password": password
            }
            response = requests.post(url, json=payload)

            if response.status_code == 200:
                self.authenticated = True
                self.authToken = response.json()["accessToken"]
                print("Successful login!")
            else:
                print("Login failed")
                print(response.json()["errors"][0])

        if self.authenticated:
            while self.validFile is False:
                print("\n==========ZIP File==============")
                if os.name == 'nt':
                    print(r"Sample: C:\Users\MyName\Documents\FathomDetectionsFolder\MyDetectionsToUpload.zip")
                else:
                    print("Sample: /Users/MyName/Documents/FathomDetectionsFolder/MyDetectionsToUpload.zip")
                self.file = input("Please specify path or drag and drop your ZIP file here and then press enter: ")

                # Remove ending blankspaces
                if self.file.endswith(" "):
                    self.file = re.sub(r'\s+$', "", self.file)

                # Remove quotes if present
                if "'" in self.file or '"' in self.file:
                    self.file = self.file[1:-1]

                if self.file.endswith(".zip") is False:
                    print("File must be a .zip file")
                else:
                    self.validFile = True

            if self.validFile:
                print("\n==========Loading===============")
                self.extract_csv_from_zip()
                print("File:", os.path.basename(self.file))
                print("Total CSV files:", self.counter)
                print("Total detections:", len(self.detections))
                print("Total events:", len(self.events))
                receivers = list(set(record['receiverName'] for record in self.detections))
                print("Total receivers:", len(receivers))

                # Begin upload
                begin_body = {
                    "fileName": os.path.basename(self.file),
                    "receivers": receivers
                }
                headers = {
                    "Authorization": "Bearer " + self.authToken
                }
                begin_data = requests.post(f"{self.protocol}://{self.host}:{self.port}/api/fathom/upload/begin",
                                           json=begin_body,
                                           headers=headers)
                if begin_data.status_code == 200:

                    print("\n==========Uploading=============")
                    print("\nNotes: please keep this terminal window open until the upload is complete.\n")
                    # Payload upload
                    chunk_size = 77
                    chunks = math.ceil(max(len(self.detections), len(self.events)) / chunk_size)

                    running_total = {
                        "newDetections": 0,
                        "newEvents": 0,
                        "duplicateEvents": 0,
                        "duplicateDetections": 0
                    }

                    for i in tqdm(range(chunks)):
                        slice_low = i * chunk_size
                        slice_high = i * chunk_size + chunk_size
                        detections_chunk = self.detections[slice_low:slice_high]
                        events_chunk = self.events[slice_low:slice_high]
                        payload = {
                            "fileId": begin_data.json()["fileId"],
                            "fileName": begin_data.json()["fileName"],
                            "detections": detections_chunk,
                            "events": events_chunk
                        }
                        res = requests.post(f"{self.protocol}://{self.host}:{self.port}/api/fathom/upload/payload",
                                            json=payload,
                                            headers=headers)
                        running_total["newDetections"] += res.json()["newDetections"]
                        running_total["newEvents"] += res.json()["newEvents"]
                        running_total["duplicateDetections"] += res.json()["duplicateDetections"]
                        running_total["duplicateEvents"] += res.json()["duplicateEvents"]
                    # End upload
                    print("\n==========Results===============")
                    end_body = {
                        "fileId": begin_data.json()["fileId"],
                        "fileName": begin_data.json()["fileName"],
                        "synchronous": True
                    }
                    end_data = requests.post(f"{self.protocol}://{self.host}:{self.port}/api/fathom/upload/end",
                                             json=end_body,
                                             headers=headers)
                    print("New detections added:", end_data.json()["detectionsAdded"])
                    print("Duplicated detections:", running_total["duplicateDetections"])
                    print("New events added:", end_data.json()["eventsAdded"])
                    print("Duplicated events:", running_total["duplicateEvents"])
                else:
                    print("\n==========Results===============")
                    print(begin_data.json()["errors"][0])

        if os.name == 'nt':
            import keyboard
            print('\nPress any keys to exit...')
            event = keyboard.read_event()
            if event.event_type == keyboard.KEY_DOWN:
                exit()


if __name__ == '__main__':
    AODNFathomZipUploader().upload()
