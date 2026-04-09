// web_app/static/main.js
document.addEventListener('DOMContentLoaded', () => {
    // === 1. TOPOLOGY VISUALIZER (Vis.js) ===
    const container = document.getElementById('network-graph');
    
    const nodes = new vis.DataSet([
        {id: 's1', label: 'S1\nSpine', color: '#ef4444', shape: 'box', level: 1},
        {id: 's2', label: 'S2\nSpine', color: '#ef4444', shape: 'box', level: 1},
        {id: 's7', label: 'S7\nCore', color: '#8b5cf6', shape: 'box', level: 1},
        
        {id: 's3', label: 'S3\nLeaf Web', color: '#3b82f6', shape: 'box', level: 2},
        {id: 's4', label: 'S4\nLeaf DNS', color: '#3b82f6', shape: 'box', level: 2},
        {id: 's5', label: 'S5\nLeaf DB', color: '#3b82f6', shape: 'box', level: 2},
        {id: 'r1', label: 'R1\nBorder', color: '#f59e0b', shape: 'ellipse', level: 2},
        
        {id: 'web_server1', label: 'web1', color: {background: '#10b981', border: '#059669'}, shape: 'database', level: 3},
        {id: 'web_server2', label: 'web2', color: {background: '#10b981', border: '#059669'}, shape: 'database', level: 3},
        {id: 'dns_server1', label: 'dns1', color: {background: '#10b981', border: '#059669'}, shape: 'database', level: 3},
        {id: 'dns_server2', label: 'dns2', color: {background: '#10b981', border: '#059669'}, shape: 'database', level: 3},
        {id: 'db_server1', label: 'db1', color: {background: '#10b981', border: '#059669'}, shape: 'database', level: 3},
        {id: 'db_server2', label: 'db2', color: {background: '#10b981', border: '#059669'}, shape: 'database', level: 3},
        
        {id: 'internet', label: 'Internet\n(8.8.8.8)', color: '#94a3b8', shape: 'ellipse', level: 3},
        {id: 'serverhcm', label: 'Server HCM', color: '#94a3b8', shape: 'database', level: 3}
    ]);

    const edges = new vis.DataSet([
        {from: 's7', to: 's1', color: '#64748b'}, {from: 's7', to: 's2', color: '#64748b'}, {from: 's7', to: 'r1', color: '#64748b'},
        {from: 'r1', to: 'internet', color: '#f59e0b'}, {from: 'r1', to: 'serverhcm', color: '#f59e0b'},
        
        {from: 's1', to: 's3', color: '#ec4899'}, {from: 's1', to: 's4', color: '#ec4899'}, {from: 's1', to: 's5', color: '#ec4899'},
        {from: 's2', to: 's3', color: '#14b8a6'}, {from: 's2', to: 's4', color: '#14b8a6'}, {from: 's2', to: 's5', color: '#14b8a6'},
        
        {from: 's3', to: 'web_server1'}, {from: 's3', to: 'web_server2'},
        {from: 's4', to: 'dns_server1'}, {from: 's4', to: 'dns_server2'},
        {from: 's5', to: 'db_server1'}, {from: 's5', to: 'db_server2'}
    ]);

    const data = { nodes: nodes, edges: edges };
    const options = {
        nodes: {
            font: { color: '#ffffff', face: 'Inter', size: 14, multi: 'html' },
            borderWidth: 2,
            shadow: true
        },
        edges: { width: 2, smooth: { type: 'continuous' } },
        layout: {
            hierarchical: {
                direction: 'UD', nodeSpacing: 100, levelSeparation: 120, edgeMinimization: true
            }
        },
        physics: false,
        interaction: { hover: true, dragNodes: false, zoomView: false }
    };
    window.networkVis = new vis.Network(container, data, options);

    // === 2. EVENT BINDING & API (POLLING) ===
    let lastLogIdx = 0;
    const consoleBox = document.getElementById('console-box');
    const modal = document.getElementById('image-modal');
    const modalImg = document.getElementById('modal-img');

    setInterval(fetchLogs, 1000);

    async function fetchLogs() {
        try {
            const res = await fetch(`/api/logs?last_idx=${lastLogIdx}`);
            const dataJSON = await res.json();
            if (dataJSON.logs && dataJSON.logs.length > 0) {
                lastLogIdx = dataJSON.next_idx;
                dataJSON.logs.forEach(log => {
                    const div = document.createElement('div');
                    div.style.marginBottom = "4px";
                    
                    let htmlLog = log;
                    if (log.includes('Lỗi') || log.includes('DENY')) div.style.color = '#ef4444';
                    else if (log.includes('ALLOW') || log.includes('PASS') || log.includes('SUCCESS')) div.style.color = '#10b981';
                    else if (log.includes('>>>') || log.includes('---')) div.style.color = '#f59e0b';
                    
                    div.textContent = htmlLog;
                    consoleBox.appendChild(div);

                    if(log.includes('Đã lưu tại:')) {
                        const imgMatches = log.match(/\/logs\/([^\s]+.png)/);
                        if(imgMatches && imgMatches[1]) showImage(imgMatches[1]);
                    }
                });
                consoleBox.scrollTop = consoleBox.scrollHeight;
            }
        } catch (e) {
            console.error(e);
        }
    }

    window.runDiagnostic = async function(action) {
        const src = document.getElementById('src-node').value;
        const dst = document.getElementById('dst-node').value;
        try {
            const res = await fetch('/api/diagnostics', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action, src, dst })
            });
            const dat = await res.json();
            if (dat.error) alert(dat.error);
        } catch(e) { alert("API Connection Error"); }
    };

    window.runCase = async function(caseNum) {
        // Simple helper to mimic the old checkboxes
        try {
            const res = await fetch('/api/run_cases', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ cases: [caseNum], src: 'web_server1', dst: 'db_server1' })
            });
            const data = await res.json();
            if (data.error) alert(data.error);
        } catch (e) {
            console.error(e);
            alert("API Connection Error");
        }
    };

    function showImage(filename) {
        modalImg.src = `/api/images/${filename}?t=${new Date().getTime()}`;
        modal.classList.add('active');
    }

    window.closeModal = function() {
        modal.classList.remove('active');
        modalImg.src = '';
    }

    // === TABS NAVIGATION ===
    window.openTab = function(tabId) {
        // Hide all tabs
        document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
        // Deactivate all buttons
        document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
        
        // Show selected tab
        document.getElementById(tabId).classList.add('active');
        event.currentTarget.classList.add('active');
        
        // Fix vis.js canvas sizing issue when unhiding the container
        if (tabId === 'tab-topo' && window.networkVis) {
            setTimeout(() => {
                window.networkVis.redraw();
                window.networkVis.fit();
            }, 100);
        }
    }

    // === TERMINAL TOGGLE ===
    window.toggleConsole = function() {
        const term = document.querySelector('.global-terminal');
        term.classList.toggle('minimized');
    }

    // === 3. REALTIME TRAFFIC CHART (Chart.js) ===
    const ctx = document.getElementById('realtimeChart').getContext('2d');
    
    // Gradient cho đồ thị
    const gradBlue = ctx.createLinearGradient(0, 0, 0, 400);
    gradBlue.addColorStop(0, 'rgba(14, 165, 233, 0.5)');
    gradBlue.addColorStop(1, 'rgba(14, 165, 233, 0.0)');
    
    const gradPurple = ctx.createLinearGradient(0, 0, 0, 400);
    gradPurple.addColorStop(0, 'rgba(99, 102, 241, 0.5)');
    gradPurple.addColorStop(1, 'rgba(99, 102, 241, 0.0)');

    const trafficChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Source TX (Kbps)',
                    borderColor: '#0ea5e9',
                    backgroundColor: gradBlue,
                    borderWidth: 2,
                    tension: 0.4,
                    fill: true,
                    data: []
                },
                {
                    label: 'Dest TX (Kbps)',
                    borderColor: '#6366f1',
                    backgroundColor: gradPurple,
                    borderWidth: 2,
                    tension: 0.4,
                    fill: true,
                    data: []
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: false,
            scales: {
                x: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.05)' } },
                y: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.05)' }, beginAtZero: true }
            },
            plugins: {
                legend: { labels: { color: '#f8fafc' } }
            }
        }
    });

    let lastSrcTx = -1, lastDstTx = -1;
    let lastTime = 0;

    setInterval(fetchTraffic, 1500); // 1.5 giây

    async function fetchTraffic() {
        const src = document.getElementById('chart-src').value;
        const dst = document.getElementById('chart-dst').value;
        
        try {
            const res = await fetch(`/api/traffic?src=${src}&dst=${dst}`);
            if(!res.ok) return;
            const data = await res.json();
            
            const curTime = data.timestamp;
            const curSrcTx = data.src.tx_bytes;
            const curDstTx = data.dst.tx_bytes;
            
            if (lastSrcTx !== -1 && lastDstTx !== -1) {
                const dt = curTime - lastTime;
                if(dt > 0) {
                    // tx_bytes difference * 8 / 1,000 / dt = Kbps
                    const srcKbps = ((curSrcTx - lastSrcTx) * 8 / 1000 / dt).toFixed(2);
                    const dstKbps = ((curDstTx - lastDstTx) * 8 / 1000 / dt).toFixed(2);
                    
                    const timeStr = new Date().toLocaleTimeString('en-US', {hour12:false});
                    
                    trafficChart.data.labels.push(timeStr);
                    trafficChart.data.datasets[0].data.push(srcKbps);
                    trafficChart.data.datasets[1].data.push(dstKbps);
                    
                    // Giữ tối đa 20 điểm trên biểu đồ
                    if(trafficChart.data.labels.length > 20) {
                        trafficChart.data.labels.shift();
                        trafficChart.data.datasets[0].data.shift();
                        trafficChart.data.datasets[1].data.shift();
                    }
                    trafficChart.update();
                }
            }
            
            lastSrcTx = curSrcTx;
            lastDstTx = curDstTx;
            lastTime = curTime;
            
        } catch(e) {
            // Im lặng bỏ qua lỗi nếu mininet tắt
        }
    }
});
