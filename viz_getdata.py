import astropy
from astropy.io import fits
import astropy.units as u
from astropy.wcs import WCS

import numpy as np
from einops import repeat

import sys, os, gc
import warnings

warnings.filterwarnings("ignore")

def get_data(self):
    if not self.sami_id:
        return False
    # Cube
    self.wav, self.cflux, self.wcs = get_cube(self)
    # Maps: total flux, gasv, stev, gasd, sted, lines(Ha, Hb, OIII, NII)
    self.tflux = get_flux(self)
    self.gasvel = get_gasv(self)
    self.stevel = get_stev(self)
    self.gasdis = get_gasd(self)
    self.stedis = get_sted(self)
    self.lines, self.snr = get_lines(self)
    self.NH, self.OH, self.BPT_mosaic, self.curve = get_BPT(self)
    
    #HSC
    self.HSC, self.wcs_HSC = get_HSC(self)

    return True

def get_BPT(self, snr_lim = 3):
    try:
        NH=np.log10(np.array(self.lines[3])/(np.array(self.lines[0])+1E-8))
        NH[self.snr < snr_lim] = np.nan
        OH=np.log10(np.array(self.lines[2])/(np.array(self.lines[1])+1E-8))
        OH[self.snr < snr_lim] = np.nan
        AGN_crit = (0.61 / (NH - 0.47) + 1.19) * (NH < 0.47) - 1E8 * (NH > 0.47)
        MIX_crit = (0.61 / (NH - 0.05) + 1.3)  * (NH < 0.05) - 1E8 * (NH > 0.05)
        pre_selection = (~np.isnan(OH)) * (~np.isnan(NH)) * (NH > -1.3) * (OH > -1.2)
        red   = pre_selection * (OH > AGN_crit)
        green = pre_selection * (OH < AGN_crit) * (OH > MIX_crit)
        blue  = pre_selection * (OH < MIX_crit)
        BPT_mosaic = np.array([red, green, blue]).transpose([1,2,0]).astype('uint8') * 255
        
        x1 = np.arange(-1.5, 0.46, 0.1)
        y1 = (0.61 / (x1 - 0.47) + 1.19)
        x2 = np.arange(-1.5, 0.04, 0.1)
        y2 = (0.61 / (x2 - 0.05) + 1.3)
        
        curve = [x1, y1, x2, y2]
        return NH, OH, BPT_mosaic, curve
    except:
        return None, None, None, None
def get_cube(self):
    cube = self.cube
    idnum = str(self.sami_id)
    try:
        hdu_blue = fits.open(cube + '/' + idnum + '/' + idnum + '_A_cube_blue.fits.gz')
        hdu_red = fits.open(cube + '/' + idnum + '/' + idnum + '_A_cube_red.fits.gz')    
        
        wcs = WCS(hdu_blue[0].header).celestial
        wcs.slice = (1, 1)
        
        step_blue = hdu_blue[0].header['CDELT3']
        start_blue = hdu_blue[0].header['CRVAL3'] - (hdu_blue[0].header['CRPIX3'] - 1) * step_blue
        end_blue = step_blue * (hdu_blue[0].header['NAXIS3'] - 1) + start_blue + 1E-8
        wav_blue = np.arange(start_blue, end_blue, step_blue)
        z_spec = hdu_blue[0].header['z_spec']
        self.scale_asec2kpc = z_spec * 299792.458 / 70 / 3600 / 180 * np.pi * 1000 # H_0 = 70 km / s / Mpc
        
        dust = np.concatenate([hdu_blue[5].data, hdu_red[5].data])
        
        step_red = hdu_red[0].header['CDELT3']
        start_red = hdu_red[0].header['CRVAL3'] - (hdu_red[0].header['CRPIX3'] - 1) * step_red
        end_red = step_red * (hdu_red[0].header['NAXIS3'] - 1) + start_red + 1E-8
        wav_red = np.arange(start_red, end_red, step_red)
        
        wav = np.concatenate([wav_blue, wav_red])
        flux = np.concatenate([hdu_blue[0].data, hdu_red[0].data])
        flux[np.isnan(flux)] = 0
        s = np.shape(flux)
        
        flux = flux * repeat(dust, 'a -> a b c', b = s[1], c = s[2])
        wav = wav / (1. + z_spec)
        flux = flux * (1. + z_spec)
    
        hdu_blue.close()
        hdu_red.close()
        
    except:
        return None, None, None
    return wav, flux, wcs
    
