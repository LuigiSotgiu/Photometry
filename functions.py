# Modules:

import warnings
import pandas as pd
import numpy as np
from astropy.io import fits
from astropy.wcs import WCS, FITSFixedWarning
from photutils.aperture import CircularAperture, aperture_photometry, CircularAnnulus, ApertureStats
#------------------------------------------------------------------------------------------------------------#
# Functions:

def PhotometryTool(path, ra_dec_coordinates, r_star, r_gap, r_sky):
    '''
    Parameters:
    path (string) -> The file path of a .fits image that we want to analyze;
    ra_dec_coordinates (pandas DataFrame) -> The Radial and Declination position of the stars of interest;
    r_star (float) -> Star aperture radius in pixel;
    r_gap (float) -> Inner radius of the sky anulus in pixel;
    r_sky (float) -> Outer radius of the sky anulus in pixel.
    
    This function opens a .fits file and does aperture photometry on a bunch of stars that takes in input 
    in the form of Radial and Declination coordinates. The function returns then the results in the form 
    of a pandas DataFrame containing the star aperture sum of DN, the sky anulus sum of DN and the instrumental 
    magnitude, all refers to the stars taken in input.
    
    (I'm working now on expand this dataframe with other variables of interest such as errors and some 
    other utilities.)
    '''
    
    # Suppress FITSFixedWarning: 
    # The fits files we have don't have the MJD-OBS and the MJD-AVG informations in the header, 
    # so the astropy module provides to set it based on the informations taken from the DATE-OBS and 
    # Date-AVG. The astropy modules do it itself properly, but prints in the terminal an annoying 
    # Warning, so I decide to ignore this with the function "simplefilter".
    warnings.simplefilter('ignore', FITSFixedWarning)
    
    # Load FITS file.
    hdu = fits.open(path)
    data = hdu[0].data
    header = hdu[0].header

    # Extract WCS information (World Coordinates System).
    wcs = WCS(header)
    
    # Convert RA/Dec to pixel coordinates.
    pixel_positions = wcs.world_to_pixel_values(ra_dec_coordinates)
    
    # Create circular and anulus apertures using pixel coordinates.
    star_apertures = CircularAperture(pixel_positions, r=r_star)  
    sky_anulus = CircularAnnulus(pixel_positions, r_in=r_gap, r_out=r_sky)  
    
    # Perform aperture photometry for both star aperture and sky anulus.
    phot_source = aperture_photometry(data, star_apertures)
    phot_sky = aperture_photometry(data, sky_anulus)
    
    # Computing the DN per pixel in the sky anulus.
    aperstats = ApertureStats(data, sky_anulus)
    bkg_mean = aperstats.mean
    
    # Just converting QTable from astropy to pandas DataFrame because I know there better.
    # For more information about QTable ---> https://docs.astropy.org/en/stable/api/astropy.table.QTable.html
    df_source = phot_source.to_pandas()
    df_source = df_source.dropna(how='any')

    df_sky = phot_sky.to_pandas()
    df_sky = df_sky.dropna(how='any')
    
    # Computing the instrumental magnitude for every star in input.
    instrumental_magnitudes = []
    for source, bkg in zip(df_source['aperture_sum'], bkg_mean):
        instrumental_magnitude = -2.5 * (np.log10(0.77) + np.log10(source - bkg * star_apertures.area))
        instrumental_magnitudes.append(instrumental_magnitude)

    # Creating a pandas DataFrame to concatenate it with others to return a single object.
    inst_mag_df = pd.DataFrame(instrumental_magnitudes)

    # Concatenating all the Dataframe with the information of interest.
    df_output = pd.concat((df_source[['aperture_sum']], 
                           df_sky[['aperture_sum']], 
                           inst_mag_df), axis=1)
    # Just renaming the columns to have a clearer DataFrame.
    df_output.columns = ['star_aperture_sum', 'sky_aperture_sum', 'instrumental_magnitude']
    
    return df_output