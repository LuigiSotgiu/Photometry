import warnings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.time import Time
from astropy.wcs import WCS, FITSFixedWarning
from photutils.aperture import CircularAperture, CircularAnnulus, aperture_photometry, ApertureStats
from photutils.centroids import centroid_sources

class PhotometryTool:
    def __init__(self, path, r_star, r_gap, r_sky, *args, **kwargs):
        """
        Initialize the PhotometryTool with basic parameters.

        Parameters:
        - path (str): Path to the FITS file.
        - r_star (float): Star aperture radius in pixels.
        - r_gap (float): Inner radius of the sky annulus in pixels.
        - r_sky (float): Outer radius of the sky annulus in pixels.
        """
        self.path = path
        self.r_star = r_star
        self.r_gap = r_gap
        self.r_sky = r_sky
        self.data, self.header, self.wcs = self._load_fits()
    
    def _load_fits(self):
        """Load FITS file and suppress warnings."""
        warnings.simplefilter('ignore', FITSFixedWarning)
        hdu = fits.open(self.path)
        data = hdu[0].data
        header = hdu[0].header
        wcs = WCS(header)
        return data, header, wcs
    
    def _convert_ra_dec_to_pixel(self, ra_dec_coordinates):
        """Convert RA/DEC coordinates to pixel positions."""
        pixel_positions = self.wcs.world_to_pixel_values(ra_dec_coordinates)
        return pixel_positions

    def _filter_pixels(self, x_pixel, y_pixel):
        """Filter out invalid pixel positions."""
        valid_x = [x for x in x_pixel if 0 <= x <= self.data.shape[1]]
        valid_y = [y for y in y_pixel if 0 <= y <= self.data.shape[0]]
        return valid_x, valid_y
    
    def _compute_centroids(self, x_pixel, y_pixel):
        """Calculate the centroids of sources."""
        return centroid_sources(self.data, x_pixel, y_pixel)
    
    def _perform_photometry(self, centroids):
        """Perform aperture photometry on stars and sky."""
        star_apertures = CircularAperture(centroids, r=self.r_star)
        sky_annulus = CircularAnnulus(centroids, r_in=self.r_gap, r_out=self.r_sky)
        
        phot_source = aperture_photometry(self.data, star_apertures)
        phot_sky = aperture_photometry(self.data, sky_annulus)
        
        sky_stats = ApertureStats(self.data, sky_annulus)
        bkg_mean = [val for val in sky_stats.mean if not np.isnan(val)]
        return phot_source, phot_sky, bkg_mean
    
    def _compute_magnitudes(self, source_sums, bkg_means):
        """Calculate instrumental magnitudes and errors."""
        A_s = np.pi * self.r_star**2
        A_b = np.pi * (self.r_sky**2 - self.r_gap**2)
        
        instrumental_magnitudes = []
        sigma_instrumental_magnitudes = []
        
        for source, bkg in zip(source_sums, bkg_means):
            log_argument = source - bkg * A_s
            safe_log_argument = np.where(log_argument > 0, log_argument, np.nan)  # Sostituisci i valori non validi con np.nan
            inst_mag = -2.5 * (np.log10(0.77) + np.log10(safe_log_argument))
            instrumental_magnitudes.append(inst_mag)
            sigma_inst_mag = 2.5 * np.log10(np.e) * (
                np.sqrt((A_s)**2 * bkg / A_b + source) / np.abs(source - bkg * A_s)
            )
            sigma_instrumental_magnitudes.append(sigma_inst_mag)
        
        return instrumental_magnitudes, sigma_instrumental_magnitudes
    
    def analyze(self, ra_dec_coordinates):
        """
        Perform photometric analysis on the given RA/DEC coordinates.

        Parameters:
        - ra_dec_coordinates (pd.DataFrame): DataFrame with RA/DEC positions.

        Returns:
        - pd.DataFrame: Photometric results.
        """
        pixel_positions = self._convert_ra_dec_to_pixel(ra_dec_coordinates)
        x_pixel, y_pixel = zip(*pixel_positions)
        x_pixel, y_pixel = self._filter_pixels(x_pixel, y_pixel)
        centroids = list(zip(*self._compute_centroids(x_pixel, y_pixel)))
        
        phot_source, phot_sky, bkg_mean = self._perform_photometry(centroids)
        
        df_source = phot_source.to_pandas()
        df_sky = phot_sky.to_pandas()
        df_centroids = pd.DataFrame(self.wcs.all_pix2world(centroids, 0), 
                                    columns=['Ra Centroid', 'Dec Centroid'])
        
        inst_mag, sigma_inst_mag = self._compute_magnitudes(df_source['aperture_sum'], bkg_mean)
        
        utc_time = self.header['DATE-AVG']
        t = Time(utc_time, format='isot', scale='utc')
        jd = t.jd
        
        results = pd.concat([
            ra_dec_coordinates.reset_index(drop=True),
            df_centroids, 
            df_source['aperture_sum'], 
            df_sky['aperture_sum'], 
            pd.Series(inst_mag, name='instrumental_magnitude'), 
            pd.Series(sigma_inst_mag, name='sigma instrumental magnitude'),
            pd.Series(np.full(len(inst_mag), jd), name='AVG Julian Date')
        ], axis=1)
        
        results = results.dropna(how='any')
        results = results.reset_index(drop=True)
        
        return results.rename(columns={
            'aperture_sum': 'star_aperture_sum',
            'aperture_sum.1': 'sky_aperture_sum'
        })
        
    def plot_curve_of_growth(self, ra_dec_coordinates, max_radius, step=1):
        """
        Plot the curve of growth for the given RA/DEC coordinates.

        Parameters:
        - ra_dec_coordinates (pd.DataFrame): DataFrame with RA/DEC positions.
        - max_radius (float): Maximum radius for the curve of growth.
        - step (float): Step size for the radius.
        """
        pixel_positions = self._convert_ra_dec_to_pixel(ra_dec_coordinates)
        x_pixel, y_pixel = zip(*pixel_positions)
        x_pixel, y_pixel = self._filter_pixels(x_pixel, y_pixel)
        centroids = list(zip(*self._compute_centroids(x_pixel, y_pixel)))
        
        _, _, bkg_mean = self._perform_photometry(centroids)
        
        radii = np.arange(step, max_radius + step, step)
        fluxes = []

        for r in radii:
            star_apertures = CircularAperture(centroids, r=r)
            phot_source = aperture_photometry(self.data, star_apertures)
            fluxes.append([phot - (bkg * np.pi * r**2) for phot, bkg in zip(phot_source['aperture_sum'], bkg_mean)])
        
        plt.figure(figsize=(10, 6))
        plt.axvline(self.r_star, color='k', linestyle='--', label='Star Aperture Radius')
        plt.axvline(self.r_gap, color='k', linestyle='--', label='Sky Annulus Inner Radius')
        plt.axvline(self.r_sky, color='k', linestyle='--', label='Sky Annulus Outer Radius')
        plt.plot(radii, fluxes, marker='o')
        plt.xlabel('Aperture Radius (pixels)')
        plt.ylabel('Flux (D.N.)')
        plt.title('Curve of Growth')
        plt.grid(True)
        plt.show()