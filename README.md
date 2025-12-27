# Toy Bank Application
A minimalist toy bank built with Python (Flask) and SQLite. This project is primarily intended to manage allowance for my daughter. 

## Quick Start (Docker)
The easiest way to get the Toy Bank running is using Docker Compose.

1. Create Directory
    ```sh
    mkdir toybank
    cd toybank
    ```
2. Download `.env.example` and change name to `.env`. 

3. Create `compose.yaml` and paste the configuration example below.
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

        # read .env file and set variables as environment variables into the container
        env_file:
        - .env
        
        # Map the data folder in the container to one on the host
        volumes:
        - ./data:/toybank/app/data
    ```

4. Start the service
    ```sh
    docker compose up -d
    ```
5. Access
The application will be available in your web browser:

    URL: http://localhost:8000
