// Chart instances for cleanup
let chartInstances = {};

// ============ CORE FUNCTIONS ============

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
    
    // Cleanup charts when switching screens
    cleanupCharts();
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

    // Enhanced dashboard with better visual design
    document.getElementById('summary').innerHTML = `
        <div class="dashboard-enhanced">
            <div class="dashboard-header">
                <h3>📊 Market Overview</h3>
                <div class="live-indicator">
                    <span class="live-dot"></span>
                    <span>Live Data</span>
                </div>
            </div>
            
            <div class="metrics-grid">
                <div class="metric-card primary">
                    <div class="metric-icon">🪙</div>
                    <div class="metric-content">
                        <div class="metric-value">${totalSymbols}</div>
                        <div class="metric-label">Total Symbols</div>
                    </div>
                </div>
                
                <div class="metric-card success">
                    <div class="metric-icon">💰</div>
                    <div class="metric-content">
                        <div class="metric-value">$${formatLargeNumber(avgVolume)}</div>
                        <div class="metric-label">Avg 24h Volume</div>
                    </div>
                </div>
                
                <div class="metric-card info">
                    <div class="metric-icon">📈</div>
                    <div class="metric-content">
                        <div class="metric-value">${totalTrades.toLocaleString()}</div>
                        <div class="metric-label">Total Trades (24h)</div>
                    </div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-content">
                        <div class="metric-row">
                            <span class="metric-label">Market Sentiment</span>
                        </div>
                        <div class="metric-row">
                            <span class="positive">▲ ${positiveChanges}</span>
                            <span class="negative">▼ ${negativeChanges}</span>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="data-source-enhanced">
                <span class="source-icon">🔗</span>
                <span>Data Source: Binance API (Real-time)</span>
                <span class="update-time">Updated: ${new Date().toLocaleTimeString()}</span>
            </div>
        </div>
    `;
}

function calculateChange(symbol) {
    if (!symbol.open || !symbol.close) return 0;
    return ((symbol.close - symbol.open) / symbol.open) * 100;
}

async function fetchSymbols() {
    try {
        const response = await fetch('/api/symbols');
        const symbols = await response.json();
        return symbols;
    } catch (error) {
        console.error('Error fetching symbols:', error);
        return [];
    }
}

async function loadSymbols() {
    const symbols = await fetchSymbols();
    const tbody = document.querySelector('#symbolTable tbody');
    if (!tbody) {
        console.error('Symbol table body not found');
        return;
    }

    if (!symbols || symbols.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="error">⚠️ No symbols available</td></tr>';
        return;
    }

    tbody.innerHTML = '';
    symbols.forEach((symbol, index) => {
        const row = document.createElement('tr');
        const changeClass = calculateChange(symbol) > 0 ? 'positive' : 
                           calculateChange(symbol) < 0 ? 'negative' : 'neutral';
        
        row.innerHTML = `
            <td><span class="rank">#${index + 1}</span></td>
            <td><strong>${symbol.symbol}</strong></td>
            <td>$${formatNumber(symbol.close, 6)}</td>
            <td class="${changeClass}">${formatChange(calculateChange(symbol))}</td>
            <td>$${formatLargeNumber(symbol.quote_volume)}</td>
            <td>${formatLargeNumber(symbol.count)}</td>
            <td>
                <button onclick="showAnalysis('${symbol.symbol}')" class="analyze-btn">
                    📊 Analyze
                </button>
            </td>
        `;
        
        tbody.appendChild(row);
    });
}

async function showAnalysis(symbol) {
    document.getElementById('analysisSymbol').textContent = symbol;
    showScreen('analysis');
    
    try {
        const response = await fetch(`/api/analysis/complete/${symbol}`);
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        displayCompleteAnalysis(data);
        
        setTimeout(() => {
            renderCharts(data);
        }, 100);
        
    } catch (error) {
        console.error('Error loading analysis:', error);
        document.getElementById('analysisContent').innerHTML = 
            `<div class="error-message">Error loading analysis: ${error.message}</div>`;
    }
}

