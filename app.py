from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import torch
import torch.nn as nn
# transformers
from transformers import AutoTokenizer, AutoModel
# optional helper to download model files from Hugging Face hub when hosted remotely
try:
    from huggingface_hub import hf_hub_download
except Exception:
    hf_hub_download = None
import os
import sys

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# ==========================================
# 1. CONFIGURATION & MODEL ARCHITECTURE (V2 P100)
# ==========================================
MODEL_NAME = "ProsusAI/finbert"
DEVICE = 'cpu'  # Keep CPU for web server stability

class SniperBase(nn.Module):
    def __init__(self, output_dim):
        super(SniperBase, self).__init__()
        self.bert = AutoModel.from_pretrained(MODEL_NAME)
        self.head = nn.Sequential(
            nn.Dropout(0.2), 
            nn.Linear(768, 128), 
            nn.ReLU(), 
            nn.Linear(128, output_dim)
        )

    def forward(self, ids, mask, token_type_ids):
        output = self.bert(ids, attention_mask=mask, token_type_ids=token_type_ids)
        return self.head(output.last_hidden_state[:, 0, :])

# Global variables
tokenizer = None
model_beat = None
model_strength = None
model_panic = None
ecosystem_db = None

def load_models():
    """Load tokenizer and the 3 Optimized Sniper Models"""
    global tokenizer, model_beat, model_strength, model_panic, ecosystem_db
    
    print("⏳ Loading Sniper Engine...")
    
    try:
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        print("   ✓ Tokenizer loaded")
    except Exception as e:
        print(f"   Tokenizer failed: {e}")

    def load_brain(filename, output_dim):
        # Look for models in 'models' folder or current root
        path = os.path.join("models", filename)
        if not os.path.exists(path):
            path = filename

        # If still missing, try to download from Hugging Face repo if configured
        if not os.path.exists(path):
            hf_repo = os.environ.get('HF_REPO_ID')
            if hf_repo and hf_hub_download is not None:
                try:
                    print(f"   → Attempting download from HF: {hf_repo} / {filename}")
                    dl_path = hf_hub_download(repo_id=hf_repo, filename=filename)
                    if dl_path and os.path.exists(dl_path):
                        path = dl_path
                        print(f"   ✓ Downloaded from HF: {dl_path}")
                except Exception as e:
                    print(f"   ✗ HF download failed for {filename}: {e}")

        if os.path.exists(path):
            try:
                model = SniperBase(output_dim)
                model.load_state_dict(torch.load(path, map_location=DEVICE))
                model.eval()
                print(f"   ✓ Loaded: {filename}")
                return model
            except Exception as e:
                print(f"    Error loading {filename}: {e}")
                return None
        else:
            print(f"   ⚠ File not found: {path}")
            return None

    # Load V2 P100 Optimized Models
    model_beat = load_brain("sniper_beat_p100.bin", 1) 
    model_strength = load_brain("sniper_strength_p100.bin", 3)
    model_panic = load_brain("sniper_panic_p100.bin", 3)
    
    # Load Ecosystem DB (Optional)
    try:
        sys.path.append('models')
        from ecosystem_db import ECOSYSTEM_DB
        ecosystem_db = ECOSYSTEM_DB
        print(f"   ✓ Ecosystem DB loaded: {len(ecosystem_db)} tickers")
    except ImportError:
        print("   ⚠ ecosystem_db.py not found. Ripples disabled.")
        ecosystem_db = {}

# ==========================================
# 2. SMART INFERENCE (With Probabilities)
# ==========================================
def analyze_news(headline):
    if not tokenizer: return None

    # Preprocess
    inputs = tokenizer.encode_plus(
        headline, None, add_special_tokens=True, max_length=64,
        padding='max_length', truncation=True, return_tensors='pt'
    )
    
    ids = inputs['input_ids'].to(DEVICE)
    mask = inputs['attention_mask'].to(DEVICE)
    tt = inputs['token_type_ids'].to(DEVICE)
    
    results = {
        'beat': 0.0,
        'strength': 0, 'strength_conf': 0.0,
        'panic': 0, 'panic_conf': 0.0
    }

    with torch.no_grad():
        # 1. Beat (Regression)
        if model_beat:
            out = model_beat(ids, mask, tt)
            results['beat'] = out.item()
            
        # 2. Strength (Classification)
        if model_strength:
            out = model_strength(ids, mask, tt)
            probs = torch.softmax(out, dim=1)
            results['strength'] = torch.argmax(probs, dim=1).item()
            results['strength_conf'] = probs.max().item()

        # 3. Panic (Classification)
        if model_panic:
            out = model_panic(ids, mask, tt)
            probs = torch.softmax(out, dim=1)
            results['panic'] = torch.argmax(probs, dim=1).item()
            results['panic_conf'] = probs.max().item()

    return results

