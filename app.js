let chartInstance = null;
let allStocks = [];

// Fallback Mock Data in case JSON fetch fails (especially useful for local file:// protocol)
const mockData = [
    {
        symbol: "ENGRO", name: "Engro Corporation", sector: "Fertilizer", price: 285.50, change: 4.20, changePercent: 1.49, volume: 1542300, marketCap: 165000000000, peRatio: 5.6,
        chart: [280, 278, 281, 283, 282, 284, 285.50]
    },
    {
        symbol: "SYS", name: "Systems Limited", sector: "Technology", price: 420.10, change: -5.30, changePercent: -1.25, volume: 845000, marketCap: 120000000000, peRatio: 15.2,
        chart: [430, 428, 425, 427, 423, 421, 420.10]
    },
    {
        symbol: "LUCK", name: "Lucky Cement", sector: "Cement", price: 590.75, change: 12.50, changePercent: 2.16, volume: 2100000, marketCap: 190000000000, peRatio: 7.1,
        chart: [570, 575, 573, 580, 585, 588, 590.75]
    },
    {
        symbol: "HUBC", name: "Hub Power Company", sector: "Power Generation", price: 105.20, change: 1.10, changePercent: 1.06, volume: 4500000, marketCap: 135000000000, peRatio: 3.8,
        chart: [102, 103, 103.5, 104, 103.8, 104.5, 105.20]
    },
    {
        symbol: "OGDC", name: "Oil & Gas Development", sector: "Oil & Gas", price: 95.60, change: -0.40, changePercent: -0.42, volume: 3200000, marketCap: 410000000000, peRatio: 4.1,
        chart: [97, 96.5, 96, 95.8, 96.2, 95.9, 95.60]
    },
    {
        symbol: "MEBL", name: "Meezan Bank", sector: "Commercial Banks", price: 150.30, change: 2.80, changePercent: 1.90, volume: 1800000, marketCap: 260000000000, peRatio: 6.5,
        chart: [145, 146, 147.5, 147, 148, 149, 150.30]
    }
];

document.addEventListener('DOMContentLoaded', () => {
    initDashboard();
});

async function initDashboard() {
    try {
        // Try fetching the generated data
        const response = await fetch('psx_data.json?t=' + Date.now());
        if (!response.ok) throw new Error('Network response was not ok');
        allStocks = await response.json();
    } catch (error) {
        console.log("Could not load psx_data.json, using rich mock data instead.", error);
        allStocks = mockData;
    }

    populateFilters();
    renderStocks(allStocks);
    setupEventListeners();
}

function populateFilters() {
    const sectorFilter = document.getElementById('sectorFilter');
    const sectors = [...new Set(allStocks.map(s => s.sector))];
    
    sectors.forEach(sector => {
        const option = document.createElement('option');
        option.value = sector;
        option.textContent = sector;
        sectorFilter.appendChild(option);
    });
}

function renderStocks(stocks) {
    const grid = document.getElementById('stockGrid');
    grid.innerHTML = '';

    if (stocks.length === 0) {
        grid.innerHTML = '<p style="color: var(--text-muted)">No stocks found.</p>';
        return;
    }

    stocks.forEach(stock => {
        const isPositive = stock.change >= 0;
        const colorClass = isPositive ? 'positive' : 'negative';
        const sign = isPositive ? '+' : '';

        const card = document.createElement('div');
        card.className = 'stock-card';
        card.innerHTML = `
            <div class="card-header">
                <h4>${stock.symbol}</h4>
                <span class="sector-tag">${stock.sector}</span>
            </div>
            <div class="card-body">
                <div class="price">₨ ${stock.price.toFixed(2)}</div>
                <div class="change ${colorClass}">${sign}${stock.change.toFixed(2)} (${sign}${stock.changePercent.toFixed(2)}%)</div>
            </div>
        `;
        
        card.addEventListener('click', () => {
            window.location.href = `stock_details.html?symbol=${stock.symbol}`;
        });
        grid.appendChild(card);
    });
}