function displayCompleteAnalysis(data) {
    const analysisContent = document.getElementById('analysisContent');
    
    let html = '<div class="analysis-grid">';
    
    // Enhanced Price Chart Section
    html += `
        <div class="analysis-section enhanced">
            <div class="section-header">
                <h3>📈 Price Chart (Last 90 Days)</h3>
                <div class="chart-controls">
                    <button class="chart-btn active" onclick="changeChartPeriod('90d', '${data.symbol}')">90D</button>
                    <button class="chart-btn" onclick="changeChartPeriod('30d', '${data.symbol}')">30D</button>
                    <button class="chart-btn" onclick="changeChartPeriod('7d', '${data.symbol}')">7D</button>
                </div>
            </div>
            <div class="chart-container enhanced">
                <canvas id="priceChart"></canvas>
            </div>
        </div>
    `;
    
    // Enhanced Technical Analysis Section
    html += `
        <div class="analysis-section enhanced">
            <h3>📊 Technical Analysis</h3>
            <div class="signal-overview">
                <div class="signal-card ${getSignalClass(data.technical_analysis?.overall_signal)}">
                    <div class="signal-label">Overall Signal</div>
                    <div class="signal-value">${data.technical_analysis?.overall_signal || 'HOLD'}</div>
                </div>
            </div>
            
            <div class="chart-row">
                <div class="chart-container-half">
                    <h4>Signals Distribution</h4>
                    <div class="chart-container">
                        <canvas id="signalsChart"></canvas>
                    </div>
                </div>
                <div class="chart-container-half">
                    <h4>Technical Indicators</h4>
                    <div class="chart-container">
                        <canvas id="technicalChart"></canvas>
                    </div>
                </div>
            </div>
            
            ${formatIndicators(data.technical_analysis)}
        </div>
    `;
    
    // Enhanced LSTM Prediction Section
    html += `
        <div class="analysis-section enhanced">
            <h3>🤖 LSTM Price Prediction</h3>
            <div class="model-performance">
                <div class="perf-item">
                    <span class="perf-label">RMSE</span>
                    <span class="perf-value">${data.lstm_prediction?.model_performance?.RMSE || 'N/A'}</span>
                </div>
                <div class="perf-item">
                    <span class="perf-label">MAPE</span>
                    <span class="perf-value">${data.lstm_prediction?.model_performance?.MAPE || 'N/A'}%</span>
                </div>
                <div class="perf-item">
                    <span class="perf-label">R²</span>
                    <span class="perf-value">${data.lstm_prediction?.model_performance?.R2 || 'N/A'}</span>
                </div>
            </div>
            
            <h4>7-Day Price Forecast</h4>
            <div class="chart-container enhanced">
                <canvas id="lstmChart"></canvas>
            </div>
            
            ${formatPredictionTable(data.lstm_prediction)}
        </div>
    `;
    
    // Enhanced Sentiment Analysis Section
    html += `
        <div class="analysis-section enhanced">
            <h3>💬 Sentiment & On-Chain Analysis</h3>
            <div class="sentiment-overview">
                <div class="sentiment-gauge">
                    <div class="gauge-circle" style="background: conic-gradient(${getGaugeGradient(data.sentiment_analysis?.combined_score || 0.5)})">
                        <div class="gauge-inner">
                            <div class="gauge-score">${(data.sentiment_analysis?.combined_score || 0.5).toFixed(2)}</div>
                            <div class="gauge-label">${data.sentiment_analysis?.sentiment_analysis?.sentiment_class || 'NEUTRAL'}</div>
                        </div>
                    </div>
                </div>
                
                <div class="sentiment-details">
                    <div class="detail-item">
                        <span class="detail-label">Combined Signal</span>
                        <span class="detail-value signal-${data.sentiment_analysis?.combined_signal?.toLowerCase() || 'hold'}">
                            ${data.sentiment_analysis?.combined_signal || 'HOLD'}
                        </span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">News Sentiment</span>
                        <span class="detail-value">${data.sentiment_analysis?.sentiment_analysis?.sentiment_class || 'NEUTRAL'}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">News Count</span>
                        <span class="detail-value">${data.sentiment_analysis?.sentiment_analysis?.news_count || 'N/A'}</span>
                    </div>
                </div>
            </div>
            
            <h4>On-Chain Metrics</h4>
            <div class="onchain-grid">
                <div class="onchain-item">
                    <div class="onchain-icon">👥</div>
                    <div class="onchain-content">
                        <div class="onchain-value">${formatLargeNumber(data.sentiment_analysis?.onchain_metrics?.active_addresses || 0)}</div>
                        <div class="onchain-label">Active Addresses</div>
                    </div>
                </div>
                <div class="onchain-item">
                    <div class="onchain-icon">⚡</div>
                    <div class="onchain-content">
                        <div class="onchain-value">${formatLargeNumber(data.sentiment_analysis?.onchain_metrics?.transaction_count || 0)}</div>
                        <div class="onchain-label">Transactions</div>
                    </div>
                </div>
                <div class="onchain-item">
                    <div class="onchain-icon">📊</div>
                    <div class="onchain-content">
                        <div class="onchain-value">${data.sentiment_analysis?.onchain_metrics?.nvt_ratio || 'N/A'}</div>
                        <div class="onchain-label">NVT Ratio</div>
                    </div>
                </div>
                <div class="onchain-item">
                    <div class="onchain-icon">🔄</div>
                    <div class="onchain-content">
                        <div class="onchain-value">${data.sentiment_analysis?.onchain_metrics?.mvrv || 'N/A'}</div>
                        <div class="onchain-label">MVRV Ratio</div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Enhanced Final Recommendation Section
    html += `
        <div class="analysis-section final-recommendation enhanced">
            <div class="recommendation-content">
                <h3>🎯 Final Recommendation</h3>
                <div class="recommendation-result ${data.final_recommendation?.toLowerCase() || 'hold'}">
                    ${data.final_recommendation || 'HOLD'}
                </div>
                <div class="recommendation-confidence">
                    Confidence: ${calculateConfidence(data)}%
                </div>
            </div>
        </div>
    `;
    
    html += '</div>';
    analysisContent.innerHTML = html;
}

function getSignalClass(signal) {
    if (!signal) return 'neutral';
    const lowerSignal = signal.toLowerCase();
    if (lowerSignal.includes('buy')) return 'buy';
    if (lowerSignal.includes('sell')) return 'sell';
    return 'hold';
}

function getGaugeGradient(score) {
    if (score > 0.6) return '#27ae60 0deg, #27ae60 ' + (score * 360) + 'deg, #e9ecef ' + (score * 360) + 'deg';
    if (score < 0.4) return '#e74c3c 0deg, #e74c3c ' + (score * 360) + 'deg, #e9ecef ' + (score * 360) + 'deg';
    return '#f39c12 0deg, #f39c12 ' + (score * 360) + 'deg, #e9ecef ' + (score * 360) + 'deg';
}

function calculateConfidence(data) {
    // Simple confidence calculation based on signal consistency
    const signals = [
        data.technical_analysis?.overall_signal,
        data.sentiment_analysis?.combined_signal
    ].filter(s => s);
    
    if (signals.length === 0) return 50;
    
    const buyCount = signals.filter(s => s?.toLowerCase().includes('buy')).length;
    const sellCount = signals.filter(s => s?.toLowerCase().includes('sell')).length;
    const holdCount = signals.filter(s => s?.toLowerCase().includes('hold')).length;
    
    const maxCount = Math.max(buyCount, sellCount, holdCount);
    return Math.round((maxCount / signals.length) * 100);
}

function formatIndicators(technical) {
    if (!technical) return '<p>No technical analysis available</p>';
    
    let html = '';
    
    ['1d', '1w', '1m'].forEach(timeframe => {
        if (technical[timeframe]) {
            const tf = technical[timeframe];
            html += `
                <div class="timeframe-card">
                    <h4>Last ${timeframe === '1d' ? '1 Day' : timeframe === '1w' ? '7 Days' : '30 Days'} Analysis</h4>
                    <div class="indicators-grid">
                        <div class="indicator-group">
                            <h5>📊 Oscillators</h5>
                            <div class="indicator-list">
                                ${formatIndicatorList(tf.oscillators)}
                            </div>
                        </div>
                        <div class="indicator-group">
                            <h5>📈 Moving Averages</h5>
                            <div class="indicator-list">
                                ${formatIndicatorList(tf.moving_averages)}
                            </div>
                        </div>
                        <div class="indicator-group">
                            <h5>🎯 Signals</h5>
                            <div class="indicator-list">
                                ${formatSignalList(tf.signals)}
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }
    });
    
    return html;
}

