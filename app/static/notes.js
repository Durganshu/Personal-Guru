/**
 * Notes functionality for Personal Guru
 * Handles sidebar toggling, rich text editing, and auto-saving.
 */

const NotesManager = (() => {
    let _topicName = null;
    let _csrfToken = null;
    let _jweToken = null;
    let _saveTimeout = null;
    let _isDirty = false;
    let _editor = null;
    let _statusEl = null;

    /**
     * Initialize the notes manager
     */
    function init(config) {
        _topicName = config.topicName;
        _csrfToken = config.csrfToken;
        _jweToken = config.jweToken || '';

        _editor = document.getElementById('notes-editor');
        _statusEl = document.getElementById('save-status');

        if (!_editor) return; // Sidebar might be closed or not present

        // Load initial content if empty (API fetch)
        loadNotes();

        // Bind events
        bindEvents();
    }

    function bindEvents() {
        // Toolbar buttons
        document.querySelectorAll('.toolbar-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const command = btn.dataset.command;
                if (command) {
                    document.execCommand(command, false, null);
                    _editor.focus();
                    triggerSave();
                }
            });
        });

        // Font selection
        const fontSelect = document.getElementById('font-select');
        if (fontSelect) {
            fontSelect.addEventListener('change', (e) => {
                document.execCommand('fontName', false, e.target.value);
                _editor.focus();
                triggerSave();
            });
        }

        // Editor input
        _editor.addEventListener('input', () => {
            triggerSave();
        });

        // Sidebar toggle (global)
        window.toggleNotesSidebar = toggleSidebar;

        // Export button
        const exportBtn = document.getElementById('export-btn');
        if (exportBtn) {
            exportBtn.addEventListener('click', exportNotes);
        }
    }

    function triggerSave() {
        _isDirty = true;
        if (_statusEl) _statusEl.textContent = 'Saving...';

        if (_saveTimeout) clearTimeout(_saveTimeout);
        _saveTimeout = setTimeout(saveNotes, 1000); // Auto-save after 1 second of inactivity
    }

    async function loadNotes() {
        if (_statusEl) _statusEl.textContent = 'Loading...';
        try {
            const response = await fetch(`/api/notes/${encodeURIComponent(_topicName)}`, {
                headers: {
                    'X-JWE-Token': _jweToken
                }
            });
            if (response.ok) {
                const data = await response.json();
                if (data.notes) {
                    _editor.innerHTML = data.notes;
                }
                if (_statusEl) _statusEl.textContent = 'All changes saved';
            }
        } catch (e) {
            console.error('Failed to load notes', e);
            if (_statusEl) _statusEl.textContent = 'Error loading notes';
        }
    }

    async function saveNotes() {
        if (!_isDirty) return;

        try {
            const content = _editor.innerHTML;
            const response = await fetch(`/api/notes/${encodeURIComponent(_topicName)}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': _csrfToken,
                    'X-JWE-Token': _jweToken
                },
                body: JSON.stringify({ notes: content })
            });

            if (response.ok) {
                _isDirty = false;
                if (_statusEl) _statusEl.textContent = 'All changes saved';
            } else {
                if (_statusEl) _statusEl.textContent = 'Error saving';
            }
        } catch (e) {
            console.error('Failed to save notes', e);
            if (_statusEl) _statusEl.textContent = 'Error saving (Network)';
        }
    }

    function toggleSidebar() {
        const sidebar = document.getElementById('notes-sidebar');
        if (sidebar) {
            sidebar.classList.toggle('active');

            // If opening and empty, load notes
            if (sidebar.classList.contains('active') && (!_editor.innerHTML.trim())) {
               loadNotes();
            }
        }
    }

    function exportNotes() {
        const content = _editor.innerText; // Plain text for now
        const blob = new Blob([content], { type: 'text/markdown' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${_topicName}_notes.md`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    return {
        init
    };
})();

// Expose to window
window.initNotes = NotesManager.init;
