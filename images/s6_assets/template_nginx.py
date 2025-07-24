import argparse
import json
import os
import django
from django.core.exceptions import AppRegistryNotReady, ImproperlyConfigured

from jinja2 import Template


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create Pulp's nginx conf file based on current settings.",
    )
    parser.add_argument("template_file", type=open)
    parser.add_argument("output_file", type=argparse.FileType("w"))
    args = parser.parse_args()

    https = os.getenv("PULP_HTTPS", "false")
    ui = os.getenv("PULP_UI", "false")
    values = {
        "https": https.lower() == "true",
        "api_root": "/pulp/",
        "content_path": "/pulp/content/",
        "domain_enabled": False,
        "ui": ui.lower() != "false",
    }

    try:
        django.setup()
        from django.conf import settings
    except (AppRegistryNotReady, ImproperlyConfigured):
        print("Failed to find settings for nginx template, using defaults")
    else:
        values["api_root"] = settings.API_ROOT
        values["content_path"] = settings.CONTENT_PATH_PREFIX
        values["domain_enabled"] = getattr(settings, "DOMAIN_ENABLED", False)

    if values["ui"]:
        static = os.getenv("PULP_STATIC_ROOT", "/var/lib/operator/static/")
        values["pulp_ui_static"] = f"{static}pulp_ui/"
        if os.path.exists(values["pulp_ui_static"]):
            ui_config_path = f'{values["pulp_ui_static"]}pulp-ui-config.json'
            if os.path.exists(ui_config_path):
                with open(ui_config_path, "r") as f:
                    ui_config = json.load(f)
                api_base_path = f"{values['api_root']}api/v3/"
                if ui_config["API_BASE_PATH"] != api_base_path:
                    ui_config["API_BASE_PATH"] = api_base_path
                    with open(ui_config_path, "w") as f:
                        json.dump(ui_config, f)
        else:
            print(f"Failed to find the pulp-ui static files at {values['pulp_ui_static']}")
            values["ui"] = False

    template = Template(args.template_file.read())
    output = template.render(**values)
    args.output_file.write(output)
