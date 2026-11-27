"""
Cohort analysis chart.

Reads the query result exported from PostgreSQL (CSV) and plots
revenue per customer by first-purchase year (cohort), with a trend line.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

CSV_PATH = "2_cohort_analysis.csv"
OUTPUT_DIR = Path("images")

COLOR_OLD = "#B0BEC5"     # neutral
COLOR_RECENT = "#4169E1"  # highlight
COLOR_TREND = "#003B5C"
N_RECENT = 3              # how many recent cohorts to highlight

# Optional note under the chart. Only fill this in if the SQL query really
# adjusts for time in market, e.g. "Adjusted for time in market".
FOOTNOTE = ""


def load_data(path: str) -> pd.DataFrame:
    """Load the CSV and sort cohorts chronologically."""
    df = pd.read_csv(path)
    return df.sort_values("cohort_year").reset_index(drop=True)


def plot_cohort_revenue(df: pd.DataFrame) -> None:
    """Bar chart of revenue per customer by cohort, plus a linear trend line."""
    years = df["cohort_year"]
    values = df["customer_revenue"]

    # Headline number: drop from the best cohort to the most recent one
    peak = df.loc[values.idxmax()]
    last = df.iloc[-1]
    drop_pct = (1 - last["customer_revenue"] / peak["customer_revenue"]) * 100

    # Highlight the most recent cohorts
    colors = [COLOR_RECENT if i >= len(df) - N_RECENT else COLOR_OLD
              for i in range(len(df))]

    # Linear trend line (least squares)
    slope, intercept = np.polyfit(years, values, 1)
    trend = slope * years + intercept

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(years.astype(str), values, color=colors)
    ax.plot(years.astype(str), trend, color=COLOR_TREND, linestyle="--",
            linewidth=2.5, label="Linear trend")

    # Value labels inside the base of each bar (the trend line never crosses them)
    for bar, color in zip(bars, colors):
        text_color = "white" if color == COLOR_RECENT else "#263238"
        ax.annotate(f"${bar.get_height():,.0f}",
                    xy=(bar.get_x() + bar.get_width() / 2, 0),
                    xytext=(0, 12), textcoords="offset points",
                    ha="center", va="bottom", fontsize=12,
                    fontweight="bold", color=text_color)

    ax.set_title(
        f"Newer customers are worth less: revenue per customer\n"
        f"fell {drop_pct:.0f}% from the {int(peak['cohort_year'])} cohort "
        f"to {int(last['cohort_year'])}",
        fontsize=16, loc="left", pad=20)
    ax.set_xlabel("First purchase year (cohort)", fontsize=12)
    ax.set_ylabel("Revenue per customer ($)", fontsize=12)
    ax.set_ylim(0, values.max() * 1.15)

    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.legend(frameon=False, fontsize=12, loc="upper right")

    if FOOTNOTE:
        fig.text(0.01, 0.01, FOOTNOTE, fontsize=10, color="gray")

    plt.tight_layout(rect=(0, 0.03, 1, 1))
    plt.savefig(OUTPUT_DIR / "2_cohort_analysis_chart.png", dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    OUTPUT_DIR.mkdir(exist_ok=True)

    data = load_data(CSV_PATH)
    print(data[["cohort_year", "total_customers", "customer_revenue"]]
          .round(0).to_string(index=False))

    plot_cohort_revenue(data)
    print(f"Chart saved to {OUTPUT_DIR}/")
