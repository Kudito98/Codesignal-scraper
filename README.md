[![license](https://img.shields.io/badge/license-MIT-green)](LICENSE)

# CONFIGURATION
Setup python venv and install selenium
```sh
cd PATH_TO_SCRAPER
python3 -m venv venv
source venv/bin/activate
pip install selenium
```

Check your chrome version and next download chromedriver from [this page](https://chromedriver.chromium.org/downloads)
```sh
google-chrome --version
```

Make scraper.py executable
```sh
chmod +x scraper.py
```

# USAGE OF SCRAPER
The methods to download tasks:
 -  Download all of task you finish
    ```sh
    ./scraper.py
    ```

 -  Download all of tasks in chosen chapter
    ```sh
    ./scraper.py CHAPTER
    ```
    for example:
    ```sh
    ./scraper.py Intro
    ```

 -  Download specific tasks in cosen chapter
    ```sh
    ./scraper.py CHAPTER -t [LIST OF TASKS]
    ```
    for example:
    ```sh
    ./scraper.py TheCore -t 21 37
    ```

Each downloaded task is stored in ``tasks/CHAPTER/id-name/`` directory.

# LICENSE
This project is relased by Kamil Kud under [MIT license](LICENSE)