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
                        <div class="certificate-org">Jefferson Amateur Radio Club</div>
                        <div class="certificate-subtitle">Takes pleasure in awarding this Certificate of Merit to</div>
                    </div>

                    <div style="display: flex; align-items: center; justify-content: center;">
                        <img src="/static/images/fleur.svg" class="certificate-fleur" alt="Fleur de lis" onerror="this.style.display='none'">
                        <div class="certificate-callsign">${result.callsign}</div>
                        <img src="/static/images/fleur.svg" class="certificate-fleur" alt="Fleur de lis" onerror="this.style.display='none'">
                    </div>

                    <div class="certificate-recognition">In Recognition of Achievement</div>

                    <div class="certificate-contest">${result.year} Louisiana QSO Party</div>

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
                        <img src="/static/images/sticker2.png" class="certificate-logo" alt="Jefferson Amateur Radio Club">
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
        html += `<div class="result-item"><div class="result-label">Callsign:</div><div class="result-value highlight">${result.callsign}</div></div>`;
        if (result.name) {
            html += `<div class="result-item"><div class="result-label">Operator Name:</div><div class="result-value">${result.name}</div></div>`;
        }
        html += `<div class="result-item"><div class="result-label">Category:</div><div class="result-value">${result.category}</div></div>`;
        if (result.overlay) {
            html += `<div class="result-item"><div class="result-label">Overlay:</div><div class="result-value">${result.overlay}</div></div>`;
        }
        html += `<div class="result-item"><div class="result-label">Location Type:</div><div class="result-value">${result.location_type}</div></div>`;
        html += `<div class="result-item"><div class="result-label">Mode Category:</div><div class="result-value">${result.mode_category}</div></div>`;
        html += `<div class="result-item"><div class="result-label">Power Level:</div><div class="result-value">${result.power_level}</div></div>`;
        html += '</div>';

        // Score Summary
        html += '<div class="result-group"><h4>Score Summary</h4>';
        html += `<div class="result-item"><div class="result-label">Final Score:</div><div class="result-value highlight">${result.final_score.toLocaleString()}</div></div>`;
        html += `<div class="result-item"><div class="result-label">QSO Points:</div><div class="result-value">${result.qso_points.toLocaleString()}</div></div>`;
        html += `<div class="result-item"><div class="result-label">Total Multipliers:</div><div class="result-value">${result.total_multipliers}</div></div>`;
        if (result.claimed_score) {
            html += `<div class="result-item"><div class="result-label">Claimed Score:</div><div class="result-value">${result.claimed_score.toLocaleString()}</div></div>`;
        }
        html += '</div>';

        // QSO Statistics
        html += '<div class="result-group"><h4>QSO Statistics</h4>';
        html += `<div class="result-item"><div class="result-label">Total QSOs:</div><div class="result-value">${result.total_qsos}</div></div>`;
        html += `<div class="result-item"><div class="result-label">Valid QSOs:</div><div class="result-value">${result.valid_qsos}</div></div>`;
        html += '</div>';

        // Add more sections as needed (multipliers, bonuses, etc.)
        // ... (similar to upload.js formatting)

        return html;
    }

    // Helper functions
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
