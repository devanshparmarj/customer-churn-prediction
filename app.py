import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout="wide")

RENDER_URL = "https://customer-churn-prediction-3-42s7.onrender.com"

html_code = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Customer Churn</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    font-family: Arial, sans-serif;
    background: #0a0d14;
    color: white;
    padding: 30px;
}
h2 { margin-bottom: 20px; color: #a78bfa; }
label { display: block; margin-bottom: 5px; font-size: 14px; color: #ccc; }
input, select {
    width: 100%;
    padding: 10px;
    margin-bottom: 15px;
    background: #1a1d26;
    color: white;
    border: 1px solid #333;
    border-radius: 4px;
    font-size: 14px;
}
input:focus, select:focus {
    outline: none;
    border-color: #7c3aed;
}
select option { background: #1a1d26; }
button {
    padding: 12px;
    width: 100%;
    background: #7c3aed;
    color: white;
    border: none;
    cursor: pointer;
    border-radius: 4px;
    font-size: 16px;
    font-weight: bold;
    transition: background 0.2s;
}
button:hover  { background: #6d28d9; }
button:disabled { background: #444; cursor: not-allowed; }
.result {
    margin-top: 20px;
    padding: 15px;
    background: #1a1d26;
    border-radius: 4px;
    border: 1px solid #333;
    min-height: 60px;
    font-size: 15px;
    line-height: 1.8;
}
.error   { color: #f87171; }
.success { color: #86efac; }
</style>
</head>
<body>
<h2>Customer Churn Prediction</h2>

<label>Tenure (months)</label>
<input id="tenure" type="number" value="12" min="0" max="120">

<label>Monthly Charges ($)</label>
<input id="charges" type="number" value="70" min="0" step="0.01">

<label>Support Calls</label>
<input id="calls" type="number" value="2" min="0" max="50">

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

<button id="predictBtn" onclick="predict()">Predict</button>
<div id="result" class="result"></div>

<script>
const BACKEND_URL = "RENDER_URL_PLACEHOLDER";

function validate(tenure, charges, calls) {
    if (isNaN(tenure) || tenure < 0 || tenure > 120)
        return "Tenure must be between 0 and 120.";
    if (isNaN(charges) || charges < 0)
        return "Monthly Charges must be a non-negative number.";
    if (isNaN(calls) || calls < 0 || calls > 50)
        return "Support Calls must be between 0 and 50.";
    return null;
}

async function predict() {
    const tenure   = parseInt(document.getElementById('tenure').value);
    const charges  = parseFloat(document.getElementById('charges').value);
    const calls    = parseInt(document.getElementById('calls').value);
    const contract = document.getElementById('contract').value;
    const internet = document.getElementById('internet').value;

    const resultBox = document.getElementById("result");
    const btn       = document.getElementById("predictBtn");

    const err = validate(tenure, charges, calls);
    if (err) {
        resultBox.innerHTML = '<span class="error">warning ' + err + '</span>';
        return;
    }

    const payload = {
        tenure:           tenure,
        monthly_charges:  charges,
        support_calls:    calls,
        contract_type:    contract,
        internet_service: internet
    };

    btn.disabled    = true;
    btn.textContent = "Predicting...";
    resultBox.innerHTML = "Loading...";

    try {
        const res  = await fetch(BACKEND_URL + "/predict", {
            method:  "POST",
            headers: { "Content-Type": "application/json" },
            body:    JSON.stringify(payload)
        });

        const data = await res.json();

        if (!res.ok) {
            resultBox.innerHTML =
                '<span class="error">Error: ' + (data.detail || "Backend error " + res.status) + '</span>';
            return;
        }

        const prob      = (data.churn_probability * 100).toFixed(2);
        const riskColor = data.risk_level === "High"   ? "#f87171"
                        : data.risk_level === "Medium" ? "#fbbf24"
                        : "#86efac";
        const label     = data.churn_prediction === 1 ? "Will Churn" : "Will Stay";

        resultBox.innerHTML =
            '<span class="success">Prediction complete</span><br><br>' +
            "<b>Prediction:</b> "  + label + "<br>" +
            "<b>Probability:</b> " + prob + "%<br>" +
            "<b>Risk Level:</b> <span style='color:" + riskColor + ";font-weight:bold'>"
                + data.risk_level + "</span>";

    } catch (err) {
        resultBox.innerHTML =
            '<span class="error">Could not reach backend. ' +
            'Check the Render server is running.<br>Error: ' + err.message + '</span>';
    } finally {
        btn.disabled    = false;
        btn.textContent = "Predict";
    }
}
</script>
</body>
</html>
"""

# Safe replacement – no f-string so JS braces never conflict with Python
html_code = html_code.replace("RENDER_URL_PLACEHOLDER", RENDER_URL)
components.html(html_code, height=620, scrolling=True)