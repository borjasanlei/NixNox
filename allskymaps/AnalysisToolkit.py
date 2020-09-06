import matplotlib.pyplot as plt
import numpy as np
from lmfit import Model
from time import time

plt.style.use('static/matplotlibrc/plots')
from .backend import PhotometerObs


def to_lum(mag):
    return 10**(0.4*(20-mag))

def to_mag(lum):
    return 20 - 2.5*np.log10(lum)

def azi_profiles(table, azi, zen, axes):
    '''Generates a plot with magnitude vs. elevation for all azimuths.

    Returns:
        * axes: axes
        * median_mag: median magnitude profile in zenith distance
        '''

    axes.scatter(table['zenith'], table['magnitude'], s = .8, c = table['azimuth'], alpha = 0.4)

    median_mag = []
    for z in zen:
        minitable = table[table['zenith'] == z]
        median_mag += [np.nanmedian(minitable['magnitude'])]

    axes.plot(zen, median_mag, linewidth = 1, c = 'red', label = 'Median')
    axes.set_xlabel(r'Zenith distance [$^\circ$]')
    axes.set_ylabel('Magnitude')
    axes.legend()

    return axes, median_mag


def azi_profiles_sub(table, azi, zen, axes):
    """Generates a plot with magnitude vs. elevation for all azimuths subtracted with the median magnitude value at
    each zenith distance.

    Returns:
        * axes: axes
        * dispersion: max(magnitude) - min(magnitude) profile
        """

    dispersion = []
    for z in zen:
        minitable = table[table['zenith'] == z]
        dispersion += [np.max(minitable['magnitude']) - np.min(minitable['magnitude'])]
        diff = minitable['magnitude'] - np.nanmedian(minitable['magnitude'])
        axes.scatter(minitable['zenith'], diff, s = .1, c = minitable['azimuth'], alpha = 1)

    axes.axhline(c = 'black', linewidth = .8, alpha = 0.3)  # horizontal line at 0
    axes.plot(zen, dispersion, linewidth = 1, c = 'red', label = 'Dispersion')
    axes.set_xlabel(r'Zenith distance [$^\circ$]')
    axes.set_ylabel('Magnitude difference')
    axes.legend()

    return axes, dispersion


def azi_profiles_maxmin(table, azi, zen, axes):
    """Generates a plot with magnitude vs. elevation for the brightest and darkest at horizon.

    Returns:
        * axes: axes
        * max_mean_azi: azimuth for the brightest direction
        * min_mean_azi: azimuth for the darkest direction
        """

    horizon = table[table['zenith'] == zen[-1]]['magnitude']
    max_azi = table[table['magnitude'] == np.max(horizon)]['azimuth']
    min_azi = table[table['magnitude'] == np.min(horizon)]['azimuth']

    median_mag = []
    for z in zen:
        minitable = table[table['zenith'] == z]
        median_mag += [to_mag(np.nanmedian(to_lum(minitable['magnitude'])))]

    zenith = np.mean(table[table['zenith'] == 0]['magnitude'])

    axes.axhline(y = zenith, linestyle = '--', c = 'black', linewidth = .8, alpha = 0.3, label = 'Magnitude at '
                                                                                                'zenith')  #
    # horizontal
    # line at 0
    axes.plot(zen, table[table['azimuth'] == min_azi]['magnitude'], linewidth = 1, c = '#ebe42d',
              label = 'Brightest at horizon')
    axes.plot(zen, table[table['azimuth'] == max_azi]['magnitude'], linewidth = 1, c = '#346399',
              label = 'Darkest at horizon')
    axes.plot(zen, median_mag, linewidth=3, c = '#ff1f1f',
              label = 'Median')
    axes.set_xlabel(r'Zenith distance [$^\circ$]')
    axes.set_ylabel('Magnitude')
    axes.legend()

    return axes, max_azi, min_azi

def gra_azi_profiles(table, azi, zen, axes, direction = 'zen'):
    """Generates a plot with gradient in the AZI direction vs. ZEN for all the AZI."""

    t = table[['azimuth', 'zenith', f'gradient_{direction}']].copy()
    t[f'gradient_{direction}'].name = 'magnitude'
    axes, med_value =  azi_profiles(t, azi, zen, axes)
    axes.set_ylabel(f'Gradient [{direction}]')
    return axes, med_value


