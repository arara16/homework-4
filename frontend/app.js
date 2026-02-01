let allSymbols = [];
let chartInstances = {};

async function fetchSymbols() {
    try {
        const response = await fetch('/api/symbols');
        if (!response.ok) {
            console.error('Failed to fetch symbols');
            return [];
        }
        allSymbols = await response.json();
        return allSymbols;
    } catch (error) {
        console.error('Error fetching symbols:', error);
        return [];
    }
}

function formatNumber(num, decimals = 2) {
    const n = parseFloat(num);
    if (isNaN(n)) return '0.00';
    return n.toLocaleString('en-US', {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
    });
}

function formatLargeNumber(num) {
    const n = parseFloat(num);
    if (isNaN(n)) return '0';
    if (n >= 1e12) return (n / 1e12).toFixed(2) + 'T';
    if (n >= 1e9) return (n / 1e9).toFixed(2) + 'B';
    if (n >= 1e6) return (n / 1e6).toFixed(2) + 'M';
    if (n >= 1e3) return (n / 1e3).toFixed(2) + 'K';
    return n.toFixed(2);
}

function calculateChange(symbol) {
    const priceChangePercent = parseFloat(symbol.price_change_percent || 0);
    return priceChangePercent;
}

function formatChange(change) {
    const sign = change > 0 ? '+' : '';
    let className = 'neutral';
    if (change > 0) {
        className = 'positive';
    } else if (change < 0) {
        className = 'negative';
    }
    return `<span class="${className}">${sign}${change.toFixed(2)}%</span>`;
}

function showScreen(screenName) {
    document.querySelectorAll('.screen').forEach(s => s.classList.add('hidden'));
    const screen = document.getElementById(screenName);
    if (screen) {
        screen.classList.remove('hidden');
    }
    
    if (screenName === 'dashboard') {
        loadDashboard();
    } else if (screenName === 'symbols') {
        loadSymbols();
    }
}

async function loadDashboard() {
    const symbols = await fetchSymbols();
    if (!symbols || symbols.length === 0) {
        document.getElementById('summary').innerHTML = '<p class="error">⚠️ No data available. Please check the API connection.</p>';
        return;
    }

    const totalSymbols = symbols.length;
    const avgVolume = symbols.reduce((sum, s) => sum + parseFloat(s.quote_volume || 0), 0) / totalSymbols;
    const totalTrades = symbols.reduce((sum, s) => sum + parseInt(s.count || 0), 0);
    const positiveChanges = symbols.filter(s => calculateChange(s) > 0).length;
    const negativeChanges = symbols.filter(s => calculateChange(s) < 0).length;

    document.getElementById('summary').innerHTML = `
        <h3>📊 Market Summary</h3>
        <p><strong>Total Symbols:</strong> ${totalSymbols}</p>
        <p><strong>Average 24h Volume:</strong> $${formatLargeNumber(avgVolume)}</p>
        <p><strong>Total Trades (24h):</strong> ${totalTrades.toLocaleString()}</p>
        <p><strong>Gainers:</strong> <span class="positive">${positiveChanges}</span> | 
           <strong>Losers:</strong> <span class="negative">${negativeChanges}</span></p>
        <p><strong>Data Source:</strong> Binance API (Historical data)</p>
    `;
}

