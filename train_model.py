"""
train_model.py
--------------
Full ML pipeline for customer churn prediction.

Steps:
  1. Load and inspect data
  2. Preprocess (impute, encode, scale)
  3. Train a RandomForestClassifier
  4. Evaluate with accuracy, precision, recall, F1
  5. Save model bundle to model/churn_model.pkl

Run from the project root:
    python train_model.py
"""

import os
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
    f1_score, classification_report, confusion_matrix,
)

# ──────────────────────────────────────────────
# CONFIGURATION
# ──────────────────────────────────────────────

# Supports running from project root OR from model/ subfolder
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
DATA_PATH  = os.path.join(BASE_DIR, "customer_churn_data.csv")
MODEL_DIR  = os.path.join(BASE_DIR, "model")
MODEL_PATH = os.path.join(MODEL_DIR, "churn_model.pkl")

os.makedirs(MODEL_DIR, exist_ok=True)

TARGET_COL            = "churn"
NUMERIC_FEATURES      = ["tenure", "monthly_charges", "support_calls"]
CATEGORICAL_FEATURES  = ["contract_type", "internet_service"]

# ──────────────────────────────────────────────
# LOAD DATA
# ──────────────────────────────────────────────
print("\n📂 Loading data …")
df = pd.read_csv(DATA_PATH)

# Normalise column names to snake_case so they match regardless of source file
df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
    .str.replace(r"[^a-z0-9_]", "", regex=True)
)

print(f"   Shape      : {df.shape}")
print(f"   Columns    : {list(df.columns)}")
print(f"   Churn rate : {df[TARGET_COL].mean():.1%}")

# Encode target: "Yes"/"No" → 1/0  (handle both string and numeric targets)
if df[TARGET_COL].dtype == object:
    df[TARGET_COL] = df[TARGET_COL].str.strip().str.lower().map({"yes": 1, "no": 0})

X = df[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
y = df[TARGET_COL]

# ──────────────────────────────────────────────
# PREPROCESSING PIPELINE
# ──────────────────────────────────────────────
numeric_transformer = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler",  StandardScaler()),
])

categorical_transformer = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("onehot",  OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
])

preprocessor = ColumnTransformer(transformers=[
    ("num", numeric_transformer,     NUMERIC_FEATURES),
    ("cat", categorical_transformer, CATEGORICAL_FEATURES),
])

# ──────────────────────────────────────────────
# FULL PIPELINE
# ──────────────────────────────────────────────
model_pipeline = Pipeline(steps=[
    ("preprocessor", preprocessor),
    ("classifier", RandomForestClassifier(
        n_estimators=200,
        max_depth=10,
        min_samples_leaf=5,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )),
])

# ──────────────────────────────────────────────
# TRAIN / TEST SPLIT & TRAINING
# ──────────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)

print(f"\n🔀 Train: {len(X_train)} | Test: {len(X_test)}")
print("\n🏋️  Training RandomForest …")
model_pipeline.fit(X_train, y_train)
print("   Done.")

# ──────────────────────────────────────────────
# EVALUATION
# ──────────────────────────────────────────────
y_pred = model_pipeline.predict(X_test)

print("\n📊 Evaluation on test set")
print(f"   Accuracy : {accuracy_score(y_test, y_pred):.4f}")
print(f"   Precision: {precision_score(y_test, y_pred):.4f}")
print(f"   Recall   : {recall_score(y_test, y_pred):.4f}")
print(f"   F1-Score : {f1_score(y_test, y_pred):.4f}")
print("\n   Classification Report:")
print(classification_report(y_test, y_pred, target_names=["No Churn", "Churn"]))
print("   Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))

cv_scores = cross_val_score(model_pipeline, X, y, cv=5, scoring="f1")
print(f"\n   5-Fold CV F1: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

# ──────────────────────────────────────────────
# SAVE MODEL BUNDLE
# ──────────────────────────────────────────────
bundle = {
    "pipeline":             model_pipeline,
    "numeric_features":     NUMERIC_FEATURES,
    "categorical_features": CATEGORICAL_FEATURES,
}
joblib.dump(bundle, MODEL_PATH)
print(f"\n✅ Model saved → {MODEL_PATH}")