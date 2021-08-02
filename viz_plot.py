import matplotlib.pyplot as plt
import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.gridspec     import GridSpec
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg    as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
matplotlib.use('Qt5Agg')

import numpy as np
from einops import repeat

import sys, os, gc
import warnings
warnings.filterwarnings("ignore")

def snap(data, permin = 30, permax = 100):
    '''
    data: 2-dim array
    permin, permax: float (0 < # < 100)
    '''
    image = data + 0
    image[np.isnan(image)] = 0
    image[image < np.percentile(image.flatten(),permin)] = np.percentile(image.flatten(),permin)
    #image[image > np.percentile(image.flatten(),permax)] = np.percentile(image.flatten(),permax)

    image = np.log(image - np.percentile(image.flatten(),permin) + 1) / np.max(np.log(image - np.percentile(image.flatten(),permin) + 1))
    return image

# Plot stuff
def plot_(self):
    if not self.sami_id:
        return False
    # clear the screen
    plt.cla()
    if self.nofig:
        self.fig = plt.figure(figsize=(40,30), dpi=100)
        self.nofig = False
    if self.com_view:
        self.gs = GridSpec(4, 8, width_ratios = [0.1,1,1,0.1,1,1,1,1])
        # Create panels
        self.axes = []
        self.axes.append( plt.subplot( self.gs[0,6]  ) ) # Ha
        self.axes.append( plt.subplot( self.gs[0,7]  ) ) # Hb
        self.axes.append( plt.subplot( self.gs[1,6]  ) ) # NII
        self.axes.append( plt.subplot( self.gs[1,7]  ) )  # OIII
        self.axes.append( plt.subplot( self.gs[2,6]) )  # SII
        self.axes.append( plt.subplot( self.gs[2,7]) )  # SII
        self.axes.append( plt.subplot( self.gs[3,6]  ) )  # OII
        
        self.axes.append( plt.subplot( self.gs[0:2,1:3], projection = self.wcs))#, slices = ('x', 'y', 0)) )  # Map
        self.axes.append( plt.subplot( self.gs[0:2,4:6], projection = self.wcs))#, slices = ('x', 'y', 0)) )  # Map
        self.axes.append( plt.subplot( self.gs[2:4,1:3], projection = self.wcs))#, slices = ('x', 'y', 0)) )  # Map
        self.axes.append( plt.subplot( self.gs[2:4,4:6], projection = self.wcs))#, slices = ('x', 'y', 0)) )  # Map

        self.axes.append( plt.subplot( self.gs[0:2,0]  ) )  # Colorbar of the Map
        self.axes.append( plt.subplot( self.gs[0:2,3]  ) )  # Colorbar of the Map
        self.axes.append( plt.subplot( self.gs[2:4,0]  ) )  # Colorbar of the Map
        self.axes.append( plt.subplot( self.gs[2:4,3]  ) )  # Colorbar of the Map

        self.axes.append( plt.subplot( self.gs[3,7]  ) )  # BPT panel #Not fin yet
    
        plt.tight_layout(pad = 10, h_pad = 15, w_pad = 0)
    
        #Cube to emission lines
        if self.cflux is not None and self.wav is not None:
            linesnap(self)
            
        #Maps:
        mapsnap(self)
    else:
        self.gs = GridSpec(4, 7, width_ratios = [0.1,1,1,1,1,1,1])
        # Create panels
        self.axes = []
        self.axes.append( plt.subplot( self.gs[0,5]  ) ) # Ha
        self.axes.append( plt.subplot( self.gs[0,6]  ) ) # Hb
        self.axes.append( plt.subplot( self.gs[1,5]  ) ) # NII
        self.axes.append( plt.subplot( self.gs[1,6]  ) )  # OIII
        self.axes.append( plt.subplot( self.gs[2,5]) )  # SII
        self.axes.append( plt.subplot( self.gs[2,6]) )  # SII
        self.axes.append( plt.subplot( self.gs[3,5]  ) )  # OII
        self.axes.append( plt.subplot( self.gs[0:4,1:5], projection = self.wcs))#, slices = ('x', 'y', 0)) )  # Map
        self.axes.append( plt.subplot( self.gs[0:4,0]  ) )  # Colorbar of the Map
        self.axes.append( plt.subplot( self.gs[3,6]  ) )  # BPT panel #Not fin yet
    
    plt.tight_layout(pad = 10, h_pad = 15, w_pad = 0)
    
    #Cube to emission lines
    if self.cflux is not None and self.wav is not None:
        linesnap(self)
            
        #Maps: 
    mapsnap(self)
        
    self.canvas = FigureCanvas(self.fig)
    self.canvas.mpl_connect('button_release_event', self.focus)
    # Centralize the image Widget
    self.setCentralWidget(self.canvas)