function formatIndicatorList(indicators) {
    if (!indicators) return '<div class="indicator-item">No data available</div>';
    
    return Object.entries(indicators).map(([key, value]) => 
        `<div class="indicator-item">
            <span class="indicator-name">${key}</span>
            <span class="indicator-value">${typeof value === 'number' ? value.toFixed(4) : value}</span>
        </div>`
    ).join('');
}

function formatSignalList(signals) {
    if (!signals) return '<div class="indicator-item">No signals available</div>';
    
    return Object.entries(signals).map(([key, value]) => {
        const signalClass = value.toLowerCase().includes('buy') ? 'buy' : 
                           value.toLowerCase().includes('sell') ? 'sell' : 'hold';
        return `<div class="indicator-item">
            <span class="indicator-name">${key}</span>
            <span class="indicator-value signal-${signalClass}">${value}</span>
        </div>`;
    }).join('');
}

function formatPredictionTable(lstm) {
    if (!lstm?.future_predictions) return '<p>No prediction data available</p>';
    
    const { dates, predictions } = lstm.future_predictions;
    
    let html = '<div class="prediction-table-enhanced"><div class="table-header"><h4>7-Day Forecast</h4></div><div class="table-body">';
    
    for (let i = 0; i < dates.length && i < predictions.length; i++) {
        const change = i > 0 ? ((predictions[i] - predictions[i-1]) / predictions[i-1]) * 100 : 0;
        const changeClass = change > 0 ? 'positive' : change < 0 ? 'negative' : 'neutral';
        
        html += `
            <div class="prediction-row">
                <div class="prediction-date">${dates[i]}</div>
                <div class="prediction-price">$${formatNumber(predictions[i], 2)}</div>
                <div class="prediction-change ${changeClass}">${change > 0 ? '+' : ''}${change.toFixed(2)}%</div>
            </div>
        `;
    }
    
    html += '</div></div>';
    return html;
}

