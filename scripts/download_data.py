import os
import argparse
import requests
import yaml


def download_data(yaml_path: str, dest_dir: str) -> None:
    """Download all files specified in a YAML config to dest_dir.

    Args:
        yaml_path: Path to the YAML file listing datasets to download.
        dest_dir: Directory where downloaded files will be saved.
    """
    os.makedirs(dest_dir, exist_ok=True)

    with open(yaml_path, "r") as f:
        entries = yaml.safe_load(f)

    for entry in entries:
        for name, info in entry.items():
            url = info["url"]
            filename = os.path.join(dest_dir, os.path.basename(info["filename"]))
            description = info.get("description", "")

            if os.path.exists(filename):
                print("Skipping {} (already exists): {}".format(name, filename))
                continue

            print("Downloading {}: {}".format(name, description))
            print("  {} -> {}".format(url, filename))

            response = requests.get(url, stream=True)
            response.raise_for_status()

            with open(filename, "wb") as out_file:
                for chunk in response.iter_content(chunk_size=8192):
                    out_file.write(chunk)

            print("  Done.")


if __name__ == "__main__":
    def parse_args():
        parser = argparse.ArgumentParser(description="Download datasets listed in a YAML config file.")
        parser.add_argument("-y", "--yaml", help="Path to download_data.yaml", required=False,
                            type=str, default="download_data.yaml")
        parser.add_argument("-d", "--dest", help="Destination directory for downloads", required=False,
                            type=str, default="zfin_test_data")
        return parser.parse_args()

    args = parse_args()
    download_data(args.yaml, args.dest)