def get_map(self, filename):
    data = fits.getdata(filename)
    #data[np.isnan(data)] = 0
    return data   
        
def get_map_err(self, filename):
    hdu = fits.open(filename)
    data = hdu[1].data
    hdu.close()
    #data[np.isnan(data)] = 0
    return data
        
def get_lines(self):
    line_flux = self.line_flux 
    idnum = self.sami_id
    #try:
    if True:
        file_Ha = line_flux + '/' + str(idnum) + '/' + str(idnum) + '_A_Halpha_default_recom-comp.fits'
        file_Hb = line_flux + '/' + str(idnum) + '/' + str(idnum) + '_A_Hbeta_default_recom-comp.fits'
        file_OIII = line_flux + '/' + str(idnum) + '/' + str(idnum) + '_A_OIII5007_default_recom-comp.fits'
        file_NII = line_flux + '/' + str(idnum) + '/' + str(idnum) + '_A_NII6583_default_recom-comp.fits'
        maps = []
        maps_err = []

        flux_Ha = get_map(self, file_Ha)[0]
        flux_Ha_err = get_map_err(self, file_Ha)[0]
        maps.append(flux_Ha)
        maps_err.append(flux_Ha_err)
        
        flux_Hb = get_map(self, file_Hb)
        flux_Hb_err = get_map_err(self, file_Hb)
        maps.append(flux_Hb)
        maps_err.append(flux_Hb_err)

        flux_OIII = get_map(self, file_OIII)
        flux_OIII_err = get_map_err(self, file_OIII)
        maps.append(flux_OIII)
        maps_err.append(flux_OIII_err)

        flux_NII = get_map(self, file_NII)
        flux_NII_err = get_map_err(self, file_NII)
        maps.append(flux_NII)
        maps_err.append(flux_NII_err)
        
        snr = np.min(np.array(maps) / np.array(maps_err), axis = 0) 
        
        self.lines_avail = True
        return maps, snr
    else:
    #except:
        self.lines_avail = False
        return [None, None, None, None], None

def get_flux(self):
    # WIP
    return None
    
def get_gasv(self):
    gasv = self.gasv
    idnum = str(self.sami_id)
    try:
        maps = get_map(self, gasv + '/' + idnum + '/' + idnum + '_A_gas-velocity_default_recom-comp.fits')
        self.gasv_avail = True

    except:
        self.gasv_avail = False
        return None
    return maps

def get_gasd(self):
    gasd = self.gasd
    idnum = str(self.sami_id)
    try:
        maps = get_map(self, gasd + '/' + idnum + '/' + idnum + '_A_gas-vdisp_default_recom-comp.fits')
        self.gasd_avail = True
    except:
        self.gasd_avail = False
        return None
    return maps
        
def get_stev(self):
    stev = self.stev
    idnum = str(self.sami_id)
    try:
        maps = get_map(self, stev + '/' + idnum + '/' + idnum + '_A_stellar-velocity_default_two-moment.fits')
        self.stev_avail = True
    except:
        self.stev_avail = False
        return None
    return maps

def get_sted(self):
    # Not downloaded yet
    sted = self.sted
    idnum = str(self.sami_id)
    try:
        maps = get_map(self, sted + '/' + idnum + '/' + idnum + '_A_stellar-velocity-dispersion_default_two-moment.fits')
        self.sted_avail = True
    except:
        self.sted_avail = False
        return None
    return maps

def get_HSC(self):
    hsc_image = self.hsc_image
    idnum = str(self.sami_id)
    images = []
    try:
        for band in ['G','R','I','Z','Y']:
            hdu = fits.open(hsc_image + '/' + idnum + '_HSC-' + band + '.fits')
            data = hdu[1].data
            wcs_HSC = WCS(hdu[1].header).celestial
    
            images.append(data)
            hdu.close()
        self.HSC_avail = True
    except:
        self.HSC_avail = False
        return [None, None, None, None, None], None
    return images, wcs_HSC
