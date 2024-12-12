# Photometry Tool

This repository provides a tool for performing aperture photometry on `.fits` images. It processes celestial object data based on their coordinates and outputs instrumental magnitudes along with other photometric data.

---

## Features

- Analyze `.fits` files containing celestial object data.
- Calculate photometric properties such as:
  - Star aperture sum
  - Sky annulus sum
  - Instrumental magnitude
  - Instrumental magnitude error
- Output results in a clear and structured `pandas` DataFrame.

---

## Installation

### Prerequisites

This tool requires the following Python packages:

- **Astropy**: For reading `.fits` files and working with celestial coordinates.  
  Installation: `pip install astropy`
- **Pandas**: For handling tabular data.  
  Installation: `pip install pandas`
- **Numpy**: For numerical operations.  
  Installation: `pip install numpy`
- **Photutils**: For performing aperture photometry.  
  Installation: `pip install photutils`
- **Matplotlib**: For visualization.
  Installation: `pip install matplotlib`
- **Seaborn**: For visualization.
  Installation: `pip install seaborn`

### Optional: Using a Virtual Environment

If you working on Windows I suggest using:
- wsl ---> https://learn.microsoft.com/it-it/windows/wsl/install
- VSCode with wsl ---> https://learn.microsoft.com/en-us/windows/wsl/tutorials/wsl-vscode
- miniconda ---> https://docs.anaconda.com/miniconda/

Using this setup you could simply create a Virtual Environment using this code on wsl:
```bash
conda create -n env_name astropy pandas numpy photutils matplotlib seaborn
```

## Usage

### File Structure

- **`Photometry_Tool.py`**: Contains the main class structure.
  - `PhotometryTool`: The Class to performs the photometric analysis.
- **`utilities.py`**: Contains some useful functions to manage the data.
- **`visualization.py`**: Contains some useful functions to visualize the data.
- **`main.ipynb`**: Demonstrates the usage of `PhotometryTool` step by step.
- **`testing.ipynb`**: Just for me to test and debug stuff (please don't open it).

### Example Workflow

1. Clone the repository:
   ```bash
   git clone https://github.com/LuigiSotgiu/photometry-tool.git
   cd photometry-tool
   ```
2. Install dependencies
3. Open Jupiter Notebook and explore examples
   ```bash
   jupyter notebook main.ipynb
   ```

