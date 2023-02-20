# Animal Tracking Fathom Upload

This tool is used for uploading zip files that contain Fathom CSV files to the Animal Tracking server via a command line interface (CLI).

## Usage

### Download the `animaltracking` executable

It should have already been downloaded if you have clicked on the download link from the [Australian Animal Acoustic Telemetry](https://animaltracking.aodn.org.au/) web-interface while trying to upload your Fathom events and detections ZIP file.

If you haven't downloaded it yet, please [download here](https://github.com/aodn/animaltracking-fathom-upload/raw/main/dist/animaltracking)

### If you use Linux/Mac, open a terminal:

For Mac, click the Launchpad icon in the Dock, type Terminal in the search field, then click Terminal
For Linux (Ubuntu) press Ctrl+Alt+T .

Change working directory to where you downloaded the file `animaltracking`. 
If the file is saved in your `Downloads` folder, execute the following:

```bash
cd ~/Downloads
```

Then run:

```bash
chmod +x animaltracking
./animatracking
```

### If you are using Windows, double click on `animaltracking.exe` that you've just downloaded.

Note: you might be warned about the `.exe` file, click "Keep/Run anyway" or "Continue".

![image](https://user-images.githubusercontent.com/26201635/219268565-35860a53-3cfd-457b-957c-a3f3dda64749.png)
![image](https://user-images.githubusercontent.com/26201635/219268921-4b1bcbbe-dfef-433a-982b-81f931e3b28b.png)


### If you use the `animaltracking.py` file directly:

This tool has been tested with Python 3+

Clone this repo and change working directory to `animaltracking-fathom-upload` 

```bash
git clone https://github.com/aodn/animaltracking-fathom-upload.git
cd animaltracking-fathom-upload
```

Then execute the following command to install the required packages:

```bash
pip install -r requirements.txt
```

Finally, run the Python script:

```bash
python animaltracking.py
```
