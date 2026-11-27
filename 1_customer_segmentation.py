"""
Customer segmentation - revenue share pie chart.

Reads the query result exported from PostgreSQL (CSV) and generates
a pie chart showing each segment's share of total revenue.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

CSV_PATH = "1_customer_segmentation.csv"
OUTPUT_DIR = Path("images")

# Same palette as the original combined script
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
    plt.savefig(OUTPUT_DIR / "1_customer_segmentation.png", dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    OUTPUT_DIR.mkdir(exist_ok=True)
    data = load_data(CSV_PATH)
    print(data[["segment", "customer_count", "total_ltv", "pct_customers", "pct_revenue"]]
          .round(1).to_string(index=False))
    plot_pie(data)
    print(f"Pie chart saved to {OUTPUT_DIR}/1_customer_segmentation_pie.png")
