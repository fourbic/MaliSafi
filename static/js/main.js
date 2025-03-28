// MaliSafi main JavaScript functionality

document.addEventListener('DOMContentLoaded', function() {
    // Handle form submissions with loading indicator
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            // Prevent default submission only for the main search form
            // Don't prevent the card form submissions as they work fine with normal submission
            if (!this.closest('.search-card')) {
                e.preventDefault();
                
                // Basic form validation
                const inputs = this.querySelectorAll('input[type="text"]');
                let isValid = true;
                
                inputs.forEach(input => {
                    if (!input.value.trim()) {
                        isValid = false;
                        input.classList.add('error');
                    } else {
                        input.classList.remove('error');
                    }
                });
                
                if (!isValid) {
                    // Create a flash message for validation errors
                    const flashContainer = document.querySelector('.flash-messages') || document.createElement('div');
                    if (!document.querySelector('.flash-messages')) {
                        flashContainer.classList.add('flash-messages');
                        this.closest('section').insertAdjacentElement('afterend', flashContainer);
                    }
                    
                    const alert = document.createElement('div');
                    alert.classList.add('alert', 'alert-error');
                    alert.textContent = 'Please fill in all search fields';
                    flashContainer.appendChild(alert);
                    
                    // Remove the alert after 3 seconds
                    setTimeout(() => {
                        alert.remove();
                        if (flashContainer.children.length === 0) {
                            flashContainer.remove();
                        }
                    }, 3000);
                    
                    return;
                }
                
                // Show loading indicator
                const loadingOverlay = document.createElement('div');
                loadingOverlay.className = 'loading-overlay';
                loadingOverlay.innerHTML = '<div class="spinner"></div><p>Our AI agents are analyzing properties...</p>';
                document.body.appendChild(loadingOverlay);
                
                // Submit the form after a short delay to ensure the loading indicator is visible
                setTimeout(() => {
                    this.submit();
                }, 100);
            } else {
                // For card forms, just show a loading indicator
                const button = this.querySelector('button[type="submit"]');
                button.textContent = 'Processing...';
                button.disabled = true;
            }
        });
    });
    
    // Add input focus effects
    const inputs = document.querySelectorAll('input');
    
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.classList.add('focused');
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