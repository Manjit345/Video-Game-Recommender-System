# Steam Video Games Recommender System 🎮

## Project Overview
From playing Mario, Pac-Man, Pinball in Arcade Game Shops or touchpad phones to games like God of War, Batman Arkham Trilogy, Tomb Raider and many more in desktops, playstations and Nintendo Switch we have all grown up. Steam happens to be a platform consisting of a multitude of games. If you are someone who is into video games a lot then you might have come across it. You then must have played and finished a game from there and wondered what else you could play. Then this video game recommender system is just the right place for you. Here, you could gather information about which other games you would like based on your taste in them or are popular amongst other users.

</div>

<div align="center">

<img src="https://raw.githubusercontent.com/Manjit345/Video-Game-Recommender-System/main/app.gif" alt="application gif" width="400"/>

</div>

## How to install and run the application

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/Video-Game-Recommender-System.git
cd Video-Game-Recommender-System
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Download the Kaggle Dataset
You need to download the Kaggle dataset using which the model is trained from the link given below :
```
https://www.kaggle.com/datasets/antonkozyriev/game-recommendations-on-steam
```
Download them in the form of a zip file and extract the files in your cloned repository.

#### Note - The games_metadata.json file should be in correct format i.e storing all the objects in an array by adding square brackets [] at the very beginning and very end of the file and adding a comma at the end of each object/line. This step is crucial as if the file is not formatted correctly then the notebook code to fetch data from JSON file will throw an error.

### 4. Run the Jupyter Notebook File
You need to click Run All in the "model_training.ipynb" file to train and store the model in the form of "model.pkl". This step is necessary as I am unable to upload my pretrained model to GitHub due to the file size restrictions.


### 5. Run the application
```bash
streamlit run game_recommender.py
```

## How It Works
1. There is a list of games extracted from the Kaggle dataset
2. Select a game which you have played before
3. Click on Get Recommendations button
4. Let the model find you the best recommendations
5. A set of 5 games will be recommended to you based on your selection.


## License
This project is open-source and available under the MIT License.

## Contact
For issues or questions, please open a GitHub issue.