def mapsnap(self):
    if self.com_view and self.stev_avail and self.gasv_avail and self.lines_avail:
        image = self.stevel + 0
        scale_max = np.percentile(image[~np.isnan(image)], 99)
        scale_min = np.percentile(image[~np.isnan(image)], 1)
        map_image = self.axes[7].imshow(image, cmap = 'RdBu_r',vmax = scale_max, vmin = scale_min, )
        self.fig.colorbar(map_image, ax = self.axes[7], cax = self.axes[11])
        self.axes[7].set_title('Stellar velocity map of SAMI %s, 1 \" = %.2f kpc'%(self.sami_id, self.scale_asec2kpc))
        self.axes[7].grid()
        self.axes[7].scatter(self.pos_x, self.pos_y, marker = '+', c = 'yellow', s = 1000)
        
        
        scale_max = np.percentile(self.gasvel[~np.isnan(self.gasvel)], 99)
        scale_min = np.percentile(self.gasvel[~np.isnan(self.gasvel)], 1)
        for i in range(3):
            image = self.gasvel[i] + 0
            map_image = self.axes[i + 8].imshow(image, cmap = 'RdBu_r',vmax = scale_max, vmin = scale_min, )
            self.fig.colorbar(map_image, ax = self.axes[i + 8], cax = self.axes[i + 12])
            self.axes[i + 8].set_title('%s-comp velocity map of SAMI %s, 1 \" = %.2f kpc'%(i + 1, self.sami_id, self.scale_asec2kpc))
            self.axes[i + 8].grid()
            self.axes[i + 8].scatter(self.pos_x, self.pos_y, marker = '+', c = 'yellow', s = 1000)
        self.axes[15].scatter(self.NH, self.OH, s = 1, c = 'black')
        self.axes[15].scatter(self.NH[self.pos_y,self.pos_x], self.OH[self.pos_y,self.pos_x], s = 30, c = 'yellow')
        self.axes[15].set_xlim([-1.5, 0.5])
        self.axes[15].set_ylim([-1.2, 1.5])
        self.axes[15].set_title('BPT classification')
        self.axes[15].plot(self.curve[0],self.curve[1], c = 'black')
        self.axes[15].plot(self.curve[2],self.curve[3], c = 'black')

    elif self.HSC_bkg:
        self.axes[7].grid()
        self.axes[7].set_xlim([-0.5, 49.5])
        self.axes[7].set_ylim([-0.5, 49.5])
        self.axes[7].scatter(self.pos_x, self.pos_y, marker = '+', c = 'yellow', s = 1000)
        if self.HSC_avail:
            print(np.shape(snap(self.HSC[2])), np.shape(snap(self.HSC[1])), np.shape(snap(self.HSC[0])))
            RGB = np.array([snap(self.HSC[2]), snap(self.HSC[1]), snap(self.HSC[0])]).transpose([1, 2, 0])
            self.axes[7].imshow(RGB, transform=self.axes[7].get_transform(self.wcs_HSC))
        if self.map == 'flux':
            pass
        if self.map == 'gasv' and self.gasv_avail:
            image = self.gasvel[self.component - 1] + 0
            scale_max = np.percentile(image[~np.isnan(image)], 99)
            scale_min = np.percentile(image[~np.isnan(image)], 1)
            map_image = self.axes[7].contourf(image, cmap = 'RdBu_r',vmax = scale_max, vmin = scale_min, linewidths = 5, levels = 4, alpha = 0.5)
            self.fig.colorbar(map_image, ax = self.axes[7], cax = self.axes[8])
            self.axes[7].set_title('%s-comp velocity map of SAMI %s, 1 \" = %.2f kpc'%(self.component, self.sami_id, self.scale_asec2kpc))
    
        if self.map == 'stev' and self.stev_avail:
            image = self.stevel + 0
            scale_max = np.percentile(image[~np.isnan(image)], 99)
            scale_min = np.percentile(image[~np.isnan(image)], 1)
            map_image = self.axes[7].contourf(image, cmap = 'RdBu_r',vmax = scale_max, vmin = scale_min, linewidths = 5, levels = 4, alpha = 0.5)
            self.fig.colorbar(map_image, ax = self.axes[7], cax = self.axes[8])
            self.axes[7].set_title('stellar velocity map of SAMI %s, 1 \" = %.2f kpc'%(self.sami_id, self.scale_asec2kpc))
            
        if self.map == 'gasd' and self.gasd_avail:
            image = self.gasdis[self.component - 1] + 0
            scale_max = np.percentile(image[~np.isnan(image)], 99)
            map_image = self.axes[7].contourf(image, cmap = 'Reds',vmax = scale_max, vmin = 0, linewidths = 5, levels = 4, alpha = 0.5)
            self.fig.colorbar(map_image, ax = self.axes[7], cax = self.axes[8])
            self.axes[7].set_title('%s-comp velocity dispersion map of SAMI %s, 1 \" = %.2f kpc'%(self.component, self.sami_id, self.scale_asec2kpc))
        
        if self.map == 'sted' and self.sted_avail:
            image = self.stedis + 0
            scale_max = np.percentile(image[~np.isnan(image)], 99)
            map_image = self.axes[7].contourf(image, cmap = 'Reds',vmax = scale_max, vmin = 0, linewidths = 5, levels = 4, alpha = 0.5)
            self.fig.colorbar(map_image, ax = self.axes[7], cax = self.axes[8])
            self.axes[7].set_title('stellar velocity map of SAMI %s, 1 \" = %.2f kpc'%(self.sami_id, self.scale_asec2kpc))
            
        if self.map == 'LWM' and self.cflux is not None:
            mask = (self.wav > min(self.wav_min_max)) * (self.wav < max(self.wav_min_max))
            lwm = np.sum(self.cflux[mask], axis = 0)
            map_image = self.axes[7].contourf(np.log10(lwm), cmap = 'Greys_r', linewidths = 5, levels = 4, alpha = 0.5)
            self.fig.colorbar(map_image, ax = self.axes[7], cax = self.axes[8])
            self.axes[7].set_title('Line Wing Map between %.1f AA and %.1f AA of SAMI %s, 1 \" = %.2f kpc'%(min(self.wav_min_max), max(self.wav_min_max), self.sami_id, self.scale_asec2kpc))
    
        if self.map == 'BPT' and self.lines_avail:
            self.axes[7].imshow(self.BPT_mosaic, alpha=0.2)

    else:
        if self.map == 'flux':
            pass
        if self.map == 'gasv' and self.gasv_avail:
            image = self.gasvel[self.component - 1] + 0
            scale_max = np.percentile(image[~np.isnan(image)], 99)
            scale_min = np.percentile(image[~np.isnan(image)], 1)
            map_image = self.axes[7].imshow(image, cmap = 'RdBu_r',vmax = scale_max, vmin = scale_min, )
            self.fig.colorbar(map_image, ax = self.axes[7], cax = self.axes[8])
            self.axes[7].set_title('%s-comp velocity map of SAMI %s, 1 \" = %.2f kpc'%(self.component, self.sami_id, self.scale_asec2kpc))
    
        if self.map == 'stev' and self.stev_avail:
            print(self.stev_avail)
            image = self.stevel + 0
            scale_max = np.percentile(image[~np.isnan(image)], 99)
            scale_min = np.percentile(image[~np.isnan(image)], 1)
            map_image = self.axes[7].imshow(image, cmap = 'RdBu_r',vmax = scale_max, vmin = scale_min)
            self.fig.colorbar(map_image, ax = self.axes[7], cax = self.axes[8])
            self.axes[7].set_title('stellar velocity map of SAMI %s, 1 \" = %.2f kpc'%(self.sami_id, self.scale_asec2kpc))
            
        if self.map == 'gasd' and self.gasd_avail:
            image = self.gasdis[self.component - 1] + 0
            scale_max = np.percentile(image[~np.isnan(image)], 99)
            map_image = self.axes[7].imshow(image, cmap = 'Reds',vmax = scale_max, vmin = 0)
            self.fig.colorbar(map_image, ax = self.axes[7], cax = self.axes[8])
            self.axes[7].set_title('%s-comp velocity dispersion map of SAMI %s, 1 \" = %.2f kpc'%(self.component, self.sami_id, self.scale_asec2kpc))
        
        if self.map == 'sted' and self.sted_avail:
            image = self.stedis + 0
            scale_max = np.percentile(image[~np.isnan(image)], 99)
            map_image = self.axes[7].imshow(image, cmap = 'Reds',vmax = scale_max, vmin = 0)
            self.fig.colorbar(map_image, ax = self.axes[7], cax = self.axes[8])
            self.axes[7].set_title('stellar velocity map of SAMI %s, 1 \" = %.2f kpc'%(self.sami_id, self.scale_asec2kpc))
        if self.map == 'BPT' and self.lines_avail:
            self.axes[7].imshow(self.BPT_mosaic)
            self.axes[7].set_xlabel('DE')
            self.axes[7].set_xlabel('RA')
            self.axes[7].set_title('BPT classification of SAMI %s, 1 \" = %.2f kpc'%(self.sami_id, self.scale_asec2kpc))
            
        if self.map == 'LWM' and self.cflux is not None:
            mask = (self.wav > min(self.wav_min_max)) * (self.wav < max(self.wav_min_max))
            lwm = np.sum(self.cflux[mask], axis = 0)
            map_image = self.axes[7].imshow(np.log10(lwm), cmap = 'Greys_r')
            self.fig.colorbar(map_image, ax = self.axes[7], cax = self.axes[8])
            self.axes[7].set_title('Line Wing Map between %.1f AA and %.1f AA of SAMI %s, 1 \" = %.2f kpc'%(min(self.wav_min_max), max(self.wav_min_max), self.sami_id, self.scale_asec2kpc))
    
        self.axes[7].grid()
        self.axes[7].scatter(self.pos_x, self.pos_y, marker = '+', c = 'yellow', s = 1000)
    if not self.com_view and self.lines_avail:
        self.axes[9].scatter(self.NH, self.OH, s = 1, c = 'black')
        self.axes[9].scatter(self.NH[self.pos_y,self.pos_x], self.OH[self.pos_y,self.pos_x], s = 30, c = 'yellow')
        self.axes[9].set_xlim([-1.5, 0.5])
        self.axes[9].set_ylim([-1.2, 1.5])
        self.axes[9].set_title('BPT classification')
        self.axes[9].plot(self.curve[0],self.curve[1], c = 'black')
        self.axes[9].plot(self.curve[2],self.curve[3], c = 'black')
    