def gra_map(table, unraveled_data, direction = 'zen'):
    """Creates the interpolated allsky GRADIENT map.
        Plot a polar contour plot, with 0 degrees at the North.
        """

    fig, ax = plt.subplots(subplot_kw = {'projection': 'polar'}, figsize = (9, 9))

    ax.set_theta_zero_location("N")  # Set the north to the north
    ax.set_theta_direction(-1)
    ax.set_xticklabels(['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'], fontdict = {'fontsize': 18})
    fig.text(0.75, 0.18, table.meta['mean_datetime'].iso.split('.')[0], fontsize = 14,
             horizontalalignment = 'center')
    fig.text(0.25, 0.18, 'LONG ' + table.meta['mean_LONG'].to_string(), fontsize = 14,
             horizontalalignment = 'center')
    fig.text(0.25, 0.22, 'LAT ' + table.meta['mean_LAT'].to_string(), fontsize = 14 , horizontalalignment = 'center')

    levels = 50
    '''Interpolated map'''
    cax = ax.contourf(unraveled_data['azimuth'], unraveled_data['zenith'], unraveled_data[f'gradient_{direction}'], levels, cmap = 'bwr',
                      vmin = -.3, vmax = +.3)

    '''Colorbar'''
    cb = fig.colorbar(cax, orientation = 'horizontal', fraction = 0.048)
    cb.set_label(rf"Gradient mag/arcsec$^2$/$^\circ$ ({direction} direction)", fontsize = 17)

    '''Cut the axes to fit data'''
    ax.set_ylim(0, max(table['zenith']))
    fig.suptitle(table.meta['place'], size = 30, y = 1)
    return fig, ax, cax


#### Miro Bara fit #################################################################################

def M(z):
    """
    Optical mass function from Bara's paper.

    Arguments:
        - z: 1-D array like. Zenital distances in radians.

    """
    h = np.pi / 2 - z

    return 2.0016 / (np.sin(h) + np.sqrt((np.sin(h)) ** 2 + 0.003147))

def nsb_m(z, A, g, t, s1 = 1, s2 = 2.5, s3 = 5, s4 = 6,
          l1 = 1, l2 = 1, l3 = 1, l4 = 1):
    """
    Model for the NSB from Bara's paper.

    Arguments:
        - z, A: 1D arrays. Zenith distance and Azimuth. Independent variables.
        - g, t: floats. Atmospherical parameters.
        - s1, s2, s3: Floats. Azimuth value for each light pollution source at the horizon.
        - pi_2_mags: list or 1d array. Measured magnitude for z = pi/2
        - pi_2_azi: list or 1d array. Measured azimuth for z = pi/2"""

    # Luminosities for the give light sources

    A_0 = [s1, s2, s3, s4]
    l_c = [l1, l2, l3, l4]

    # Actual model
    z_source = 90
    M_pi_2 = M(z_source * np.pi / 180)

    L0 = ((1 - g) ** 2 / (1 + g)) * (M(z) / (M_pi_2 * t)) * (np.exp((M_pi_2 - M(z)) * t - 1)) / (M_pi_2 - M(z))

    L1 = 0

    for i in range(len(l_c)):
        Ai = A_0[i]
        li = l_c[i]

        L1 += li * (1 - g ** 2) / ((1 + g ** 2 - 2 * g * np.sin(z) * np.cos(A - Ai)) ** (3 / 2))

    L = L0 * L1

    return L


### Model ###

