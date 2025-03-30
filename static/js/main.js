// MaliSafi main JavaScript functionality

document.addEventListener('DOMContentLoaded', function() {
    // Handle form submissions with loading indicator
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            // Prevent default submission only for the main search form
            if (!this.closest('.search-card')) {
                e.preventDefault();
                
                // Basic form validation
                const inputs = this.querySelectorAll('input[type="text"], select');
                let isValid = true;
                let errorMessage = '';
                
                inputs.forEach(input => {
                    if (!input.value.trim()) {
                        isValid = false;
                        input.classList.add('error');
                        errorMessage = 'Please fill in all search fields';
                    } else {
                        input.classList.remove('error');
                    }
                });
                
                if (!isValid) {
                    showFlashMessage(errorMessage, 'error');
                    return;
                }
                
                // Show loading indicator with progress
                showLoadingOverlay();
                
                // Submit the form after a short delay to ensure the loading indicator is visible
                setTimeout(() => {
                    this.submit();
                }, 100);
            } else {
                // For card forms, show loading state on button
                const button = this.querySelector('button[type="submit"]');
                const originalText = button.textContent;
                button.textContent = 'Processing...';
                button.disabled = true;
                
                // Reset button state after 5 seconds (in case of error)
                setTimeout(() => {
                    button.textContent = originalText;
                    button.disabled = false;
                }, 5000);
            }
        });
    });
    
    // Add input focus effects
    const inputs = document.querySelectorAll('input, select');
    
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.classList.add('focused');
            this.classList.remove('error');
        });
        
        input.addEventListener('blur', function() {
            this.classList.remove('focused');
            
            // Validate on blur
            if (!this.value.trim() && this.hasAttribute('required')) {
                this.classList.add('error');
            } else {
                this.classList.remove('error');
            }
        });
    });
});

// Helper functions
function showFlashMessage(message, type = 'error') {
    const flashContainer = document.querySelector('.flash-messages') || document.createElement('div');
    if (!document.querySelector('.flash-messages')) {
        flashContainer.classList.add('flash-messages');
        document.body.insertBefore(flashContainer, document.body.firstChild);
    }
    
    const alert = document.createElement('div');
    alert.classList.add('alert', `alert-${type}`);
    alert.textContent = message;
    flashContainer.appendChild(alert);
    
    // Remove the alert after 3 seconds
    setTimeout(() => {
        alert.remove();
        if (flashContainer.children.length === 0) {
            flashContainer.remove();
        }
    }, 3000);
}

function showLoadingOverlay() {
    const loadingOverlay = document.createElement('div');
    loadingOverlay.className = 'loading-overlay';
    loadingOverlay.innerHTML = `
        <div class="skyscraper-loader">
            <div class="building">
                <div class="floor"></div>
                <div class="floor"></div>
                <div class="floor"></div>
                <div class="floor"></div>
                <div class="floor"></div>
                <div class="floor"></div>
                <div class="floor"></div>
                <div class="floor"></div>
                <div class="floor"></div>
                <div class="floor"></div>
            </div>
        </div>
        <div class="loading-text">
            <p id="loadingMessage">Building your property analysis...</p>
            <p class="animate-fade-in" style="font-size: 0.9rem; margin-top: 0.5rem;">This may take a few moments</p>
        </div>
    `;
    document.body.appendChild(loadingOverlay);
    
    // Update loading message periodically
    const loadingMessages = [
        "Analyzing market trends...",
        "Calculating property values...",
        "Checking location insights...",
        "Preparing investment recommendations...",
        "Finalizing your report..."
    ];
    
    let messageIndex = 0;
    const messageInterval = setInterval(() => {
        messageIndex = (messageIndex + 1) % loadingMessages.length;
        const messageElement = loadingOverlay.querySelector('#loadingMessage');
        messageElement.style.opacity = 0;
        
        setTimeout(() => {
            messageElement.textContent = loadingMessages[messageIndex];
            messageElement.style.opacity = 1;
        }, 500);
    }, 3000);
    
    // Clean up on page unload
    window.addEventListener('unload', () => {
        clearInterval(messageInterval);
        loadingOverlay.remove();
    });
} 