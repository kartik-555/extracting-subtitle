# Subtitle Project

This project is a Django application for managing subtitles. Below are the instructions to run the project either locally or using Docker.

## Prerequisites

- Python 3.9+
- PostgreSQL
- Docker (optional, for running with Docker)
- Docker Compose (optional, for running with Docker)

## Running Locally

1. **Clone the repository**:
    ```bash
    git clone https://github.com/kartik-555/extracting-subtitle.git
    cd extracting-subtitle
    ```

2. **Create and activate a virtual environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the dependencies**:
    ```bash
    pip install --upgrade pip
    pip install -r requirements.txt
    ```

4. **Set up the database**:
    - Ensure PostgreSQL is running.
    - Create a database named `fatmug`.
    - Update the `DATABASES` settings in `subtitle/settings.py` if necessary.

5. **Apply migrations**:
    ```bash
    python manage.py migrate
    ```

6. **Run the development server**:
    ```bash
    python manage.py runserver
    ```

## Running with Docker

1. **Clone the repository**:
    ```bash
    git clone https://github.com/kartik-555/extracting-subtitle.git
    cd extracting-subtitle
    ```

2. **Build and run the Docker containers**:
    ```bash
    docker-compose up --build
    ```

3. **Apply migrations**:
    ```bash
    docker-compose exec web python manage.py migrate
    ```

4. **Access the application**:
    Open your browser and go to `http://localhost:8000`.

## Additional Commands

- **Create a superuser**:
    ```bash
    python manage.py createsuperuser  # For local
    docker-compose exec web python manage.py createsuperuser  # For Docker
    ```

- **Collect static files**:
    ```bash
    python manage.py collectstatic  # For local
    docker-compose exec web python manage.py collectstatic  # For Docker
    ```

## Environment Variables

Ensure the following environment variables are set:

- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `DB_HOST`
- `DB_PORT`
- `RUNNING_IN_DOCKER` (set to `1` when running in Docker)

## Note
## Note

- I have used `ccextractor` with bash commands from the view function to extract subtitles from video files. To test the functionality, I used videos provided by the `ccextractor` repository. However, these videos do not have embedded subtitles, so the `ccextractor` tool was unable to extract subtitles from them. The functionality is complete but only tested with the videos from the `ccextractor` repository.

- I faced several problems while dockerizing the `ccextractor` image with other libraries. I was unable to resolve these issues within the required time. The images available on Docker Hub do not run well in the application. Therefore, the Docker image of this application may not run as expected. However, the project will run perfectly if set up on a local machine.