def define_model(mod = nsb_m):
    model_nsb = Model(mod,
                  independent_vars = ['z', 'A'],
                  param_names = ['g', 't', 's1', 's2', 's3', 's4',
                                 'l1', 'l2', 'l3', 'l4'],
                  )
    params = model_nsb.make_params()

    params['g'].min = 1e-7
    params['g'].max = 1
    params['t'].min = 1e-7
    params['t'].max = 1
    params['g'].value = 0.5
    params['t'].value = 0.5
    params['s1'].min = 0
    params['s2'].min = 0
    params['s3'].min = 0
    params['s4'].min = 0
    params['s1'].max = 2 * np.pi
    params['s2'].max = 2 * np.pi
    params['s3'].max = 2 * np.pi
    params['s4'].max = 2 * np.pi
    params['s1'].value = 0.1
    params['s2'].value = 2.
    params['s3'].value = 4.
    params['s4'].value = 5.
    params['l1'].value = 1
    params['l2'].value = 1
    params['l3'].value = 1
    params['l4'].value = 1
    params['l1'].min = 0
    params['l2'].min = 0.
    params['l3'].min = 0.
    params['l4'].min = 0.
    params['l1'].max = 5 * 1e+2
    params['l2'].max = 5 * 1e+2
    params['l3'].max = 5 * 1e+2
    params['l4'].max = 5 * 1e+2

    return model_nsb,params

def fit_test(obs, name, model_nsb, params, method = 'leastsq'):
    init_time = time()
    azii, magi, zeni = obs.i_azimuths, obs.i_magnitudes, obs.i_zeniths * np.pi / 180

    l = to_lum(obs.data['Mag'])
    A = obs.data['Azi'] * np.pi / 180
    z = (90 - obs.data['Alt']) * np.pi / 180

    fit = model_nsb.fit(data = l, z = z, A = A,
                        params = params, method = method, nan_policy = 'omit'
                        )

    l_fit = nsb_m(zeni, azii, g = fit.params['g'].value, t = fit.params['t'].value,
                  s1 = fit.params['s1'].value, s2 = fit.params['s2'].value, s3 = fit.params['s3'].value,
                  s4 = fit.params['s4'].value,
                  l1 = fit.params['l1'], l2 = fit.params['l2'], l3 = fit.params['l3'],
                  l4 = fit.params['l4'])

    m_fit = to_mag(l_fit)

    theta = obs.i_azimuths
    r = obs.i_zeniths
    m = obs.i_magnitudes

    fig, ax = plt.subplots(subplot_kw = {'projection': 'polar'}, figsize = (9, 9))

    ax.set_theta_zero_location("N")  # Set the north to the north
    ax.set_theta_direction(-1)
    ax.set_xticklabels(['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'], fontdict = {'fontsize': 18})

    levels = 50

    cax = ax.contourf(theta, r, m_fit,
                      levels, cmap = 'YlGnBu',
                      vmin = 15, vmax = 25)

    ax.set_ylim(0, np.max(r))
    fig.colorbar(cax, orientation = 'horizontal', fraction = 0.048)

    fig.savefig(f'media/fit/{name}_fit.png', dpi = 70)

    plt.close()
    fig, ax = plt.subplots(subplot_kw = {'projection': 'polar'}, figsize = (9, 9))

    ax.set_theta_zero_location("N")  # Set the north to the north
    ax.set_theta_direction(-1)
    ax.set_xticklabels(['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'], fontdict = {'fontsize': 18})

    levels = 50

    cax = ax.contourf(theta, r, m_fit - m,
                      levels, cmap = 'bwr',
                      vmin = -3, vmax = 3)

    ax.set_ylim(0, np.max(r))
    cbar = fig.colorbar(cax, orientation = 'horizontal', fraction = 0.048)
    fig.savefig(f'media/fit/{name}_error.png', dpi = 70)
    plt.close()
    time_spent = time() - init_time

    return fit.params, time_spent





#### Tests ###


#obsname = '6a12de38-a66b-48ad-bdc4-f29c22eb5efa'

def complete_analysis(obsname):
    obs = PhotometerObs(f'media/observation_files/{obsname}.ecsv',
        name = 'Analysis')

    obs.__interpolate_measurements__()

    table = obs.i_data_table
    azi = obs.initial_azi
    zen = obs.initial_zen

    table['azimuth'] = table['azimuth'] * 180 / np.pi

    f, ax1 = plt.subplots(1, 1)

    ax1, _, _ = azi_profiles_maxmin(table, azi, zen, ax1)

    f.savefig(f'media/analysis/mm_{obsname}_azi.png')

    model_nsb, params = define_model()
    parameters = fit_test(obs, obsname, model_nsb, params)

    return parameters
