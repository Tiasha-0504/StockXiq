// --- CONFIGURATION ---
// IMPORTANT: Replace this with your Hugging Face Space URL once created!
// Example: 'https://username-spacename.hf.space'
// For local testing, keep it as 'http://localhost:5000'
const API_URL = 'http://localhost:5000';

const headlineInput = document.getElementById('headline-input');
const analyzeBtn = document.getElementById('analyze-btn');
const resultsSection = document.getElementById('results-section');
const errorSection = document.getElementById('error-section');

// Result elements
const signalText = document.getElementById('signal-text');
const signalEmoji = document.getElementById('signal-emoji');
// 🟢 NEW: Get the reason element
const signalReason = document.getElementById('signal-reason');
const signalHeadline = document.getElementById('signal-headline');
const marketBeatValue = document.getElementById('market-beat-value');
const signalStrengthValue = document.getElementById('signal-strength-value');
const panicCheckValue = document.getElementById('panic-check-value');
const rippleSection = document.getElementById('ripple-section');
const rippleList = document.getElementById('ripple-list');
const errorMessage = document.getElementById('error-message');

analyzeBtn.addEventListener('click', handleAnalyze);
headlineInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && e.ctrlKey) {
        handleAnalyze();
    }
});

async function handleAnalyze() {
    const headline = headlineInput.value.trim();
    
    if (!headline) {
        showError('Please enter a headline to analyze.');
        return;
    }
    
    // Hide previous results and errors
    resultsSection.style.display = 'none';
    errorSection.style.display = 'none';
    
    // Show loading state
    setLoadingState(true);
    
    try {
        const response = await fetch(`${API_URL}/predict`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ headline: headline })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Prediction failed');
        }
        
        displayResults(data);
        
    } catch (error) {
        console.error('Error:', error);
        showError(error.message || 'Failed to analyze headline. Please check if the server is running.');
    } finally {
        setLoadingState(false);
    }
}

function setLoadingState(loading) {
    const btnText = analyzeBtn.querySelector('.btn-text');
    const btnSpinner = analyzeBtn.querySelector('.btn-spinner');
    
    if (loading) {
        analyzeBtn.disabled = true;
        btnText.style.display = 'none';
        btnSpinner.style.display = 'inline-block';
    } else {
        analyzeBtn.disabled = false;
        btnText.style.display = 'inline';
        btnSpinner.style.display = 'none';
    }
}

function displayResults(data) {
    // Display signal
    signalText.textContent = data.signal;
    signalEmoji.textContent = data.signal_emoji;
    signalHeadline.textContent = `"${data.headline}"`;

    // 🟢 NEW: Update Reason Text
    if (signalReason) {
        signalReason.textContent = data.reason;
        
        // Optional: Add dynamic coloring for the reason text
        if (data.signal === 'BUY') {
            signalReason.style.color = '#4ade80'; // Green
        } else if (data.signal === 'SELL') {
            signalReason.style.color = '#f87171'; // Red
        } else {
            signalReason.style.color = '#fbbf24'; // Yellow/Orange
        }
    }
    
    // Apply signal color classes
    signalText.className = 'signal-text';
    if (data.signal === 'BUY') {
        signalText.classList.add('signal-buy');
    } else if (data.signal === 'SELL') {
        signalText.classList.add('signal-sell');
    } else {
        signalText.classList.add('signal-hold');
    }
    
    // Display Market Beat
    const beatValue = data.market_beat_value;
    const beatElement = marketBeatValue.querySelector('.value');
    beatElement.textContent = data.market_beat;
    marketBeatValue.className = 'metric-value';
    if (beatValue > 0) {
        marketBeatValue.classList.add('positive');
    } else if (beatValue < 0) {
        marketBeatValue.classList.add('negative');
    } else {
        marketBeatValue.classList.add('neutral');
    }
    
    // Display Signal Strength
    const strengthElement = signalStrengthValue.querySelector('.value');
    strengthElement.textContent = data.signal_strength;
    signalStrengthValue.className = 'metric-value neutral';
    
    // Display Panic Check
    const panicElement = panicCheckValue.querySelector('.value');
    panicElement.textContent = data.panic_check;
    panicCheckValue.className = 'metric-value';
    
    // Apply panic color based on level
    if (data.panic_check.includes('High Risk') || data.panic_check.includes('Chaos')) {
        panicCheckValue.classList.add('negative');
    } else if (data.panic_check === 'Moderate') {
        panicCheckValue.classList.add('neutral');
    } else {
        panicCheckValue.classList.add('positive');
    }
    
    // Display Ripple Effect
    if (data.ripple_effect && data.ripple_effect.length > 0) {
        rippleList.innerHTML = '';
        data.ripple_effect.forEach(stock => {
            // Handle both object format (with ticker and reason) and string format (backward compatibility)
            const ticker = typeof stock === 'object' ? stock.ticker : stock;
            const reason = typeof stock === 'object' ? stock.reason : '';
            
            const item = document.createElement('div');
            item.className = 'ripple-item';
            
            const tickerSpan = document.createElement('span');
            tickerSpan.className = 'ripple-ticker';
            tickerSpan.textContent = ticker;
            
            item.appendChild(tickerSpan);
            
            if (reason) {
                const reasonSpan = document.createElement('span');
                reasonSpan.className = 'ripple-reason';
                reasonSpan.textContent = ` - ${reason}`;
                item.appendChild(reasonSpan);
            }
            
            rippleList.appendChild(item);
        });
        rippleSection.style.display = 'block';
    } else {
        rippleSection.style.display = 'none';
    }
    
    // Show results section
    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function showError(message) {
    errorMessage.textContent = message;
    errorSection.style.display = 'block';
    errorSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}