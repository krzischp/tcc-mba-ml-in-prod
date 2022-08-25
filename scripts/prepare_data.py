import os
import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dataset",
        "-d",
        type=str,
        required=True,
        help="Path to the dataset (should be extracted)",
    )
    parser.add_argument(
        "--output", "-o", type=str, required=True, help="Path to dump prepared dataset"
    )

    args = parser.parse_args()
    data = pd.read_csv(os.path.join(args.dataset, "styles.csv"), error_bad_lines=False)

    # get images from folder to leave records with existed image id
    images = [
        int(Path(file_name).stem)
        for file_name in os.listdir(os.path.join(args.dataset, "images"))
    ]

    data = data[data["id"].isin(images)]
    data["year"] = data["year"].apply(
        lambda y: str(int(y)) if not np.isnan(y) else "null"
    )

    target_folder = Path(args.output).parent
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    print(f"Generated csv file with {len(data)} records")
    data.to_csv(args.output, header=False)


if __name__ == "__main__":
    main()
