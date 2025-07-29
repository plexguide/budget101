// Budget101 - JavaScript functionality

document.addEventListener('DOMContentLoaded', function() {
    // Sidebar toggle functionality
    const sidebarCollapse = document.getElementById('sidebarCollapse');
    const sidebar = document.getElementById('sidebar');
    const content = document.getElementById('content');

    if (sidebarCollapse) {
        sidebarCollapse.addEventListener('click', function() {
            sidebar.classList.toggle('collapsed');
            content.classList.toggle('expanded');
        });
    }

    // Mobile sidebar toggle
    function handleMobileResize() {
        if (window.innerWidth <= 768) {
            sidebar.classList.add('collapsed');
            content.classList.add('expanded');
        } else {
            sidebar.classList.remove('collapsed');
            content.classList.remove('expanded');
        }
    }

    // Initial check
    handleMobileResize();

    // Listen for window resize
    window.addEventListener('resize', handleMobileResize);

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            if (alert && alert.parentNode) {
                alert.classList.remove('show');
                setTimeout(function() {
                    if (alert.parentNode) {
                        alert.parentNode.removeChild(alert);
                    }
                }, 150);
            }
        }, 5000);
    });

    // Add fade-in animation to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach(function(card, index) {
        card.style.animationDelay = (index * 0.1) + 's';
        card.classList.add('fade-in');
    });

    // Enhanced form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Loading state for buttons
    function addLoadingState(button) {
        if (!button) {
            return function() {}; // Return no-op function if button is null
        }
        
        const originalText = button.innerHTML;
        button.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span>Loading...';
        button.disabled = true;

        return function() {
            button.innerHTML = originalText;
            button.disabled = false;
        };
    }

    // API helper functions
    window.Budget101 = {
        // Show toast notification
        showToast: function(message, type = 'success') {
            const toastHtml = `
                <div class="toast align-items-center text-bg-${type} border-0" role="alert">
                    <div class="d-flex">
                        <div class="toast-body">${message}</div>
                        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                    </div>
                </div>
            `;
            
            let toastContainer = document.querySelector('.toast-container');
            if (!toastContainer) {
                toastContainer = document.createElement('div');
                toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
                document.body.appendChild(toastContainer);
            }
            
            toastContainer.insertAdjacentHTML('beforeend', toastHtml);
            const toast = toastContainer.lastElementChild;
            const bsToast = new bootstrap.Toast(toast);
            bsToast.show();
            
            toast.addEventListener('hidden.bs.toast', function() {
                toast.remove();
            });
        },

        // API request helper
        apiRequest: function(url, options = {}) {
            const defaultOptions = {
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'same-origin' // Include session cookies
            };

            // If body is provided but no method specified, default to POST
            if (options.body && !options.method) {
                options.method = 'POST';
            }

            const finalOptions = { ...defaultOptions, ...options };
            console.log('API Request - URL:', url, 'Options:', finalOptions);

            return fetch(url, finalOptions)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .catch(error => {
                    console.error('API request failed:', error);
                    this.showToast('An error occurred. Please try again.', 'danger');
                    throw error;
                });
        },

        // Add new bill
        addBill: function(billData) {
            return this.apiRequest('/api/bills', {
                method: 'POST',
                body: JSON.stringify(billData)
            });
        },

        // Add new tax record
        addTaxRecord: function(taxData) {
            return this.apiRequest('/api/taxes', {
                method: 'POST',
                body: JSON.stringify(taxData)
            });
        },

        // Format currency
        formatCurrency: function(amount) {
            return new Intl.NumberFormat('en-US', {
                style: 'currency',
                currency: 'USD'
            }).format(amount);
        },

        // Format date
        formatDate: function(date) {
            return new Intl.DateTimeFormat('en-US').format(new Date(date));
        }
    };

    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Handle form submissions with AJAX
    const ajaxForms = document.querySelectorAll('[data-ajax="true"]');
    ajaxForms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());
            
            // Find submit button - either inside form or outside with form attribute
            let submitButton = form.querySelector('button[type="submit"]');
            if (!submitButton && form.id) {
                submitButton = document.querySelector(`button[type="submit"][form="${form.id}"]`);
            }
            
            let resetLoading = function() {}; // Default no-op function
            if (submitButton) {
                resetLoading = addLoadingState(submitButton);
            }
            
            const action = form.action || window.location.pathname;
            const method = (form.method && form.method.toUpperCase()) || 'POST';
            
            console.log('Form submission - Action:', action, 'Method:', method, 'Data:', data);
            
            Budget101.apiRequest(action, {
                method: method,
                body: JSON.stringify(data)
            })
            .then(response => {
                Budget101.showToast('Success!', 'success');
                form.reset();
                
                // Close modal if it exists
                const modal = form.closest('.modal');
                if (modal) {
                    const bsModal = bootstrap.Modal.getInstance(modal);
                    if (bsModal) {
                        bsModal.hide();
                    }
                }
                
                // Reload page or update content as needed
                if (response.redirect) {
                    window.location.href = response.redirect;
                } else if (response.reload) {
                    window.location.reload();
                } else {
                    // Default to reload for successful submissions
                    window.location.reload();
                }
            })
            .catch(error => {
                console.error('Form submission error:', error);
                Budget101.showToast('An error occurred. Please try again.', 'danger');
            })
            .finally(() => {
                resetLoading();
            });
        });
    });

    // Dark mode toggle (if needed in future)
    const darkModeToggle = document.getElementById('darkModeToggle');
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', function() {
            document.body.classList.toggle('light-theme');
            localStorage.setItem('theme', document.body.classList.contains('light-theme') ? 'light' : 'dark');
        });

        // Apply saved theme
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme === 'light') {
            document.body.classList.add('light-theme');
        }
    }

    // Search functionality
    const searchInputs = document.querySelectorAll('[data-search]');
    searchInputs.forEach(function(input) {
        const target = input.getAttribute('data-search');
        const searchTarget = document.querySelector(target);
        
        if (searchTarget) {
            input.addEventListener('input', function() {
                const searchTerm = input.value.toLowerCase();
                const items = searchTarget.querySelectorAll('[data-searchable]');
                
                items.forEach(function(item) {
                    const text = item.textContent.toLowerCase();
                    if (text.includes(searchTerm)) {
                        item.style.display = '';
                    } else {
                        item.style.display = 'none';
                    }
                });
            });
        }
    });

    // Auto-save functionality for forms
    const autoSaveForms = document.querySelectorAll('[data-autosave]');
    autoSaveForms.forEach(function(form) {
        const inputs = form.querySelectorAll('input, textarea, select');
        
        inputs.forEach(function(input) {
            input.addEventListener('change', function() {
                const formData = new FormData(form);
                const data = Object.fromEntries(formData.entries());
                
                // Save to localStorage
                localStorage.setItem(`autosave_${form.id}`, JSON.stringify(data));
            });
        });
        
        // Restore saved data
        const savedData = localStorage.getItem(`autosave_${form.id}`);
        if (savedData) {
            const data = JSON.parse(savedData);
            Object.keys(data).forEach(function(key) {
                const input = form.querySelector(`[name="${key}"]`);
                if (input) {
                    input.value = data[key];
                }
            });
        }
    });

    console.log('Budget101 initialized successfully');
}); 