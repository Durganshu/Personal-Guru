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

            // Adjust body padding to push content
            if (sidebar.classList.contains('active')) {
                const width = sidebar.offsetWidth;
                document.body.style.transition = "padding-right 0.3s cubic-bezier(0.4, 0, 0.2, 1)";
                document.body.style.paddingRight = width + "px";

                if (!_editor.innerHTML.trim()) {
                    loadNotes();
                }
                initResizer(sidebar);
            } else {
                document.body.style.paddingRight = "0";
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
            document.body.style.transition = "none"; // Disable transition during drag
            sidebar.style.transition = "none";
            document.documentElement.addEventListener('mousemove', doResize, false);
            document.documentElement.addEventListener('mouseup', stopResize, false);
            resizer.classList.add('resizing');
        }

        function doResize(e) {
            const newWidth = startWidth + (startX - e.clientX);
            if (newWidth > 200 && newWidth < 800) {
                sidebar.style.width = newWidth + 'px';
                document.body.style.paddingRight = newWidth + 'px';
            }
        }

        function stopResize(e) {
            document.documentElement.removeEventListener('mousemove', doResize, false);
            document.documentElement.removeEventListener('mouseup', stopResize, false);
            resizer.classList.remove('resizing');
            // Re-enable transitions
            document.body.style.transition = "padding-right 0.3s cubic-bezier(0.4, 0, 0.2, 1)";
            sidebar.style.transition = "transform 0.3s cubic-bezier(0.4, 0, 0.2, 1)";
        }

        resizer.addEventListener('mousedown', startResize, false);
    }

    function htmlToMarkdown(html) {
        let text = html;

        // Block elements spacing
        text = text.replace(/<div>/gi, '\n');
        text = text.replace(/<\/div>/gi, '');
        text = text.replace(/<p>/gi, '\n');
        text = text.replace(/<\/p>/gi, '\n');
        text = text.replace(/<br\s*\/?>/gi, '\n');

        // Headers
        text = text.replace(/<h1>(.*?)<\/h1>/gi, '# $1\n');
        text = text.replace(/<h2>(.*?)<\/h2>/gi, '## $1\n');
        text = text.replace(/<h3>(.*?)<\/h3>/gi, '### $1\n');

        // Lists - Handle nested structure simply
        // Process Ordered Lists first
        text = text.replace(/<ol>(.*?)<\/ol>/gis, (match, content) => {
            let itemIndex = 1;
            return content.replace(/<li>(.*?)<\/li>/gi, (m, c) => {
                return `${itemIndex++}. ${c}\n`;
            });
        });

        // Process Unordered Lists
        text = text.replace(/<ul>(.*?)<\/ul>/gis, (match, content) => {
            return content.replace(/<li>(.*?)<\/li>/gi, '- $1\n');
        });

        // Cleanup wrapper list tags if any remain or nested ones (simplified approach)
        text = text.replace(/<(ul|ol)>/gi, '');
        text = text.replace(/<\/(ul|ol)>/gi, '');
        text = text.replace(/<li>(.*?)<\/li>/gi, '- $1\n'); // Fallback for orphans

        // Text Styles
        text = text.replace(/<b>(.*?)<\/b>/gi, '**$1**');
        text = text.replace(/<strong>(.*?)<\/strong>/gi, '**$1**');
        text = text.replace(/<i>(.*?)<\/i>/gi, '*$1*');
        text = text.replace(/<em>(.*?)<\/em>/gi, '*$1*');
        text = text.replace(/<u>(.*?)<\/u>/gi, '__$1__');
        text = text.replace(/<s>(.*?)<\/s>/gi, '~~$1~~');
        text = text.replace(/<strike>(.*?)<\/strike>/gi, '~~$1~~');

        // Code
        text = text.replace(/<pre>(.*?)<\/pre>/gis, '\n```\n$1\n```\n');
        text = text.replace(/<code>(.*?)<\/code>/gi, '`$1`');

        // Blockquotes
        text = text.replace(/<blockquote>(.*?)<\/blockquote>/gi, '> $1\n');

        // Cleanup HTML tags
        text = text.replace(/<[^>]+>/g, '');

        // Decode entities
        const txt = document.createElement("textarea");
        txt.innerHTML = text;
        return txt.value.trim();
    }

    function exportNotes() {
        const content = _editor.innerHTML;
        const markdown = htmlToMarkdown(content);

        const blob = new Blob([markdown], { type: 'text/markdown' });
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