// ============ CHART RENDERING ============

function renderCharts(data) {
    if (data.charts) {
        if (data.charts.price) renderPriceChart(data.charts.price);
        if (data.charts.technical) renderTechnicalChart(data.charts.technical);
        if (data.charts.lstm) renderLSTMChart(data.charts.lstm);
        if (data.charts.signals_distribution) renderSignalsChart(data.charts.signals_distribution);
    }
}

function renderPriceChart(chartData) {
    const ctx = document.getElementById('priceChart');
    if (!ctx) return;
    
    if (chartInstances.priceChart) chartInstances.priceChart.destroy();
    
    chartInstances.priceChart = new Chart(ctx, {
        type: 'line',
        data: chartData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        label: function(context) {
                            return `Price: $${formatNumber(context.parsed.y, 2)}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    ticks: {
                        callback: function(value) {
                            return '$' + formatNumber(value, 0);
                        }
                    }
                }
            }
        }
    });
}

function renderTechnicalChart(chartData) {
    const ctx = document.getElementById('technicalChart');
    if (!ctx) return;
    
    if (chartInstances.technicalChart) chartInstances.technicalChart.destroy();
    
    chartInstances.technicalChart = new Chart(ctx, {
        type: 'line',
        data: chartData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'top' },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: $${formatNumber(context.parsed.y, 2)}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    ticks: {
                        callback: function(value) {
                            return '$' + formatNumber(value, 0);
                        }
                    }
                }
            }
        }
    });
}

function renderLSTMChart(chartData) {
    const ctx = document.getElementById('lstmChart');
    if (!ctx) return;
    
    if (chartInstances.lstmChart) chartInstances.lstmChart.destroy();
    
    chartInstances.lstmChart = new Chart(ctx, {
        type: 'line',
        data: chartData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'top' },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: $${formatNumber(context.parsed.y, 2)}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    ticks: {
                        callback: function(value) {
                            return '$' + formatNumber(value, 0);
                        }
                    }
                }
            }
        }
    });
}

function renderSignalsChart(chartData) {
    const ctx = document.getElementById('signalsChart');
    if (!ctx) return;
    
    if (chartInstances.signalsChart) chartInstances.signalsChart.destroy();
    
    chartInstances.signalsChart = new Chart(ctx, {
        type: 'doughnut',
        data: chartData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom' },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

function cleanupCharts() {
    Object.values(chartInstances).forEach(chart => {
        if (chart) chart.destroy();
    });
    chartInstances = {};
}

// ============ FORMATTING FUNCTIONS ============

function formatNumber(num, decimals = 2) {
    if (num === null || num === undefined) return 'N/A';
    return parseFloat(num).toLocaleString('en-US', {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
    });
}

function formatLargeNumber(num) {
    if (num === null || num === undefined) return 'N/A';
    
    if (num >= 1e12) return (num / 1e12).toFixed(2) + 'T';
    if (num >= 1e9) return (num / 1e9).toFixed(2) + 'B';
    if (num >= 1e6) return (num / 1e6).toFixed(2) + 'M';
    if (num >= 1e3) return (num / 1e3).toFixed(2) + 'K';
    return formatNumber(num, 0);
}

function formatChange(change) {
    if (change === null || change === undefined) return 'N/A';
    
    const numChange = parseFloat(change);
    const sign = numChange >= 0 ? '+' : '';
    return `${sign}${numChange.toFixed(2)}%`;
}

// ============ INITIALIZATION ============

document.addEventListener('DOMContentLoaded', () => {
    showScreen('dashboard');
});
