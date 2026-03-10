    
# 🔮 Customer Churn Prediction – Backend

A production-ready ML backend that predicts whether a telecom customer will churn.  
Built with **scikit-learn** (RandomForest), **FastAPI**, and **Pydantic**.

---

## 📁 Project Structure

```
customer-churn-project/
│
├── data/
│   ├── generate_data.py     # synthetic dataset generator
│   └── churn.csv            # generated dataset (5 000 rows)
│
├── model/
│   ├── train_model.py       # full ML pipeline: preprocess → train → evaluate → save
│   └── churn_model.pkl      # saved model bundle (created after training)
│
├── backend/
│   ├── main.py              # FastAPI app with /  and /predict endpoints
│   └── schema.py            # Pydantic request / response models
│
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup

### 1. Create & activate a virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🧠 Train the Model

```bash
# From the project root
python model/train_model.py
```

**What it does:**
- Loads `data/churn.csv`
- Builds a `ColumnTransformer` pipeline (impute → scale numerics, impute → one-hot-encode categoricals)
- Trains a `RandomForestClassifier` (200 trees, balanced class weights)
- Prints accuracy, precision, recall, F1, and feature importances
- Saves the full pipeline to `model/churn_model.pkl`

**Expected output (approximate):**
```
Accuracy : 0.8520
Precision: 0.8701
Recall   : 0.8433
F1-Score : 0.8565
5-Fold CV F1: 0.8541 ± 0.0083
```

---

## 🚀 Run the API Server

```bash
# From the project root
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

The server starts at **http://localhost:8000**

| URL | Description |
|---|---|
| `http://localhost:8000/` | Health check |
| `http://localhost:8000/docs` | Interactive Swagger UI |
| `http://localhost:8000/redoc` | ReDoc documentation |

---

## 📡 API Reference

### `GET /`
Health check – confirms the server is running and the model is loaded.

**Response:**
```json
{
  "status": "ok",
  "model_loaded": true,
  "version": "1.0.0"
}
```

---

### `POST /predict`
Send customer data → get back a churn prediction.

**Request body:**
```json
{
  "tenure": 12,
  "monthly_charges": 70.5,
  "contract_type": "Month-to-month",
  "internet_service": "Fiber optic",
  "support_calls": 2
}
```

| Field | Type | Allowed values |
|---|---|---|
| `tenure` | int | 0 – 120 |
| `monthly_charges` | float | 0 – 500 |
| `contract_type` | string | `"Month-to-month"` \| `"One year"` \| `"Two year"` |
| `internet_service` | string | `"DSL"` \| `"Fiber optic"` \| `"No"` |
| `support_calls` | int | 0 – 50 |

**Response:**
```json
{
  "churn_prediction": 1,
  "churn_probability": 0.82,
  "risk_level": "High"
}
```

| Field | Meaning |
|---|---|
| `churn_prediction` | `1` = will churn, `0` = will stay |
| `churn_probability` | Model confidence (0.0 – 1.0) |
| `risk_level` | `Low` (< 0.40) / `Medium` (0.40–0.70) / `High` (≥ 0.70) |

---

## 🌐 Calling the API from a Frontend (JavaScript)

### Fetch API
```javascript
async function predictChurn(customerData) {
  const response = await fetch("http://localhost:8000/predict", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(customerData),
  });

  if (!response.ok) {
    const err = await response.json();
    throw new Error(err.detail);
  }

  return await response.json();
}

// Usage
const result = await predictChurn({
  tenure: 12,
  monthly_charges: 70.5,
  contract_type: "Month-to-month",
  internet_service: "Fiber optic",
  support_calls: 2,
});

console.log(result);
// → { churn_prediction: 1, churn_probability: 0.82, risk_level: "High" }
```

### Axios
```javascript
import axios from "axios";

const { data } = await axios.post("http://localhost:8000/predict", {
  tenure: 12,
  monthly_charges: 70.5,
  contract_type: "Month-to-month",
  internet_service: "Fiber optic",
  support_calls: 2,
});
console.log(data.risk_level);  // "High"
```

### curl
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "tenure": 12,
    "monthly_charges": 70.5,
    "contract_type": "Month-to-month",
    "internet_service": "Fiber optic",
    "support_calls": 2
  }'
```

---

## 🔗 Connecting to an Antigravity UI

1. Run the FastAPI backend on `http://localhost:8000` (or deploy it to a server / Railway / Render).
2. In your Antigravity UI, point the form's submit action to `POST /predict`.
3. Map each form field to the matching JSON key in the request body.
4. Display `churn_probability` as a percentage and `risk_level` as a badge.

CORS is enabled for all origins by default – tighten `allow_origins` in `backend/main.py` for production.

---

## 🛠️ VS Code Tips

- Install the **Python** and **REST Client** extensions.
- Use the built-in terminal: `Ctrl+`` to open, then run the commands above.
- The `--reload` flag on uvicorn auto-restarts the server when you save a file.
- Visit `http://localhost:8000/docs` to test endpoints interactively without writing any client code.
=======
# customer-churn-prediction
>>>>>>> 51732013f2ef5add067a2eaf24b8c356ebd6f611
