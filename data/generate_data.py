"""
generate_data.py  —  11-feature telecom churn dataset
Run: python data/generate_data.py
"""
import numpy as np
import pandas as pd

np.random.seed(42)
N = 5000

tenure           = np.random.randint(1, 73, N)
monthly_charges  = np.round(np.random.uniform(20, 120, N), 2)
total_charges    = np.clip(np.round(monthly_charges * tenure + np.random.normal(0, 50, N), 2), 0, None)
support_calls    = np.random.randint(0, 11, N)
contract_type    = np.random.choice(["Month-to-month","One year","Two year"], N, p=[0.55,0.25,0.20])
internet_service = np.random.choice(["DSL","Fiber optic","No"], N, p=[0.35,0.45,0.20])
payment_method   = np.random.choice(["Credit card","Bank transfer","Electronic check","Mailed check"], N, p=[0.25,0.25,0.35,0.15])
tech_support       = np.random.choice(["Yes","No"], N, p=[0.45,0.55])
online_security    = np.random.choice(["Yes","No"], N, p=[0.40,0.60])
streaming_services = np.random.choice(["Yes","No"], N, p=[0.50,0.50])

churn_score = (
    -0.045 * tenure
    + 0.008 * monthly_charges
    + 0.10  * support_calls
    + np.where(contract_type    == "Month-to-month",    0.80, 0.0)
    + np.where(internet_service == "Fiber optic",       0.30, 0.0)
    + np.where(payment_method   == "Electronic check",  0.25, 0.0)
    + np.where(tech_support       == "No",  0.20, -0.10)
    + np.where(online_security    == "No",  0.20, -0.10)
    + np.where(streaming_services == "Yes", 0.10,  0.0)
    + np.random.normal(0, 0.5, N)
)
churn = (1 / (1 + np.exp(-churn_score)) > 0.5).astype(int)

df = pd.DataFrame({
    "tenure": tenure, "monthly_charges": monthly_charges,
    "total_charges": total_charges, "support_calls": support_calls,
    "contract_type": contract_type, "internet_service": internet_service,
    "payment_method": payment_method, "tech_support": tech_support,
    "online_security": online_security, "streaming_services": streaming_services,
    "churn": churn,
})
df.to_csv("churn.csv", index=False)
print(f"Saved {len(df)} rows | Churn rate: {churn.mean():.1%}")
