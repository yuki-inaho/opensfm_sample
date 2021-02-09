import click
import cv2
from tqdm import trange
from pathlib import Path
from scripts.utils import make_output_dir


@click.command()
@click.option("--input-mp4-path", "-i", default="./mp4/movie.mp4")
@click.option("--output-mp4-name", "-o", default="movie.mp4")
def main(input_mp4_path, output_mp4_name):
    reader = cv2.VideoCapture(input_mp4_path)

    n_flames = int(reader.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"Number of Frame: {n_flames}")

    frame_rate = 30.0
    ret, frame = reader.read()
    size = (frame.shape[1], frame.shape[0])

    fmt = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
    writer = cv2.VideoWriter(output_mp4_name, fmt, frame_rate, size)

    for i in trange(1, n_flames-1):
        ret, frame = reader.read()
        if ret: writer.write(frame)

    reader.release()
    writer.release()


if __name__ == "__main__":
    main()