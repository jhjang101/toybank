# Toy Bank Application
A minimalist toy bank built with Python (Flask) and SQLite. This project is primarily intended to manage allowance for my daughter. 

## Quick Start (Docker)
The easiest way to get the Toy Bank running is using Docker Compose.

1. Create Directory
    ```sh
    mkdir toybank
    cd toybank
    ```
2. Create `compose.yaml` and paste the configuration example below.
    ```yaml
    services:
    toybank:
        # Use the image you built locally with the updated app.py file
        image: ghcr.io/jhjang101/toybank:latest

        # Give container name
        container_name: toybank

        # Instruct Docker to restart the container if it stops unexpectedly
        restart: always 
        
        # Map the container port (8000) to the host machine port (8000)
        ports:
        - "8000:8000"

        # This overrides the enviroment settings from the .env file in the image
        environment:
        - ACCOUNT_HOLDER_NAME=Arya # Change to account holder's name
        - TELLER_PASSWORD=0000 # This overrides the default password from the .env file in the image
        
        # Map the data folder in the container to one on the host
        volumes:
        - ./data:/usr/src/app/app/data
    ```

3. Start the service
    ```sh
    docker compose up -d
    ```
4. Access
The application will be available in your web browser:

    URL: http://localhost:8000
