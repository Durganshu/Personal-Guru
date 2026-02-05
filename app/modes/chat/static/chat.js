// Initialize markdown-it (same config as Chapter Mode)
const md = window.markdownit({
    html: true,
    linkify: true,
    typographer: true,
    breaks: true
});

function toggleSidebar() {
    const sidebar = document.getElementById('plan-sidebar');
    sidebar.classList.toggle('collapsed');
    localStorage.setItem('chatSidebarCollapsed', sidebar.classList.contains('collapsed'));
}

// Restoration handled by inline script in template to prevent flicker

// Re-enable transitions after initial render
document.addEventListener('DOMContentLoaded', () => {
    // Small timeout to ensure paint has happened
    setTimeout(() => {
        const sidebar = document.getElementById('plan-sidebar');
        if (sidebar) {
            sidebar.classList.remove('no-transition');
        }
    }, 100);

    setupSelectionMenu();
});


// Extract raw content and render markdown for AI messages
function renderMarkdown() {
    const messages = document.querySelectorAll('.message');

    messages.forEach(function (messageEl) {
        const contentEl = messageEl.querySelector('.message-content');
        const rawEl = messageEl.querySelector('.raw-markdown');

        if (contentEl && rawEl && !contentEl.dataset.rendered) {
            const rawContent = rawEl.textContent;

            if (messageEl.classList.contains('assistant-message')) {
                // Render markdown for assistant messages
                contentEl.innerHTML = md.render(rawContent);
            } else {
                // Plain text for user messages
                contentEl.textContent = rawContent;
            }

            contentEl.dataset.rendered = "true";
        }
    });
}

function scrollToBottom() {
    const chatWindow = document.getElementById('chat-window');
    if (!chatWindow) {
        return;
    }
    const messages = chatWindow.querySelectorAll('.message-wrapper');

    if (messages.length > 0) {
        const lastMessage = messages[messages.length - 1];

        // If the last message is from the assistant, scroll to its top
        if (lastMessage.classList.contains('assistant-wrapper')) {
            lastMessage.scrollIntoView({ block: 'start', behavior: 'auto' });
        } else {
            // Otherwise (e.g. user message or empty), scroll to the very bottom
            chatWindow.scrollTop = chatWindow.scrollHeight;
        }
    }
}

