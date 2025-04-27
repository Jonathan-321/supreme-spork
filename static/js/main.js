/**
 * AgriFinance - Main JavaScript
 * Common functionality used across the platform
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl, {
            boundary: document.body
        });
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Apply score circle styling
    initScoreCircles();

    // Initialize collapsible cards
    initCollapsibleCards();

    // Add active class to current nav item based on URL
    highlightActiveNavItem();
});

/**
 * Initializes credit score circle visualizations
 */
function initScoreCircles() {
    const scoreCircles = document.querySelectorAll('.score-circle');
    
    scoreCircles.forEach(circle => {
        const scoreText = circle.textContent.trim();
        const score = parseInt(scoreText, 10);
        
        if (!isNaN(score)) {
            // Set the custom property for the circle gradient
            circle.style.setProperty('--score', score);
            
            // Add color classes based on score
            if (score >= 80) {
                circle.classList.add('text-success');
            } else if (score >= 60) {
                circle.classList.add('text-info');
            } else if (score >= 40) {
                circle.classList.add('text-warning');
            } else {
                circle.classList.add('text-danger');
            }
        }
    });
}

/**
 * Initializes collapsible card functionality
 */
function initCollapsibleCards() {
    const cardToggles = document.querySelectorAll('.card-toggle');
    
    cardToggles.forEach(toggle => {
        toggle.addEventListener('click', function() {
            const targetId = this.getAttribute('data-bs-target');
            const targetElement = document.querySelector(targetId);
            const icon = this.querySelector('i');
            
            if (targetElement) {
                if (targetElement.classList.contains('show')) {
                    icon.classList.remove('fa-chevron-up');
                    icon.classList.add('fa-chevron-down');
                } else {
                    icon.classList.remove('fa-chevron-down');
                    icon.classList.add('fa-chevron-up');
                }
            }
        });
    });
}

/**
 * Highlights the active navigation item based on current URL
 */
function highlightActiveNavItem() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href && currentPath.includes(href) && href !== '/') {
            link.classList.add('active');
        } else if (href === '/' && currentPath === '/') {
            link.classList.add('active');
        }
    });
}

/**
 * Formats a number as currency
 * @param {number} amount - The amount to format
 * @param {string} currency - The currency code (default: USD)
 * @returns {string} Formatted currency string
 */
function formatCurrency(amount, currency = 'USD') {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency,
        minimumFractionDigits: 2
    }).format(amount);
}

/**
 * Formats a date string
 * @param {string} dateString - The date string to format
 * @param {string} format - The format type (short, medium, long)
 * @returns {string} Formatted date string
 */
function formatDate(dateString, format = 'medium') {
    const date = new Date(dateString);
    
    if (isNaN(date)) {
        return dateString;
    }
    
    switch (format) {
        case 'short':
            return new Intl.DateTimeFormat('en-US', {
                month: 'numeric',
                day: 'numeric',
                year: '2-digit'
            }).format(date);
        case 'long':
            return new Intl.DateTimeFormat('en-US', {
                weekday: 'long',
                month: 'long',
                day: 'numeric',
                year: 'numeric'
            }).format(date);
        case 'medium':
        default:
            return new Intl.DateTimeFormat('en-US', {
                month: 'short',
                day: 'numeric',
                year: 'numeric'
            }).format(date);
    }
}

/**
 * Creates a simple toast notification
 * @param {string} message - The message to display
 * @param {string} type - The type of toast (success, danger, warning, info)
 * @param {number} duration - Duration in milliseconds
 */
function showToast(message, type = 'info', duration = 3000) {
    // Create toast container if it doesn't exist
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }
    
    // Create toast element
    const toastEl = document.createElement('div');
    toastEl.className = `toast align-items-center text-white bg-${type} border-0`;
    toastEl.setAttribute('role', 'alert');
    toastEl.setAttribute('aria-live', 'assertive');
    toastEl.setAttribute('aria-atomic', 'true');
    
    // Create toast content
    const toastBody = document.createElement('div');
    toastBody.className = 'd-flex';
    
    const toastMessage = document.createElement('div');
    toastMessage.className = 'toast-body';
    toastMessage.textContent = message;
    
    const closeButton = document.createElement('button');
    closeButton.type = 'button';
    closeButton.className = 'btn-close btn-close-white me-2 m-auto';
    closeButton.setAttribute('data-bs-dismiss', 'toast');
    closeButton.setAttribute('aria-label', 'Close');
    
    toastBody.appendChild(toastMessage);
    toastBody.appendChild(closeButton);
    toastEl.appendChild(toastBody);
    toastContainer.appendChild(toastEl);
    
    // Initialize and show toast
    const toast = new bootstrap.Toast(toastEl, {
        autohide: true,
        delay: duration
    });
    
    toast.show();
    
    // Remove toast from DOM after it's hidden
    toastEl.addEventListener('hidden.bs.toast', function() {
        toastEl.remove();
    });
}