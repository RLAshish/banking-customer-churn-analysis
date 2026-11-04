from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "outputs"
DATA.mkdir(exist_ok=True)
OUT.mkdir(exist_ok=True)

DATA_URL = (
    "https://synapseaisolutionsa.z13.web.core.windows.net/"
    "data/bankcustomerchurn/churn.csv"
)
RAW_FILE = DATA / "bank_customer_churn.csv"


def main():
    if not RAW_FILE.exists():
        response = requests.get(DATA_URL, timeout=60)
        response.raise_for_status()
        RAW_FILE.write_bytes(response.content)

    df = pd.read_csv(RAW_FILE)
    df.columns = [str(column).strip().lower() for column in df.columns]

    required = {
        "customerid", "creditscore", "geography", "gender", "age",
        "tenure", "balance", "numofproducts", "hascrcard",
        "isactivemember", "estimatedsalary", "exited",
    }
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"Dataset schema mismatch; missing: {sorted(missing)}")

    numeric_columns = [
        "creditscore", "age", "tenure", "balance", "numofproducts",
        "hascrcard", "isactivemember", "estimatedsalary", "exited",
    ]
    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    df = df.dropna(subset=["customerid", "exited"]).copy()
    df["exited"] = df["exited"].astype(int)
    if not df["exited"].isin([0, 1]).all():
        raise ValueError("Expected exited to contain only 0 and 1.")

    df["age_group"] = pd.cut(
        df["age"],
        bins=[0, 30, 40, 50, 60, 120],
        labels=["18-30", "31-40", "41-50", "51-60", "60+"],
        include_lowest=True,
    )
    df["tenure_band"] = pd.cut(
        df["tenure"],
        bins=[-1, 2, 5, 8, 10],
        labels=["0-2 years", "3-5 years", "6-8 years", "9-10 years"],
    )
    df["churn_status"] = df["exited"].map({1: "Exited", 0: "Retained"})

    overall = pd.DataFrame([{
        "customers": len(df),
        "exited_customers": int(df["exited"].sum()),
        "retained_customers": int((df["exited"] == 0).sum()),
        "churn_rate_pct": round(df["exited"].mean() * 100, 2),
        "average_age": round(df["age"].mean(), 2),
        "average_tenure_years": round(df["tenure"].mean(), 2),
        "exited_customer_balance": round(df.loc[df["exited"] == 1, "balance"].sum(), 2),
    }])

    def segment_summary(column):
        return df.groupby(column, dropna=False, observed=False).agg(
            customers=("customerid", "count"),
            exited_customers=("exited", "sum"),
            churn_rate_pct=("exited", lambda values: values.mean() * 100),
            avg_balance=("balance", "mean"),
        ).reset_index()

    geography = segment_summary("geography")
    age = segment_summary("age_group")
    tenure = segment_summary("tenure_band")
    activity = segment_summary("isactivemember")
    products = segment_summary("numofproducts")

    clean = df.drop(columns=["surname"], errors="ignore")
    clean.to_csv(OUT / "clean_bank_customers.csv", index=False)
    with pd.ExcelWriter(OUT / "bank_churn_analysis.xlsx", engine="openpyxl") as writer:
        overall.to_excel(writer, sheet_name="KPIs", index=False)
        geography.to_excel(writer, sheet_name="Geography", index=False)
        age.to_excel(writer, sheet_name="Age Groups", index=False)
        tenure.to_excel(writer, sheet_name="Tenure", index=False)
        activity.to_excel(writer, sheet_name="Activity", index=False)
        products.to_excel(writer, sheet_name="Products", index=False)

    print(overall.to_string(index=False))
    print("\nChurn by geography:\n", geography.to_string(index=False))
    print(f"Outputs saved to: {OUT}")


if __name__ == "__main__":
    main()
