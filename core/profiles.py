import os
import json
from datetime import datetime
import re
import shutil

BASE_DIR = os.path.join("Data", "Profiles")

def profile_path(name):
    return os.path.join(BASE_DIR, name)

def validate_profile_name(profile_name):
    if not profile_name:
        return False, "Profile name cannot be empty."
    name = profile_name.strip()
    if not name:
        return False, "Profile name cannot be empty."
    if name in {".", ".."}:
        return False, "Profile name is not allowed."
    if os.path.sep in name or (os.path.altsep and os.path.altsep in name):
        return False, "Profile name cannot include path separators."
    if name != os.path.basename(name):
        return False, "Profile name is not allowed."
    if not re.match(r"^[A-Za-z0-9 _-]+$", name):
        return False, "Profile name can only include letters, numbers, spaces, _ or -."
    return True, ""

def list_profiles():
    if not os.path.exists(BASE_DIR):
        return []
    profiles = [
        d for d in os.listdir(BASE_DIR)
        if os.path.isdir(profile_path(d))
    ]
    return sorted(profiles, key=str.lower)


def get_profile_dirs(profile_name):
    root = os.path.join(BASE_DIR, profile_name)

    dirs = {
        "root": root,
        "references": os.path.join(root, "references"),
        "captures": os.path.join(root, "captures"),
        "frames": os.path.join(root, "frames"),
        "debug": os.path.join(root, "debug"),
        "meta": os.path.join(root, "meta.json"),
    }

    for k, path in dirs.items():
        if k != "meta":
            os.makedirs(path, exist_ok=True)

    if not os.path.exists(dirs["meta"]):
        with open(dirs["meta"], "w") as f:
            json.dump({"name": profile_name}, f, indent=2)

    return dirs

def create_profile(profile_name):
    """
    Create a new profile with required folder structure.
    Returns (success, message).
    """
    valid, message = validate_profile_name(profile_name)
    if not valid:
        return False, message
    base = os.path.join(BASE_DIR, profile_name)

    if os.path.exists(base):
        return False, "A profile with that name already exists."

    os.makedirs(os.path.join(base, "frames"), exist_ok=True)
    os.makedirs(os.path.join(base, "references"), exist_ok=True)
    os.makedirs(os.path.join(base, "captures"), exist_ok=True)
    os.makedirs(os.path.join(base, "debug"), exist_ok=True)

    meta_path = os.path.join(base, "meta.json")
    with open(meta_path, "w") as f:
        json.dump(
            {
                "name": profile_name,
                "created_at": datetime.now().isoformat()
            },
            f,
            indent=2
        )

    return True, f"Profile '{profile_name}' created."

def delete_profile(profile_name):
    valid, message = validate_profile_name(profile_name)
    if not valid:
        return False, message
    base = os.path.realpath(BASE_DIR)
    target = os.path.realpath(profile_path(profile_name))
    if not target.startswith(base + os.path.sep):
        return False, "Invalid profile path."
    if not os.path.exists(target):
        return False, "Profile not found."
    shutil.rmtree(target)
    return True, f"Profile '{profile_name}' deleted."
