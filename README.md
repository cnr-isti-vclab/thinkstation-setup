# thinkstation-setup

This repository contains the configuration files and setup scripts for deploying a JupyterHub instance on a ThinkStation with GPU support. The setup uses Docker to manage the JupyterHub environment and its dependencies.

# Setup Instructions

1. Clone the repository to your local machine:

   ```bash
   git clone https://github.com/cnr-isti-vclab/thinkstation-setup.git
   ```

2. Navigate to the cloned directory:

   ```bash
   cd thinkstation-setup
    ```
3. Run the setup script to create necessary directories, set permissions, pull Docker images, and start the JupyterHub service:
    ```bash
    ./setup.sh
    ```

4. To access the Portainer interface, open your web browser and navigate to `http://localhost:9000`. You can log in with the default credentials (admin/admin) and change them after the first login.

5. To access JupyterHub, open your web browser and navigate to `http://localhost:8000`. 
    - Log in with the `admin` username to create new user accounts. You can create additional users as needed.

# Data Storage

JupyterHub data and user directories are located at `/data/jupyterhub` on the host machine. This directory is mounted as a volume in the Docker container, allowing JupyterHub to read and write user data and configurations.

JupyterHub data is stored in the `jupyterhub_data` Docker volume, which is also mounted to the container. This setup ensures that user data persists even if the container is recreated.

Portainer data is stored in the `portainer_data` Docker volume, which is mounted to the Portainer container. This allows Portainer to maintain its state and configurations across container restarts.
