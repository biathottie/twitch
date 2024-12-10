# League of Legends Data Analysis

This project is designed to analyze and predict various aspects of League of Legends gameplay using data from multiple sources. The project includes scripts for data manipulation, prediction, and scraping.

## Files and Directories

- `better.py`: Contains functions for data manipulation and conversion of usernames into PUUIDs.
- `champion_data.json`: JSON file containing champion data.
- `classifier.pkl`: Pickle file containing a pre-trained classifier model.
- `gameInfo.csv`: CSV file containing game information.
- `opgg`: Directory containing scripts related to the OPGG API.
- `point_logic.py`: Script for calculating points based on game data.
- `predict.py`: Script for making predictions using the classifier model.
- `requirements.txt`: List of required Python packages.
- `scripts`: Directory containing various scripts for data manipulation, scraping, and analysis.
  - `combine.py`: Script for combining data from multiple sources.
  - `Main.ipynb`: Jupyter notebook for data analysis and visualization.
  - `main.py`: Main script for running the project.
  - `scrape.py`: Script for scraping data from the web.
  - `season1414.*.csv`: CSV files containing game data for different seasons.
  - `xpath_and_css_selectors.py`: Script containing XPath and CSS selectors for web scraping.

## Getting Started

### Prerequisites

- Python 3.x
- Required Python packages (listed in `requirements.txt`)

### Installation

1. Clone the repository:
   ```sh
   git clone <repository_url>
   ```
2. Navigate to the project directory:
    ```sh 
    cd <project_directory>
    ```
3. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

### Usage
1. To get twitch cookies:
    ```
    Follow this video for instructions on how to upload your twitch cookies: https://youtu.be/vhjKJ7huN-w
    Put the cookies in the file named twitch_cookies.csv
    ```
2. Run the main script:
    ```sh
    python better.py
    ```
3. To analyze data using the Jupyter notebook, open scripts/Main.ipynb:
    ```sh
    jupyter notebook scripts/Main.ipynb
    ```

### Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

### License

This project is licensed under the MIT License. See the LICENSE file for details.

### Acknowledgements

Riot Games for providing the data and API.
Contributors to the project.