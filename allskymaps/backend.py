import re
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import griddata
from astropy.table import Table, vstack
from astropy.time import Time
from astropy.coordinates import Angle
import astropy.units as u

from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent = 'nixnox')

plt.style.use('static/matplotlibrc/maps')

class PhotometerObs():

    """Main photometer class. Reads from .ecsv and performs map generations and diverse operations."""

    def __init__(self, ecsv_path, name = 'Observation'):
        """Instance initializes by reading the ecsv file in ecsv_path."""

        self.ecsv_path = ecsv_path
        self.name = name
        # Reads .ecsv data
        self.data = Table.read(self.ecsv_path, format='ascii.ecsv', delimiter=',')
        self.magnitudes = self.data['Mag']  # All magnitude values
        self.azimuths = self.data['Azi']  # All azimuth values
        self.zeniths = 90 - self.data['Alt']  # All zeniths values

        self.magnitud_zenith = np.mean(self.data[self.data['Azi'] == 90]['Mag'])

        '''Latitudes and longitudes'''

        self.mean_LAT = Angle(np.mean(self.data['Lat']), unit=u.deg)  # degrees
        self.mean_LONG = Angle(np.mean(self.data['Long']), unit=u.deg)  # degrees

        '''Date'''
        self.mean_datetime = self.data['Datetime'][0]
        self.data.meta['mean_datetime'] = self.mean_datetime
        self.data.meta['mean_LONG'] = self.mean_LONG
        self.data.meta['mean_LAT'] = self.mean_LAT

    ### Once ecsv is read ###
    def __interpolate_measurements__(self):

        '''
        Interpolate to create grid. Needed to be performed before magnitud_map() if interpolated == True.

         * squaresize -- int: Lenght of the side of the square for the interpolation grid
         * method -- str: {'linear', 'nearest', 'cubic'} Method of interpolation

        '''

        zen = np.arange(0, np.max(90 - self.data['Alt']) +1, 1)  # grid values in zen direction
        azi = np.arange(0, 361, 1)  # grid values in azi direction

        # '''Create periodic boundary conditions for interpolation'''

        data = self.data
        dfa = data.copy()
        dfa['Azi'] = dfa['Azi'] + 360

        dfb = data.copy()
        dfb['Azi'] = dfb['Azi'] - 360
        self.periodic_data = vstack([data, dfa, dfb])

        self.periodic_magnitudes = np.array(self.periodic_data['Mag'])
        self.periodic_zeniths = 90 - np.array(self.periodic_data['Alt'])
        self.periodic_azimuths = np.array(self.periodic_data['Azi'])

        ZEN, AZI = np.meshgrid(zen, azi)  # coordinated zen and azi (for vectorized computations) INTERPOLATION grid
        r, theta = np.meshgrid(zen, np.radians(azi))  # coordinated zen and azi (for vectorized computations)
        VALUES = griddata((self.periodic_zeniths, self.periodic_azimuths), self.periodic_magnitudes, (ZEN, AZI),
                          method = 'cubic')  # Interpolated values (magnitudes) for the grid points

        values = np.array(VALUES)  # INTERPOLATED magnitudes but array instead of meshgrid


        # Zernike polynomials
        '''from zernike import RZern, FitZern

        npoly = 40     # number of polynomials
        pol = RZern(npoly)      # create a set of orthonormal Zernike polynomials

        K, L = int(np.max(azi)+1), int(np.max(zen)+1)       # Number of points in the grid
        ip = FitZern(pol, L, K)     # Instance from the previous set ready to fit with the grid
        pol.make_pol_grid(ip.rho_j, ip.theta_i)     # Create grid

        c_hat = ip.fit(values.ravel())      # Fit the points from the map (values) following the grid. c_hat are the
        # zernike coefficients

        zern_values = pol.eval_grid(c_hat)      # Recreate the map using the coefficients

        # ... plotting ... #
        print(c_hat[0:20], len(c_hat))
        fig, ax = plt.subplots(subplot_kw = {'projection': 'polar'}, figsize = (9, 9))

        ax.set_theta_zero_location("N")  # Set the north to the north
        ax.set_theta_direction(-1)
        ax.set_xticklabels(['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'], fontdict = {'fontsize': 18})

        levels = 50
        
        ax.contourf(theta, r, zern_values.reshape(len(azi), len(zen)),
                          levels, cmap = 'YlGnBu',
                          vmin = 15, vmax = 25)

        ax.set_ylim(0, np.max(zen))
        fig.savefig(f'zernike_fit_{npoly}.png', dpi = 100)
        cax = ax.contourf(theta, r, zern_values.reshape(len(azi), len(zen)) - values,
                    levels, cmap = 'bwr',
                    vmin = -2, vmax = 2)

        fig.colorbar(cax, orientation = 'horizontal', fraction = 0.048)
        fig.savefig(f'zernike_error_{npoly}.png', dpi = 100)
        del fig
        ###########'''


        values = values.reshape(len(azi), len(zen))


        self.i_azimuths = theta
        self.i_zeniths = r
        self.i_magnitudes = values

        gradient = np.gradient(VALUES)
        gradient[0] = -gradient[0]  #change sign to be consistent with azimuth definition


        i_data = {
            'azimuth': theta.ravel(),
            'zenith': r.ravel(),
            'magnitude': values.ravel(),
            'gradient_azi': gradient[0].ravel(),
            'gradient_zen': gradient[1].ravel()
        }

        self.unraveled_data = {
            'azimuth': theta,
            'zenith': r,
            'magnitude': values,
            'gradient_azi': gradient[0],
            'gradient_zen': gradient[1]
        }

        self.i_data_table = Table(i_data)
        self.i_data_table.meta = self.data.meta
        self.initial_azi = azi
        self.initial_zen = zen

    def magnitude_map(self, interpolated=True, levels=50, min_mag=15, max_mag=25, cmap='YlGnBu',
                      normalize=False,
                      font_scale=1):
        '''Creates the interpolated allsky magnitude map.
        Plot a polar contour plot, with 0 degrees at the North.

        * interpolated -- boolean: If True then map will be created with interpolated values. First, interpolation
        must be done via interpolate_measurements
        * levels -- int: Contourf number of levels.
        * l -- float: Tick space in magnitudes for contour and cbar.
        * c map -- str: Colormap for plotting magnitudes. See
        https://matplotlib.org/examples/color/colormaps_reference.html
        * normalize -- boolean or float: Value (origin) for differential normalization. If 'True', magnitude of the
        zenith is chosen. If False no normalization is performed. If float, then it's the value taken as the origin.
        * font_scale -- int or float: Fontsize scaling.
        '''
        l = 0.3
        l = (np.max(self.magnitudes)-np.min(self.magnitudes))/8


        if l < 0.05:
            l = 0.05
        elif l > 0.1:
            l = np.round(l, 1)

        fig, ax = plt.subplots(subplot_kw={'projection': 'polar'}, figsize=(9, 9))
        # fig.patch.set_facecolor('lightblue')  #Background color
        ax.set_theta_zero_location("N")  # Set the north to the north
        ax.set_theta_direction(-1)
        ax.set_xticklabels(['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'], fontdict={'fontsize': 18 * font_scale})
        fig.text(0.75, 0.18, self.mean_datetime.iso.split('.')[0], fontsize=14 * font_scale,
                 horizontalalignment='center')
        fig.text(0.25, 0.18, r'LONG   ' + self.mean_LONG.to_string(sep=':', pad = True) + ' E', fontsize=14 * font_scale, horizontalalignment='center')
        fig.text(0.25, 0.22, r'LAT       ' + self.mean_LAT.to_string(sep=':', pad = True) + ' N', fontsize=14 * font_scale, horizontalalignment='center')

        if normalize:
            m_normal = self.magnitud_zenith

        elif isinstance(normalize, float):
            m_normal = normalize

        else:
            m_normal = 0

        self.levels = levels
        lev = np.arange(min_mag - m_normal, max_mag - m_normal, l)  # Min, max and stepsize for contour lines and cbar ticks
        self.lev = lev

        if interpolated:

            self.__interpolate_measurements__()

            try:
                '''Interpolated map'''
                cax = ax.contourf(self.i_azimuths, self.i_zeniths, self.i_magnitudes - m_normal, self.levels, cmap=cmap,
                                  vmin=min_mag - m_normal, vmax=max_mag - m_normal)

            except:
                print('ERROR: Interpolated values not found.\n')
                print('Try ".interpolate_measurements()" method for generating interpolated Magnitude Map before.\n')

            try:
                '''Measured points for reference'''
                ax.scatter(np.radians(self.azimuths), self.zeniths, c='red', zorder=2, s=8)
            except:
                print('ERROR: It was not possible to draw reference measured points')

            try:
                '''Contour lines'''
                smallest_mag = np.min(self.i_magnitudes - m_normal)
                biggest_mag = np.nanmax(self.i_magnitudes - m_normal)

                if biggest_mag > 18:
                    line_color = 'w'
                else:
                    line_color = '#2F82C2'
                cax_lines = ax.contour(cax, colors=line_color, levels=self.lev)
                ax.clabel(cax_lines, colors=line_color, inline=True, fmt='%1.1f', rightside_up=True,
                          fontsize='medium')

            except:
                print('ERROR: It was not possible to draw contour lines')

        else:
            '''Measured points'''
            cax = ax.scatter(np.radians(self.azimuths), self.zeniths, c=self.magnitudes - m_normal, cmap=cmap,
                             vmin=min_mag, vmax=max_mag)

        '''Colorbar'''
        cb = fig.colorbar(cax, orientation='horizontal', fraction=0.048, ticks=lev)
        cb.set_label("Magnitude mag/arcsec$^2$", fontsize=17 * font_scale)
        cb.ax.tick_params(labelsize=12) 

        '''Cut the axes to fit data'''
        ax.set_ylim(0, max(self.zeniths))
        fig.suptitle(self.name, size=30, y=1)
        plt.close()
        return fig, ax, cax


    def pipeline(self, path_map = None):

        if path_map is None:
            path_map = self.ecsv_path.split('.ecsv')[0] + '.png'

        self.path_map = path_map
        fig, _, _ = self.magnitude_map()


        fig.suptitle(self.name, size = 30 * 1, y = 0.995)

        fig.savefig(self.path_map, dpi = 300)

        return self.path_map, self.ecsv_path, self.data, self.i_magnitudes, self.i_azimuths, 90 - self.i_zeniths, \
               self.mean_LAT, self.mean_LONG