function setupEventListeners() {
    const searchInput = document.getElementById('searchInput');
    const sectorFilter = document.getElementById('sectorFilter');

    const filterData = () => {
        const query = searchInput.value.toLowerCase();
        const sector = sectorFilter.value;

        const filtered = allStocks.filter(stock => {
            const matchesSearch = stock.symbol.toLowerCase().includes(query) || stock.name.toLowerCase().includes(query);
            const matchesSector = sector === 'all' || stock.sector === sector;
            return matchesSearch && matchesSector;
        });

        renderStocks(filtered);
    };

    searchInput.addEventListener('input', filterData);
    sectorFilter.addEventListener('change', filterData);

    // Modal Close
    document.querySelector('.close-btn').addEventListener('click', closeModal);
    window.addEventListener('click', (e) => {
        if (e.target === document.getElementById('reportModal')) {
            closeModal();
        }
    });

    // PDF Download
    document.getElementById('downloadPdfBtn').addEventListener('click', downloadPDF);
}

function openModal(stock) {
    document.getElementById('modalSymbol').textContent = stock.symbol;
    document.getElementById('modalName').textContent = stock.name;
    document.getElementById('modalPrice').textContent = `₨ ${stock.price.toFixed(2)}`;
    
    const isPositive = stock.change >= 0;
    const sign = isPositive ? '+' : '';
    const changeEl = document.getElementById('modalChange');
    changeEl.textContent = `${sign}${stock.change.toFixed(2)} (${sign}${stock.changePercent.toFixed(2)}%)`;
    changeEl.className = isPositive ? 'positive' : 'negative';

    document.getElementById('modalVolume').textContent = stock.volume.toLocaleString();
    
    // Format market cap
    let mcapStr = stock.marketCap.toLocaleString();
    if(stock.marketCap > 1000000000) {
        mcapStr = (stock.marketCap / 1000000000).toFixed(2) + ' Billion';
    }
    document.getElementById('modalMarketCap').textContent = `₨ ${mcapStr}`;

    renderChart(stock);
    document.getElementById('reportModal').style.display = 'flex';
}

function closeModal() {
    document.getElementById('reportModal').style.display = 'none';
    if(chartInstance) {
        chartInstance.destroy();
        chartInstance = null;
    }
}

function renderChart(stock) {
    const ctx = document.getElementById('stockChart').getContext('2d');
    
    if(chartInstance) {
        chartInstance.destroy();
    }

    const isPositive = stock.change >= 0;
    const color = isPositive ? '#00e676' : '#ff5252';
    const bgColor = isPositive ? 'rgba(0, 230, 118, 0.1)' : 'rgba(255, 82, 82, 0.1)';

    // Dummy labels for past days
    const labels = stock.chart.map((_, i) => `Day ${i+1}`);

    chartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: `${stock.symbol} Price`,
                data: stock.chart,
                borderColor: color,
                backgroundColor: bgColor,
                borderWidth: 3,
                tension: 0.4,
                fill: true,
                pointBackgroundColor: color,
                pointRadius: 4,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: '#1a1d24',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: 'rgba(255,255,255,0.1)',
                    borderWidth: 1
                }
            },
            scales: {
                x: {
                    display: false,
                    grid: { display: false }
                },
                y: {
                    display: true,
                    position: 'right',
                    grid: { color: 'rgba(255,255,255,0.05)' },
                    ticks: { color: '#8b92a5' }
                }
            }
        }
    });
}

function downloadPDF() {
    const element = document.getElementById('reportContentToPrint');
    
    // Hide close btn and download btn during PDF generation
    const closeBtn = element.querySelector('.close-btn');
    const downloadBtn = document.getElementById('downloadPdfBtn');
    
    closeBtn.style.display = 'none';
    downloadBtn.style.display = 'none';

    const opt = {
        margin:       1,
        filename:     `${document.getElementById('modalSymbol').textContent}_Report.pdf`,
        image:        { type: 'jpeg', quality: 0.98 },
        html2canvas:  { scale: 2, backgroundColor: '#1a1d24' },
        jsPDF:        { unit: 'in', format: 'letter', orientation: 'landscape' }
    };

    html2pdf().set(opt).from(element).save().then(() => {
        // Restore buttons
        closeBtn.style.display = 'block';
        downloadBtn.style.display = 'block';
    });
}
