// OS Assistant - Custom JavaScript functionality

// Global variables
let searchTimeout = null;
let currentFeedbackCaseId = null;

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeComponents();
    setupEventListeners();
    loadUserPreferences();
    createScrollToTopButton();
    setupScrollToTop();
});

// Initialize various components
function initializeComponents() {
    // Initialize tooltips if Bootstrap tooltips are available
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    // Auto-resize textareas
    autoResizeTextareas();
    
    // Initialize search functionality
    setupSearchFunctionality();
}

// Setup event listeners
function setupEventListeners() {
    // Form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', handleFormSubmission);
    });
    
    // Keyboard shortcuts
    document.addEventListener('keydown', handleKeyboardShortcuts);
    
    // Auto-save functionality for forms
    setupAutoSave();
    
    // Handle back button navigation
    window.addEventListener('popstate', handleBackNavigation);
}

// System color mapping function
function getSystemColor(systemType) {
    const systemColors = {
        'Sistema SGU': 'primary',
        'SGU-CRM': 'info', 
        'SGU-Card': 'success',
        'SGU-Portais': 'warning',
        'SGU GPL': 'secondary',
        'Autorizador/AutSC': 'danger',
        'Aplicativo Unimed Criciúma': 'dark',
        'Tasy': 'purple',
        'Syngoo': 'cyan',
        'Pep RS': 'orange',
        'Database': 'pink'
    };
    return systemColors[systemType] || 'secondary';
}

// Create scroll to top button
function createScrollToTopButton() {
    const scrollBtn = document.createElement('button');
    scrollBtn.id = 'scrollToTop';
    scrollBtn.innerHTML = '<i data-feather="arrow-up"></i>';
    scrollBtn.className = 'btn btn-primary scroll-to-top-btn';
    scrollBtn.style.cssText = `
        position: fixed;
        bottom: 30px;
        right: 30px;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        display: none;
        z-index: 1000;
        border: none;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        transition: all 0.3s ease;
    `;
    
    scrollBtn.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
    
    document.body.appendChild(scrollBtn);
    
    // Initialize feather icons for the new button
    if (typeof feather !== 'undefined') {
        feather.replace();
    }
}

// Setup scroll to top functionality
function setupScrollToTop() {
    const scrollBtn = document.getElementById('scrollToTop');
    
    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            scrollBtn.style.display = 'block';
        } else {
            scrollBtn.style.display = 'none';
        }
    });
}

// Handle Enter key submission for textarea
function handleEnterSubmit(event) {
    // Check if Enter key is pressed without Shift (Shift+Enter for new line)
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault(); // Prevent new line
        
        // Find the form and submit it
        const form = event.target.closest('form');
        if (form) {
            // Check if textarea has content
            const textarea = event.target;
            if (textarea.value.trim().length > 0) {
                form.submit();
            }
        }
    }
}

// Handle form submissions with loading states
function handleFormSubmission(event) {
    const form = event.target;
    const submitButton = form.querySelector('button[type="submit"]');
    
    if (submitButton) {
        // Show loading state
        const originalText = submitButton.innerHTML;
        submitButton.innerHTML = '<i data-feather="loader" class="me-1"></i>Processing...';
        submitButton.disabled = true;
        
        // Re-initialize feather icons
        if (typeof feather !== 'undefined') {
            feather.replace();
        }
        
        // Reset button after 10 seconds (fallback)
        setTimeout(() => {
            submitButton.innerHTML = originalText;
            submitButton.disabled = false;
            if (typeof feather !== 'undefined') {
                feather.replace();
            }
        }, 10000);
    }
}

// Keyboard shortcuts
function handleKeyboardShortcuts(event) {
    // Ctrl+Enter to submit forms
    if (event.ctrlKey && event.key === 'Enter') {
        const activeForm = document.querySelector('form:focus-within');
        if (activeForm) {
            activeForm.submit();
        }
    }
    
    // Escape to close modals
    if (event.key === 'Escape') {
        const openModal = document.querySelector('.modal.show');
        if (openModal && typeof bootstrap !== 'undefined') {
            const modal = bootstrap.Modal.getInstance(openModal);
            if (modal) {
                modal.hide();
            }
        }
    }
}

// Auto-resize textareas
function autoResizeTextareas() {
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 400) + 'px';
        });
        
        // Initial resize
        textarea.dispatchEvent(new Event('input'));
    });
}

// Setup search functionality
function setupSearchFunctionality() {
    const searchInputs = document.querySelectorAll('input[name="search"]');
    searchInputs.forEach(input => {
        input.addEventListener('input', function() {
            // Debounce search
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                performInstantSearch(this.value);
            }, 300);
        });
    });
}

// Perform instant search (for future enhancement)
function performInstantSearch(query) {
    // This could be enhanced to perform real-time search
    console.log('Searching for:', query);
}

// Auto-save functionality
function setupAutoSave() {
    const autoSaveInputs = document.querySelectorAll('textarea[name="problem_description"], textarea[name="solution"]');
    autoSaveInputs.forEach(input => {
        input.addEventListener('input', debounce(saveFormData, 2000));
    });
}

