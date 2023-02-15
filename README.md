# Animal Tracking Fathom Upload

This tool is used for uploading zip files that contain Fathom CSV files to the Animal Tracking server via CLI.

**Benefit:** to handle large ZIP files containing too many CSV files without keeping the browser tab open, users can run the command from their desktop or remote desktop terminal and leave the task running until completion.

## Installation

This tool has been tested with Python 3+

Clone this repo and change working directory to `animaltracking-fathom-upload` 

```bash
git clone https://github.com/aodn/animaltracking-fathom-upload.git
cd animaltracking-fathom-upload
```

Then executing the following command to install required packages:

```bash
pip install -r requirements.txt
```

## Usage

If you use the `animaltracking.py` file directly, you can run the following command to upload a zip file:

```bash
python animaltracking.py -f <zip_file_path> -H <hostname>
```

E.g
```bash
python animaltracking.py -f /home/Downloads/MyZipFile.zip -H animaltracking.aodn.org.au
```
