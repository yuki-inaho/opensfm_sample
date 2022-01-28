import cv2
import click
import numpy as np
from pathlib import Path
from tqdm import tqdm
from scripts.utils import make_output_dir
import json


def colorize_int_image(img, max_var=1024):
    img_colorized = np.zeros([img.shape[0], img.shape[1], 3]).astype(np.uint8)
    img_colorized[:, :, 1] = 255
    img_colorized[:, :, 2] = 255

    img_hue = img.copy().astype(np.float32)
    img_hue[np.where(img_hue > max_var)] = 0
    zero_idx = np.where((img_hue > max_var) | (img_hue == 0))
    img_hue *= 255.0 / max_var
    img_colorized[:, :, 0] = img_hue.astype(np.uint8)
    img_colorized = cv2.cvtColor(img_colorized, cv2.COLOR_HSV2RGB)
    img_colorized[zero_idx[0], zero_idx[1], :] = 0
    return img_colorized


class RGBDImage:
    def __init__(self, rgb_image_path, depth_image_path, max_depth=100):
        self._rgb_image_path = rgb_image_path
        self._depth_image_path = depth_image_path
        self._rgb_image = cv2.imread(str(rgb_image_path))
        self._image_height, self._image_width, _ = self._rgb_image.shape
        depth_npz = np.load(depth_image_path)
        depth_image_normalized = depth_npz["depth"] / max_depth
        depth_image_normalized = np.clip(depth_image_normalized, 0, 1.0)
        depth_image_uc1 = np.floor(depth_image_normalized * 1024).astype(np.int16)
        depth_image_resized = cv2.resize(depth_image_uc1, self.image_size)
        self._depth_image = depth_image_resized
        self._depth_image_colorized = colorize_int_image(self._depth_image, max_depth)
        self._max_depth = max_depth

    @property
    def configured_max_depth(self):
        return self._max_depth

    @property
    def rgb(self):
        return self._rgb_image

    @property
    def depth(self):
        return self._depth_image

    @property
    def depth_colorized(self):
        return self._depth_image_colorized

    @property
    def rgb_name(self):
        suf = Path(self._rgb_image_path).suffix
        return Path(self._rgb_image_path).name.replace(suf, ".jpg")

    @property
    def depth_name(self):
        return self.rgb_name.replace(".jpg", ".png")

    @property
    def depth_colorized_name(self):
        return self.rgb_name

    @property
    def image_size(self):
        return (self._image_width, self._image_height)


def extract_rgbd_result(rgb_dir_path, depth_dir_path, max_depth_configuration):
    rgbd_obj_list = []

    rgb_path_list = [path for path in rgb_dir_path.glob("*") if path.suffix in [".png", ".jpg", ".jpeg"]]

    print("Data is loading...")
    for rgb_image_path in tqdm(rgb_path_list):
        rgb_image_name = rgb_image_path.name
        image_height, image_width, _ = cv2.imread(str(rgb_image_path)).shape
        depth_image_path = Path(
            depth_dir_path,
            rgb_image_name + ".clean.npz",
        )

        # print([key for key in depth_npz.keys()])  -> 'depth', 'plane', 'score'
        rgbd_obj = RGBDImage(rgb_image_path, depth_image_path, max_depth=max_depth_configuration)
        rgbd_obj_list.append(rgbd_obj)
    return rgbd_obj_list


@click.command()
@click.option("--input-dir", "-i", default="./project")
@click.option("--output-dir-name", "-o", default="rgbd")
@click.option("--max-depth-configuration", "-m", default=100.0)
def main(input_dir, output_dir_name, max_depth_configuration):
    output_dir_path = Path(input_dir).joinpath(output_dir_name)
    make_output_dir(output_dir_path, clean=True)
    make_output_dir(output_dir_path.joinpath("rgb"))
    make_output_dir(output_dir_path.joinpath("depth"))
    make_output_dir(output_dir_path.joinpath("depth_colorized"))

    input_dir_path = Path(input_dir)
    rgb_dir_path = input_dir_path.joinpath("undistorted/images")
    depth_dir_path = input_dir_path.joinpath("undistorted/depthmaps")

    """Load RGB and Depth info
    """
    # @TODO: generate rgbd_obj sequentially, to reduce memory use
    rgbd_depth_obj_list = extract_rgbd_result(rgb_dir_path, depth_dir_path, max_depth_configuration)
    print("Saving images ...")
    for rgbd_obj in tqdm(rgbd_depth_obj_list):
        rgb_save_path = output_dir_path.joinpath("rgb", f"{rgbd_obj.rgb_name}")
        depth_save_path = output_dir_path.joinpath("depth", f"{rgbd_obj.depth_name}")
        depth_colorized_save_path = output_dir_path.joinpath("depth_colorized", f"{rgbd_obj.depth_colorized_name}")

        cv2.imwrite(str(rgb_save_path), rgbd_obj.rgb)
        cv2.imwrite(str(depth_save_path), rgbd_obj.depth)
        cv2.imwrite(str(depth_colorized_save_path), rgbd_obj.depth_colorized)
        cv2.waitKey(10)

    """ Dump meta information
    """
    with open(input_dir_path.joinpath("camera_models.json"), "r") as f:
        _camera_models = json.load(f)
        camera_models = [val for val in _camera_models.values()][0]
    info_dict = {
        "max_depth": max_depth_configuration,
        "width": camera_models["width"],
        "height": camera_models["height"],
        "focal": camera_models["focal"],
    }
    output_json_path = str(output_dir_path.joinpath("meta.json"))
    with open(output_json_path, "w") as f:
        json.dump(info_dict, f)

    print("Done")


if __name__ == "__main__":
    main()
