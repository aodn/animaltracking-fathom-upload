# Animal Tracking Fathom Upload Tool

This tool is used for uploading zip files that contain Fathom CSV files to the Animal Tracking server via CLI.

**Benefit:** to handle large ZIP files containing too many CSV files without keeping the browser tab open, users can run the command from their desktop or remote desktop terminal and leave the task running until completion.

## Installation

This tool has been tested with Python 3+

```bash
pip install animaltracking-fathom-upload
```

## Usage

You can run the following command to upload a zip file:

```bash
animaltracking-fathom-upload -f <zip_file_path> -H <hostname>
```

e.g
```bash
animaltracking-fathom-upload -f /home/Downloads/MyZipFile.zip -H animaltracking.aodn.org.au
```
