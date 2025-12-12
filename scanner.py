import os
import json


def is_laravel_project(path):
    artisan_path = os.path.join(path, 'artisan')
    composer_path = os.path.join(path, 'composer.json')

    if not os.path.isfile(artisan_path):
        return False

    if not os.path.isfile(composer_path):
        return False

    try:
        with open(composer_path, 'r') as f:
            composer = json.load(f)
        dependencies = composer.get('require', {})
        if 'laravel/framework' in dependencies:
            return True
    except Exception:
        return False

    return False


def scan_for_laravel_projects(root_dir):
    laravel_projects = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        if is_laravel_project(dirpath):
            laravel_projects.append(dirpath)
            dirnames.clear()  # Avoid scanning subdirs of this project
    return laravel_projects