// Debounce function
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Save form data to localStorage
function saveFormData() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        const formData = new FormData(form);
        const data = {};
        
        for (let [key, value] of formData.entries()) {
            data[key] = value;
        }
        
        if (Object.keys(data).length > 0) {
            localStorage.setItem(`form_${form.action}`, JSON.stringify(data));
        }
    });
}

// Load form data from localStorage
function loadFormData() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        const saved = localStorage.getItem(`form_${form.action}`);
        if (saved) {
            try {
                const data = JSON.parse(saved);
                Object.keys(data).forEach(key => {
                    const input = form.querySelector(`[name="${key}"]`);
                    if (input && input.type !== 'file') {
                        input.value = data[key];
                    }
                });
            } catch (e) {
                console.error('Error loading saved form data:', e);
            }
        }
    });
}

// Handle back button navigation
function handleBackNavigation(event) {
    // Clean up any unsaved data warnings if needed
    console.log('Navigating back');
}

// Load user preferences
function loadUserPreferences() {
    const prefs = localStorage.getItem('userPreferences');
    if (prefs) {
        try {
            const preferences = JSON.parse(prefs);
            applyPreferences(preferences);
        } catch (e) {
            console.error('Error loading user preferences:', e);
        }
    }
}

// Apply user preferences
function applyPreferences(preferences) {
    // Apply theme preferences, font size, etc.
    if (preferences.theme) {
        document.documentElement.setAttribute('data-bs-theme', preferences.theme);
    }
}

// Utility functions
const Utils = {
    // Show notification toast
    showToast: function(message, type = 'info', duration = 5000) {
        const toastId = 'toast-' + Date.now();
        const toastHtml = `
            <div id="${toastId}" class="toast align-items-center text-bg-${type} border-0" role="alert" 
                 style="position: fixed; top: 20px; right: 20px; z-index: 1050;">
                <div class="d-flex">
                    <div class="toast-body">${message}</div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', toastHtml);
        
        if (typeof bootstrap !== 'undefined') {
            const toastElement = document.getElementById(toastId);
            const toast = new bootstrap.Toast(toastElement, { delay: duration });
            toast.show();
            
            // Remove toast element after it's hidden
            toastElement.addEventListener('hidden.bs.toast', function() {
                toastElement.remove();
            });
        }
    },
    
    // Copy text to clipboard
    copyToClipboard: function(text) {
        if (navigator.clipboard && window.isSecureContext) {
            return navigator.clipboard.writeText(text).then(() => {
                this.showToast('Copied to clipboard!', 'success');
            }).catch(err => {
                console.error('Failed to copy:', err);
                this.fallbackCopyTextToClipboard(text);
            });
        } else {
            this.fallbackCopyTextToClipboard(text);
        }
    },
    
    // Fallback copy method
    fallbackCopyTextToClipboard: function(text) {
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.top = '0';
        textArea.style.left = '0';
        textArea.style.position = 'fixed';
        textArea.style.opacity = '0';
        
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
            const successful = document.execCommand('copy');
            if (successful) {
                this.showToast('Copied to clipboard!', 'success');
            } else {
                this.showToast('Failed to copy to clipboard', 'danger');
            }
        } catch (err) {
            console.error('Fallback copy failed:', err);
            this.showToast('Failed to copy to clipboard', 'danger');
        }
        
        document.body.removeChild(textArea);
    },
    
    // Format date for display
    formatDate: function(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diffTime = Math.abs(now - date);
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        
        if (diffDays === 1) {
            return 'Yesterday';
        } else if (diffDays < 7) {
            return `${diffDays} days ago`;
        } else {
            return date.toLocaleDateString();
        }
    },
    
    // Validate form fields
    validateForm: function(form) {
        const errors = [];
        const requiredFields = form.querySelectorAll('[required]');
        
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                errors.push(`${field.labels[0]?.textContent || field.name} is required`);
                field.classList.add('is-invalid');
            } else {
                field.classList.remove('is-invalid');
            }
        });
        
        return {
            isValid: errors.length === 0,
            errors: errors
        };
    },
    
    // Highlight search terms
    highlightText: function(text, searchTerm) {
        if (!searchTerm) return text;
        
        const regex = new RegExp(`(${searchTerm})`, 'gi');
        return text.replace(regex, '<span class="search-highlight">$1</span>');
    }
};

// Export utility functions to global scope
window.OSAssistant = {
    Utils: Utils,
    showToast: Utils.showToast,
    copyToClipboard: Utils.copyToClipboard
};

// Performance monitoring
window.addEventListener('load', function() {
    // Log performance metrics
    if (window.performance) {
        const loadTime = window.performance.timing.loadEventEnd - window.performance.timing.navigationStart;
        console.log(`Page loaded in ${loadTime}ms`);
    }
});

// Error handling
window.addEventListener('error', function(event) {
    console.error('JavaScript error:', event.error);
    // Could send error reports to server in production
});

// Handle offline/online status
window.addEventListener('offline', function() {
    Utils.showToast('You are now offline. Some features may not work.', 'warning');
});

window.addEventListener('online', function() {
    Utils.showToast('You are back online!', 'success');
});
