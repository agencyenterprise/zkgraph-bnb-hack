#!/bin/sh

# Configuration variables
WORKER_IMAGE="kevinkonsaestudio/worker:latest"
WORKER_CONTAINER_NAME="zkGraph-worker"

# Function to check Docker status
check_docker_status() {
    if ! command -v docker &> /dev/null; then
        echo "not_installed"
    elif ! docker info &> /dev/null; then
        if docker info 2>&1 | grep -q "Cannot connect to the Docker daemon"; then
            echo "not_running"
        else
            echo "no_permission"
        fi
    else
        echo "running"
    fi
}

# Check Docker status
docker_status=$(check_docker_status)

echo "============== zkGraph Worker Setup ======================"
echo "==============     [BSC testnet]    ======================"
echo "==============    https://0k.wtf    ======================"


echo "Checking Docker status..."

case "$docker_status" in
    "not_installed")
        echo "Docker is not installed. Please install Docker and ensure you have permissions to run Docker commands."
        echo "Visit https://docs.docker.com/get-docker/ for installation instructions."
        exit 1
        ;;
    "not_running")
        echo "The Docker daemon is not running. Please start the Docker daemon and try again."
        echo "On most systems, you can start Docker with:"
        echo "sudo systemctl start docker    # For systemd-based systems"
        echo "sudo service docker start      # For init.d-based systems"
        echo "On macOS, launch the Docker Desktop application."
        exit 1
        ;;
    "no_permission")
        echo "You don't have permission to run Docker commands."
        echo "Ensure your user is part of the Docker group:"
        echo "sudo usermod -aG docker $USER"
        echo "After adding yourself to the Docker group, you'll need to log out and log back in for the changes to take effect."
        exit 1
        ;;
    "running")
        echo "\nDocker is running and you have the necessary permissions.\n"
        ;;
    *)
        echo "An unknown error occurred while checking Docker status."
        exit 1
        ;;
esac

# Prompt for BSC wallet address (optional)
echo "Please enter your BSC wallet public key for receiving payments (press Enter to skip):"
read wallet_address

# Prepare Docker run command
docker_run_cmd="docker run -d -p 8000:8000"
if [ -n "$wallet_address" ]; then
    docker_run_cmd="$docker_run_cmd -e WORKER_WALLET=$wallet_address"
fi
docker_run_cmd="$docker_run_cmd --name $WORKER_CONTAINER_NAME $WORKER_IMAGE"

# Pull the latest Docker image
echo "Pulling the latest worker Docker image..."
if ! docker pull "$WORKER_IMAGE"; then
    echo "Error: Failed to pull Docker image. Please check your internet connection and Docker installation."
    exit 1
fi

# Run the Docker container
echo "Starting the worker container..."
if ! eval "$docker_run_cmd"; then
    echo "Error: Failed to start the worker container. Please check the error message above."
    exit 1
else
    echo "Worker container started successfully!"
    echo "You can check the logs with: docker logs $WORKER_CONTAINER_NAME"
fi
