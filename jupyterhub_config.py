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

class LabDockerSpawner(DockerSpawner):
    def user_env(self, env):
        env['USER'] = 'jovyan'
        env['HOME'] = '/home/jovyan'
        env['PWD'] = '/home/jovyan'
        return env

c.JupyterHub.spawner_class = LabDockerSpawner

# images.json is re-read on every spawn request, so edits take effect without restart
_images_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images.json')

def options_form(spawner):
    with open(_images_path) as f:
        images = json.load(f)
    options_html = '\n'.join(
        f'<option value="{image}">{label}</option>'
        for label, image in images.items()
    )
    return f'''
        <label for="image">Select environment:</label><br>
        <select name="image" id="image" class="form-control">
            {options_html}
        </select>
    '''

def options_from_form(formdata):
    # Use 'selected_image' instead of 'image' to avoid DockerSpawner's
    # built-in image validation, which requires allowed_images to be set.
    return {'selected_image': formdata.get('image', [None])[0]}

c.DockerSpawner.options_form = options_form
c.DockerSpawner.options_from_form = options_from_form

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

# Single pre_spawn_hook: blocks admin, creates user dir, and sets the selected image
def pre_spawn_hook(spawner):
    if spawner.user.name == 'admin':
        raise Exception("Admin user cannot spawn a server. Please log in with a different user.")

    username = spawner.user.name
    volume_path = os.path.join('/data/jupyterhub/users', username)
    if not os.path.exists(volume_path):
        os.makedirs(volume_path, mode=0o755, exist_ok=True)
        os.chown(volume_path, 1000, 1000)

    selected_image = spawner.user_options.get('selected_image')
    if selected_image:
        with open(_images_path) as f:
            allowed = list(json.load(f).values())
        if selected_image not in allowed:
            raise Exception(f"Image '{selected_image}' is not in the allowed list.")
        spawner.image = selected_image

c.Spawner.pre_spawn_hook = pre_spawn_hook

# ==========================================
# 4. INTERNAL NETWORKING
# ==========================================
c.JupyterHub.hub_ip = '0.0.0.0'
c.JupyterHub.hub_connect_ip = 'jupyterhub'
