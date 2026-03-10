import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout="wide", page_title="Customer Success Analytics", page_icon="⚡", initial_sidebar_state="collapsed")

# Hide Streamlit wrappers so our custom UI takes over completely
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container {
        padding: 0 !important;
        max-width: 100% !important;
        margin: 0 !important;
    }
    iframe {
        width: 100vw;
        border: none;
        display: block;
    }
    body {
        margin: 0;
    }
</style>
""", unsafe_allow_html=True)

custom_app_html = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Customer Success Analytics</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=Syne:wght@700;800&display=swap" rel="stylesheet">
<style>
    :root {
        --bg-color: #0a0d14;
        --card-bg: #0f1117;
        --accent: #7c3aed;
        --border-color: #ffffff0a;
        --text-muted: #64748b;
        --high-risk: #ef4444;
        --medium-risk: #f59e0b;
        --low-risk: #10b981;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }
    
    body {
        font-family: 'DM Sans', sans-serif;
        background-color: var(--bg-color);
        background-image: radial-gradient(ellipse 80% 50% at 50% -10%, #1a1040, transparent);
        background-repeat: no-repeat;
        color: #fff;
        min-height: 100vh;
        overflow-x: hidden;
        opacity: 0;
        animation: fadeIn 0.5s ease forwards;
    }

    @keyframes fadeIn { to { opacity: 1; } }

    /* Typography */
    h1, h2, h3, .syne { font-family: 'Syne', sans-serif; }
    .label { font-size: 11px; text-transform: uppercase; letter-spacing: 1px; color: var(--text-muted); font-weight: 700; margin-bottom: 6px; display: block; }
    
    /* Header */
    header {
        position: sticky; top: 0; z-index: 100;
        backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
        border-bottom: 1px solid var(--border-color);
        padding: 16px 32px;
        display: flex; justify-content: space-between; align-items: center;
    }
    .header-left { display: flex; align-items: center; gap: 16px; }
    .logo-icon {
        background: linear-gradient(135deg, var(--accent), #4f46e5);
        width: 40px; height: 40px; border-radius: 12px;
        display: flex; align-items: center; justify-content: center;
        font-size: 20px; box-shadow: 0 0 20px #7c3aed66;
    }
    .app-title { font-weight: 700; font-size: 20px; line-height: 1.2; }
    .app-subtitle { font-size: 10px; color: var(--text-muted); font-weight: 700; letter-spacing: 1.5px; }
    .status-badge {
        display: flex; align-items: center; gap: 8px;
        background: #10b9811a; border: 1px solid #10b98133; padding: 6px 12px; border-radius: 20px;
        font-size: 12px; font-weight: 600; color: #10b981;
    }
    .status-dot { width: 8px; height: 8px; border-radius: 50%; background: #10b981; animation: pulse 2s infinite; }
    @keyframes pulse { 0% { box-shadow: 0 0 0 0 #10b98180; } 70% { box-shadow: 0 0 0 6px #10b98100; } 100% { box-shadow: 0 0 0 0 #10b98100; } }

    /* Layout */
    .container {
        display: grid; grid-template-columns: 380px 1fr; gap: 24px;
        max-width: 1320px; margin: 32px auto; padding: 0 32px;
    }
    
    /* Cards */
    .card {
        background: var(--card-bg); border: 1px solid var(--border-color);
        border-radius: 16px; padding: 24px;
        box-shadow: 0 4px 32px #00000040;
        transition: transform 0.3s ease, background 0.5s ease, border 0.5s ease, box-shadow 0.5s ease;
    }
    
    /* Form Elements */
    .input-group { margin-bottom: 16px; }
    
    .stepper {
        display: flex; align-items: center;
        background: #161925; border: 1px solid var(--border-color); border-radius: 8px;
        overflow: hidden; height: 40px;
    }
    .stepper button {
        background: transparent; border: none; color: #fff; width: 40px; height: 100%;
        font-size: 18px; cursor: pointer; transition: background 0.2s;
    }
    .stepper button:hover { background: #ffffff0a; }
    .stepper input {
        flex: 1; background: transparent; border: none; color: #fff;
        text-align: center; font-size: 15px; font-weight: 500; font-family: 'DM Sans';
        -moz-appearance: textfield; height: 100%; width: 100%;
    }
    .stepper input::-webkit-outer-spin-button, .stepper input::-webkit-inner-spin-button { -webkit-appearance: none; margin: 0; }
    
    select {
        width: 100%; height: 40px; background: #0a0d14; border: 1px solid #ffffff10;
        border-radius: 8px; color: #fff; padding: 0 12px; appearance: none;
        font-family: 'DM Sans'; font-size: 15px; cursor: pointer; outline: none;
    }
    select option { background: #0f1117; }
    .select-wrapper { position: relative; }
    .select-wrapper::after {
        content: "▼"; position: absolute; right: 14px; top: 12px; font-size: 10px; color: #64748b; pointer-events: none;
    }
    
    .btn-primary {
        width: 100%; background: linear-gradient(135deg, var(--accent), #4f46e5); color: #fff;
        border: none; border-radius: 8px; padding: 14px; font-family: 'Syne'; font-weight: 700; font-size: 16px;
        cursor: pointer; box-shadow: 0 0 32px #7c3aed44; transition: all 0.3s ease;
        display: flex; align-items: center; justify-content: center; gap: 8px; margin-top: 24px;
    }
    .btn-primary:hover { filter: brightness(1.1); transform: scale(1.02); }
    
    .loader {
        width: 18px; height: 18px; border: 3px solid rgba(255,255,255,0.3); border-radius: 50%;
        border-top-color: #fff; animation: spin 1s linear infinite; display: none;
    }
    @keyframes spin { to { transform: rotate(360deg); } }

    .error-box {
        background: #f59e0b1a; border: 1px solid #f59e0b40; color: #f59e0b;
        padding: 12px; border-radius: 8px; font-size: 13px; font-weight: 500; margin-top: 16px;
        display: none; align-items: center; justify-content: center; gap: 8px; text-align: center;
    }

    /* Left Panel KPIs */
    .kpi-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 16px; }
    .kpi-card { background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 12px; padding: 16px; text-align: center; }
    .kpi-val { font-family: 'Syne'; font-weight: 800; font-size: 22px; margin-bottom: 4px; }
    
    /* Right Panel Layout */
    .right-panel { display: flex; flex-direction: column; gap: 20px; }

    /* Right Panel Result Card */
    #result-card { display: flex; flex-direction: column; gap: 20px; min-height: 380px; justify-content: center; }
    .result-empty { text-align: center; color: var(--text-muted); font-size: 18px; display: flex; flex-direction: column; align-items: center; gap: 12px; }
    .result-content { display: none; }
    .result-header { display: flex; justify-content: space-between; align-items: center; }
    .result-title { font-family: 'Syne'; font-weight: 700; font-size: 18px; border-left: 3px solid; padding-left: 12px; display: flex; align-items: center; }
    .risk-badge { font-family: 'Syne'; font-weight: 800; font-size: 13px; padding: 6px 16px; border-radius: 20px; letter-spacing: 0.5px; border: 1px solid; }

    .result-main { display: grid; grid-template-columns: 180px 1fr; gap: 32px; align-items: center; margin-top: 10px; }
    
    /* Gauge SVG */
    .gauge { width: 180px; height: 180px; position: relative; }
    .gauge svg { transform: rotate(-90deg); width: 100%; height: 100%; }
    .gauge-bg { fill: none; stroke: #ffffff08; stroke-width: 12; }
    .gauge-arc { fill: none; stroke-width: 12; stroke-linecap: round; stroke-dasharray: 440; stroke-dashoffset: 440; transition: stroke-dashoffset 1.2s cubic-bezier(0.4, 0, 0.2, 1); }
    .gauge-glow { filter: url(#glow); }
    .gauge-text { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; }
    .gauge-percent { font-family: 'Syne'; font-weight: 800; font-size: 32px; line-height: 1; }
    .gauge-label { font-size: 10px; font-weight: 700; color: var(--text-muted); letter-spacing: 1px; margin-top: 4px; }

    .pred-detail h2 { font-size: 28px; font-weight: 800; margin-bottom: 8px; }
    .pred-desc { color: #94a3b8; font-size: 14px; margin-bottom: 16px; line-height: 1.5; }
    .summary-chips { display: flex; flex-wrap: wrap; gap: 8px; }
    .chip { background: #ffffff0a; padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: 500; color: #cbd5e1; }

    .strategy-card { margin-top: 24px; padding: 16px; border-radius: 12px; background: rgba(0,0,0,0.2); }
    .strategy-title { font-weight: 700; font-size: 15px; margin-bottom: 12px; display: flex; align-items: center; gap: 8px; }
    .strategy-pills { display: flex; flex-direction: column; gap: 8px; }
    .step-pill { background: #ffffff0a; padding: 8px 12px; border-radius: 6px; font-size: 13px; display: flex; align-items: center; gap: 8px; }
    .step-pill::before { content: "•"; font-weight: bold; }

    /* Analytics Row */
    .analytics-row { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
    .chart-container { display: flex; flex-direction: column; gap: 16px; position: relative; }
    
    /* Custom Bar Chart */
    .bar-chart { display: flex; align-items: flex-end; justify-content: space-around; height: 160px; margin-top: 20px; }
    .bar-col { display: flex; flex-direction: column; align-items: center; gap: 8px; width: 60px; }
    .bar-val { font-weight: 700; font-family: 'Syne'; font-size: 14px; }
    .bar { width: 40px; border-radius: 6px 6px 0 0; transform-origin: bottom; transform: scaleY(0); transition: transform 1.2s cubic-bezier(0.22, 1, 0.36, 1); text-align: center; }
    .bar-label { font-size: 11px; color: var(--text-muted); font-weight: 600; text-align: center; }
    
    /* Custom Donut Widget */
    .donut-widget { display: flex; align-items: center; gap: 24px; margin-top: 10px; }
    .donut-svg { width: 120px; height: 120px; transform: rotate(-90deg); }
    .donut-bg { fill: none; stroke: #10b981; stroke-width: 24; }
    .donut-seg { fill: none; stroke: #ef4444; stroke-width: 24; stroke-dasharray: 314; stroke-dashoffset: 314; transition: stroke-dashoffset 1.5s ease-out; }
    .donut-details { flex: 1; }
    .d-row { margin-bottom: 12px; }
    .d-top { display: flex; justify-content: space-between; font-size: 12px; font-weight: 700; margin-bottom: 4px; }
    .d-bar-bg { height: 6px; background: #ffffff0a; border-radius: 3px; overflow: hidden; }
    .d-bar-fill { height: 100%; border-radius: 3px; width: 0; transition: width 1.5s ease-out; }
    .stat-box { margin-top: 16px; background: #ef44441a; border: 1px solid #ef444433; padding: 12px; border-radius: 8px; text-align: center; }

    .risk-high-text { color: var(--high-risk); }
    .risk-medium-text { color: var(--medium-risk); }
    .risk-low-text { color: var(--low-risk); }
    
    /* SVG Glow Filter Definition */
    /* Handled inline in the markup */
</style>
</head>
<body>

<svg width="0" height="0" style="position:absolute">
  <defs>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="4" result="blur" />
      <feComposite in="SourceGraphic" in2="blur" operator="over" />
    </filter>
  </defs>
</svg>

<header>
    <div class="header-left">
        <div class="logo-icon">⚡</div>
        <div>
            <div class="app-title syne">Customer Success Analytics</div>
            <div class="app-subtitle">ML CHURN INTELLIGENCE PLATFORM</div>
        </div>
    </div>
    <div class="status-badge">
        <div class="status-dot"></div>
        Model Active · RF Classifier v2.0
    </div>
</header>

<div class="container">
    <!-- LEFT PANEL -->
    <div class="left-panel">
        <div class="card">
            
            <div class="input-group">
                <span class="label">TENURE (MONTHS)</span>
                <div class="stepper">
                    <button type="button" onclick="step('tenure', -1)">−</button>
                    <input type="number" id="tenure" value="12" min="0" max="120">
                    <button type="button" onclick="step('tenure', 1)">+</button>
                </div>
            </div>
            
            <div class="input-group">
                <span class="label">MONTHLY CHARGES ($)</span>
                <div class="stepper">
                    <button type="button" onclick="step('charges', -0.5)">−</button>
                    <input type="number" id="charges" value="65.00" min="0" max="500" step="0.5">
                    <button type="button" onclick="step('charges', 0.5)">+</button>
                </div>
            </div>
            
            <div class="input-group">
                <span class="label">TOTAL CHARGES ($)</span>
                <div class="stepper">
                    <button type="button" onclick="step('total_charges', -10)">−</button>
                    <input type="number" id="total_charges" value="780.00" min="0" max="99999" step="10">
                    <button type="button" onclick="step('total_charges', 10)">+</button>
                </div>
            </div>
            
            <div class="input-group">
                <span class="label">RECENT SUPPORT CALLS</span>
                <div class="stepper">
                    <button type="button" onclick="step('calls', -1)">−</button>
                    <input type="number" id="calls" value="1" min="0" max="50">
                    <button type="button" onclick="step('calls', 1)">+</button>
                </div>
            </div>
            
            <div class="input-group">
                <span class="label">CONTRACT TYPE</span>
                <div class="select-wrapper">
                    <select id="contract">
                        <option>Month-to-month</option>
                        <option>One year</option>
                        <option>Two year</option>
                    </select>
                </div>
            </div>
            
            <div class="input-group">
                <span class="label">INTERNET SERVICE</span>
                <div class="select-wrapper">
                    <select id="internet">
                        <option>DSL</option>
                        <option>Fiber optic</option>
                        <option>No</option>
                    </select>
                </div>
            </div>
            
            <div class="input-group">
                <span class="label">PAYMENT METHOD</span>
                <div class="select-wrapper">
                    <select id="payment">
                        <option>Credit card</option>
                        <option>Bank transfer</option>
                        <option>Electronic check</option>
                        <option>Mailed check</option>
                    </select>
                </div>
            </div>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
                <div class="input-group">
                    <span class="label">TECH SUPPORT</span>
                    <div class="select-wrapper">
                        <select id="tech_support">
                            <option>Yes</option>
                            <option>No</option>
                        </select>
                    </div>
                </div>
                <div class="input-group">
                    <span class="label">ONLINE SECURITY</span>
                    <div class="select-wrapper">
                        <select id="security">
                            <option>Yes</option>
                            <option>No</option>
                        </select>
                    </div>
                </div>
            </div>
            
            <div class="input-group">
                <span class="label">STREAMING SERVICES</span>
                <div class="select-wrapper">
                    <select id="streaming">
                        <option>Yes</option>
                        <option>No</option>
                    </select>
                </div>
            </div>
            
            <button class="btn-primary" id="predictBtn" onclick="runPrediction()">
                <svg class="loader" id="btnLoader" viewBox="0 0 50 50"><circle cx="25" cy="25" r="20" fill="none" stroke-width="5" stroke="#fff" stroke-dasharray="31.4 31.4" stroke-linecap="round"></circle></svg>
                <span id="btnText">⚡ Predict Churn Risk</span>
            </button>
            <div class="error-box" id="errorBox">
                ⚡ Backend offline — showing demo prediction
            </div>
        </div>
        
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-val" id="kpi-customers">0</div>
                <div class="label" style="margin:0;">Total Customers</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-val" id="kpi-rate">0.0%</div>
                <div class="label" style="margin:0;">Avg Churn Rate</div>
            </div>
        </div>
    </div>

    <!-- RIGHT PANEL -->
    <div class="right-panel">
        
        <div class="card" id="result-card">
            <!-- Empty State -->
            <div class="result-empty" id="res-empty">
                <span style="font-size: 48px;">📊</span>
                <span style="font-weight: 500;">Awaiting Customer Data</span>
            </div>
            
            <!-- Result Data -->
            <div class="result-content" id="res-content">
                <div class="result-header">
                    <div class="result-title" id="res-title" style="border-color: var(--accent);">Prediction Result</div>
                    <div class="risk-badge" id="res-badge">HIGH RISK</div>
                </div>
                
                <div class="result-main">
                    <!-- Gauge SVG -->
                    <div class="gauge">
                        <svg viewBox="0 0 160 160">
                            <!-- 440 comes from 2*pi*70 ~= 440 -->
                            <circle class="gauge-bg" cx="80" cy="80" r="70"></circle>
                            <circle class="gauge-arc gauge-glow" id="res-arc" cx="80" cy="80" r="70"></circle>
                        </svg>
                        <div class="gauge-text">
                            <div class="gauge-percent" id="res-pct">0%</div>
                            <div class="gauge-label">CHURN RISK</div>
                        </div>
                    </div>
                    
                    <div class="pred-detail">
                        <h2 id="res-decision" class="syne">Will Churn</h2>
                        <div class="pred-desc" id="res-desc">
                            Based on the behavioral profile, this customer has a <b style="color:white;" id="desc-prob">0%</b> likelihood of churning.
                        </div>
                        <div class="summary-chips">
                            <div class="chip" id="chip-ten">Tenure: 12M</div>
                            <div class="chip" id="chip-chg">$65/mo</div>
                            <div class="chip" id="chip-tot">$780</div>
                            <div class="chip" id="chip-cll">1 Call</div>
                            <div class="chip" id="chip-ctr">M-to-M</div>
                            <div class="chip" id="chip-pay">Credit card</div>
                        </div>
                    </div>
                </div>
                
                <div class="strategy-card" id="res-strat">
                    <div class="strategy-title" id="strat-title">🚨 Urgent Intervention Required</div>
                    <div class="strategy-pills" id="strat-pills">
                        <!-- populated via JS -->
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Analytics Row -->
        <div class="analytics-row">
            <div class="card chart-container">
                <h3 style="font-size: 16px;">Avg Monthly Charges by Contract</h3>
                <!-- Custom Flexbox Bar Chart -->
                <div class="bar-chart">
                    <div class="bar-col">
                        <span class="bar-val">$72.4</span>
                        <!-- max target height based on 72.4 relative to e.g. 80 -->
                        <div class="bar" style="height: 120px; background: linear-gradient(0deg, #7c3aed40, #7c3aed); box-shadow: 0 0 16px #7c3aed40;"></div>
                        <span class="bar-label">Month-to-month</span>
                    </div>
                    <div class="bar-col">
                        <span class="bar-val">$54.1</span>
                        <div class="bar" style="height: 90px; background: linear-gradient(0deg, #0ea5e940, #0ea5e9); box-shadow: 0 0 16px #0ea5e940;"></div>
                        <span class="bar-label">One Year</span>
                    </div>
                    <div class="bar-col">
                        <span class="bar-val">$41.8</span>
                        <div class="bar" style="height: 70px; background: linear-gradient(0deg, #10b98140, #10b981); box-shadow: 0 0 16px #10b98140;"></div>
                        <span class="bar-label">Two Year</span>
                    </div>
                </div>
            </div>
            
            <div class="card chart-container">
                <h3 style="font-size: 16px;">Global Churn Distribution</h3>
                <div class="donut-widget">
                    <svg class="donut-svg" viewBox="0 0 100 100">
                        <circle class="donut-bg" cx="50" cy="50" r="38"></circle>
                        <!-- circumference = 2 * pi * 38 = 238.76 -->
                        <!-- Churn 26.4%, 238.76 * .264 = 63.03. -->
                        <circle class="donut-seg" id="anim-donut" cx="50" cy="50" r="38" stroke-dasharray="239"></circle>
                    </svg>
                    <div class="donut-details">
                        <div class="d-row">
                            <div class="d-top"><span style="color:#ef4444">Will Churn</span> <span>26.4%</span></div>
                            <div class="d-bar-bg"><div class="d-bar-fill" id="anim-db1" style="background:#ef4444;"></div></div>
                        </div>
                        <div class="d-row">
                            <div class="d-top"><span style="color:#10b981">Will Stay</span> <span>73.6%</span></div>
                            <div class="d-bar-bg"><div class="d-bar-fill" id="anim-db2" style="background:#10b981;"></div></div>
                        </div>
                    </div>
                </div>
                <div class="stat-box">
                    <span class="label" style="color:#f87171; letter-spacing: 2px; margin-bottom: 4px;">CUSTOMERS AT RISK</span>
                    <div class="syne" style="font-size:24px; font-weight:800; color:#ef4444;" id="kpi-risk">0</div>
                </div>
            </div>
        </div>

    </div>
</div>

<script>
    // Utils
    function step(id, val) {
        const el = document.getElementById(id);
        const min = parseFloat(el.min);
        const max = parseFloat(el.max);
        const step = parseFloat(el.step) || 1;
        let n = parseFloat(el.value) || 0;
        n += val;
        if(n < min) n = min;
        if(n > max) n = max;
        // avoid floating point math issues
        el.value = (Math.round(n * 2) / 2).toFixed(step === 0.5 ? 2 : (step === 10 ? 2 : 0));
    }

    function countUp(elId, target, duration, isPercent=false) {
        const el = document.getElementById(elId);
        const start = 0;
        const startTime = performance.now();
        
        function cubicOut(t) { return 1 - Math.pow(1 - t, 3); }
        
        function update(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const ease = cubicOut(progress);
            
            const current = start + (target - start) * ease;
            
            if(isPercent) {
                el.innerText = current.toFixed(1) + "%";
            } else {
                el.innerText = Math.round(current).toLocaleString();
            }
            
            if(progress < 1) requestAnimationFrame(update);
        }
        requestAnimationFrame(update);
    }

    // On Mount Animations
    window.onload = () => {
        countUp('kpi-customers', 14832, 1200);
        countUp('kpi-rate', 26.4, 1200, true);
        countUp('kpi-risk', 3915, 1200);
        
        document.querySelectorAll('.bar').forEach(bar => {
            bar.style.transform = 'scaleY(1)';
        });
        
        // animate donut: 26.4% of 239 = 63. offset = 239 - 63 = 176
        setTimeout(() => {
            document.getElementById('anim-donut').style.strokeDashoffset = "176";
            document.getElementById('anim-db1').style.width = "26.4%";
            document.getElementById('anim-db2').style.width = "73.6%";
        }, 100);
    };

    // UI Configuration based on Risk
    const uiCfg = {
        "High": {
            color: "#ef4444", class: "risk-high-text", label: "HIGH RISK", decision: "Will Churn",
            stratTitle: "🚨 Urgent Intervention Required",
            pills: ["Assign dedicated CSM immediately", "Offer 30% loyalty discount", "Schedule executive business review", "Enable premium support tier"]
        },
        "Medium": {
            color: "#f59e0b", class: "risk-medium-text", label: "MEDIUM RISK", decision: "Will Stay",
            stratTitle: "⚠️ Proactive Engagement Recommended",
            pills: ["Send personalized check-in email", "Highlight unused premium features", "Offer annual plan incentive"]
        },
        "Low": {
            color: "#10b981", class: "risk-low-text", label: "LOW RISK", decision: "Will Stay",
            stratTitle: "✅ Healthy Relationship — Nurture",
            pills: ["Include in referral program", "Invite to beta features", "Request case study participation"]
        }
    };

    async function runPrediction() {
        // Collect UI elements
        const btnLoader = document.getElementById('btnLoader');
        const btnText = document.getElementById('btnText');
        const errBox = document.getElementById('errorBox');
        const predictBtn = document.getElementById('predictBtn');
        
        // Inputs
        const tenureStr = document.getElementById('tenure').value;
        const chargesStr = document.getElementById('charges').value;
        const totalChargesStr = document.getElementById('total_charges').value;
        const callsStr = document.getElementById('calls').value;
        
        const contract = document.getElementById('contract').value;
        const internet = document.getElementById('internet').value;
        const payment = document.getElementById('payment').value;
        const techSupport = document.getElementById('tech_support').value;
        const security = document.getElementById('security').value;
        const streaming = document.getElementById('streaming').value;
        
        const tenure = parseInt(tenureStr) || 0;
        const charges = parseFloat(chargesStr) || 0;
        const total_charges = parseFloat(totalChargesStr) || 0;
        const calls = parseInt(callsStr) || 0;
        
        // Show loading state
        btnLoader.style.display = 'block';
        btnText.innerText = 'Analyzing...';
        predictBtn.style.opacity = '0.8';
        errBox.style.display = 'none';

        let probPct = 0;
        let riskLvl = "Low";
        let isFallback = false;

        const payload = {
            tenure: tenure,
            monthly_charges: charges,
            total_charges: total_charges,
            support_calls: calls,
            contract_type: contract,
            internet_service: internet,
            payment_method: payment,
            tech_support: techSupport,
            online_security: security,
            streaming_services: streaming
        };

        try {
            // Wait min 500ms to show loading UI nicely
            const timer = new Promise(r => setTimeout(r, 600));
            const fetchReq = fetch("http://localhost:8000/predict", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify(payload)
            });
            
            const results = await Promise.all([fetchReq, timer]);
            const response = results[0];
            
            if(!response.ok) throw new Error("Fetch failed");
            const data = await response.json();
            
            probPct = data.churn_probability * 100;
            const rString = data.risk_level.charAt(0).toUpperCase() + data.risk_level.slice(1).toLowerCase();
            if(uiCfg[rString]) riskLvl = rString;

        } catch (e) {
            console.warn("Backend unavailable, using fallback scoring", e);
            isFallback = true;
            // Local fallback logic exactly as specified
            let score = (calls * 8) + Math.max(0, 30 - tenure);
            
            if(contract === "Month-to-month") score += 35;
            else if (contract === "One year") score += 15;
            else score += 5;
            
            if(internet === "Fiber optic") score += 12;
            if(payment === "Electronic check") score += 10;
            
            if(techSupport === "No") score += 8; else score -= 5;
            if(security === "No") score += 8; else score -= 5;
            if(streaming === "Yes") score += 5;
            
            if(charges > 80) score += 10;
            
            probPct = Math.min(99, Math.max(0, score));
            riskLvl = probPct >= 70 ? "High" : probPct >= 40 ? "Medium" : "Low";
        }

        // Restore button state
        btnLoader.style.display = 'none';
        btnText.innerText = '⚡ Predict Churn Risk';
        predictBtn.style.opacity = '1';
        if(isFallback) {
            errBox.style.display = 'flex';
        }

        renderResults(probPct, riskLvl, {tenure, charges, total_charges, calls, contract, payment});
    }

    function renderResults(prob, risk, inputs) {
        document.getElementById('res-empty').style.display = 'none';
        
        const rt = document.getElementById('res-content');
        rt.style.display = 'block';
        rt.style.opacity = '0';
        
        const card = document.getElementById('result-card');
        const cfg = uiCfg[risk];
        
        // Apply styling transitions
        card.style.background = `linear-gradient(135deg, var(--card-bg) 60%, ${cfg.color}0d)`;
        card.style.borderColor = `${cfg.color}22`;
        card.style.boxShadow = `0 0 48px ${cfg.color}11`;
        
        document.getElementById('res-title').style.borderLeftColor = cfg.color;
        
        const badge = document.getElementById('res-badge');
        badge.innerText = cfg.label;
        badge.style.color = cfg.color;
        badge.style.borderColor = cfg.color;
        badge.style.backgroundColor = `${cfg.color}1a`;

        // Text & Chips
        const dec = document.getElementById('res-decision');
        dec.innerText = cfg.decision;
        dec.className = "syne " + cfg.class;
        
        document.getElementById('desc-prob').innerText = prob.toFixed(1) + "%";
        
        // Tenure | Monthly | Total | Calls | Contract | Payment
        let ctShort = "M-to-M";
        if(inputs.contract === "One year") ctShort = "1 Yr";
        if(inputs.contract === "Two year") ctShort = "2 Yr";
        
        let payShort = "Card";
        if(inputs.payment === "Bank transfer") payShort = "Bank";
        if(inputs.payment === "Electronic check") payShort = "eCheck";
        if(inputs.payment === "Mailed check") payShort = "Mail";
        
        document.getElementById('chip-ten').innerText = `${inputs.tenure}M`;
        document.getElementById('chip-chg').innerText = `$${inputs.charges}/mo`;
        document.getElementById('chip-tot').innerText = `$${inputs.total_charges}`;
        document.getElementById('chip-cll').innerText = `${inputs.calls} Call${inputs.calls !== 1 ? 's' : ''}`;
        document.getElementById('chip-ctr').innerText = ctShort;
        document.getElementById('chip-pay').innerText = payShort;
        
        // Strategy config
        document.getElementById('strat-title').innerText = cfg.stratTitle;
        document.getElementById('strat-title').style.color = cfg.color;
        document.getElementById('res-strat').style.backgroundColor = `${cfg.color}0a`;
        document.getElementById('strat-pills').innerHTML = cfg.pills.map(p => {
            return `<div class="step-pill"><span style="color:${cfg.color}"></span>${p}</div>`;
        }).join('');

        // Gauge Animation
        // Gauge stroke dasharray = 440 (circumference of r=70).
        document.getElementById('res-arc').style.stroke = cfg.color;
        // set immediately to 0 for transition
        document.getElementById('res-arc').style.strokeDashoffset = "440";
        
        // fade in
        setTimeout(() => { rt.style.opacity = '1'; }, 50);
        
        // Count up and draw gauge
        countUp('res-pct', prob, 1200, false);
        
        setTimeout(() => {
            // calculate offset: 440 * (1 - prob/100)
            const offset = 440 * (1 - (prob / 100));
            document.getElementById('res-arc').style.strokeDashoffset = offset;
        }, 100);
    }

</script>
</body>
</html>
"""

components.html(custom_app_html, height=1300, scrolling=True)