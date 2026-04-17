FROM jupyterhub/jupyterhub:latest

# Install DockerSpawner and FirstUseAuthenticator
RUN pip install --no-cache-dir \
    dockerspawner \
    "dockerspawner>=12.0" \
    jupyterhub-firstuseauthenticator
