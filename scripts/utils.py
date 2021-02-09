import shutil
from pathlib import PosixPath

def make_output_dir(output_image_dir_path: PosixPath):
    if output_image_dir_path.exists():
        shutil.rmtree(str(output_image_dir_path))
    output_image_dir_path.mkdir()
