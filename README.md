# League of Legends Data Analysis

This project is designed to analyze data from a set of league of legends ranked game, and use it to determine the win probability of a live game in order to make correct predictions on twitch.tv

## Files and Directories

- `better.py`: The flask app responsible for returning the win probabilities of a given game.
- `champion_data.json`: JSON file containing champion names and IDs.
- `classifier.pkl`: Pickle file containing a pre-trained classifier model.
- `gameInfo.csv`: CSV file containing the ranked game dataset for this project.
- `opgg`: Temporary library to use the opgg.py.v2 library until it gets published to pip.
- `requirements.txt`: List of required Python packages.
- `scripts`: Directory containing various scripts for data manipulation, scraping, and analysis.
  - `combine.py`: Script for combining data from multiple sources.
  - `Main.ipynb`: Jupyter notebook for data analysis and visualization. Used to generate the classifier we use.
  - `main.py`: Main script used to generate the dataset.
  - `scrape.py`: Script for scraping champion winrate data.
  - `season1414.*.csv`: CSV files containing champion winrate for each champion per rank for different patches during season 14.
- `extension`: Directory containing all the neccessary files to run the chrome extension part of this project.

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
1. Install the chrome extension
    - Open up chrome://extensions/ on your chrome browser
    - Enable developer mode
    - Click load unpacked
    - Select the extension folder found in this repository<br><br>

    It may be helpful to pin this extension when setting up everything.<br><br>

2. Run the main script:
    ```sh
    python better.py
    ```
    This will start the flask app that will be returning API calls. Ensure this is running whenever you're using the extension.<br><br>
3. Use the chrome extension
    Once you input all neccesary fields and toggle the extension on, it should make automatic bets whenever the program deems it profitable.

### Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

### License

This project is licensed under the MIT License. See the LICENSE file for details.

### Acknowledgements

Riot Games for providing the data and API.
The OPGG.py library author for his help in answering questions and implementing useful functions while working on this project.
Contributors to the project.