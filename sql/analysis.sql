-- Load outputs/clean_bank_customers.csv into a table named bank_customers.
-- Column names below use lowercase snake_case after import.

-- 1. Overall churn rate
SELECT COUNT(*) AS customers,
       SUM(exited) AS exited_customers,
       COUNT(*) - SUM(exited) AS retained_customers,
       ROUND(100.0 * SUM(exited) / COUNT(*), 2) AS churn_rate_pct
FROM bank_customers;

-- 2. Churn by geography
SELECT geography, COUNT(*) AS customers,
       SUM(exited) AS exited_customers,
       ROUND(100.0 * AVG(exited), 2) AS churn_rate_pct
FROM bank_customers
GROUP BY geography
ORDER BY churn_rate_pct DESC;

-- 3. Churn by age group
SELECT CASE WHEN age <= 30 THEN '18-30'
            WHEN age <= 40 THEN '31-40'
            WHEN age <= 50 THEN '41-50'
            WHEN age <= 60 THEN '51-60'
            ELSE '60+' END AS age_group,
       COUNT(*) AS customers,
       ROUND(100.0 * AVG(exited), 2) AS churn_rate_pct
FROM bank_customers
GROUP BY 1
ORDER BY 1;

-- 4. Active vs inactive customers
SELECT isactivemember, COUNT(*) AS customers,
       ROUND(100.0 * AVG(exited), 2) AS churn_rate_pct
FROM bank_customers
GROUP BY isactivemember
ORDER BY isactivemember;

-- 5. Churn by number of bank products
SELECT numofproducts, COUNT(*) AS customers,
       ROUND(100.0 * AVG(exited), 2) AS churn_rate_pct
FROM bank_customers
GROUP BY numofproducts
ORDER BY numofproducts;

-- 6. Average balance and salary by churn status
SELECT exited, COUNT(*) AS customers,
       ROUND(AVG(balance), 2) AS avg_balance,
       ROUND(AVG(estimatedsalary), 2) AS avg_estimated_salary
FROM bank_customers
GROUP BY exited;