class TASObs(PhotometerObs):

    def __init__(self, txt_path, meta_dict, name='Observation', ecsv_path=None):
        """Reads a forms .txt file and transforms it into a .ecsv file standarized for nixnox."""

        # Transforms .txt to astropy table

        table = Table(
            data=None,
            names=['ind', 'Datetime', 'Temp_IR', 'T_sens', 'Mag', 'Hz', 'Alt', 'Azi', 'Lat', 'Long', 'SL'],
            dtype=['int64', 'str', 'float64', 'float64', 'float64', 'float64', 'float64', 'float64', 'float64',
                   'float64', 'int64']
        )

        with open(txt_path, 'r', encoding='utf-8', errors='ignore') as file_object:  # Abrir el fichero

            lines = file_object.readlines()

            for line in lines:  # Corregir las lineas
                if line.startswith('#'):  # Omitir los comentarios
                    pass
                else:
                    line = line.rstrip()  # Quitar espacio final
                    line = re.sub(r',', '.', line)  # Cambiar comas a puntos
                    line = re.sub(r'\s+', ',', line)  # Cambiar separación a ;
                    line = line.split(',')

                    # Lat longitude to float (degrees)
                    line[7] = Angle(line[7], unit=u.deg)
                    line[8] = Angle(line[8], unit=u.deg)
                    line[9] = Angle(line[9], unit=u.deg)
                    line[10] = Angle(line[10], unit=u.deg)


                    # Datetime column
                    line[1] = line[1] + ' ' + line[2]
                    line.pop(2)

                    table.add_row(line)

        table['Datetime'] = Time(table['Datetime'], format='iso')

        # Metadata (author, photometer...)
        table.meta = meta_dict

        if ecsv_path is None:
            ecsv_path = txt_path.split('.txt')[0] + '.ecsv'

        table.write(ecsv_path, format='ascii.ecsv', delimiter=',', overwrite=True)

        # Now that .ecsv is create initialize the PhotometerObservation class
        super().__init__(ecsv_path, name)

