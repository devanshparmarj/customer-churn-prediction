<<<<<<< HEAD
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
import joblib

def main():
    print("Loading dataset...")
    df = pd.read_csv('customer_churn_data.csv')

    print("Preprocessing data...")
    # Select features and target
    X = df[["Tenure", "MonthlyCharges", "ContractType", "TechSupport"]].copy()
    y = df["Churn"].apply(lambda x: 1 if x == "Yes" else 0)

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y.values.ravel(), test_size=0.2, random_state=42)

    # Preprocessing pipelines for both numeric and categorical data
    numeric_features = ["Tenure", "MonthlyCharges"]
    numeric_transformer = StandardScaler()

    categorical_features = ["ContractType", "TechSupport"]
    categorical_transformer = OneHotEncoder(handle_unknown='ignore')

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ])

    # Append classifier to preprocessing pipeline
    # Now we have a full prediction pipeline
    clf = Pipeline(steps=[('preprocessor', preprocessor),
                          ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))])

    print("Training Pipeline...")
    clf.fit(X_train, y_train)

    # Evaluate
    accuracy = clf.score(X_test, y_test)
    print(f"Model accuracy on test set: {accuracy:.4f}")

    # Export the entire pipeline (no need for separate scaler)
    print("Saving pipeline.pkl...")
    joblib.dump(clf, "pipeline.pkl")
    print("Training complete! Pipeline saved successfully.")

if __name__ == "__main__":
    main()
=======
"""
train_model.py
--------------
Full ML pipeline for customer churn prediction.

Steps:
  1. Load and inspect data
  2. Preprocess (impute, encode, scale)
  3. Train a RandomForestClassifier
  4. Evaluate with accuracy, precision, recall, F1
  5. Save model + preprocessor bundle to churn_model.pkl

Run from the project root:
    python model/train_model.py
"""

import os
import sys
import joblib
import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, classification_report, confusion_matrix
)

# ──────────────────────────────────────────────
# 1.  CONFIGURATION
# ──────────────────────────────────────────────
DATA_PATH  = os.path.join(os.path.dirname(__file__), "..", "data", "churn.csv")
MODEL_PATH = os.path.join(os.path.dirname(__file__), "churn_model.pkl")

TARGET_COL       = "churn"
NUMERIC_FEATURES = ["tenure", "monthly_charges", "support_calls"]
CATEGORICAL_FEATURES = ["contract_type", "internet_service"]


# ──────────────────────────────────────────────
# 2.  LOAD DATA
# ──────────────────────────────────────────────
print("\n📂  Loading data …")
df = pd.read_csv(DATA_PATH)
print(f"    Shape : {df.shape}")
print(f"    Churn rate: {df[TARGET_COL].mean():.1%}")
print(df.dtypes)
print(df.head(3))

# Separate features and target
X = df[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
y = df[TARGET_COL]


# ──────────────────────────────────────────────
# 3.  PREPROCESSING PIPELINE
# ──────────────────────────────────────────────
# Numeric branch: impute missing values → scale
numeric_transformer = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="median")),   # robust to outliers
    ("scaler",  StandardScaler()),                   # zero-mean, unit-variance
])

# Categorical branch: impute → one-hot encode
categorical_transformer = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("onehot",  OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
])

# Combine both branches with ColumnTransformer
preprocessor = ColumnTransformer(transformers=[
    ("num", numeric_transformer,  NUMERIC_FEATURES),
    ("cat", categorical_transformer, CATEGORICAL_FEATURES),
])


# ──────────────────────────────────────────────
# 4.  FULL PIPELINE  (preprocessor + model)
# ──────────────────────────────────────────────
model_pipeline = Pipeline(steps=[
    ("preprocessor", preprocessor),
    ("classifier",   RandomForestClassifier(
        n_estimators=200,    # number of trees
        max_depth=10,        # prevents overfitting
        min_samples_leaf=5,
        class_weight="balanced",  # handles class imbalance
        random_state=42,
        n_jobs=-1,           # use all CPU cores
    )),
])


# ──────────────────────────────────────────────
# 5.  TRAIN / TEST SPLIT & TRAINING
# ──────────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)
print(f"\n🔀  Train: {len(X_train)} | Test: {len(X_test)}")

print("\n🏋️  Training RandomForest …")
model_pipeline.fit(X_train, y_train)
print("    Done.")


# ──────────────────────────────────────────────
# 6.  EVALUATION
# ──────────────────────────────────────────────
y_pred = model_pipeline.predict(X_test)
y_prob = model_pipeline.predict_proba(X_test)[:, 1]

print("\n📊  Evaluation on test set")
print(f"    Accuracy : {accuracy_score(y_test, y_pred):.4f}")
print(f"    Precision: {precision_score(y_test, y_pred):.4f}")
print(f"    Recall   : {recall_score(y_test, y_pred):.4f}")
print(f"    F1-Score : {f1_score(y_test, y_pred):.4f}")
print("\n    Classification Report:")
print(classification_report(y_test, y_pred, target_names=["No Churn", "Churn"]))
print("    Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# 5-fold cross-validation for robustness check
cv_scores = cross_val_score(model_pipeline, X, y, cv=5, scoring="f1")
print(f"\n    5-Fold CV F1: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

# Feature importances (after fitting)
rf = model_pipeline.named_steps["classifier"]
ohe_cols = (model_pipeline
            .named_steps["preprocessor"]
            .named_transformers_["cat"]
            .named_steps["onehot"]
            .get_feature_names_out(CATEGORICAL_FEATURES))
feature_names = NUMERIC_FEATURES + list(ohe_cols)
importances = pd.Series(rf.feature_importances_, index=feature_names).sort_values(ascending=False)
print("\n🔍  Feature Importances:")
print(importances.to_string())


# ──────────────────────────────────────────────
# 7.  SAVE MODEL BUNDLE
# ──────────────────────────────────────────────
bundle = {
    "pipeline":            model_pipeline,
    "numeric_features":    NUMERIC_FEATURES,
    "categorical_features": CATEGORICAL_FEATURES,
}
joblib.dump(bundle, MODEL_PATH)
print(f"\n✅  Model saved → {MODEL_PATH}")
>>>>>>> ca4fe2c0863f59d90092a28418872c2a7b753cfc
