# Assignment 1
Assignment 1 Repo

# Requirements
- Python 3.12
- Flask

# Guidelines

## Setup
- Clone the repository
- Install the requirements using `pip install -r requirements.txt`
- Run the app using `python3 app.py`

# API

## Headers Required
- Content-Type: application/json

## Endpoints

- POST /register
    - Register a new user
    - Request Body: {"username": "username", "password": "password"}
    - Response: 201 if successful, 400 if failed

- POST /login
    - Login a user
    - Request Body: {"username": "username", "password": "password"}
    - Response: 200 if successful, 401 if failed

- POST /changepw
    - Change password of a user
    - Request Body: {"username": "username", "old_password": "old_password", "new_password": "new_password"}
    - Response: 201 if successful, 400 if failed

- GET /admin
    - Get admin access using cookies from login
    - only admin can access
    - Response: 200 if successful, 401 if failed

- GET /user
    - Get user access using cookies from login
    - Response: 200 if successful, 401 if failed