# TODO: There is an error in azimuth with .py files from Jaime's rpository. All rotated 180 degrees (the azimuth it's
#  not ok)

class NixnoxPy(PhotometerObs):
    '''Class to work with nixnox.py Zamorano's oservations'''

    def __init__(self, filepath, meta_dict, name='Observation', ecsv_path = None):
        self.nixnox_py_path = filepath

        if ecsv_path is None:
            ecsv_path = filepath.split('.py')[0] + '.ecsv'

        self.ecsv_path = ecsv_path

        # Read the .py file. Format is mXX = [X1, X2, X3] for magnitudes and xXX = [Y1, Y2, Y3] where XX is the
        # elevation and Yn is the

        # Read the .py file until the xx linspace
        with open(self.nixnox_py_path, 'r', encoding='utf-8', errors='ignore') as file:
            pyfile_total = file.read()
            pyfile = pyfile_total.split('linspace')[0]

        # Remove spaces and tabs
        pyfile = re.sub(' ', '', pyfile)
        pyfile = re.sub('\t', '', pyfile)
        # Remove comments
        # pyfile = re.sub('#.*', '', pyfile)


        # Look for mXX (magnitudes) and xXX (its correspondant aximuths)
        raw_magnitudes = re.findall('m\d\d=\[.*\]', pyfile)
        raw_azimuths = re.findall('x\d\d=\[.*\]', pyfile)

        # Generate floats vector of the elevation values
        elevation = []
        magnitude = []
        azimuth = []

        dict_mag = {'Alt':elevation, 'Mag':magnitude,
                    'Azi': azimuth}

        for l in raw_magnitudes:
            k, v = l.split('=')
            aux_mag = eval(v)
            dict_mag['Mag'] += aux_mag
            dict_mag['Alt'] += [float(k[1:])] * len(aux_mag)

        for l in raw_azimuths:
            _, v = l.split('=')
            dict_mag['Azi'] += eval(v)

        # The dictionary with the 3 columns elev, azi, mag
        self.dict_mag = dict_mag

        lat = re.findall('(LAT)( *)=( *)(\")(.+)( +N|S)(\")', pyfile_total)[0]
        long = re.findall('(LONG)( *)=( *)(\")(.+)( +W|E)(\")', pyfile_total)[0]


        if re.sub(' ', '', lat[5]) == 'N':
            lat_sign = 1
        else:
            lat_sign = -1
        a, b, c = re.sub('[^0-9\.]', ',', lat[4]).split(',')
        lat_coord = [float(a), float(b), float(c)]

        if re.sub(' ', '', long[5]) == 'E':
            long_sign = 1
        else:
            long_sign = -1
        a, b, c = re.sub('[^0-9\.]', ',', long[4]).split(',')
        long_coord = [float(a), float(b), float(c)]

        # The dictionary with 5 columns (lat, long added)

        latitude = lat_sign * (lat_coord[0] + lat_coord[1]/60 + lat_coord[2]/3600)
        longitude = long_sign * (long_coord[0] + long_coord[1] / 60 + long_coord[2] / 3600)

        table = Table(self.dict_mag)
        table['Lat'] = latitude
        table['Long'] = longitude

        table['ind'] = 1414

        dt = Time(meta_dict['Datetime'], format = 'datetime')
        dt.format = 'iso'
        table['Datetime'] = dt

        table['T_IR'] = 999.0
        table['T_sensor'] = 999.0
        table['hz'] = 999.0
        table['sl'] = 999
        self.table = table

        table.meta = meta_dict

        table.write(self.ecsv_path, format='ascii.ecsv', delimiter=',', overwrite=True)

        # Now that .ecsv is created
        super().__init__(self.ecsv_path, name)
