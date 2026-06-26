import glob
from text import lower
from fs import replace_text, delete_files, remove_dependabot_ecosystem

def setup_frontend(default_mod, config_mod):
    def_name = default_mod["name"]
    cfg_name = config_mod["name"]
    def_pkg = default_mod["package"]
    cfg_pkg = config_mod["package"]

    def_lower = lower(def_name)
    cfg_lower = lower(cfg_name)

    # Replacements for app.config.js
    config_file = "frontend/apps/expo/app.config.js"
    replace_text(config_file, def_pkg, cfg_pkg)
    replace_text(config_file, def_name, cfg_name)
    replace_text(config_file, def_lower, cfg_lower)

    # Replace lower case name in all workspace configurations and workflows
    other_files = [
        ".github/workflows/frontend-web.yml",
        ".github/workflows/frontend-android.yml",
        ".github/workflows/frontend-ci.yml",
        "frontend/package.json",
        "frontend/apps/expo/package.json",
        "frontend/apps/expo/tsconfig.json",
        "frontend/apps/expo/eslint.config.mjs",
        "frontend/packages/api-client/package.json"
    ]
    for f in other_files:
        replace_text(f, def_lower, cfg_lower)

def delete_frontend():
    delete_files("frontend")
    # Delete GitHub workflows
    for f in glob.glob(".github/workflows/frontend-*.yml"):
        delete_files(f)
    remove_dependabot_ecosystem("/frontend")
