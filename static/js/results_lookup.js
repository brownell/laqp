// Louisiana QSO Party Results Lookup - JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const yearSelect = document.getElementById('year');
    const callsignInput = document.getElementById('callsign');
    const showIndividualBtn = document.getElementById('showIndividualBtn');
    const showFinalReportBtn = document.getElementById('showFinalReportBtn');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const messageBox = document.getElementById('messageBox');
    const individualResults = document.getElementById('individualResults');
    const finalReport = document.getElementById('finalReport');

    // Auto-uppercase callsign
    callsignInput.addEventListener('input', function() {
        this.value = this.value.toUpperCase();
    });

    // Show individual results
    showIndividualBtn.addEventListener('click', async function() {
        const year = yearSelect.value.trim();
        const callsign = callsignInput.value.trim().toUpperCase();

        if (!year) {
            showMessage('Please select a contest year', 'error');
            return;
        }

        if (!callsign) {
            showMessage('Please enter your callsign', 'error');
            return;
        }

        await loadIndividualResults(year, callsign);
    });

    // Show final report
    showFinalReportBtn.addEventListener('click', async function() {
        const year = yearSelect.value.trim();

        if (!year) {
            showMessage('Please select a contest year', 'error');
            return;
        }

        await loadFinalReport(year);
    });

    // Load individual results
    async function loadIndividualResults(year, callsign) {
        hideMessage();
        hideResults();
        showLoading();

        try {
            const response = await fetch('/api/individual_results', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    year: year,
                    callsign: callsign
                })
            });

            const data = await response.json();
            hideLoading();

            if (data.success) {
                displayIndividualResults(data.result, data.rankings_display);
                scrollToResults();
            } else {
                showMessage(data.error || 'Results not found', 'error');
            }

        } catch (error) {
            hideLoading();
            showMessage('Error loading results: ' + error.message, 'error');
        }
    }

    // Load final report
    async function loadFinalReport(year) {
        hideMessage();
        hideResults();
        showLoading();

        try {
            const response = await fetch(`/api/final_report/${year}`);
            const data = await response.json();

            hideLoading();

            if (data.success) {
                displayFinalReport(data.html);
                scrollToResults();
            } else {
                showMessage(data.error || 'Final report not found', 'error');
            }

        } catch (error) {
            hideLoading();
            showMessage('Error loading final report: ' + error.message, 'error');
        }
    }

    // Display individual results
    function displayIndividualResults(result, rankingsDisplay) {
        // Generate certificate
        const certificateHTML = generateCertificate(result, rankingsDisplay);
        document.getElementById('certificateContent').innerHTML = certificateHTML;

        // Generate statistics (reuse existing format function from upload.js)
        const statisticsHTML = generateStatisticsHTML(result);
        document.getElementById('statisticsContent').innerHTML = statisticsHTML;

        // Show individual results section
        individualResults.style.display = 'block';
        finalReport.style.display = 'none';
    }

    // Display final report
    function displayFinalReport(html) {
        document.getElementById('finalReportContent').innerHTML = html;

        // Show final report section
        finalReport.style.display = 'block';
        individualResults.style.display = 'none';
    }

    // Generate certificate HTML
    function generateCertificate(result, rankingsDisplay) {
        const rankingsHTML = rankingsDisplay.map(r => 
            `<div class="certificate-ranking-item"><strong>${r}</strong></div>`
        ).join('');

        return `
            <div class="certificate">
                <div class="certificate-border">
                    <div class="certificate-header">
                    <div class="certificate-title">${result.year} Louisiana QSO Party</div>
                        <div class="certificate-org">Jefferson Amateur Radio Club</div>
                        <div class="certificate-subtitle">Takes pleasure in awarding this Certificate of Merit to</div>
                    </div>

                    <div style="display: flex; align-items: center; justify-content: center;">
                        <div class="certificate-callsign">${result.callsign}</div>
                    </div>

                    <div class="rankings">In Recognition of Achievement</div>

                    <div class="certificate-score">
                        <strong>${result.final_score.toLocaleString()} Points</strong>
                    </div>

                    <div class="certificate-rankings">
                        ${rankingsHTML}
                    </div>

                    <div class="certificate-footer">
                        <div class="certificate-signature">
                            [Signature Placeholder]
                        </div>
                        <img src="/static/images/jarc_logo.png" class="certificate-logo" alt="Jefferson Amateur Radio Club">
                    </div>
                </div>
            </div>
        `;
    }

    // Generate statistics HTML (adapted from upload.js)
    function generateStatisticsHTML(result) {
        let html = '';

        // Station Information
        html += '<div class="result-group"><h4>Station Information</h4>';
        html += `<div class="result-item"><div class="result-label">Callsign:</div><div class="result-value">${result.callsign}</div></div>`;
        if (result.name) {
            html += `<div class="result-item"><div class="result-label">Operator Name:</div><div class="result-value">${result.name}</div></div>`;
        }
        if (result.category) {
        html += `<div class="result-item"><div class="result-label">Category:</div><div class="result-value">${result.category}</div></div>`;
        } else {
            html += `<div class="result-item"><div class="result-label">Category:</div><div class="result-value">None - Not in rankings</div></div>`;
        }
        if (result.overlay) {
            html += `<div class="result-item"><div class="result-label">Overlay:</div><div class="result-value">${result.overlay}</div></div>`;
        }
        html += `<div class="result-item"><div class="result-label">Location Type:</div><div class="result-value">${result.location_type}</div></div>`;
        html += `<div class="result-item"><div class="result-label">Mode Category:</div><div class="result-value">${result.mode_category}</div></div>`;
        html += `<div class="result-item"><div class="result-label">Power Level:</div><div class="result-value">${result.power_level}</div></div>`;
        html += '</div>';

        // Score Summary
        html += '<div class="result-group"><h4>Score Summary</h4>';
        html += `<div class="result-item"><div class="result-label">Final Score:</div><div class="result-value ">${result.final_score.toLocaleString()}</div></div>`;
        if (result.claimed_score) {
            html += `<div class="result-item"><div class="result-label">Claimed Score:</div><div class="result-value">${result.claimed_score.toLocaleString()}</div></div>`;
        }
        html += `<div class="result-item"><div class="result-label">QSO Points:</div><div class="result-value">${result.qso_points.toLocaleString()}</div></div>`;
        html += `<div class="result-item"><div class="result-label">Total Multipliers:</div><div class="result-value">${result.total_multipliers}</div></div>`;

        // Bonuses
        let hasBonuses = false;
        let bonusesHTML = '<div class="result-group">';
        bonusesHTML += '<h4>Bonuses</h4>';

        if (result.worked_n5lcc && result.worked_n5lcc !== 'N/A') {
            hasBonuses = true;
            bonusesHTML += renderResultItem('Worked N5LCC', result.worked_n5lcc ? 'Yes' : 'No');
            if (result.num_n5lcc_contacts > 0) {
                bonusesHTML += renderResultItem('N5LCC Contacts', result.num_n5lcc_contacts);
            }
        }

        if (result.parishes_activated && result.parishes_activated.length > 0) {
            hasBonuses = true;
            bonusesHTML += renderResultItem('Parishes Activated (Rover)', result.parishes_activated.length);
            bonusesHTML += '<div class="result-list">';
            result.parishes_activated.forEach(parish => {
                bonusesHTML += `<span class="result-list-item">${parish}</span>`;
            });
            bonusesHTML += '</div>';
        }

        if (result.rover_bonus_points > 0) {
            hasBonuses = true;
            bonusesHTML += renderResultItem('Rover Bonus Points', result.rover_bonus_points.toLocaleString());
        }

        bonusesHTML += '</div>';

        if (hasBonuses) {
            html += bonusesHTML;
        }
        html += '</div>';

        // QSO Statistics
        html += '<div class="result-group"><h4>QSO Statistics</h4>';
        html += `<div class="result-item"><div class="result-label">Total QSOs:</div><div class="result-value ">${result.total_qsos.toLocaleString()}</div></div>`;
        html += `<div class="result-item"><div class="result-label">Valid QSOs:</div><div class="result-value ">${result.valid_qsos.toLocaleString()}</div></div>`;
        html += '</div>';

        // QSOs by Band
        if (result.qsos_by_band && result.qsos_by_band.length > 0) {
            html += '<div class="result-group">';
            html += '<h4>QSOs by Band</h4>';
            html += '<table class="result-table">';
            html += '<thead><tr><th>Band</th><th>Count</th></tr></thead>';
            html += '<tbody>';
            result.qsos_by_band.forEach(item => {
                if (item.count > 0) {
                    html += `<tr><td>${item.band}m</td><td>${item.count}</td></tr>`;
                }
            });
            html += '</tbody></table>';
            html += '</div>';
        }

        // QSOs by Mode
        if (result.qsos_by_mode && result.qsos_by_mode.length > 0) {
            html += '<div class="result-group">';
            html += '<h4>QSOs by Mode</h4>';
            html += '<table class="result-table">';
            html += '<thead><tr><th>Mode</th><th>Count</th></tr></thead>';
            html += '<tbody>';
            result.qsos_by_mode.forEach(item => {
                if (item.count > 0) {
                    html += `<tr><td>${item.mode}</td><td>${item.count}</td></tr>`;
                }
            });
            html += '</tbody></table>';
            html += '</div>';
        }

        // QSOs by Hour
        if (result.qsos_by_hour && result.qsos_by_hour.length > 0) {
            html += '<div class="result-group">';
            html += '<h4>QSOs by Hour</h4>';
            html += '<table class="result-table">';
            html += '<thead><tr><th>Hour</th><th>Count</th></tr></thead>';
            html += '<tbody>';
            result.qsos_by_hour.forEach(item => {
                if (item.count > 0) {
                    html += `<tr><td>Hour ${item.hour + 1}</td><td>${item.count}</td></tr>`;
                }
            });
            html += '</tbody></table>';
            html += '</div>';
        }

                // Multipliers
        html += '<div class="result-group">';
        html += '<h4>Multipliers</h4>';
        
        // Parishes worked (for NON-LA stations)
        if (result.parishes_worked && result.parishes_worked.length > 0) {
            html += renderResultItem('Parishes Worked', result.parishes_worked_multiplier);
            html += '<div class="result-list">';
            result.parishes_worked.forEach(parish => {
                html += `<span class="result-list-item">${parish}</span>`;
            });
            html += '</div>';
        }

        // States worked (for LA stations)
        if (result.states_worked && result.states_worked.length > 0) {
            html += renderResultItem('States Worked', result.states_worked_multiplier);
            html += '<div class="result-list">';
            result.states_worked.forEach(state => {
                html += `<span class="result-list-item">${state}</span>`;
            });
            html += '</div>';
        }

        // Provinces worked (for LA stations)
        if (result.provinces_worked && result.provinces_worked.length > 0) {
            html += renderResultItem('Provinces Worked', result.provinces_multiplier);
            html += '<div class="result-list">';
            result.provinces_worked.forEach(province => {
                html += `<span class="result-list-item">${province}</span>`;
            });
            html += '</div>';
        }

        // DX worked (for LA stations)
        if (result.dx_worked && result.dx_worked.length > 0) {
            html += renderResultItem('DX Worked', result.dx_worked_multiplier);
            html += '<div class="result-list">';
            result.dx_worked.forEach(dx => {
                html += `<span class="result-list-item">${dx}</span>`;
            });
            html += '</div>';
        }

        // Bands Worked
        if (result.bands_worked && result.bands_worked.length > 0) {
            html += '<div class="result-group">';
            html += '<h4>Bands Worked</h4>';
            html += '<div class="result-list">';
            result.bands_worked.forEach(band => {
                html += `<span class="result-list-item">${band}m</span>`;
            });
            html += '</div>';
            html += '</div>';
        }

        return html;
    }

    // Helper functions
    // Function to render a result item
    function renderResultItem(label, value, highlight = false) {
        const highlightClass = highlight ? ' highlight' : '';
        return `
            <div class="result-item">
                <div class="result-label">${label}:</div>
                <div class="result-value${highlightClass}">${value}</div>
            </div>
        `;
    }
    function showLoading() {
        loadingIndicator.style.display = 'block';
        showIndividualBtn.disabled = true;
        showFinalReportBtn.disabled = true;
    }

    function hideLoading() {
        loadingIndicator.style.display = 'none';
        showIndividualBtn.disabled = false;
        showFinalReportBtn.disabled = false;
    }

    function showMessage(message, type) {
        messageBox.innerHTML = message;
        messageBox.className = 'message-box ' + type;
        messageBox.style.display = 'block';
    }

    function hideMessage() {
        messageBox.style.display = 'none';
    }

    function hideResults() {
        individualResults.style.display = 'none';
        finalReport.style.display = 'none';
    }

    function scrollToResults() {
        setTimeout(() => {
            if (individualResults.style.display === 'block') {
                individualResults.scrollIntoView({ behavior: 'smooth' });
            } else if (finalReport.style.display === 'block') {
                finalReport.scrollIntoView({ behavior: 'smooth' });
            }
        }, 300);
    }
});

// Print functions
function printCertificate() {
    document.body.classList.add('print-certificate');
    window.print();
    document.body.classList.remove('print-certificate');
}

function printStatistics() {
    document.body.classList.add('print-statistics');
    window.print();
    document.body.classList.remove('print-statistics');
}

function printFinalReport() {
    document.body.classList.add('print-final-report');
    window.print();
    document.body.classList.remove('print-final-report');
}
