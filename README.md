[![Build Status](https://travis-ci.org/pierscin/battleships.svg?branch=master)](https://travis-ci.org/pierscin/battleships)
[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](https://raw.githubusercontent.com/pierscin/battleships/master/LICENSE)

# battleships

💥Battleships with Python and Flask. It is meant to be a showcase of
patterns I often use in my projects. More in [this chapter](#very-useful-code-snippets)

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


## Very useful code snippets

Those can be often copy-pasted to the new project and tailored to fit your needs.

- [application factory](https://github.com/pierscin/battleships/app/__init__.py#L16)
- [Config class](https://github.com/pierscin/battleships/blob/6f4688f51a56f34446cd2e2d7baaed93c125e1ab/config.py#L11)
- `pytest` fixtures for [app creation](https://github.com/pierscin/battleships/blob/6f4688f51a56f34446cd2e2d7baaed93c125e1ab/tests/conftest.py#L8),
[in-memory db](https://github.com/pierscin/battleships/blob/6f4688f51a56f34446cd2e2d7baaed93c125e1ab/tests/conftest.py#L22),
[session with changes reversal](https://github.com/pierscin/battleships/blob/6f4688f51a56f34446cd2e2d7baaed93c125e1ab/tests/conftest.py#L33)
and Flask [api test client](https://github.com/pierscin/battleships/blob/6f4688f51a56f34446cd2e2d7baaed93c125e1ab/tests/conftest.py#L48)
- api blueprint with [ApiResult](https://github.com/pierscin/battleships/blob/6f4688f51a56f34446cd2e2d7baaed93c125e1ab/app/api/__init__.py#L4),
[ApiException](https://github.com/pierscin/battleships/blob/6f4688f51a56f34446cd2e2d7baaed93c125e1ab/app/api/__init__.py#L17) classes, Flask
[response converter](https://github.com/pierscin/battleships/blob/6f4688f51a56f34446cd2e2d7baaed93c125e1ab/app/api/__init__.py#L31)
and custom [exception handler](https://github.com/pierscin/battleships/blob/6f4688f51a56f34446cd2e2d7baaed93c125e1ab/app/api/error_handlers.py#L5)
- [api_schema](https://github.com/pierscin/battleships/blob/6f4688f51a56f34446cd2e2d7baaed93c125e1ab/app/api/utils.py#L10) decorator for natural validation of requests
- [token_required](https://github.com/pierscin/battleships/blob/6f4688f51a56f34446cd2e2d7baaed93c125e1ab/app/api/utils.py#L36) decorator for checking jwt token and injecting decoded data to decorated method

