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
            if (sidebar.classList.contains('active')) {
                if (!_editor.innerHTML.trim()) {
                    loadNotes();
                }
                // Initialize resizer if not already done
                initResizer(sidebar);
            }
        }
    }

    function initResizer(sidebar) {
        if (sidebar.querySelector('#notes-sidebar-resizer')) return;

        const resizer = document.createElement('div');
        resizer.id = 'notes-sidebar-resizer';
        sidebar.appendChild(resizer);

        let startX, startWidth;

        function startResize(e) {
            startX = e.clientX;
            startWidth = parseInt(document.defaultView.getComputedStyle(sidebar).width, 10);
            document.documentElement.addEventListener('mousemove', doResize, false);
            document.documentElement.addEventListener('mouseup', stopResize, false);
            resizer.classList.add('resizing');
        }

        function doResize(e) {
            const newWidth = startWidth + (startX - e.clientX);
            if (newWidth > 200 && newWidth < 800) { // Min 200px, Max 800px
                sidebar.style.width = newWidth + 'px';
            }
        }

        function stopResize(e) {
            document.documentElement.removeEventListener('mousemove', doResize, false);
            document.documentElement.removeEventListener('mouseup', stopResize, false);
            resizer.classList.remove('resizing');
        }

        resizer.addEventListener('mousedown', startResize, false);
    }

    function exportNotes() {
        const content = _editor.innerHTML;
        // Basic HTML structure with embedded styles for a better "Rich Text" export experience
        const htmlContent = `
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>${_topicName} Notes</title>
<style>
    body { font-family: sans-serif; line-height: 1.6; max-width: 800px; margin: 2rem auto; padding: 0 1rem; color: #333; }
    h1 { border-bottom: 2px solid #eee; padding-bottom: 0.5rem; }
    /* Basic Markdown-ish styles */
    blockquote { border-left: 4px solid #ccc; margin: 0; padding-left: 1rem; color: #666; }
    code { background: #f4f4f4; padding: 0.2rem 0.4rem; border-radius: 3px; }
    pre { background: #f4f4f4; padding: 1rem; overflow-x: auto; }
</style>
</head>
<body>
    <h1>${_topicName}</h1>
    ${content}
</body>
</html>`;

        const blob = new Blob([htmlContent], { type: 'text/html' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${_topicName}_notes.html`; // CHANGED: Export as HTML to preserve formatting
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
