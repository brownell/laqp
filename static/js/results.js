// Louisiana QSO Party Results Lookup - JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('lookupForm');
    const lookupBtn = document.getElementById('lookupBtn');
    const clearBtn = document.getElementById('clearBtn');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const messageBox = document.getElementById('messageBox');
    const resultsSection = document.getElementById('resultsSection');
    const resultsSeparator = document.getElementById('resultsSeparator');
    const resultsContent = document.getElementById('resultsContent');
    const callsignInput = document.getElementById('callsign');

    // Auto-uppercase callsign as user types
    callsignInput.addEventListener('input', function() {
        this.value = this.value.toUpperCase();
    });

    // Clear form
    clearBtn.addEventListener('click', function() {
        form.reset();
        hideMessage();
        hideResults();
    });

    // Form submission
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Get form data
        const callsign = document.getElementById('callsign').value.trim().toUpperCase();
        const year = document.getElementById('year').value.trim();
        
        // Validate
        if (!callsign || !year) {
            showMessage('Please enter both callsign and year', 'error');
            return;
        }
        
        // Clear previous results
        hideMessage();
        hideResults();
        
        // Show loading
        showLoading();
        
        try {
            const response = await fetch('/lookup_results', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    callsign: callsign,
                    year: year
                })
            });
            
            const data = await response.json();
            
            // Hide loading
            hideLoading();
            
            if (data.success) {
                // Display results
                displayResults(data.html);
                
                // Scroll to results
                setTimeout(() => {
                    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }, 300);
            } else {
                // Show error
                showMessage(data.error || 'Results not found', 'error');
            }
            
        } catch (error) {
            hideLoading();
            showMessage('Error communicating with server: ' + error.message, 'error');
        }
    });

    // Show loading indicator
    function showLoading() {
        loadingIndicator.style.display = 'block';
        lookupBtn.disabled = true;
    }

    // Hide loading indicator
    function hideLoading() {
        loadingIndicator.style.display = 'none';
        lookupBtn.disabled = false;
    }

    // Show message
    function showMessage(message, type) {
        messageBox.innerHTML = message;
        messageBox.className = 'message-box ' + type;
        messageBox.style.display = 'block';
    }

    // Hide message
    function hideMessage() {
        messageBox.style.display = 'none';
    }

    // Hide results
    function hideResults() {
        resultsSection.style.display = 'none';
        resultsSeparator.style.display = 'none';
    }

    // Display results
    function displayResults(html) {
        resultsContent.innerHTML = html;
        resultsSection.style.display = 'block';
        resultsSeparator.style.display = 'block';
    }
});
