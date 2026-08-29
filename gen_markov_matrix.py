import math
import os
import pandas as pd
import numpy as np
from argparse import ArgumentParser
import config
import matplotlib.pyplot as plt
import seaborn as sns   

states = config.CONFIG["states"]

def load_list(file_path):
    list_data = []
    df = (pd.read_excel(file_path, usecols = "D", header = None)).values.tolist()
    previous_label = None
    for row in df:  # Start from the second row
        if (row[0] in states) and (row[0] != previous_label):  
            list_data.append(row[0])
            previous_label = row[0]  # Update previous_label
    print(list_data)
    return list_data

# Generate a Markov transition matrix from the video labels
def gen_markov_matrix(input_dir_path, output_dir_path):
    zero_matrix = np.zeros((len(states)), dtype=int)
    first_order_matrix = np.zeros((len(states), len(states)), dtype=int)
    second_order_matrix = np.zeros((len(states), len(states), len(states)), dtype=int)

    for file_name in sorted(os.listdir(input_dir_path)):
        # Skip Excel lock files (~$foo.xlsx) and macOS resource forks (._foo.xlsx)
        if file_name.startswith(("~$", ".")):
            continue
        if file_name.endswith(".xlsx"):
            file_path = os.path.join(input_dir_path, file_name)
            video_labels = load_list(file_path)

            # Update the zero-order matrix
            for label in video_labels:
                zero_matrix[states.index(label)] += 1

            # Update the first-order matrix
            for (i, j) in zip(video_labels[:-1], video_labels[1:]):
                first_order_matrix[states.index(i), states.index(j)] += 1

            # Update the second-order matrix
            for (i, j, k) in zip(video_labels[:-2], video_labels[1:-1], video_labels[2:]):
                second_order_matrix[states.index(i), states.index(j), states.index(k)] += 1

    # Normalize      
    zero_matrix = zero_matrix / np.sum(zero_matrix)
    first_order_matrix = np.divide(
        first_order_matrix,
        np.sum(first_order_matrix, axis=1, keepdims=True),
        out = np.zeros_like(first_order_matrix, dtype=float),
        where = np.sum(first_order_matrix, axis=1, keepdims=True) != 0
    )
    second_order_matrix = np.divide(
        second_order_matrix,
        np.sum(second_order_matrix, axis=2, keepdims=True),
        out = np.zeros_like(second_order_matrix, dtype=float),
        where = np.sum(second_order_matrix, axis=2, keepdims=True) != 0
    )
    np.save(os.path.join(output_dir_path, "zero_order_markov_matrix.npy"), zero_matrix)
    np.save(os.path.join(output_dir_path, "first_order_markov_matrix.npy"), first_order_matrix)
    np.save(os.path.join(output_dir_path, "second_order_markov_matrix.npy"), second_order_matrix)

    return zero_matrix, first_order_matrix, second_order_matrix

def visualize_markov_matrix(zero_matrix, first_order_matrix, second_order_matrix, output_dir):
    plt.rcParams["font.sans-serif"] = ["Arial Unicode MS"]
    plt.rcParams["axes.unicode_minus"] = False

    plt.figure(figsize=(12, 8))
    bars = plt.bar(states, zero_matrix)
    plt.bar_label(bars, fmt="%.3f", padding=3)
    plt.xlabel("State")
    plt.ylabel("Probability")
    plt.title("Zero-order Markov Matrix")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "zero_order_markov_matrix.png"))
    plt.close()


    plt.figure(figsize=(12, 8))
    sns.heatmap(
    first_order_matrix,
    annot=True,
    fmt=".3f",
    cmap="Blues",
    xticklabels=states,
    yticklabels=states,
    vmin=0,
    vmax=1,
    )
    plt.xlabel("Next state")
    plt.ylabel("Current state")
    plt.title("1st order Markov Matrix")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "first_order_markov_matrix.png"))
    plt.close()

    n_cols = math.ceil(math.sqrt(len(states)))
    n_rows = math.ceil(len(states) / n_cols)
    plt.figure(figsize=(6 * n_cols, 6 * n_rows))
    for i in range(len(states)):
        plt.subplot(n_rows, n_cols, i+1)
        sns.heatmap(
            second_order_matrix[i],
            annot=True,
            fmt=".3f",
            cmap="Blues",
            xticklabels=states,
            yticklabels=states,
            vmin=0,
            vmax=1
        )
        plt.xlabel("Next state")
        plt.ylabel(f"Current state")
        plt.title(f"2nd order Markov Matrix with previous state : {states[i]}")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "second_order_markov_matrix.png"))
    plt.close()

def main():
    parser = ArgumentParser()
    parser.add_argument("--input_dir", default="./dataset/train", help="Path to the video file")
    parser.add_argument("--output_dir", default="./results/markov_matrices", help="Output directory for batch processing")
    parser.add_argument("--vis_dir", default="./visualized/markov_matrices", help="Path to the YOLO model")
    args = parser.parse_args()
    if not os.path.exists(args.input_dir):
        raise FileNotFoundError(f"Input directory '{args.input_dir}' does not exist.")
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
    if not os.path.exists(args.vis_dir):
        os.makedirs(args.vis_dir)

    zero_matrix, first_order_matrix, second_order_matrix = gen_markov_matrix(args.input_dir, args.output_dir)
    print("Zero-order matrix:")
    print(zero_matrix)
    print("First-order matrix:")
    print(first_order_matrix)
    print("Second-order matrix:")
    print(second_order_matrix)
    visualize_markov_matrix(zero_matrix, first_order_matrix, second_order_matrix, args.vis_dir)


if __name__ == "__main__":
    # Load the list of video labels from the CSV file
    main()  

