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
1. Create cutout table string from your csv file. Enter `python HSCimage.py [*.csv] cutout [Output]` in command line, and the table string will be in the output file.
2. Download cutout from [HSC-SSP cutout service](https://hsc-release.mtk.nao.ac.jp/das_cutout/pdr2/). Extract the file.
3. Change the names of FITS files with `python HSCimage.py [*.csv] cutout [Output]` so that `sami_viz` can read the image. 

### Set PATH to the file
Edit config.ini to set the right path. Leave terms blank for the files not downloaded yet.

### Open the GUI
Now type `python sami_viz.py` to open the GUI. Feel free to explore the SAMI data!

## Known issues
### Boundery condition
The code will stop working when invalid path / sami_id is set.
### Bad cutout
The code will stop working when the sizes of HSC images are not the same.
