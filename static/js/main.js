/**
 * ProTechCV - Main JavaScript File
 * Handles all the interactive elements of the application
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    initTooltips();
    
    // Initialize dropdowns
    initDropdowns();
    
    // Initialize modals
    initModals();
    
    // Initialize tabs
    initTabs();
    
    // Initialize file upload previews
    initFileUploads();
    
    // Initialize form validation
    initFormValidation();
    
    // Initialize date pickers
    initDatePickers();
    
    // Initialize rich text editors
    initRichTextEditors();
    
    // Initialize CV builder steps
    initCVBuilderSteps();
});

/**
 * Initialize tooltips
 */
function initTooltips() {
    const tooltipTriggers = document.querySelectorAll('[data-tooltip]');
    
    tooltipTriggers.forEach(trigger => {
        const tooltip = document.createElement('div');
        tooltip.className = 'tooltip';
        tooltip.textContent = trigger.getAttribute('data-tooltip');
        
        // Position the tooltip
        const updateTooltipPosition = () => {
            const rect = trigger.getBoundingClientRect();
            tooltip.style.top = `${rect.top + window.scrollY - tooltip.offsetHeight - 10}px`;
            tooltip.style.left = `${rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2)}px`;
        };
        
        // Show tooltip on hover
        trigger.addEventListener('mouseenter', () => {
            document.body.appendChild(tooltip);
            updateTooltipPosition();
            tooltip.classList.add('opacity-100');
        });
        
        // Hide tooltip on mouse leave
        trigger.addEventListener('mouseleave', () => {
            tooltip.remove();
        });
        
        // Update position on window resize
        window.addEventListener('resize', updateTooltipPosition);
    });
}

/**
 * Initialize dropdown menus
 */
function initDropdowns() {
    const dropdowns = document.querySelectorAll('.dropdown');
    
    // Close all dropdowns when clicking outside
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.dropdown')) {
            document.querySelectorAll('.dropdown-menu').forEach(menu => {
                menu.classList.add('hidden');
            });
        }
    });
    
    dropdowns.forEach(dropdown => {
        const button = dropdown.querySelector('.dropdown-toggle');
        const menu = dropdown.querySelector('.dropdown-menu');
        
        if (button && menu) {
            button.addEventListener('click', (e) => {
                e.stopPropagation();
                const isOpen = !menu.classList.contains('hidden');
                
                // Close all other dropdowns
                document.querySelectorAll('.dropdown-menu').forEach(m => {
                    if (m !== menu) m.classList.add('hidden');
                });
                
                // Toggle current dropdown
                menu.classList.toggle('hidden', isOpen);
            });
        }
    });
}

/**
 * Initialize modals
 */
function initModals() {
    // Open modal
    document.querySelectorAll('[data-modal-toggle]').forEach(button => {
        const modalId = button.getAttribute('data-modal-toggle');
        const modal = document.getElementById(modalId);
        
        if (modal) {
            button.addEventListener('click', () => {
                modal.classList.remove('hidden');
                document.body.classList.add('overflow-hidden');
            });
            
            // Close button
            const closeButton = modal.querySelector('[data-modal-hide]');
            if (closeButton) {
                closeButton.addEventListener('click', () => {
                    modal.classList.add('hidden');
                    document.body.classList.remove('overflow-hidden');
                });
            }
            
            // Close when clicking outside
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    modal.classList.add('hidden');
                    document.body.classList.remove('overflow-hidden');
                }
            });
            
            // Close with Escape key
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape' && !modal.classList.contains('hidden')) {
                    modal.classList.add('hidden');
                    document.body.classList.remove('overflow-hidden');
                }
            });
        }
    });
}

/**
 * Initialize tab functionality
 */
function initTabs() {
    const tabGroups = document.querySelectorAll('[data-tabs]');
    
    tabGroups.forEach(group => {
        const tabs = group.querySelectorAll('[data-tab]');
        const tabContents = group.querySelectorAll('[data-tab-content]');
        
        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const tabId = tab.getAttribute('data-tab');
                
                // Update active tab
                tabs.forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                
                // Show corresponding content
                tabContents.forEach(content => {
                    if (content.getAttribute('data-tab-content') === tabId) {
                        content.classList.remove('hidden');
                    } else {
                        content.classList.add('hidden');
                    }
                });
            });
        });
        
        // Activate first tab by default
        if (tabs.length > 0) {
            tabs[0].click();
        }
    });
}

/**
 * Initialize file upload previews
 */
