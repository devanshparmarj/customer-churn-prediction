import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout="wide")

# 👉 PUT YOUR REAL BACKEND URL HERE
RENDER_URL = "https://customer-churn-prediction-3-42s7.onrender.com/"

components.html(f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Customer Churn</title>
<style>
body {{
    font-family: Arial;
    background: #0a0d14;
    color: white;
    padding: 40px;
}}
input, select {{
    width: 100%;
    padding: 10px;
    margin-bottom: 15px;
    background: #111;
    color: white;
    border: 1px solid #333;
}}
button {{
    padding: 12px;
    width: 100%;
    background: #7c3aed;
    color: white;
    border: none;
    cursor: pointer;
}}
.result {{
    margin-top: 20px;
    padding: 15px;
    background: #111;
}}
</style>
</head>

<body>

<h2>Customer Churn Prediction</h2>

<label>Tenure</label>
<input id="tenure" type="number" value="12">

<label>Monthly Charges</label>
<input id="charges" type="number" value="70">

<label>Support Calls</label>
<input id="calls" type="number" value="2">

<label>Contract Type</label>
<select id="contract">
<option>Month-to-month</option>
<option>One year</option>
<option>Two year</option>
</select>

<label>Internet Service</label>
<select id="internet">
<option>DSL</option>
<option>Fiber optic</option>
<option>No</option>
</select>

<button onclick="predict()">Predict</button>

<div id="result" class="result"></div>

<script>

const BACKEND_URL = "{RENDER_URL}";

async function predict() {{

    const tenure = parseInt(document.getElementById('tenure').value);
    const charges = parseFloat(document.getElementById('charges').value);
    const calls = parseInt(document.getElementById('calls').value);
    const contract = document.getElementById('contract').value;
    const internet = document.getElementById('internet').value;

    const payload = {{
        tenure: tenure,
        monthly_charges: charges,
        support_calls: calls,
        contract_type: contract,
        internet_service: internet
    }};

    const resultBox = document.getElementById("result");
    resultBox.innerHTML = "Loading...";

    try {{
        const res = await fetch(BACKEND_URL + "/predict", {{
            method: "POST",
            headers: {{
                "Content-Type": "application/json"
            }},
            body: JSON.stringify(payload)
        }});

           let data;

try {
    data = await res.json();
} catch {
    resultBox.innerHTML = "❌ Invalid response from backend";
    return;
}

if (!res.ok) {
    resultBox.innerHTML = "❌ Backend error: " + (data.detail || "Unknown error");
    return;
}

if (!data.churn_prediction && data.churn_prediction !== 0) {
    resultBox.innerHTML = "❌ Invalid data format from backend";
    return;
}

resultBox.innerHTML = `
    <b>Prediction:</b> ${data.churn_prediction} <br>
    <b>Probability:</b> ${(data.churn_probability * 100).toFixed(2)}% <br>
    <b>Risk:</b> ${data.risk_level}
`;

    }} catch (err) {{
        resultBox.innerHTML = "❌ Backend error or wrong URL";
    }}
}}

</script>

</body>
</html>
""", height=800)