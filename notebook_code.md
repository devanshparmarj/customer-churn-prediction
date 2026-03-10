### Cell 0
```python



```

### Cell 1
```python
import pandas as pd
```

### Cell 2
```python
import pandas as pd
print(pd.__version__)
```

### Cell 3
```python
import pandas as pd
```

### Cell 4
```python
df = pd.read_csv(r"C:\Users\Lenovo -pc\OneDrive\python project\customer churn\customer_churn_data.csv")
df.head()

```

### Cell 5
```python
df.info()
```

### Cell 6
```python
df["InternetService"] = df["InternetService"].fillna("")
```

### Cell 7
```python
df.isna().sum().sum()
```

### Cell 8
```python
df.duplicated().sum()
```

### Cell 9
```python
df.describe()

```

### Cell 10
```python
numeric_columns_data = df.select_dtypes( include=["number"])
```

### Cell 11
```python
numeric_columns_data
```

### Cell 12
```python
import matplotlib.pyplot as plt
```

### Cell 13
```python
df["Churn"].value_counts().plot(kind="pie")
plt.title("Churn  (Yes/No)")
plt.ylabel("")
plt.show
```

### Cell 14
```python
df.head(2)
```

### Cell 15
```python
df.groupby("Churn")["MonthlyCharges"].mean()
```

### Cell 16
```python
df.groupby(["Churn","Gender"])["MonthlyCharges"].mean()
```

### Cell 17
```python
df.groupby("Churn")["Tenure"].mean()
```

### Cell 18
```python
df.groupby("Churn")["Age"].mean()
```

### Cell 19
```python
df.groupby("ContractType")["MonthlyCharges"].mean().plot(kind="bar")
```

### Cell 20
```python
y = df[["Churn"]]
x = df[["Age","Gender","MonthlyCharges"]]
```

### Cell 21
```python
x["Gender"] = x["Gender"].apply(lambda x: 1 if x== "Female" else 0)
```

### Cell 22
```python
x.head()
```

### Cell 23
```python
y["Churn"] = y["Churn"].apply(lambda x: 1 if x== "Yes" else 0)
```

### Cell 24
```python
from sklearn.model_selection import train_test_split
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size= 0.2)
```

### Cell 25
```python
x
```

### Cell 26
```python
from sklearn.preprocessing import StandardScaler
```

### Cell 27
```python
scaler = StandardScaler()
```

### Cell 28
```python
x_train = scaler.fit_transform(x_train)
```

### Cell 29
```python
 import joblib
joblib.dump(scaler,"scaler.pkl")
```