function initFileUploads() {
    document.querySelectorAll('.file-upload').forEach(upload => {
        const input = upload.querySelector('input[type="file"]');
        const preview = upload.querySelector('.file-upload-preview');
        const removeButton = upload.querySelector('.file-upload-remove');
        
        if (input && preview) {
            input.addEventListener('change', (e) => {
                const file = input.files[0];
                if (file) {
                    if (file.type.startsWith('image/')) {
                        const reader = new FileReader();
                        reader.onload = (e) => {
                            preview.innerHTML = `<img src="${e.target.result}" class="max-h-32 mx-auto" alt="Preview">`;
                            upload.classList.add('has-file');
                        };
                        reader.readAsDataURL(file);
                    } else {
                        preview.textContent = file.name;
                        upload.classList.add('has-file');
                    }
                }
            });
            
            if (removeButton) {
                removeButton.addEventListener('click', () => {
                    input.value = '';
                    preview.innerHTML = '';
                    upload.classList.remove('has-file');
                });
            }
        }
    });
}

/**
 * Initialize form validation
 */
function initFormValidation() {
    const forms = document.querySelectorAll('form[novalidate]');
    
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input, textarea, select');
        
        const validateField = (field) => {
            const errorElement = field.nextElementSibling;
            
            if (!field.validity.valid) {
                let errorMessage = '';
                
                if (field.validity.valueMissing) {
                    errorMessage = field.getAttribute('data-required-message') || 'This field is required';
                } else if (field.validity.typeMismatch) {
                    if (field.type === 'email') {
                        errorMessage = 'Please enter a valid email address';
                    } else if (field.type === 'url') {
                        errorMessage = 'Please enter a valid URL';
                    }
                } else if (field.validity.tooShort) {
                    errorMessage = `Please enter at least ${field.minLength} characters`;
                } else if (field.validity.tooLong) {
                    errorMessage = `Please enter no more than ${field.maxLength} characters`;
                } else if (field.validity.patternMismatch) {
                    errorMessage = field.getAttribute('title') || 'Please match the requested format';
                }
                
                field.classList.add('border-red-500');
                
                if (errorElement && errorElement.classList.contains('form-error')) {
                    errorElement.textContent = errorMessage;
                    errorElement.classList.remove('hidden');
                }
                
                return false;
            } else {
                field.classList.remove('border-red-500');
                
                if (errorElement && errorElement.classList.contains('form-error')) {
                    errorElement.textContent = '';
                    errorElement.classList.add('hidden');
                }
                
                return true;
            }
        };
        
        inputs.forEach(input => {
            input.addEventListener('blur', () => validateField(input));
            input.addEventListener('input', () => validateField(input));
        });
        
        form.addEventListener('submit', (e) => {
            let isValid = true;
            
            inputs.forEach(input => {
                if (!validateField(input)) {
                    isValid = false;
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                
                // Scroll to first error
                const firstError = form.querySelector('.border-red-500');
                if (firstError) {
                    firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    firstError.focus();
                }
            }
        });
    });
}

/**
 * Initialize date pickers
 */
function initDatePickers() {
    const dateInputs = document.querySelectorAll('input[type="date"]');
    
    dateInputs.forEach(input => {
        // Add date picker UI if not supported natively
        if (!Modernizr.inputtypes.date) {
            // Fallback for browsers that don't support date input
            const datePicker = document.createElement('div');
            datePicker.className = 'date-picker';
            // Initialize a date picker library here if needed
            // For example: new Pikaday({ field: input });
        }
        
        // Format the date for display
        input.addEventListener('change', () => {
            if (input.value) {
                const date = new Date(input.value);
                const formattedDate = date.toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'short',
                    day: 'numeric'
                });
                
                // Update any associated display element
                const displayElement = document.getElementById(`${input.id}-display`);
                if (displayElement) {
                    displayElement.textContent = formattedDate;
                }
            }
        });
    });
}

/**
 * Initialize rich text editors
 */
