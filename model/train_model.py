"""
train_model.py  —  Full 11-feature churn prediction pipeline
Run: python model/train_model.py
"""
import os, joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report

DATA_PATH  = os.path.join(os.path.dirname(__file__), "..", "data", "churn.csv")
MODEL_PATH = os.path.join(os.path.dirname(__file__), "churn_model.pkl")

NUMERIC_FEATURES     = ["tenure", "monthly_charges", "total_charges", "support_calls"]
CATEGORICAL_FEATURES = ["contract_type", "internet_service", "payment_method",
                         "tech_support", "online_security", "streaming_services"]
TARGET = "churn"

# ── Load ──────────────────────────────────────────────────────
print("\n📂  Loading data …")
df = pd.read_csv(DATA_PATH)
print(f"    Shape: {df.shape}  |  Churn rate: {df[TARGET].mean():.1%}")

X = df[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
y = df[TARGET]

# ── Preprocessing pipeline ────────────────────────────────────
numeric_transformer = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler",  StandardScaler()),
])
categorical_transformer = Pipeline([
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("onehot",  OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
])
preprocessor = ColumnTransformer([
    ("num", numeric_transformer,     NUMERIC_FEATURES),
    ("cat", categorical_transformer, CATEGORICAL_FEATURES),
])

# ── Full pipeline ─────────────────────────────────────────────
pipeline = Pipeline([
    ("preprocessor", preprocessor),
    ("classifier",   RandomForestClassifier(
        n_estimators=200, max_depth=12, min_samples_leaf=5,
        class_weight="balanced", random_state=42, n_jobs=-1,
    )),
])

# ── Train ─────────────────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y)
print(f"\n🔀  Train: {len(X_train)} | Test: {len(X_test)}")
print("\n🏋️  Training …")
pipeline.fit(X_train, y_train)

# ── Evaluate ──────────────────────────────────────────────────
y_pred = pipeline.predict(X_test)
print(f"\n📊  Accuracy : {accuracy_score(y_test, y_pred):.4f}")
print(f"    Precision: {precision_score(y_test, y_pred):.4f}")
print(f"    Recall   : {recall_score(y_test, y_pred):.4f}")
print(f"    F1-Score : {f1_score(y_test, y_pred):.4f}")
print("\n", classification_report(y_test, y_pred, target_names=["No Churn","Churn"]))

cv = cross_val_score(pipeline, X, y, cv=5, scoring="f1")
print(f"    5-Fold CV F1: {cv.mean():.4f} ± {cv.std():.4f}")

# Feature importances
ohe_cols = (pipeline.named_steps["preprocessor"]
            .named_transformers_["cat"]
            .named_steps["onehot"]
            .get_feature_names_out(CATEGORICAL_FEATURES))
feat_names = NUMERIC_FEATURES + list(ohe_cols)
importances = pd.Series(pipeline.named_steps["classifier"].feature_importances_, index=feat_names)
print("\n🔍  Top 10 Feature Importances:")
print(importances.sort_values(ascending=False).head(10).to_string())

# ── Save ──────────────────────────────────────────────────────
joblib.dump({
    "pipeline":            pipeline,
    "numeric_features":    NUMERIC_FEATURES,
    "categorical_features": CATEGORICAL_FEATURES,
}, MODEL_PATH)
print(f"\n✅  Model saved → {MODEL_PATH}")
