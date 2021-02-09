import click
from tqdm import trange
import shutil
from pathlib import Path
from scripts.utils import make_output_dir


@click.command()
@click.option("--input-image-dir", "-i", default="./images")
@click.option("--config-directory-path", "-c", default="./cfg/")
@click.option("--output-project-dir", "-o", default="./project")
def main(input_image_dir, config_directory_path, output_project_dir):
    output_project_dir_path = Path(output_project_dir)
    make_output_dir(output_project_dir_path)

    # copy image directory
    shutil.copytree(input_image_dir, output_project_dir_path.joinpath("images"))

    # copy config files
    config_dir_path = Path(config_directory_path)
    config_file_pathlist = [str(path) for path in config_dir_path.glob("*")]
    for config_file_path in config_file_pathlist:
        config_file_name = Path(config_file_path).name
        shutil.copyfile(config_file_path, str(output_project_dir_path.joinpath(config_file_name)))    

if __name__ == "__main__":
    main()