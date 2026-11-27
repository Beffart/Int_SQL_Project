"""
Customer segmentation charts (LTV).

Reads the query result exported from PostgreSQL (CSV) and generates:
  - a pie chart of revenue share by segment
  - a bar chart comparing % of customers vs % of revenue by segment
"""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

CSV_PATH = "1_customer_segmentation.csv"
OUTPUT_DIR = Path("images")

# Same palette in both charts
COLORS = {"High-Value": "#4169E1", "Mid-Value": "#00BFFF", "Low-Value": "#ADD8E6"}
NEUTRAL = "#B0BEC5"


def load_data(path: str) -> pd.DataFrame:
    """Load the CSV and compute each segment's share of customers and revenue."""
    df = pd.read_csv(path)

    # "3 - High Value" -> "High-Value"
    df["segment"] = (
        df["customer_segment"]
        .str.replace(r"^\d+\s*-\s*", "", regex=True)
        .str.replace(" ", "-", regex=False)
    )

    df["pct_customers"] = df["customer_count"] / df["customer_count"].sum() * 100
    df["pct_revenue"] = df["total_ltv"] / df["total_ltv"].sum() * 100

    # Display order: High, Mid, Low
    order = ["High-Value", "Mid-Value", "Low-Value"]
    return df.set_index("segment").loc[order].reset_index()


def plot_pie(df: pd.DataFrame) -> None:
    """Pie chart: share of total revenue by segment."""
    labels = [f"{seg}\n{pct:.1f}%" for seg, pct in zip(df["segment"], df["pct_revenue"])]
    colors = [COLORS[seg] for seg in df["segment"]]

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.pie(
        df["pct_revenue"],
        labels=labels,
        colors=colors,
        startangle=90,
        counterclock=False,
        labeldistance=1.08,
        wedgeprops={"edgecolor": "white", "linewidth": 2},
        textprops={"fontsize": 15},
    )

    high = df.loc[df["segment"] == "High-Value"].iloc[0]
    ax.set_title(
        "Customer Segmentation: Total LTV Distribution",
        fontsize=20,
        pad=25,
    )

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "1_customer_segmentation_pie.png", dpi=200)
    plt.close(fig)


def plot_bars(df: pd.DataFrame) -> None:
    """Grouped bars: % of customers vs % of revenue by segment."""
    x = range(len(df))
    width = 0.38

    fig, ax = plt.subplots(figsize=(9, 6))
    bars_customers = ax.bar([i - width / 2 for i in x], df["pct_customers"], width,
                            label="% of customers", color=NEUTRAL)
    bars_revenue = ax.bar([i + width / 2 for i in x], df["pct_revenue"], width,
                          label="% of revenue", color=COLORS["High-Value"])

    # Value labels on top of each bar
    for bars in (bars_customers, bars_revenue):
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f"{height:.1f}%",
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 4), textcoords="offset points",
                        ha="center", va="bottom", fontsize=12)

    ax.set_title("Share of customers vs share of revenue, by segment",
                 fontsize=16, loc="left", pad=20)
    ax.set_xticks(list(x))
    ax.set_xticklabels(df["segment"], fontsize=13)
    ax.set_ylim(0, df[["pct_customers", "pct_revenue"]].max().max() * 1.15)
    ax.set_yticks([])  # values are already labeled on the bars

    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.legend(frameon=False, fontsize=12, loc="upper right")

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "1_customer_segmentation_bars.png", dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    OUTPUT_DIR.mkdir(exist_ok=True)

    data = load_data(CSV_PATH)
    print(data[["segment", "customer_count", "total_ltv", "pct_customers", "pct_revenue"]]
          .round(1).to_string(index=False))

    plot_pie(data)
    plot_bars(data)
    print(f"Charts saved to {OUTPUT_DIR}/")
