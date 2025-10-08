document.addEventListener('DOMContentLoaded', function() {
    // State management
    const state = {
        currentSection: 'profile',
        cvData: {},
        history: [],
        historyIndex: -1,
        isEditing: false,
        autoSaveTimeout: null,
        lastSaved: new Date()
    };

    // DOM Elements
    const elements = {
        cvTitle: document.getElementById('cv-title'),
        cvTemplate: document.getElementById('cv-template'),
        defaultCv: document.getElementById('default-cv'),
        saveCvBtn: document.getElementById('save-cv'),
        downloadPdfBtn: document.getElementById('download-pdf'),
        previewBtn: document.getElementById('preview-btn'),
        closePreviewBtn: document.getElementById('close-preview'),
        printCvBtn: document.getElementById('print-cv'),
        downloadCvBtn: document.getElementById('download-cv'),
        sectionContent: document.getElementById('section-content'),
        editorPanel: document.getElementById('editor-panel'),
        editorContent: document.getElementById('editor-content'),
        editorTitle: document.getElementById('editor-title'),
        closeEditorBtn: document.getElementById('close-editor'),
        previewModal: document.getElementById('preview-modal'),
        cvFullPreview: document.getElementById('cv-full-preview'),
        lastSavedEl: document.getElementById('last-saved')
    };

    // Template data
    const templates = {
        // Template data will be loaded from the server
    };

    // Initialize the application
    function init() {
        loadCvData();
        setupEventListeners();
        updateLastSavedTime();
    }

    // Load CV data from the server
    async function loadCvData() {
        try {
            const response = await fetch('/api/cv/current/');
            if (response.ok) {
                const data = await response.json();
                state.cvData = data;
                renderCurrentSection();
                updateUI();
            } else {
                console.error('Failed to load CV data');
            }
        } catch (error) {
            console.error('Error loading CV data:', error);
        }
    }

    // Save CV data to the server
    async function saveCvData() {
        try {
            const response = await fetch('/api/cv/save/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify({
                    title: elements.cvTitle.value,
                    template_id: elements.cvTemplate.value,
                    is_default: elements.defaultCv.checked,
                    content: state.cvData
                })
            });

            if (response.ok) {
                state.lastSaved = new Date();
                updateLastSavedTime();
                showNotification('CV saved successfully', 'success');
                return true;
            } else {
                throw new Error('Failed to save CV');
            }
        } catch (error) {
            console.error('Error saving CV:', error);
            showNotification('Failed to save CV', 'error');
            return false;
        }
    }

    // Render the current section
    function renderCurrentSection() {
        const section = state.currentSection;
        const sectionData = state.cvData[section] || {};
        
        // Clear current content
        elements.sectionContent.innerHTML = '';
        
        // Render section based on current section
        switch (section) {
            case 'profile':
                renderProfileSection(sectionData);
                break;
            case 'summary':
                renderSummarySection(sectionData);
                break;
            case 'experience':
                renderExperienceSection(sectionData);
                break;
            case 'education':
                renderEducationSection(sectionData);
                break;
            case 'skills':
                renderSkillsSection(sectionData);
                break;
            case 'projects':
                renderProjectsSection(sectionData);
                break;
            case 'languages':
                renderLanguagesSection(sectionData);
                break;
            default:
                elements.sectionContent.innerHTML = `
                    <div class="text-center py-12">
                        <h3 class="text-lg font-medium text-gray-900">Select a section to edit</h3>
                        <p class="mt-2 text-sm text-gray-500">Choose a section from the sidebar to start editing your CV</p>
                    </div>
                `;
        }
    }

    // Render profile section
    function renderProfileSection(data = {}) {
        elements.sectionContent.innerHTML = `
            <div class="space-y-6">
                <div class="flex justify-between items-center">
                    <h2 class="text-xl font-bold text-gray-900">Profile Information</h2>
                    <button id="edit-profile" class="text-indigo-600 hover:text-indigo-800 text-sm font-medium">
                        <i class="fas fa-edit mr-1"></i> Edit
                    </button>
                </div>
                
                <div class="bg-white shadow overflow-hidden sm:rounded-lg">
                    <div class="px-4 py-5 sm:px-6">
                        <h3 class="text-lg leading-6 font-medium text-gray-900">Personal Information</h3>
                    </div>
                    <div class="border-t border-gray-200 px-4 py-5 sm:p-0">
                        <dl class="sm:divide-y sm:divide-gray-200">
                            <div class="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                                <dt class="text-sm font-medium text-gray-500">Full name</dt>
                                <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2" id="profile-fullname">
                                    ${data.first_name || ''} ${data.last_name || ''}
                                </dd>
                            </div>
                            <div class="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                                <dt class="text-sm font-medium text-gray-500">Email address</dt>
                                <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2" id="profile-email">
                                    ${data.email || 'Not provided'}
                                </dd>
                            </div>
                            <div class="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                                <dt class="text-sm font-medium text-gray-500">Phone</dt>
                                <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2" id="profile-phone">
                                    ${data.phone || 'Not provided'}
                                </dd>
                            </div>
                            <div class="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                                <dt class="text-sm font-medium text-gray-500">Location</dt>
                                <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2" id="profile-location">
                                    ${[data.city, data.country].filter(Boolean).join(', ') || 'Not provided'}
                                </dd>
                            </div>
                            <div class="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                                <dt class="text-sm font-medium text-gray-500">Professional Summary</dt>
                                <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2" id="profile-summary">
                                    ${data.professional_summary || 'Not provided'}
                                </dd>
                            </div>
                        </dl>
                    </div>
                </div>
                
                <div class="bg-white shadow overflow-hidden sm:rounded-lg mt-6">
                    <div class="px-4 py-5 sm:px-6">
                        <h3 class="text-lg leading-6 font-medium text-gray-900">Online Presence</h3>
                    </div>
                    <div class="border-t border-gray-200 px-4 py-5 sm:p-0">
                        <dl class="sm:divide-y sm:divide-gray-200">
                            <div class="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                                <dt class="text-sm font-medium text-gray-500">LinkedIn</dt>
                                <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                                    ${data.linkedin_url ? `<a href="${data.linkedin_url}" target="_blank" class="text-indigo-600 hover:text-indigo-800">${data.linkedin_url}</a>` : 'Not provided'}
                                </dd>
                            </div>
                            <div class="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                                <dt class="text-sm font-medium text-gray-500">GitHub</dt>
                                <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                                    ${data.github_url ? `<a href="${data.github_url}" target="_blank" class="text-indigo-600 hover:text-indigo-800">${data.github_url}</a>` : 'Not provided'}
                                </dd>
                            </div>
                            <div class="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                                <dt class="text-sm font-medium text-gray-500">Portfolio</dt>
                                <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                                    ${data.portfolio_url ? `<a href="${data.portfolio_url}" target="_blank" class="text-indigo-600 hover:text-indigo-800">${data.portfolio_url}</a>` : 'Not provided'}
                                </dd>
                            </div>
                        </dl>
                    </div>
                </div>
            </div>
        `;
        
        // Add event listener for edit button
        document.getElementById('edit-profile')?.addEventListener('click', () => {
            openEditor('profile', data);
        });
    }

    // Render other section functions (summary, experience, education, skills, projects, languages)
    // These would follow a similar pattern to renderProfileSection
    
    // Open editor panel
    function openEditor(section, data = {}) {
        state.isEditing = true;
        elements.editorTitle.textContent = `Edit ${section.charAt(0).toUpperCase() + section.slice(1)}`;
        elements.editorContent.innerHTML = getEditorForm(section, data);
        elements.editorPanel.classList.remove('hidden');
        
        // Add event listeners for form submission
        const form = document.getElementById('editor-form');
        if (form) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                saveEditorForm(section);
            });
        }
    }

    // Close editor panel
    function closeEditor() {
        state.isEditing = false;
        elements.editorPanel.classList.add('hidden');
    }

    // Get editor form HTML based on section
    function getEditorForm(section, data = {}) {
        // This would return different form HTML based on the section
        // For brevity, here's a simplified version
        return `
            <form id="editor-form" class="space-y-4">
                <div class="form-group">
                    <label for="field-name" class="form-label">Name</label>
                    <input type="text" id="field-name" class="w-full" value="${data.name || ''}">
                </div>
                <div class="flex justify-end space-x-3 pt-4">
                    <button type="button" id="cancel-edit" class="btn btn-outline">Cancel</button>
                    <button type="submit" class="btn btn-primary">Save Changes</button>
                </div>
            </form>
        `;
    }

    // Save editor form data
    function saveEditorForm(section) {
        // This would collect data from the form and update the state
        const formData = {};
        
        // Update state
        if (!state.cvData[section]) {
            state.cvData[section] = {};
        }
        
        Object.assign(state.cvData[section], formData);
        
        // Close editor and update UI
        closeEditor();
        renderCurrentSection();
        scheduleAutoSave();
    }

    // Setup event listeners
    function setupEventListeners() {
        // Section navigation
        document.querySelectorAll('.section-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const section = btn.dataset.section;
                if (section) {
                    state.currentSection = section;
                    updateActiveSection();
                    renderCurrentSection();
                }
            });
        });

        // Save CV button
        elements.saveCvBtn?.addEventListener('click', saveCvData);
        
        // Download PDF button
        elements.downloadPdfBtn?.addEventListener('click', () => {
            // This would generate and download a PDF
            console.log('Downloading PDF...');
        });
        
        // Preview button
        elements.previewBtn?.addEventListener('click', showPreview);
        
        // Close preview button
        elements.closePreviewBtn?.addEventListener('click', hidePreview);
        
        // Print CV button
        elements.printCvBtn?.addEventListener('click', printCv);
        
        // Close editor button
        elements.closeEditorBtn?.addEventListener('click', closeEditor);
        
        // Auto-save on input changes
        elements.cvTitle?.addEventListener('input', scheduleAutoSave);
        elements.cvTemplate?.addEventListener('change', scheduleAutoSave);
        elements.defaultCv?.addEventListener('change', scheduleAutoSave);
    }

    // Update active section in the UI
    function updateActiveSection() {
        document.querySelectorAll('.section-btn').forEach(btn => {
            if (btn.dataset.section === state.currentSection) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });
    }

    // Schedule auto-save
    function scheduleAutoSave() {
        if (state.autoSaveTimeout) {
            clearTimeout(state.autoSaveTimeout);
        }
        
        state.autoSaveTimeout = setTimeout(() => {
            saveCvData();
        }, 1000);
    }

    // Show preview
    function showPreview() {
        // This would render the full CV in the preview modal
        elements.cvFullPreview.innerHTML = `
            <div class="p-8">
                <h1 class="text-2xl font-bold mb-4">${elements.cvTitle.value || 'My CV'}</h1>
                <!-- Full CV content would be rendered here -->
            </div>
        `;
        
        elements.previewModal.classList.remove('hidden');
    }

    // Hide preview
    function hidePreview() {
        elements.previewModal.classList.add('hidden');
    }

    // Print CV
    function printCv() {
        window.print();
    }

    // Update last saved time
    function updateLastSavedTime() {
        if (elements.lastSavedEl) {
            elements.lastSavedEl.textContent = formatTimeAgo(state.lastSaved);
        }
    }

    // Format time ago
    function formatTimeAgo(date) {
        const seconds = Math.floor((new Date() - date) / 1000);
        
        let interval = Math.floor(seconds / 31536000);
        if (interval >= 1) return interval + ' years ago';
        
        interval = Math.floor(seconds / 2592000);
        if (interval >= 1) return interval + ' months ago';
        
        interval = Math.floor(seconds / 86400);
        if (interval >= 1) return interval + ' days ago';
        
        interval = Math.floor(seconds / 3600);
        if (interval >= 1) return interval + ' hours ago';
        
        interval = Math.floor(seconds / 60);
        if (interval >= 1) return interval + ' minutes ago';
        
        return 'Just now';
    }

    // Show notification
    function showNotification(message, type = 'info') {
        // This would show a toast notification
        console.log(`[${type}] ${message}`);
    }

    // Get CSRF token
    function getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    }

    // Initialize the app
    init();
});
