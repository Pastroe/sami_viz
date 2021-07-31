# sami_viz
A GUI for SAMI survey visualization

## Introduction
The [SAMI Galaxy Survey](https://docs.datacentral.org.au/sami/) is an integral field spectroscopy survey targeting ~3000 nearby galaxies spanning a range of environments. It has measured the spatially resolved stellar and gas properties of each of these galaxies, providing a wealth of information on every object. The [official SOV service](https://datacentral.org.au/services/sov/) supports checking data products like gas velocity / stellar velocity / SFR ... maps, but the original data cube is unable to be displayed in that page.

This visualization tool is developed for the purpose of emission-line analysis. It supports:
 - Display gas / stellar kinematics in one panel
 - Plot BPT diagram spatially
 - Plot the emission profiles at given spaxel
 - Interactive view: Change the cursor with mouse / arrow key
 - Interactive view: Set wave mask on the datacube to create narrow band image
 - (If available) overplot the maps above with HSC image

## Usage
### Download the Python code
Just download and extract the file in a folder

### Prepare the object list
Prepare a list of object in a `.csv` file. It should contain SAMI_id, RA and DE at least for data retrieving.

### Download SAMI data product 
To use the tool, please download the data products (datacubes and maps) of objects to visualize at [bulk download page](https://datacentral.org.au/services/download/). Extract the data to the same folder as the code.

### Download HSC image (optional)
This requires to have an account at [HSC-SSP website](https://hsc-release.mtk.nao.ac.jp/doc/).  
1. Create sql string from your csv file. Enter `python csv2sql.py [*.csv] [radius] [*.txt]` in command line, and the sql string will be in the output file.
2. Copy-paste the string to HSC sql service to get the result. Crossmatch the result with original catalog to obtain the tract each object locates in, and save the result in a new csv file in the folder (suppose it to be 'HSC_tract.csv').
3. Download HSC image from the HscMap server. Enter `python download_HSC.py HSC_tract.csv`, and the download will start soon. It may take a time as the code download files via a spider. 

### Set PATH to the file
Edit config.ini to set the right path. Leave terms blank for the files not downloaded yet.

### Open the GUI
Now type `python sami_viz.py` to open the GUI. Feel free to explore the SAMI data!