document.addEventListener('DOMContentLoaded', function () {
    renderMarkdown();
    scrollToBottom();

    // Focus input after rendering
    document.getElementById('chat-input').focus();

    // Disable plan modification form while submitting
    document.getElementById('plan-modification-form').addEventListener('submit', function (e) {
        const textarea = document.getElementById('plan-modification-input');
        const button = document.getElementById('plan-modification-button');

        // Prevent submission if textarea is empty
        if (!textarea.value.trim()) {
            e.preventDefault();
            return false;
        }

        // Disable interactions during submission
        button.disabled = true;
        textarea.readOnly = true;
    });

    // Auto-resize and Keydown logic for main chat input
    const chatInput = document.getElementById('chat-input');
    const CHAT_INPUT_MAX_HEIGHT = 190;

    // Removed scrollUpBtn/scrollDownBtn selectors and logic

    function handleInput() {
        chatInput.style.height = 'auto'; // Reset height to calculate scrollHeight

        const scrollHeight = chatInput.scrollHeight;

        chatInput.style.height = Math.min(scrollHeight, CHAT_INPUT_MAX_HEIGHT) + 'px';

        // Hide scrollbar if content fits, show if it overflows
        chatInput.style.overflowY = scrollHeight > CHAT_INPUT_MAX_HEIGHT ? 'auto' : 'hidden';
    }

    /* Removed updateScrollIndicators function and its listeners */

    chatInput.addEventListener('input', handleInput);

    // Change cursor to default when hovering over scrollbar
    chatInput.addEventListener('mousemove', function (e) {
        // clientWidth excludes scrollbar, offsetWidth includes it
        const isOverScrollbar = e.offsetX > this.clientWidth || e.offsetY > this.clientHeight;
        this.style.cursor = isOverScrollbar ? 'default' : 'text';
    });

    chatInput.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            // Only submit if not empty
            if (this.value.trim()) {
                document.getElementById('chat-form').requestSubmit();
            }
        }
    });

    // Plan Modification Input Keydown Logic
    const planInput = document.getElementById('plan-modification-input');
    planInput.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (this.value.trim()) {
                document.getElementById('plan-modification-form').requestSubmit();
            }
        }
    });

    // Auto-resize for plan modification input (optional, but consistent)
    planInput.addEventListener('input', function () {
        this.style.height = 'auto';
        this.style.height = Math.min(this.scrollHeight, 200) + 'px';
    });

    // Prevent empty submissions and disable input while loading
    // AJAX Submission Logic
    document.getElementById('chat-form').addEventListener('submit', async function (e) {
        e.preventDefault();

        const input = document.getElementById('chat-input');
        const button = document.getElementById('send-button');
        const loading = document.getElementById('loading-indicator');
        const chatWindow = document.getElementById('chat-window');

        const messageValue = input.value.trim();
        if (!messageValue) return false;

        // 1. UI Updates - User Message
        // Create wrapper
        const userWrapper = document.createElement('div');
        userWrapper.className = 'message-wrapper user-wrapper';
        userWrapper.innerHTML = `
            <div class="message-label user-label">You</div>
            <div class="message user-message">
                <div class="message-content" data-rendered="true">${messageValue}</div>
                <div class="raw-markdown" style="display: none;">${messageValue}</div>
            </div>
        `;
        chatWindow.appendChild(userWrapper);

        // 2. UI Updates - Skeleton Message
        const skeletonWrapper = document.createElement('div');
        skeletonWrapper.className = 'message-wrapper assistant-wrapper skeleton-wrapper'; // tag for easy removal
        skeletonWrapper.innerHTML = `
            <div class="message-label assistant-label">AI Tutor</div>
            <div class="message assistant-message skeleton-message">
                <div class="skeleton-content">
                    <div class="thinking-label" style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 8px; font-weight: 500;">Thinking...</div>
                    <div class="skeleton-line"></div>
                    <div class="skeleton-line"></div>
                    <div class="skeleton-line"></div>
                </div>
            </div>
        `;
        chatWindow.appendChild(skeletonWrapper);
        scrollToBottom();

        // Capture FormData BEFORE clearing input
        const formData = new FormData(this);

        // Clear and Disable Input
        input.value = '';
        input.style.height = 'auto'; // Reset height
        input.readOnly = true;
        button.disabled = true;

        // Disable mic button
        const micButton = document.getElementById('mic-button');
        if (micButton) micButton.disabled = true;

        try {
            // 3. Send AJAX Request
            // Ensure time_spent is sent if needed, usually passed by hidden input logic, but let's trust formData

            // We need to send it as form data but expect JSON
            // Using fetch with FormData automatically sets Content-Type (multipart)
            // But routes.py expects form data for 'message', so this works.
            // Just need headers for JSON acceptance.

            console.log('Sending AJAX request to:', this.action);
            const response = await fetch(this.action, {
                method: 'POST',
                headers: {
                    'Accept': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || ''
                },
                body: formData
            });

            console.log('Response status:', response.status);
            if (!response.ok) {
                const errorText = await response.text();
                console.error('Response error body:', errorText);
                throw new Error(`Network response was not ok: ${response.status}`);
            }

            const data = await response.json();
            console.log('Received data:', data);
            const answer = data.answer;

            // 4. Replace Skeleton with Real Message
            skeletonWrapper.remove();

            const aiWrapper = document.createElement('div');
            aiWrapper.className = 'message-wrapper assistant-wrapper';
            aiWrapper.innerHTML = `
                <div class="message-label assistant-label">AI Tutor</div>
                <div class="message assistant-message">
                    <div class="message-content"></div>
                    <div class="raw-markdown" style="display: none;"></div>
                </div>
            `;

            // Set content safely
            const rawDiv = aiWrapper.querySelector('.raw-markdown');
            rawDiv.textContent = answer;

            chatWindow.appendChild(aiWrapper);

            // Render Markdown
            const contentDiv = aiWrapper.querySelector('.message-content');
            contentDiv.innerHTML = md.render(answer);
            contentDiv.dataset.rendered = "true";

            scrollToBottom();

        } catch (error) {
            console.error('Chat error:', error);
            // Show error in chat
            skeletonWrapper.remove();
            const errorWrapper = document.createElement('div');
            errorWrapper.className = 'message-wrapper assistant-wrapper error';
            errorWrapper.innerHTML = `
                <div class="message-label assistant-label">System</div>
                <div class="message assistant-message" style="color: red;">
                    <div class="message-content">Sorry, an error occurred. Please try again.</div>
                </div>
            `;
            chatWindow.appendChild(errorWrapper);
        } finally {
            // 5. Re-enable Input
            input.readOnly = false;
            button.disabled = false;
            if (micButton) {
                micButton.disabled = false;
                // Ensure mic icon is reset if it was stuck (unlikely here as mic logic is separate, but good safety)
                if (micButton.classList.contains('recording') === false) {
                    // Only reset if NOT recording. If recording logic shares state, be careful.
                    // Actually mic logic is separate.
                }
            }
            input.focus();
        }
    });

    // Voice Input Logic
    const micButton = document.getElementById('mic-button');
    let mediaRecorder;
    let audioChunks = [];

    if (micButton) {
        micButton.addEventListener('click', async () => {
            if (!mediaRecorder || mediaRecorder.state === "inactive") {
                // Start Recording
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    mediaRecorder = new MediaRecorder(stream);
                    audioChunks = [];

                    mediaRecorder.addEventListener("dataavailable", event => {
                        audioChunks.push(event.data);
                    });

                    mediaRecorder.addEventListener("stop", async () => {
                        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                        const formData = new FormData();
                        formData.append("audio", audioBlob, "recording.wav");

                        // Show some loading state on input
                        const chatInput = document.getElementById('chat-input');
                        const originalPlaceholder = chatInput.placeholder;
                        chatInput.placeholder = "Understanding audio...";
                        chatInput.disabled = true;

                        // Show Spinner
                        micButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
                        micButton.disabled = true;

                        try {
                            const response = await fetch("/api/transcribe", {
                                method: "POST",
                                headers: {
                                    'X-CSRFToken': document.querySelector('input[name="csrf_token"]').value,
                                    'X-JWE-Token': document.querySelector('meta[name="jwe-token"]')?.getAttribute('content') || ''
                                },
                                body: formData
                            });

                            if (!response.ok) {
                                throw new Error("Transcription failed");
                            }

                            const data = await response.json();

                            if (data.error) {
                                throw new Error(data.error);
                            }

                            if (data.transcript) {
                                chatInput.value += (chatInput.value ? " " : "") + data.transcript;
                                // Auto-submit: ensure the input is enabled so its value is included in form submission
                                chatInput.disabled = false;
                                chatInput.readOnly = false; // Ensure it's not readonly from previous state
                                document.getElementById('chat-form').requestSubmit();
                            }
                        } catch (err) {
                            console.error("Error sending audio:", err);
                            alert("Error sending audio: " + err);
                        } finally {
                            chatInput.disabled = false;
                            chatInput.placeholder = originalPlaceholder || "Ask your AI tutor a question...";

                            // Revert Icon
                            micButton.innerHTML = '';
                            micButton.textContent = "🎙️";
                            micButton.disabled = false;

                            chatInput.focus();

                            // Ensure microphone is released
                            stream.getTracks().forEach(track => track.stop());
                        }
                    });

                    mediaRecorder.start();
                    micButton.textContent = "⏹️"; // Stop icon
                    micButton.classList.add("recording");

                } catch (err) {
                    console.error("Error accessing microphone:", err);
                    alert("Could not access microphone.");
                }
            } else {
                // Stop Recording
                mediaRecorder.stop();
                micButton.textContent = "🎙️";
                micButton.classList.remove("recording");
            }
        });
    }
});

