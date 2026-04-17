FROM jupyterhub/jupyterhub:latest

# Install DockerSpawner and FirstUseAuthenticator
RUN pip install --no-cache-dir \
    dockerspawner \
    jupyterhub-firstuseauthenticator
