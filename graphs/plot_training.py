"""
=========================================================
GameBrain

Training Graph Generator

Generates:
1. Reward vs Episode
2. Loss vs Episode
3. Epsilon vs Episode

=========================================================
"""

import os
import pandas as pd
import matplotlib.pyplot as plt

# ----------------------------------------------------
# Get Project Root
# ----------------------------------------------------

BASE_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        ".."
    )
)

LOG_FILE = os.path.join(
    BASE_DIR,
    "logs",
    "training_log.csv"
)

OUTPUT_FOLDER = os.path.join(
    BASE_DIR,
    "graphs"
)


def generate_graphs():

    print("Looking for log file at:")
    print(LOG_FILE)
    print()

    if not os.path.exists(LOG_FILE):

        print("ERROR: training_log.csv not found!")
        return

    os.makedirs(
        OUTPUT_FOLDER,
        exist_ok=True
    )

    data = pd.read_csv(LOG_FILE)

    # ---------------- Reward ----------------

    plt.figure(figsize=(8, 5))

    plt.plot(data["Episode"], data["Reward"])

    plt.title("Reward vs Episode")

    plt.xlabel("Episode")

    plt.ylabel("Reward")

    plt.grid(True)

    plt.savefig(
        os.path.join(
            OUTPUT_FOLDER,
            "reward_graph.png"
        )
    )

    plt.close()

    # ---------------- Loss ----------------

    plt.figure(figsize=(8, 5))

    plt.plot(data["Episode"], data["Loss"])

    plt.title("Loss vs Episode")

    plt.xlabel("Episode")

    plt.ylabel("Loss")

    plt.grid(True)

    plt.savefig(
        os.path.join(
            OUTPUT_FOLDER,
            "loss_graph.png"
        )
    )

    plt.close()

    # ---------------- Epsilon ----------------

    plt.figure(figsize=(8, 5))

    plt.plot(data["Episode"], data["Epsilon"])

    plt.title("Epsilon Decay")

    plt.xlabel("Episode")

    plt.ylabel("Epsilon")

    plt.grid(True)

    plt.savefig(
        os.path.join(
            OUTPUT_FOLDER,
            "epsilon_graph.png"
        )
    )

    plt.close()

    print()
    print("✅ Graphs Generated Successfully!")
    print()
    print("Saved inside:")
    print(OUTPUT_FOLDER)


if __name__ == "__main__":

    generate_graphs()