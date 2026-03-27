// Public/script.js

// --- State Management ---
let allHistory = [];
let leftSidebarCollapsed = false;
let rightSidebarCollapsed = false;

// --- Helper Functions ---
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));

// --- Elements ---
const fileInput = document.getElementById('file-input');
const navBtns = {
    dashboard: document.getElementById('nav-dashboard'),
    analyze: document.getElementById('nav-analyze'),
    history: document.getElementById('nav-history')
};
const views = {
    dashboard: document.getElementById('view-dashboard'),
    analyze: document.getElementById('view-analyze'),
    history: document.getElementById('view-history')
};

// --- Initialization ---
document.addEventListener('DOMContentLoaded', () => {
    navBtns.dashboard.onclick = () => showView('dashboard');
    navBtns.analyze.onclick = () => showView('analyze');
    navBtns.history.onclick = () => showView('history');
});

// --- Sidebar Toggles ---
function toggleLeftSidebar() {
    leftSidebarCollapsed = !leftSidebarCollapsed;
    const sidebar = document.getElementById('left-sidebar');
    const main = document.getElementById('main-content');
    const icon = document.getElementById('left-toggle-icon');

    if (leftSidebarCollapsed) {
        sidebar.classList.add('collapsed');
        main.style.marginLeft = "80px";
        icon.innerText = "side_navigation";
    } else {
        sidebar.classList.remove('collapsed');
        main.style.marginLeft = "256px";
        icon.innerText = "menu_open";
    }
}

function toggleRightSidebar() {
    rightSidebarCollapsed = !rightSidebarCollapsed;
    const sidebar = document.getElementById('analyze-sidebar');
    const icon = document.getElementById('right-toggle-icon');

    if (rightSidebarCollapsed) {
        sidebar.classList.add('collapsed');
        icon.innerText = "keyboard_double_arrow_left";
    } else {
        sidebar.classList.remove('collapsed');
        icon.innerText = "keyboard_double_arrow_right";
    }
}

// --- View Switching ---
function showView(viewName) {
    Object.keys(views).forEach(key => {
        views[key].classList.add('hidden');
        navBtns[key].classList.remove('nav-active');
    });
    views[viewName].classList.remove('hidden');
    navBtns[viewName].classList.add('nav-active');

    const side = document.getElementById('analyze-sidebar');
    const toggle = document.getElementById('right-sidebar-toggle');
    
    if (viewName === 'analyze') {
        side.classList.remove('hidden');
    } else {
        side.classList.add('hidden');
    }

    if (viewName === 'history') renderFullHistory();
}

// --- Upload Logic ---
function triggerUpload() {
    fileInput.click();
}

fileInput.onchange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    showView('analyze');
    
    const statusText = document.getElementById('status-text');
    const statusBar = document.getElementById('status-bar');
    const placeholder = document.getElementById('analysis-placeholder');
    const resultsArea = document.getElementById('analysis-results');

    statusText.innerText = "Initializing Neural Link...";
    statusBar.style.width = "15%";
    statusBar.style.backgroundColor = "#4ade80"; 
    
    placeholder.innerHTML = `
        <div class="flex flex-col items-center">
            <div class="scanning-wrapper mb-6">
                <div class="scan-line"></div>
                <span class="loader"></span>
            </div>
            <p class="text-primary font-bold animate-pulse tracking-widest uppercase text-xs">Sequencing...</p>
        </div>
    `;
    placeholder.classList.remove('hidden');
    resultsArea.classList.add('hidden');
    
    const formData = new FormData();
    formData.append('file', file);

    try {
        const fetchPromise = fetch('/predict', { method: 'POST', body: formData });
        const randomDelayTime = Math.floor(Math.random() * 2000) + 1000;
        
        setTimeout(() => {
            statusText.innerText = "Analyzing Cellular Integrity...";
            statusBar.style.width = "50%";
        }, randomDelayTime / 2);

        const [response] = await Promise.all([
            fetchPromise,
            sleep(randomDelayTime)
        ]);

        const data = await response.json();

        placeholder.classList.add('hidden');
        resultsArea.classList.remove('hidden');
        
        document.getElementById('ana-plant').innerText = data.plant;
        document.getElementById('ana-disease').innerText = data.disease;
        document.getElementById('ana-report').innerText = data.report;
        
        statusText.innerText = "Analysis Complete";
        statusBar.style.width = "100%";

        saveToHistory(data);
    } catch (err) {
        statusText.innerText = "Inference Error";
        statusBar.style.backgroundColor = "#ef4444";
        placeholder.innerHTML = `<p class="text-red-500 font-bold">Diagnostic Failure: Server Unreachable.</p>`;
    } finally {
        fileInput.value = '';
    }
};

// --- History Rendering (UPDATED) ---
function saveToHistory(data) {
    const entry = {
        ...data,
        time: new Date().toLocaleString([], { month:'short', day:'numeric', hour: '2-digit', minute: '2-digit' })
    };
    allHistory.unshift(entry);
    renderSmallHistory();
}

function renderSmallHistory() {
    const container = document.getElementById('history-list-small');
    container.innerHTML = '';
    allHistory.slice(0, 5).forEach(item => {
        const div = document.createElement('div');
        div.className = "bg-white p-4 rounded-xl shadow-sm border border-slate-200 text-sm mb-3 sidebar-card";
        div.innerHTML = `
            <p class="font-bold text-primary mb-1">${item.plant}</p>
            <p class="text-xs text-slate-500 truncate mb-3">${item.disease}</p>
            <div class="flex flex-col gap-1 text-[10px] font-bold uppercase">
                <span class="${item.status === 'Optimal Health' ? 'text-green-600' : 'text-red-500'}">${item.status}</span>
                <span class="text-slate-300">${item.time}</span>
            </div>
        `;
        container.appendChild(div);
    });
}

function renderFullHistory() {
    const table = document.getElementById('full-history-table');
    table.innerHTML = '';
    let healthyCount = 0;
    let criticalCount = 0;

    allHistory.forEach(item => {
        if(item.status === 'Optimal Health') healthyCount++;
        else criticalCount++;

        const tr = document.createElement('tr');
        tr.className = "border-b border-slate-100 hover:bg-slate-50 transition-colors";
        tr.innerHTML = `
            <td class="px-6 py-4 font-bold text-slate-800">${item.plant}</td>
            <td class="px-6 py-4 text-slate-600">${item.disease}</td>
            <td class="px-6 py-4 text-[10px] font-bold uppercase ${item.status === 'Optimal Health' ? 'text-green-600' : 'text-red-500'}">${item.status}</td>
            <td class="px-6 py-4 text-right text-slate-400 text-xs">${item.time}</td>
        `;
        table.appendChild(tr);
    });

    document.getElementById('metric-total').innerText = allHistory.length;
    document.getElementById('metric-healthy').innerText = healthyCount;
    document.getElementById('metric-critical').innerText = criticalCount;
}