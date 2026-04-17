import json
import os
c = get_config()

# ==========================================
# 1. AUTHENTICATION (FirstUse Authenticator)
# ==========================================
c.JupyterHub.authenticator_class = 'firstuseauthenticator.FirstUseAuthenticator'

# The file where passwords will be stored securely and persistently
c.FirstUseAuthenticator.dbm_path = '/srv/jupyterhub/passwords.dbm'

# IMPORTANT: Prevents anyone from logging in unless the admin has created them first
c.FirstUseAuthenticator.create_users = False

# Define who has admin privileges
c.Authenticator.admin_users = {'admin'}
c.Authenticator.allowed_users = {'admin'}

# ==========================================
# 2. SPAWNER AND LAUNCH RULES
# ==========================================
from dockerspawner import DockerSpawner

# Block server spawning for the admin
def prevent_admin_spawn(spawner):
    if spawner.user.name == 'admin':
        raise Exception("Admin user cannot spawn a server. Please log in with a different user.")

c.Spawner.pre_spawn_hook = prevent_admin_spawn

class LabDockerSpawner(DockerSpawner):
    def user_env(self, env):
        env['USER'] = 'jovyan'
        env['HOME'] = '/home/jovyan'
        env['PWD'] = '/home/jovyan'
        return env

c.JupyterHub.spawner_class = LabDockerSpawner

# Dropdown menu for users (loaded from images.json)
_images_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images.json')
with open(_images_path) as _f:
    c.DockerSpawner.allowed_images = json.load(_f)

c.DockerSpawner.notebook_dir = '/home/jovyan/work'
c.DockerSpawner.network_name = 'lab_network'
c.DockerSpawner.remove = True

c.DockerSpawner.extra_host_config = {
    'device_requests': [
        {
            'Driver': 'nvidia',
            'Capabilities': [['gpu']],
            'Count': -1,  
        }
    ]
}

# ==========================================
# 3. DATA PERSISTENCE (VOLUMES)
# ==========================================

# Define where to mount the directories
c.DockerSpawner.volumes = {
    # Private folder: each user will have their own subfolder based on their username
    '/data/jupyterhub/users/{username}': '/home/jovyan/work',
    
    # Shared datasets folder: read-only ('ro' = read only)
    '/data/jupyterhub/shared_datasets': {
        'bind': '/home/jovyan/datasets',
        'mode': 'ro'
    }
}

# Ensure JupyterHub creates the user's directory if it does not exist
def create_dir_hook(spawner):
    username = spawner.user.name
    volume_path = os.path.join('/data/jupyterhub/users', username)
    if not os.path.exists(volume_path):
        os.makedirs(volume_path, mode=0o755, exist_ok=True)
        # Change ownership to the jovyan user (1000)
        os.chown(volume_path, 1000, 1000)

c.Spawner.pre_spawn_hook = create_dir_hook

# ==========================================
# 4. INTERNAL NETWORKING
# ==========================================
c.JupyterHub.hub_ip = '0.0.0.0'
c.JupyterHub.hub_connect_ip = 'jupyterhub'
