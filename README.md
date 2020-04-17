# Kivy Video Form
Desktop App developed using kivy (open source Python library for user interface design). Login screen to log to the main window and play or stop two different videos. Create user window to create a new user, new user is only created if the username and the email are not already created (email and username are unique in the database).


## Requirements
 - Python 3.5 or higher
 - Python libraries:
   - kivy 1.11.1
   - opencv-python
 - DB Browser for SQLite (only if needed to visualize the databases)

## Installation
To use in a python3 virtual environment, create the environment, activate it and run:

    $ pip3 install -r requirements.txt

If you do not use virtual environment, download the kivy library from source following the steps in the guide [Manually installing Kivy from source](https://kivy.org/doc/stable/installation/installation-linux-venvs.html#installation-in-venv) and install opencv as you prefer (from source or pip3 installation).

Another way of installing kivy from source:

    sudo add-apt-repository ppa:kivy-team/kivy-daily
    sudo apt-get update
    sudo apt-get install python3-kivy

To install DB Browser for SQLite follow the instructions in [DB Browser Downloads](https://sqlitebrowser.org/dl/).

## Videos
The test videos were downloaded from pexels:
 - [Video of a flower field](https://www.pexels.com/video/video-of-flower-field-854700/) 
 - [Video of a landscape](https://www.pexels.com/video/from-dusk-to-dawn-1621682/)