function initRichTextEditors() {
    const richTextAreas = document.querySelectorAll('.rich-text-editor');
    
    richTextAreas.forEach(container => {
        const textarea = container.querySelector('textarea');
        const toolbar = document.createElement('div');
        toolbar.className = 'rich-text-toolbar mb-2 flex flex-wrap gap-1';
        
        // Add formatting buttons
        const buttons = [
            { icon: 'bold', command: 'bold', title: 'Bold' },
            { icon: 'italic', command: 'italic', title: 'Italic' },
            { icon: 'underline', command: 'underline', title: 'Underline' },
            { icon: 'list-ul', command: 'insertUnorderedList', title: 'Bullet List' },
            { icon: 'list-ol', command: 'insertOrderedList', title: 'Numbered List' },
            { icon: 'link', command: 'createLink', title: 'Insert Link' },
            { icon: 'undo', command: 'undo', title: 'Undo' },
            { icon: 'redo', command: 'redo', title: 'Redo' },
        ];
        
        buttons.forEach(btn => {
            const button = document.createElement('button');
            button.type = 'button';
            button.className = 'p-1 rounded hover:bg-gray-100';
            button.title = btn.title;
            button.innerHTML = `<i class="fas fa-${btn.icon}"></i>`;
            
            button.addEventListener('click', () => {
                document.execCommand(btn.command, false, btn.command === 'createLink' ? 'https://' : null);
                textarea.focus();
            });
            
            toolbar.appendChild(button);
        });
        
        // Insert the toolbar before the textarea
        container.insertBefore(toolbar, textarea);
        
        // Make the textarea contentEditable
        const editor = document.createElement('div');
        editor.className = 'rich-text-content border border-gray-300 rounded p-3 min-h-32 focus:outline-none focus:ring-2 focus:ring-indigo-500';
        editor.contentEditable = true;
        
        // Transfer initial content
        editor.innerHTML = textarea.value || '';
        
        // Update the hidden textarea on input
        editor.addEventListener('input', () => {
            textarea.value = editor.innerHTML;
        });
        
        // Replace the textarea with the contentEditable div
        textarea.style.display = 'none';
        container.insertBefore(editor, textarea.nextSibling);
    });
}

/**
 * Initialize CV builder step navigation
 */
function initCVBuilderSteps() {
    const form = document.querySelector('.cv-builder-form');
    
    if (!form) return;
    
    const steps = form.querySelectorAll('.cv-step');
    const prevButtons = form.querySelectorAll('[data-prev-step]');
    const nextButtons = form.querySelectorAll('[data-next-step]');
    const progressBar = document.querySelector('.progress-bar-fill');
    
    let currentStep = 0;
    
    // Show the first step
    showStep(0);
    
    // Previous button click handler
    prevButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            e.preventDefault();
            showStep(currentStep - 1);
        });
    });
    
    // Next button click handler
    nextButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            e.preventDefault();
            
            // Validate current step before proceeding
            if (validateStep(currentStep)) {
                showStep(currentStep + 1);
            }
        });
    });
    
    // Show a specific step
    function showStep(stepIndex) {
        if (stepIndex < 0 || stepIndex >= steps.length) return;
        
        // Hide all steps
        steps.forEach(step => {
            step.classList.add('hidden');
        });
        
        // Show the current step
        steps[stepIndex].classList.remove('hidden');
        
        // Update current step
        currentStep = stepIndex;
        
        // Update progress bar
        if (progressBar) {
            const progress = ((stepIndex + 1) / steps.length) * 100;
            progressBar.style.width = `${progress}%`;
        }
        
        // Update button states
        updateButtonStates();
        
        // Scroll to top of the form
        form.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    
    // Validate the current step
    function validateStep(stepIndex) {
        const currentStepElement = steps[stepIndex];
        const requiredFields = currentStepElement.querySelectorAll('[required]');
        let isValid = true;
        
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                field.classList.add('border-red-500');
                const errorElement = field.nextElementSibling;
                
                if (errorElement && errorElement.classList.contains('form-error')) {
                    errorElement.textContent = 'This field is required';
                    errorElement.classList.remove('hidden');
                }
                
                isValid = false;
            }
        });
        
        return isValid;
    }
    
    // Update the state of navigation buttons
    function updateButtonStates() {
        const isFirstStep = currentStep === 0;
        const isLastStep = currentStep === steps.length - 1;
        
        // Update previous buttons
        prevButtons.forEach(button => {
            button.classList.toggle('opacity-50 cursor-not-allowed', isFirstStep);
            button.disabled = isFirstStep;
        });
        
        // Update next buttons
        nextButtons.forEach(button => {
            if (isLastStep) {
                button.textContent = 'Submit';
                button.setAttribute('type', 'submit');
            } else {
                button.textContent = 'Next';
                button.setAttribute('type', 'button');
            }
        });
    }
}

/**
 * Debounce function to limit the rate at which a function can fire
 */
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

/**
 * Throttle function to limit the rate at which a function can fire
 */
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * Format a date string to a more readable format
 */
function formatDate(dateString) {
    if (!dateString) return '';
    
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
}

/**
 * Copy text to clipboard
 */
function copyToClipboard(text) {
    const textarea = document.createElement('textarea');
    textarea.value = text;
    document.body.appendChild(textarea);
    textarea.select();
    
    try {
        document.execCommand('copy');
        return true;
    } catch (err) {
        console.error('Failed to copy text: ', err);
        return false;
    } finally {
        document.body.removeChild(textarea);
    }
}

// Export functions for use in other modules
window.ProTechCV = {
    copyToClipboard,
    formatDate,
    debounce,
    throttle
};
