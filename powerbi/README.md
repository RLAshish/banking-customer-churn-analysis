# Power BI report build guide

Run `python src/analyze.py` first, then import `outputs/clean_bank_customers.csv` into Power BI Desktop.

## Measures
```DAX
Total Customers = DISTINCTCOUNT(bank_customers[customerid])
Exited Customers = CALCULATE([Total Customers], bank_customers[exited] = 1)
Retained Customers = CALCULATE([Total Customers], bank_customers[exited] = 0)
Churn Rate = DIVIDE([Exited Customers], [Total Customers])
Average Balance = AVERAGE(bank_customers[balance])
Average Credit Score = AVERAGE(bank_customers[creditscore])
```

Format Churn Rate as a percentage.

## Suggested report pages
1. **Retention overview:** Total customers, exited customers, churn rate and retained customers; churn split donut; churn by geography.
2. **Customer segments:** Churn rate by age group, tenure band, gender and number of products.
3. **Engagement & balances:** Churn by active-member status; average balance and estimated salary by churn status.

Add slicers for geography, gender, age group and product count. Reconcile totals against `outputs/bank_churn_analysis.xlsx`. Save the finished `.pbix` in this folder from Power BI Desktop.
