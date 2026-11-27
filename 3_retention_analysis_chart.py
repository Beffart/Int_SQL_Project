"""
Retention analysis chart.

Reads the query result exported from PostgreSQL (CSV) and plots, for each
cohort (first-purchase year), the share of customers who are still active
versus churned.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

CSV_PATH = "3_retention_analysis.csv"
OUTPUT_DIR = Path("images")

COLOR_ACTIVE = "#4169E1"   # highlight
COLOR_CHURNED = "#B0BEC5"  # neutral

# Optional note under the chart. Fill in with the churn definition used in
# the SQL query, e.g. "Churned = no purchase in the last 6 months".
FOOTNOTE = ""


def load_data(path: str) -> pd.DataFrame:
    """Load the CSV and pivot it to one row per cohort."""
    df = pd.read_csv(path)

    # Recompute percentages from the counts (the CSV values are rounded to 2 decimals)
    df["pct"] = df["num_customers"] / df["total_customers"] * 100

    pivot = df.pivot(index="cohort_year", columns="customer_status", values="pct")
    pivot["total_customers"] = df.groupby("cohort_year")["total_customers"].first()
    return pivot.sort_index()


def plot_retention(df: pd.DataFrame) -> None:
    """100% stacked bars: active vs churned customers by cohort."""
    x_labels = [f"{year}\n(n={n:,})" for year, n in zip(df.index, df["total_customers"])]

    fig, ax = plt.subplots(figsize=(11, 6.5))
    bars_active = ax.bar(x_labels, df["Active"], color=COLOR_ACTIVE, label="Active")
    bars_churned = ax.bar(x_labels, df["Churned"], bottom=df["Active"],
                          color=COLOR_CHURNED, label="Churned")

    # Percentage labels inside each segment
    for bar in bars_active:
        ax.annotate(f"{bar.get_height():.1f}%",
                    xy=(bar.get_x() + bar.get_width() / 2, bar.get_height() / 2),
                    ha="center", va="center", fontsize=11,
                    fontweight="bold", color="white")
    for bar, bottom in zip(bars_churned, df["Active"]):
        ax.annotate(f"{bar.get_height():.1f}%",
                    xy=(bar.get_x() + bar.get_width() / 2, bottom + bar.get_height() / 2),
                    ha="center", va="center", fontsize=12,
                    fontweight="bold", color="#263238")

    low, high = df["Churned"].min(), df["Churned"].max()
    ax.set_title(f"Churn sits at {low:.0f}-{high:.0f}% in every cohort,\n"
                 f"regardless of when the customer joined",
                 fontsize=16, loc="left", pad=20)
    ax.set_xlabel("First purchase year (cohort)", fontsize=12)
    ax.set_ylabel("% of customers in the cohort", fontsize=12)
    ax.set_ylim(0, 100)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0f}%"))

    for side in ("top", "right"):
        ax.spines[side].set_visible(False)

    # Legend outside the plot, so it never covers the bars
    ax.legend(frameon=False, fontsize=12, ncol=2,
              loc="upper right", bbox_to_anchor=(1, 1.1))

    if FOOTNOTE:
        fig.text(0.01, 0.01, FOOTNOTE, fontsize=10, color="gray")

    plt.tight_layout(rect=(0, 0.03, 1, 1))
    plt.savefig(OUTPUT_DIR / "3_retention_analysis.png", dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    OUTPUT_DIR.mkdir(exist_ok=True)

    data = load_data(CSV_PATH)
    print(data.round(1).to_string())

    plot_retention(data)
    print(f"Chart saved to {OUTPUT_DIR}/")