// Ask Personal Guru Selection Menu
function setupSelectionMenu() {
    // 1. Create the button dynamically
    let guruBtn = document.createElement('button');
    guruBtn.className = 'guru-ask-btn';
    guruBtn.innerHTML = 'Ask the Personal Guru';
    document.body.appendChild(guruBtn);

    const chatWindow = document.getElementById('chat-window');

    // 2. Handle Selection
    function handleSelection() {
        const selection = window.getSelection();

        // Basic Validation
        if (!selection.rangeCount || selection.isCollapsed) {
            hideButton();
            return;
        }

        const range = selection.getRangeAt(0);
        const selectedText = selection.toString().trim();
        const commonAncestor = range.commonAncestorContainer;

        // Check if selection is within an assistant message
        // We look for .assistant-message in the ancestor chain
        let iaAssistantMessage = false;
        let node = commonAncestor.nodeType === 3 ? commonAncestor.parentNode : commonAncestor;

        while (node) {
            if (node.classList && node.classList.contains('assistant-message')) {
                iaAssistantMessage = true;
                break;
            }
            node = node.parentNode;
        }

        if (!iaAssistantMessage) {
            hideButton();
            return;
        }

        if (selectedText.length === 0) {
            hideButton();
            return;
        }

        // 3. Position Button
        const rect = range.getBoundingClientRect();

        // Calculate position: Centered above the selection
        const btnHeight = 40; // Approx height

        let top = rect.top - btnHeight - 10;
        let left = rect.left + (rect.width / 2) - (guruBtn.offsetWidth / 2);

        // Ensure not off-screen
        if (top < 10) top = rect.bottom + 10;
        if (left < 10) left = 10;
        if (left + guruBtn.offsetWidth > window.innerWidth) left = window.innerWidth - guruBtn.offsetWidth - 10;

        guruBtn.style.top = `${top}px`;
        guruBtn.style.left = `${left}px`;

        showButton();
    }

    function showButton() {
        guruBtn.classList.add('visible');
    }

    function hideButton() {
        guruBtn.classList.remove('visible');
    }

    // Events - attach to chat window or document but check context
    if (chatWindow) {
        chatWindow.addEventListener('mouseup', () => {
            setTimeout(handleSelection, 10);
        });

        chatWindow.addEventListener('keyup', (e) => {
            if (e.key === 'Shift' || e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
                setTimeout(handleSelection, 10);
            }
        });
    }

    // Hide when clicking elsewhere
    document.addEventListener('mousedown', (e) => {
        if (!guruBtn.contains(e.target)) {
            hideButton();
        }
    });

    document.addEventListener('selectionchange', () => {
        const selection = window.getSelection();
        if (selection.isCollapsed) {
            hideButton();
        }
    });

    // 4. Click Handler
    guruBtn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();

        const selection = window.getSelection();
        const text = selection.toString().trim();

        if (text) {
            openChatAndPaste(text);
        }

        hideButton();
        selection.removeAllRanges();
    });

    function openChatAndPaste(text) {
        const chatPopup = document.getElementById('chat-popup');
        const chatLauncher = document.getElementById('chat-launcher');
        const chatInput = document.getElementById('chat-input-popup');

        if (!chatPopup || !chatInput) return;

        // Open chat if closed
        if (chatPopup.style.display === 'none' || chatPopup.style.display === '') {
            if (chatLauncher) chatLauncher.click();
        }

        // Paste text
        chatInput.value = text;
        chatInput.focus();

        // Optional: Dispatch input event if you have auto-resize logic bound to it
        chatInput.dispatchEvent(new Event('input', { bubbles: true }));
    }
}
