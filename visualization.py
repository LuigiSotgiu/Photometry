import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

def Plot_All_Stars(dataset, 
                   seaborn_theme_kwargs={'palette': 'bright'}, 
                   pyplot_kwargs={}, 
                   legend_kwargs={'loc': 'best', 
                                  'fontsize': 'small'}):
    """
    Plots the instrumental magnitude of all stars in the dataset over time.

    Parameters:
        dataset: list of DataFrames, where each DataFrame represents measurements at a specific time.
        seaborn_theme_kwargs: dict, arguments to customize Seaborn theme.
        pyplot_kwargs: dict, arguments to customize Matplotlib plot.
        legend_kwargs: dict, arguments to customize the legend.
    """
    mag_list = []  # List to store magnitudes of all stars.

    # Loop through each star and extract its magnitudes over all observations.
    for i in range(dataset[0].shape[0]):
        mag = [df['instrumental_magnitude'][i] for df in dataset]
        mag_list.append(mag)

    x = range(len(mag_list[0]))  # Define an x-axis range for plotting (arbitrary time points).

    # Set up the plot theme and figure.
    sns.set_theme(**seaborn_theme_kwargs)
    fig, ax = plt.subplots()
    ax.set(xlabel='time (au)', ylabel='instrumental magnitude')  # Set axis labels.

    # Plot the magnitude for each star.
    for j in range(len(mag_list)):
        ax.plot(x, mag_list[j], label=f'{j} star', **pyplot_kwargs)

    plt.legend(**legend_kwargs)  # Add the legend.
    plt.show()  # Display the plot.

def Plot_Diff_Phot(dataset_green=None, dataset_blue=None, 
                   green_plot=True, blue_plot=True, 
                   variable_star_index=0, comparison_star_index=1, check_star_index=2, 
                   offset=-12.05, seaborn_theme_kwargs={}, subplots_kwargs={}, 
                   Axes_set_kwargs={'xlabel': 'Time (JD)', 
                                    'ylabel': 'Instrumental Magnitude'}, 
                   legend_kwargs={'loc': 'best', 
                                  'fontsize': 'xx-small'}):
    """
    Plots differential photometry comparing variable stars to reference stars.

    Parameters:
        dataset_green: list of DataFrames, measurements in the green filter.
        dataset_blue: list of DataFrames, measurements in the blue filter.
        green_plot: bool, whether to include the green filter in the plot.
        blue_plot: bool, whether to include the blue filter in the plot.
        variable_star_index: int, index of the variable star in the dataset.
        comparison_star_index: int, index of the comparison star in the dataset.
        check_star_index: int, index of the check star in the dataset.
        offset: float, offset for visualization purpose in magnitude.
        seaborn_theme_kwargs: dict, arguments to customize Seaborn theme.
        subplots_kwargs: dict, arguments for plt.subplots.
        Axes_set_kwargs: dict, axis labels and other plot customizations.
        legend_kwargs: dict, arguments to customize the legend.
    """

    if green_plot:
        # Extract magnitudes for the variable star, comparison star, and check star in the green filter.
        instr_magnit_V0536Peg_green = [df['instrumental_magnitude'][variable_star_index] for df in dataset_green]
        instr_magnit_1_green = [df['instrumental_magnitude'][comparison_star_index] for df in dataset_green]
        instr_magnit_2_green = [df['instrumental_magnitude'][check_star_index] for df in dataset_green]
        
        # Compute the magnitude difference between the two fixed stars with an offset.
        diff_magnit_2_1_green = [b - a + offset for a, b in zip(instr_magnit_1_green, instr_magnit_2_green)]
        
        # Extract errors for the stars in the green filter.
        sigma_V0536Peg_green = [df['sigma instrumental magnitude'][variable_star_index] for df in dataset_green]
        sigma_star_1_green = [df['sigma instrumental magnitude'][comparison_star_index] for df in dataset_green]
        sigma_star_2_green = [df['sigma instrumental magnitude'][check_star_index] for df in dataset_green]
        
        # Propagate errors for the magnitude difference.
        diff_error_green = [np.sqrt(sigma1**2 + sigma2**2) for sigma1, sigma2 in zip(sigma_star_1_green, sigma_star_2_green)]
        
        # Extract time values for plotting (Julian Dates).
        julian_dates_green = [df['AVG Julian Date'][variable_star_index] for df in dataset_green]

    if blue_plot:
        # Extract magnitudes for the variable star, comparison star, and check star in the blue filter.
        instr_magnit_V0536Peg_blue = [df['instrumental_magnitude'][variable_star_index] for df in dataset_blue]
        instr_magnit_1_blue = [df['instrumental_magnitude'][comparison_star_index] for df in dataset_blue]
        instr_magnit_2_blue = [df['instrumental_magnitude'][check_star_index] for df in dataset_blue]

        # Compute the magnitude difference between the two fixed stars with an offset.
        diff_magnit_2_1_blue = [b - a + offset for a, b in zip(instr_magnit_1_blue, instr_magnit_2_blue)]
        
        # Extract errors for the stars in the blue filter.
        sigma_V0536Peg_blue = [df['sigma instrumental magnitude'][variable_star_index] for df in dataset_blue]
        sigma_star_1_blue = [df['sigma instrumental magnitude'][comparison_star_index] for df in dataset_blue]
        sigma_star_2_blue = [df['sigma instrumental magnitude'][check_star_index] for df in dataset_blue]
        
        # Propagate errors for the magnitude difference.
        diff_error_blue = [np.sqrt(sigma1**2 + sigma2**2) for sigma1, sigma2 in zip(sigma_star_1_blue, sigma_star_2_blue)]
        
        # Extract time values for plotting (Julian Dates).
        julian_dates_blue = [df['AVG Julian Date'][variable_star_index] for df in dataset_blue]
    
    # Set up the plot theme and figure.
    sns.set_theme(**seaborn_theme_kwargs)
    fig, ax = plt.subplots(**subplots_kwargs)
    ax.set(**Axes_set_kwargs)

    if green_plot:
        # Plot green filter data for the variable star and the magnitude difference.
        ax.errorbar(julian_dates_green, instr_magnit_V0536Peg_green, sigma_V0536Peg_green, 
                    color='g', fmt='o', markersize=4, fillstyle='none', label='V0539 Peg green')
        ax.errorbar(julian_dates_green, diff_magnit_2_1_green, diff_error_green, 
                    color='g', fmt='x', markersize=5, label='2nd - 1st + offset')

    if blue_plot:
        # Plot blue filter data for the variable star and the magnitude difference.
        ax.errorbar(julian_dates_blue, instr_magnit_V0536Peg_blue, sigma_V0536Peg_blue, 
                    color='b', fmt='o', markersize=4, fillstyle='none', label='V0539 Peg blue')
        ax.errorbar(julian_dates_blue, diff_magnit_2_1_blue, diff_error_blue, 
                    color='b', fmt='x', markersize=5, label='2nd - 1st + offset')

    if not green_plot and not blue_plot:
        # Handle the case where no data is selected to plot.
        print('Please, select at least a set to plot.')
        return None

    plt.legend(**legend_kwargs)  # Add the legend.
    plt.show()  # Display the plot.