def get_ripple_effect(text):
    """Extract tickers and ecosystem impacts"""
    if not ecosystem_db: return []
    import re
    text_upper = text.upper()
    found_tickers = []
    # Simple ticker match
    for ticker in ecosystem_db.keys():
        clean_name = ticker.replace('.NS', '')
        if clean_name in text_upper or ticker in text_upper:
            found_tickers.append(ticker)
    
    results = []
    seen = set()
    for ticker in found_tickers:
        if ticker in ecosystem_db:
            for item in ecosystem_db[ticker]:
                rt = item.get('ticker', '')
                if rt and rt not in seen:
                    results.append(item)
                    seen.add(rt)
    return results[:10]

# ==========================================
# 3. THE SMART PREDICT ROUTE (XAI LOGIC)
# ==========================================
@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        headline = data.get('headline', '').strip()
        
        if not headline:
            return jsonify({'error': 'No headline provided'}), 400
        
        # 1. GET RAW ANALYSIS
        analysis = analyze_news(headline)
        
        pred_return = analysis['beat']
        strength = analysis['strength']
        panic_label = analysis['panic']
        panic_conf = analysis['panic_conf']
        
        # 2. SMART INTERPRETER LOGIC (V2 XAI)
        signal = "WAIT"
        emoji = "⚪"
        reason = "Analyzing..."
        
        # CONFIG: Thresholds
        buy_threshold = 0.50
        sell_threshold = -0.50
        panic_limit = 0.85
        
        # --- SCENARIO 1: THE RALLY (High Volatility + High Return) ---
        if pred_return > buy_threshold and panic_label == 2:
            signal = "BUY"
            emoji = "🟢"
            reason = f"RALLY MODE: High volatility detected, but direction is UP (+{pred_return:.2f}%). Riding momentum."

        # --- SCENARIO 2: THE CRASH (High Volatility + Negative Return) ---
        elif panic_label == 2 and panic_conf > panic_limit and pred_return < 0:
            signal = "SELL"
            emoji = "🔴"
            reason = f"CRASH ALERT: Extreme volatility ({panic_conf*100:.0f}% conf) with negative trend. Panic selling probable."

        # --- SCENARIO 3: PURE GROWTH (Strong Buy, Low Panic) ---
        elif pred_return > buy_threshold:
            signal = "BUY"
            emoji = "🟢"
            reason = f"STRONG BUY: Solid upside projected (+{pred_return:.2f}%) with safe volatility levels."

        # --- SCENARIO 4: PURE DUMP (Strong Sell, Low Panic) ---
        elif pred_return < sell_threshold:
            signal = "SELL"
            emoji = "🔴"
            reason = f"STRONG SELL: Asset projected to drop {pred_return:.2f}%. Negative sentiment dominant."

        # --- SCENARIO 5: THE "GOOD NEWS TRAP" (Positive but Weak) ---
        elif pred_return > 0 and pred_return < buy_threshold:
            signal = "HOLD"
            emoji = "🟡" # Yellow caution
            reason = f"GOOD NEWS BUT WEAK: Positive sentiment (+{pred_return:.2f}%) is below entry threshold (0.50%)."

        # --- SCENARIO 6: THE "SLOW BLEED" (Negative but Weak) ---
        elif pred_return < 0 and pred_return > sell_threshold:
            signal = "HOLD"
            emoji = "⚪"
            reason = f"WEAK NEGATIVE: Slight downward drift ({pred_return:.2f}%). Not worth shorting yet."

        # --- SCENARIO 7: NOISE ---
        else:
            signal = "HOLD"
            emoji = "⚪"
            reason = f"NOISE: Market impact is negligible ({pred_return:.2f}%)."

        # 3. FORMAT RESPONSE
        strength_map = {0: "Weak", 1: "Medium", 2: "Strong (Institutional)"}
        panic_map = {0: "Safe", 1: "Moderate", 2: "High Risk (Chaos)"}
        
        response = {
            "signal": signal,
            "signal_emoji": emoji,
            "reason": reason,
            "market_beat": f"{pred_return:+.2f}%",
            "market_beat_value": pred_return,
            "signal_strength": strength_map.get(strength, "Unknown"),
            "panic_check": panic_map.get(panic_label, "Unknown"),
            "panic_confidence": f"{panic_conf*100:.1f}%",
            "ripple_effect": get_ripple_effect(headline),
            "headline": headline
        }
        return jsonify(response)

    except Exception as e:
        print(f"Server Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('.', path)

# Load models at import time so WSGI servers (gunicorn) also initialize them
print("🚀 Initializing Sniper V2 API...")
load_models()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)