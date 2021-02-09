import click
import cv2
from tqdm import trange
from pathlib import Path
from scripts.utils import make_output_dir


@click.command()
@click.option("--input-mp4-path", "-i", default="./mp4/movie.mp4")
@click.option("--output-dir", "-o", default="images")
@click.option("--viewer-mode", "-v", is_flag=True)
def main(input_mp4_path, output_dir, viewer_mode):
    output_dir_path = Path(output_dir)
    make_output_dir(output_dir_path, clean=True)
    cap = cv2.VideoCapture(input_mp4_path)
    
    n_flames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"Number of Frame: {n_flames}")

    for i in trange(n_flames):
        ret, frame = cap.read()
        image_name = f"{i:0=3}.jpg"
        output_image_path = str(output_dir_path.joinpath(image_name))
        cv2.imwrite(output_image_path, frame)

        if not ret:
            break
        if viewer_mode:
            cv2.imshow("frame", frame)

        key = cv2.waitKey(1)

    cap.release()
    if viewer_mode:
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()