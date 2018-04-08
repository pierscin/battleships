[![Build Status](https://travis-ci.org/pierscin/battleships.svg?branch=master)](https://travis-ci.org/pierscin/battleships)
[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](https://raw.githubusercontent.com/pierscin/battleships/master/LICENSE)

# battleships

💥Battleships with Python and Flask.

Version with Flask and SQLite database.

## Quick setup

Create virtual environment in cloned/downloaded repository and install required packages.

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

After activating venv, tests can be run from the root of this repository with:

```
pytest
```

To **run application** `FLASK_APP` has to point where `app`:

```
export FLASK_APP=battleships.py
```

Database setup commands:

```
flask db init
flask db migrate
flask db upgrade
```

Running the app:
```
flask run
```
