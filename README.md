# Toy Bank Application
A minimalist toy bank built with Python (Flask) and SQLite. This project is primarily intended to manage allowance for my daughter. 

## Quick Start (Docker)
The easiest way to get the Toy Bank running is using Docker Compose.

1. Create Directory
    ```sh
    mkdir toybank
    cd toybank
    ```
2. Get `.env` file.
    ```sh
    wget -O .env https://raw.githubusercontent.com/jhjang101/toybank/main/.env.example
    ```

3. Get `compose.yaml` file.
    ```sh
    wget https://raw.githubusercontent.com/jhjang101/toybank/main/compose.yaml
    ```

4. Start the service
    ```sh
    docker compose up -d
    ```
5. Access
The application will be available in your web browser:

    URL: http://localhost:8000