def linesnap(self):
    line_set = self.line_set
    flux = self.cflux
    wav = self.wav
    pos_x = self.pos_x
    pos_y = self.pos_y
    
    light_speed = 299792.458 #km/s
    idnum = self.sami_id
    linenum = len(line_set)
    if self.gasvel is not None:
        vel_map_1 = self.gasvel[0] + 0
        vel_map_1[np.isnan(vel_map_1)] = - light_speed
        vel_map_2 = self.gasvel[1] + 0
        vel_map_2[np.isnan(vel_map_2)] = - light_speed
        vel_map_3 = self.gasvel[2] + 0
        vel_map_3[np.isnan(vel_map_3)] = - light_speed

        for k in range(linenum):
            line_wav = np.array(line_set[k][1])
            ymin = 0
            ymax = np.max(flux[:,pos_y,pos_x])
            self.axes[k].plot(wav, flux[:,pos_y,pos_x], color = 'black')
            self.axes[k].vlines(line_wav * (1 + vel_map_1[pos_y][pos_x] / light_speed), ymin, ymax, colors = 'green')
            self.axes[k].vlines(line_wav * (1 + vel_map_2[pos_y][pos_x] / light_speed), ymin, ymax, colors = 'pink')
            self.axes[k].vlines(line_wav * (1 + vel_map_3[pos_y][pos_x] / light_speed), ymin, ymax, colors = 'purple')
            self.axes[k].vlines(min(self.wav_min_max), ymin, ymax, colors = 'blue')
            self.axes[k].vlines(max(self.wav_min_max), ymin, ymax, colors = 'red')

            self.axes[k].set_xlim([np.mean(line_wav) - 15, np.mean(line_wav) + 15])
            self.axes[k].set_xlabel('wav / AA')
            self.axes[k].set_label('flux')
            self.axes[k].set_title('%s spec at (%s, %s) of SAMI %s'%(line_set[k][0], pos_x, pos_y, idnum))

    return self.axes