# Use an official Python runtime as a parent image
FROM python:3.12.3

# Set environment variables to prevent Python from writing pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set environment variable for Poetry to avoid creating a virtual environment
ENV POETRY_VIRTUALENVS_CREATE=false

# Install curl and the required build tools
RUN apt-get update && apt-get install -y curl build-essential

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to the system PATH
ENV PATH="/root/.local/bin:$PATH"

# Create a directory for the app
WORKDIR /app

# Copy only the dependency declaration files to cache the Docker build
COPY pyproject.toml poetry.lock /app/

# Install dependencies
RUN poetry install --no-root --no-dev

# Copy the entire project
COPY . /app

# Expose the port FastAPI will run on
EXPOSE 8000

# Run the application using Uvicorn with Gunicorn in production
CMD ["poetry", "run", "gunicorn", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "main:app", "--workers", "2"]