async function loadSymbols() {
    const symbols = await fetchSymbols();
    const tbody = document.querySelector('#symbolTable tbody');
    if (!tbody) {
        console.error('Symbol table body not found');
        return;
    }

    tbody.innerHTML = '';
    if (!symbols || symbols.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7">No data available</td></tr>';
        return;
    }

    symbols.forEach((symbol, index) => {
        const change = calculateChange(symbol);
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${index + 1}</td>
            <td><strong>${symbol.symbol}</strong></td>
            <td>$${formatNumber(symbol.close, 6)}</td>
            <td>${formatChange(change)}</td>
            <td>$${formatLargeNumber(symbol.quote_volume || symbol.volume)}</td>
            <td>${formatLargeNumber(symbol.count || symbol.number_of_trades || 0)}</td>
            <td><button onclick="showAnalysis('${symbol.symbol}')">Analyze</button></td>
        `;
        tbody.appendChild(row);
    });
}

async function showAnalysis(symbol) {
    showScreen('analysis');
    document.getElementById('analysisSymbol').textContent = symbol;
    document.getElementById('analysisContent').innerHTML = '<p>Loading comprehensive analysis with charts... This may take 1-2 minutes for LSTM training.</p>';
    
    // Destroy existing charts
    Object.values(chartInstances).forEach(chart => chart.destroy());
    chartInstances = {};
    
    try {
        const response = await fetch(`/api/analysis/complete/${symbol}`);
        if (!response.ok) throw new Error('Failed to load analysis');
        
        const data = await response.json();
        displayAnalysis(data);
    } catch (error) {
        document.getElementById('analysisContent').innerHTML = 
            `<p class="error">Error loading analysis: ${error.message}</p>`;
    }
}

function displayAnalysis(data) {
    const content = document.getElementById('analysisContent');
    
    let html = `
        <div class="analysis-section">
            <h3>📈 Price Chart (Last 90 Days)</h3>
            <canvas id="priceChart"></canvas>
        </div>
        
        <div class="analysis-section">
            <h3>📊 Technical Analysis</h3>
            <p><strong>Overall Signal:</strong> <span class="signal-${data.technical_analysis.overall_signal.toLowerCase().replace('_', '')}">${data.technical_analysis.overall_signal}</span></p>
            <p><em>${data.technical_analysis.description}</em></p>
            
            <div class="chart-row">
                <div class="chart-container-half">
                    <h4>Signals Distribution</h4>
                    <canvas id="signalsChart"></canvas>
                </div>
                <div class="chart-container-half">
                    <h4>Technical Indicators (Last 30 Days)</h4>
                    <canvas id="technicalChart"></canvas>
                </div>
            </div>
            
            <h4>Last 1 Day Analysis</h4>
            <p class="period-note">${data.technical_analysis['1d'].period_info}</p>
            <div class="indicators">
                ${formatIndicators(data.technical_analysis['1d'])}
            </div>
            
            <h4>Last 7 Days Analysis (1 Week)</h4>
            <p class="period-note">${data.technical_analysis['1w'].period_info}</p>
            <div class="indicators">
                ${formatIndicators(data.technical_analysis['1w'])}
            </div>
            
            <h4>Last 30 Days Analysis (1 Month)</h4>
            <p class="period-note">${data.technical_analysis['1m'].period_info}</p>
            <div class="indicators">
                ${formatIndicators(data.technical_analysis['1m'])}
            </div>
        </div>
        
        <div class="analysis-section">
            <h3>🤖 LSTM Price Prediction</h3>
            <p><strong>Model Performance:</strong></p>
            <ul>
                <li>RMSE: ${data.lstm_prediction.model_performance.RMSE.toFixed(2)}</li>
                <li>MAPE: ${data.lstm_prediction.model_performance.MAPE.toFixed(2)}%</li>
                <li>R²: ${data.lstm_prediction.model_performance.R2.toFixed(4)}</li>
            </ul>
            
            <h4>7-Day Price Forecast</h4>
            <canvas id="lstmChart"></canvas>
            
            <table class="prediction-table">
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Predicted Price</th>
                    </tr>
                </thead>
                <tbody>
                    ${data.lstm_prediction.future_predictions.dates.map((date, i) => `
                        <tr>
                            <td>${date}</td>
                            <td>$${data.lstm_prediction.future_predictions.predictions[i].toFixed(2)}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
        
        <div class="analysis-section">
            <h3>💬 Sentiment & On-Chain Analysis</h3>
            <p><strong>Combined Signal:</strong> <span class="signal-${data.sentiment_analysis.combined_signal.toLowerCase().replace('_', '')}">${data.sentiment_analysis.combined_signal}</span></p>
            
            <div class="chart-container-gauge">
                <h4>Sentiment Score</h4>
                <div class="gauge-container">
                    <div class="gauge-value" style="color: ${data.charts.sentiment_gauge.color}">
                        ${data.charts.sentiment_gauge.score.toFixed(1)}
                    </div>
                    <div class="gauge-label" style="color: ${data.charts.sentiment_gauge.color}">
                        ${data.charts.sentiment_gauge.label}
                    </div>
                </div>
            </div>
            
            <h4>News Sentiment</h4>
            <p>Sentiment: ${data.sentiment_analysis.sentiment_analysis.sentiment_class}</p>
            <p>Score: ${data.sentiment_analysis.sentiment_analysis.average_sentiment.toFixed(3)}</p>
            <p>News analyzed: ${data.sentiment_analysis.sentiment_analysis.news_count}</p>
            
            <h4>On-Chain Metrics</h4>
            <ul>
                <li>Active Addresses: ${formatLargeNumber(data.sentiment_analysis.onchain_metrics.active_addresses)}</li>
                <li>Transactions: ${formatLargeNumber(data.sentiment_analysis.onchain_metrics.transaction_count)}</li>
                <li>NVT Ratio: ${data.sentiment_analysis.onchain_metrics.nvt_ratio.toFixed(2)}</li>
                <li>MVRV Ratio: ${data.sentiment_analysis.onchain_metrics.mvrv.toFixed(2)}</li>
            </ul>
            
            <h4>On-Chain Signals</h4>
            <ul>
                ${data.sentiment_analysis.onchain_analysis.signals.map(s => `<li>${s}</li>`).join('')}
            </ul>
        </div>
        
        <div class="analysis-section final-recommendation">
            <h3>🎯 Final Recommendation</h3>
            <p>${data.final_recommendation}</p>
        </div>
    `;
    
    content.innerHTML = html;
    
    // Render charts
    setTimeout(() => {
        renderPriceChart(data.charts.price);
        renderTechnicalChart(data.charts.technical);
        renderLSTMChart(data.charts.lstm);
        renderSignalsChart(data.charts.signals_distribution);
    }, 100);
}

function renderPriceChart(chartData) {
    const ctx = document.getElementById('priceChart');
    if (!ctx) return;
    
    chartInstances.price = new Chart(ctx, {
        type: 'line',
        data: {
            labels: chartData.dates,
            datasets: [{
                label: 'Close Price',
                data: chartData.close,
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { display: true },
                title: { display: false }
            },
            scales: {
                y: { beginAtZero: false }
            }
        }
    });
}

function renderTechnicalChart(chartData) {
    const ctx = document.getElementById('technicalChart');
    if (!ctx) return;
    
    chartInstances.technical = new Chart(ctx, {
        type: 'line',
        data: {
            labels: chartData.dates.slice(-30),
            datasets: [
                {
                    label: 'Price',
                    data: chartData.price.slice(-30),
                    borderColor: '#667eea',
                    tension: 0.4,
                    yAxisID: 'y'
                },
                {
                    label: 'SMA 20',
                    data: chartData.sma_20.slice(-30),
                    borderColor: '#27ae60',
                    borderDash: [5, 5],
                    tension: 0.4,
                    yAxisID: 'y'
                },
                {
                    label: 'EMA 20',
                    data: chartData.ema_20.slice(-30),
                    borderColor: '#e74c3c',
                    borderDash: [5, 5],
                    tension: 0.4,
                    yAxisID: 'y'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { display: true, position: 'top' }
            },
            scales: {
                y: { beginAtZero: false, position: 'left' }
            }
        }
    });
}

function renderLSTMChart(chartData) {
    const ctx = document.getElementById('lstmChart');
    if (!ctx) return;
    
    chartInstances.lstm = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [...chartData.historical_dates, ...chartData.future_dates],
            datasets: [
                {
                    label: 'Historical Price',
                    data: [...chartData.historical_prices, ...Array(chartData.future_dates.length).fill(null)],
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    tension: 0.4
                },
                {
                    label: 'Predicted Price',
                    data: [...Array(chartData.historical_dates.length).fill(null), chartData.historical_prices[chartData.historical_prices.length - 1], ...chartData.predicted_prices],
                    borderColor: '#e74c3c',
                    backgroundColor: 'rgba(231, 76, 60, 0.1)',
                    borderDash: [5, 5],
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { display: true }
            },
            scales: {
                y: { beginAtZero: false }
            }
        }
    });
}

function renderSignalsChart(chartData) {
    const ctx = document.getElementById('signalsChart');
    if (!ctx) return;
    
    chartInstances.signals = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: chartData.labels,
            datasets: [{
                data: chartData.values,
                backgroundColor: chartData.colors
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { display: true, position: 'bottom' }
            }
        }
    });
}

function formatIndicators(timeframeData) {
    let html = '<div class="indicator-grid">';
    
    html += '<div class="indicator-category"><h5>Oscillators</h5><ul>';
    for (const [key, value] of Object.entries(timeframeData.oscillators)) {
        html += `<li><strong>${key}:</strong> ${typeof value === 'number' ? value.toFixed(2) : value}</li>`;
    }
    html += '</ul></div>';
    
    html += '<div class="indicator-category"><h5>Moving Averages</h5><ul>';
    for (const [key, value] of Object.entries(timeframeData.moving_averages)) {
        html += `<li><strong>${key}:</strong> ${typeof value === 'number' ? value.toFixed(2) : value}</li>`;
    }
    html += '</ul></div>';
    
    html += '<div class="indicator-category"><h5>Signals</h5><ul>';
    for (const [key, value] of Object.entries(timeframeData.signals)) {
        html += `<li><strong>${key}:</strong> <span class="signal-${value.toLowerCase().replace('_', '')}">${value}</span></li>`;
    }
    html += '</ul></div>';
    
    html += '</div>';
    return html;
}

window.onload = function() {
    showScreen('dashboard');
};
