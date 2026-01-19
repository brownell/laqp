/**
 * Louisiana QSO Party - Log Upload JavaScript
 * Handles form submission and file/paste validation
 */

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('upload-form');
    const fileInput = document.getElementById('log_file');
    const textArea = document.getElementById('log_text');
    const submitButton = form.querySelector('.submit-button');
    const resultMessage = document.getElementById('result-message');
    
    // Clear the other input when one is used
    fileInput.addEventListener('change', function() {
        if (this.files.length > 0) {
            textArea.value = '';
        }
    });
    
    textArea.addEventListener('input', function() {
        if (this.value.trim().length > 0) {
            fileInput.value = '';
        }
    });
    
    // Handle form submission
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Clear previous results
        resultMessage.style.display = 'none';
        resultMessage.className = 'result-message';
        resultMessage.innerHTML = '';
        
        // Validate that either file or text is provided
        const hasFile = fileInput.files.length > 0;
        const hasText = textArea.value.trim().length > 0;
        
        if (!hasFile && !hasText) {
            showError('Please either upload a log file or paste your log text.');
            return;
        }
        
        if (hasFile && hasText) {
            showError('Please use either file upload OR paste text, not both.');
            return;
        }
        
        // Disable submit button and show loading
        submitButton.disabled = true;
        submitButton.classList.add('loading');
        submitButton.textContent = 'Validating';
        
        // Prepare form data
        const formData = new FormData(form);
        
        try {
            // Submit to server
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (response.ok && data.success) {
                showSuccess(data);
                form.reset(); // Clear form on success
            } else {
                showError(data.errors || ['An unknown error occurred'], data.warnings, data);
            }
        } catch (error) {
            showError(['Network error: Could not connect to server. Please try again.']);
        } finally {
            // Re-enable submit button
            submitButton.disabled = false;
            submitButton.classList.remove('loading');
            submitButton.textContent = 'Submit Log';
        }
    });
    
    /**
     * Display success message
     */
    function showSuccess(data) {
        let html = `
            <h3>✓ Log Accepted!</h3>
            <p><strong>Callsign:</strong> ${escapeHtml(data.callsign)}</p>
            <p class="qso-info">Your log contains ${data.qso_count} QSOs</p>
            <p>Thank you for participating in the Louisiana QSO Party! 
               You will receive a confirmation email at the address you provided.</p>
        `;
        
        if (data.warnings && data.warnings.length > 0) {
            html += '<div class="warning">';
            html += '<div class="warning-title">Warnings:</div>';
            html += '<ul>';
            data.warnings.forEach(warning => {
                html += `<li>${escapeHtml(warning)}</li>`;
            });
            html += '</ul>';
            html += '</div>';
        }
        
        resultMessage.className = 'result-message success';
        resultMessage.innerHTML = html;
        resultMessage.style.display = 'block';
        
        // Scroll to result
        resultMessage.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
    
    /**
     * Display error message
     */
    function showError(errors, warnings, data) {
        if (!Array.isArray(errors)) {
            errors = [errors];
        }
        
        let html = '<h3>✗ Log Not Accepted</h3>';
        html += '<p>Your log could not be accepted for the following reasons:</p>';
        html += '<ul>';
        errors.forEach(error => {
            html += `<li>${escapeHtml(error)}</li>`;
        });
        html += '</ul>';
        
        if (data && data.qso_count > 0) {
            html += `<p class="qso-info">Your log contains ${data.qso_count} QSOs `;
            if (data.invalid_qso_count > 0) {
                html += `(${data.invalid_qso_count} invalid)`;
            }
            html += '</p>';
        }
        
        html += '<p><strong>Please correct the errors and try again.</strong></p>';
        
        if (warnings && warnings.length > 0) {
            html += '<div class="warning">';
            html += '<div class="warning-title">Warnings:</div>';
            html += '<ul>';
            warnings.forEach(warning => {
                html += `<li>${escapeHtml(warning)}</li>`;
            });
            html += '</ul>';
            html += '</div>';
        }
        
        resultMessage.className = 'result-message error';
        resultMessage.innerHTML = html;
        resultMessage.style.display = 'block';
        
        // Scroll to result
        resultMessage.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
    
    /**
     * Escape HTML to prevent XSS
     */
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
});
