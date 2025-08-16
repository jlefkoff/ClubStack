# ClubStack

ClubStack is a web application designed to help users manage their club memberships, events, gear rental, and merch sales. It provides a user-friendly interface for both club members and administrators to interact with the system.

This is based on the template repo for the CS 3200 Summer 2 2025 Course Project. 

## Running the Application

1. Make a copy of the `.env.template` file in the `api` folder and name it `.env`. Open the new `.env` file and on the last line, delete the `<...>` placeholder text, and put a password. Don't reuse any passwords you use for any other services (email, etc.)
2. Open a terminal and navigate to the root directory of the project.
3. Run the following command to start the application using Docker Compose:
   ```bash
   docker compose up -d
   ```
4. Open your web browser and go to `http://localhost:8501` to access the Streamlit app.

## Structure of the Repo

- The repo is organized into five main directories:
  - `./app` - the Streamlit app
  - `./api` - the Flask REST API
  - `./database-files` - SQL scripts to initialize the MySQL database

- The repo also contains a `docker-compose.yaml` file that is used to set up the Docker containers for the front end app, the REST API, and MySQL database.

- Demo Video: https://drive.google.com/file/d/17GzNVGHKVIn1pgBzuTkpCx4aZzuS44fN/view?usp=sharing
