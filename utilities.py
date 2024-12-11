import pandas as pd
from pathlib import Path
from tqdm import tqdm
from Photometry_Tool import PhotometryTool

# Function to retrieve filenames of specific types of images (green and blue filters) from the 'data' directory
def Get_files_names():
    """
    Retrieves filenames of images with green and blue filters from the 'data' directory.

    Returns:
        tuple: A tuple containing two lists - 
            files_green_filter (list): List of filenames with green filter.
            files_blue_filter (list): List of filenames with blue filter.
    """
    files_blue_filter = []  # List to store filenames with blue filter
    files_green_filter = []  # List to store filenames with green filter

    current_directory = Path.cwd()  # Get the current working directory
    directory = Path(current_directory / 'data')  # Define the path to the 'data' folder

    # Iterate through all files in the 'data' directory
    for file_path in directory.iterdir():
        if file_path.is_file():  # Check if the path points to a file
            if file_path.name.endswith('.fits'):  # Consider only files with a .fits extension
                if 'B' in file_path.name:  # Check if the filename indicates a blue-filtered image
                    files_blue_filter.append(file_path.name)
                elif 'G' in file_path.name:  # Check if the filename indicates a green-filtered image
                    files_green_filter.append(file_path.name)

    return files_green_filter, files_blue_filter  # Return lists of green and blue filter files

# Function to load and process photometry data for green and blue filtered images
def Load_dataset(files_green_filter=None,
                 files_blue_filter=None,
                 green=True, blue=True, 
                 PhotometryTool_kwargs={'r_star': 6, 
                                         'r_gap': 14, 
                                         'r_sky': 17}):
    """
    Loads and processes photometry data for images with green and blue filters.

    Parameters:
        files_green_filter (list, optional): List of filenames with green filter. Defaults to None.
        files_blue_filter (list, optional): List of filenames with blue filter. Defaults to None.
        green (bool, optional): Flag to indicate if green filter data should be processed. Defaults to True.
        blue (bool, optional): Flag to indicate if blue filter data should be processed. Defaults to True.
        PhotometryTool_kwargs (dict, optional): Dictionary of parameters for the PhotometryTool. Defaults to {'r_star': 6, 'r_gap': 14, 'r_sky': 17}.

    Returns:
        list or tuple: Processed photometry data. Returns:
            - A list of results for green filter images if only green is selected.
            - A list of results for blue filter images if only blue is selected.
            - A tuple of two lists (green, blue) if both are selected.
            - None if neither green nor blue is selected.
    """
    current_directory = Path.cwd()  # Get the current working directory

    # Load positions of comparison stars from a file
    positions = pd.read_csv('data/Ra_Deg_comp_stars.txt', names=['Ra', 'Deg'])

    # Initialize empty lists to store results for each filter
    dataset_green = []
    dataset_blue = []

    # Process green-filtered images if the green flag is True
    if green:
        print('Green Filter Loading:')
        for g in tqdm(files_green_filter):  # Iterate through green filter filenames
            tool = PhotometryTool(path=Path(current_directory / 'data' / g), 
                                  **PhotometryTool_kwargs)  # Initialize PhotometryTool
            results_green = tool.analyze(positions)  # Analyze the image for photometry
            dataset_green.append(results_green)  # Append results to the dataset

    # Process blue-filtered images if the blue flag is True
    if blue:
        print('Blue Filter Loading:')
        for b in tqdm(files_blue_filter):  # Iterate through blue filter filenames
            tool = PhotometryTool(path=Path(current_directory / 'data' / b), 
                                  **PhotometryTool_kwargs)  # Initialize PhotometryTool
            results_blue = tool.analyze(positions)  # Analyze the image for photometry
            dataset_blue.append(results_blue)  # Append results to the dataset

    # Ensure at least one filter is selected; otherwise, prompt the user
    if not green and not blue:
        print('Please, select at least 1 filter for the output.')

    # Return results based on the selected filters
    if green and not blue:
        return dataset_green
    
    elif blue and not green:
        return dataset_blue
    
    elif green and blue:
        return dataset_green, dataset_blue
    
    else:
        return None