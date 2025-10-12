import argparse
import sys
import os
import xml.etree.ElementTree as ET


def parse_config(config_path: str):
    if not os.path.isfile(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    try:
        tree = ET.parse(config_path)
    except ET.ParseError as e:
        raise ValueError(f"Invalid XML in configuration file: {e}")

    root = tree.getroot()

    def get_required_text(tag: str) -> str:
        elem = root.find(tag)
        if elem is None:
            raise ValueError(f"Missing required configuration parameter: <{tag}>")
        text = elem.text
        if text is None or text.strip() == "":
            raise ValueError(f"Configuration parameter <{tag}> is empty or whitespace-only")
        return text.strip()

    package_name = get_required_text("package_name")
    repository = get_required_text("repository")
    mode = get_required_text("mode")

    return {
        "package_name": package_name,
        "repository": repository,
        "mode": mode,
    }


parser = argparse.ArgumentParser(description="Package dependency graph visualizer (Stage 1 prototype)")
parser.add_argument(
    "--config",
    required=True,
    help="Path to the XML configuration file"
)
args = parser.parse_args()

try:
    config = parse_config(args.config)
    for key, value in config.items():
        print(f"{key}={value}")
except (FileNotFoundError, ValueError) as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)