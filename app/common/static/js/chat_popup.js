// app/common/static/js/chat_popup.js

let chatConfig = {};
let isInitialized = false;

/**
 * Initializes the chat popup UI by wiring up DOM elements and event handlers.
 *
 * The configuration object is stored in a module-level variable and is used
 * by the chat popup to interact with backend services.
 *
 * @param {{urls: {chat: string}}} config - Configuration for the chat popup.
 * @param {Object} config.urls - Collection of endpoint URLs used by the chat.
 * @param {string} config.urls.chat - URL endpoint used to send chat messages
 *     or interact with the chat backend.
 */
function initChatPopup(config) {
    chatConfig = config;

    // Prevent multiple initializations to avoid duplicate event listeners
    if (isInitialized) {
        console.warn('Chat popup already initialized. Updating configuration only.');
        return;
    }
    const chatLauncher = document.getElementById('chat-launcher');
    const chatPopup = document.getElementById('chat-popup');
    const chatToggleBtn = document.getElementById('chat-toggle-btn');
    // Maximize button removed by design
    const chatForm = document.getElementById('chat-form-popup');
    const chatInput = document.getElementById('chat-input-popup');
    const chatHistory = document.getElementById('chat-history-popup');

    const missingElements = [];
    if (!chatLauncher) missingElements.push('chat-launcher');
    if (!chatPopup) missingElements.push('chat-popup');
    if (!chatToggleBtn) missingElements.push('chat-toggle-btn');
    if (!chatForm) missingElements.push('chat-form-popup');
    if (!chatInput) missingElements.push('chat-input-popup');
    if (!chatHistory) missingElements.push('chat-history-popup');

    if (missingElements.length > 0) {
        console.error(
            'Chat popup initialization failed. Missing required element(s): ' +
            missingElements.join(', ')
        );
        return;
    }
    function openChat() {
        chatLauncher.style.display = 'none';
        chatPopup.style.display = 'flex';
        chatPopup.style.transform = 'scale(1)';
        chatPopup.style.opacity = '1';
        chatInput.focus();
    }

    function closeChat() {
        chatPopup.style.transform = 'scale(0.8)';
        chatPopup.style.opacity = '0';
        setTimeout(() => {
            chatPopup.style.display = 'none';
            chatLauncher.style.display = 'flex';
        }, 200);
    }

    chatLauncher.addEventListener('click', openChat);
    chatToggleBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        closeChat();
    });


    // Custom Resize Logic (Top-Left Handle)
    const resizeHandle = chatPopup.querySelector('.resize-handle');
    if (resizeHandle) {
        resizeHandle.addEventListener('mousedown', initResize, false);
    }

    function initResize(e) {
        e.preventDefault();
        window.addEventListener('mousemove', resize, false);
        window.addEventListener('mouseup', stopResize, false);
        chatPopup.classList.add('resizing'); // Optional: for styling
    }

    function resize(e) {
        // Calculate new size based on mouse movement relative to bottom-right anchor
        // Since anchor is bottom-right:
        // Moving mouse LEFT (negative dx) -> width INCREASES
        // Moving mouse UP (negative dy) -> height INCREASES

        // We need initial dimensions? No, just use current Rect + movement?
        // Better: Compare to initial position?
        // Simple delta approach:
        // We know the Right and Bottom are fixed.
        // The Top-Left handle follows the mouse.
        // So Width = WindowRight - MouseX
        // Height = WindowBottom - MouseY (approx)

        const rect = chatPopup.getBoundingClientRect();
        // Since right/bottom are fixed, we can just set width/height based on pointer

        // Calculate new width: Distance from MouseX to ChatRight
        const newWidth = rect.right - e.clientX;
        // Calculate new height: Distance from MouseY to ChatBottom
        const newHeight = rect.bottom - e.clientY;

        if (newWidth > 300) { // Min width
            chatPopup.style.width = newWidth + 'px';
        }
        if (newHeight > 400) { // Min height
            chatPopup.style.height = newHeight + 'px';
        }
    }

    function stopResize(e) {
        window.removeEventListener('mousemove', resize, false);
        window.removeEventListener('mouseup', stopResize, false);
        chatPopup.classList.remove('resizing');
    }


    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const question = chatInput.value;
        if (!question.trim()) return;
        chatInput.value = '';

        // Disable input and submit button during request
        const submitButton = chatForm.querySelector('button[type="submit"]');
        const micButton = document.getElementById('mic-button-popup');

        chatInput.disabled = true;
        if (submitButton) submitButton.disabled = true;
        if (micButton) micButton.disabled = true;

        const userMessage = document.createElement('div');
        userMessage.className = 'chat-message user-message';
        userMessage.innerHTML = '<strong>You:</strong> ';
        userMessage.appendChild(document.createTextNode(question));
        chatHistory.appendChild(userMessage);
        chatHistory.scrollTop = chatHistory.scrollHeight;

        // Skeleton loading placeholder
        const tutorMessage = document.createElement('div');
        tutorMessage.className = 'chat-message tutor-message skeleton-message';
        tutorMessage.innerHTML = `
            <div class="skeleton-content">
                <div class="thinking-label" style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 8px; font-weight: 500;">Thinking...</div>
                <div class="skeleton-line"></div>
                <div class="skeleton-line"></div>
                <div class="skeleton-line"></div>
            </div>
        `;
        chatHistory.appendChild(tutorMessage);
        chatHistory.scrollTop = chatHistory.scrollHeight;

        try {
            const response = await fetch(chatConfig.urls.chat, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '',
                    'X-JWE-Token': document.querySelector('meta[name="jwe-token"]')?.getAttribute('content') || ''
                },
                body: JSON.stringify({ question: question })
            });

            if (!response.ok) {
                throw new Error(`Chat request failed with status ${response.status} ${response.statusText}`);
            }
            const data = await response.json();
            const md = window.markdownit({
                html: false
            });
            const renderedAnswer = md.render(data.answer || '');
            const safeAnswer = window.DOMPurify
                ? window.DOMPurify.sanitize(renderedAnswer)
                : renderedAnswer;

            // Remove skeleton class and show actual content
            tutorMessage.classList.remove('skeleton-message');
            tutorMessage.innerHTML = `<strong>Tutor:</strong> ${safeAnswer}`;

            if (window.renderMath) {
                window.renderMath(tutorMessage);
            }

            chatHistory.scrollTop = chatHistory.scrollHeight;
        } catch (error) {
            tutorMessage.classList.remove('skeleton-message');
            tutorMessage.innerHTML = '<strong>Tutor:</strong> Sorry, something went wrong.';
            console.error('Chat error:', error);
        } finally {
            // Re-enable input and submit button after request completes
            chatInput.disabled = false;
            if (submitButton) submitButton.disabled = false;
            if (micButton) micButton.disabled = false;
            chatInput.focus();
        }
    });

    // Scroll Indicator Logic - Removed as we now use native scrollbar
    // Auto-resize logic
    function handlePopupInput() {
        chatInput.style.height = '1px'; // Correctly reset height to allow shrinking
        chatInput.style.height = (2 + chatInput.scrollHeight) + 'px'; // Add slight buffer

        const POPUP_INPUT_MAX_HEIGHT = 150;
        const scrollHeight = chatInput.scrollHeight;

        if (scrollHeight > POPUP_INPUT_MAX_HEIGHT) {
            chatInput.style.height = POPUP_INPUT_MAX_HEIGHT + 'px';
            chatInput.style.overflowY = 'auto';
        } else {
            chatInput.style.overflowY = 'hidden';
        }
    }

    chatInput.addEventListener('input', handlePopupInput);

    // Change cursor to default when hovering over scrollbar
    chatInput.addEventListener('mousemove', function (e) {
        // clientWidth excludes scrollbar, offsetWidth includes it
        const isOverScrollbar = e.offsetX > this.clientWidth || e.offsetY > this.clientHeight;
        this.style.cursor = isOverScrollbar ? 'default' : 'text';
    });

    chatInput.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (this.value.trim()) {
                chatForm.requestSubmit();
            }
        }
    });

    // Reset height on submit
    chatForm.addEventListener('submit', () => {
        setTimeout(() => {
            chatInput.style.height = 'auto';
        }, 0);
    });

    // Initially make sure the launcher is visible and popup is hidden
    chatLauncher.style.display = 'flex';
    chatPopup.style.display = 'none';
    chatPopup.style.opacity = '0';
    chatPopup.style.transform = 'scale(0.8)';


    // Voice Input Logic
    const micButton = document.getElementById('mic-button-popup');
    let mediaRecorder;
    let audioChunks = [];

    if (micButton) {
        micButton.addEventListener('click', async (e) => {
            e.preventDefault(); // Prevent form submission if inside form
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

                        // visual feedback
                        const chatInput = document.getElementById('chat-input-popup');
                        const originalPlaceholder = chatInput.placeholder;
                        chatInput.placeholder = "Understanding audio...";
                        chatInput.disabled = true;

                        // Show Spinner
                        micButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
                        micButton.disabled = true;

                        try {
                            // Use X-CSRFToken from meta tag
                            const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';

                            const response = await fetch("/api/transcribe", {
                                method: "POST",
                                headers: {
                                    'X-CSRFToken': csrfToken,
                                    'X-JWE-Token': document.querySelector('meta[name="jwe-token"]')?.getAttribute('content') || ''
                                },
                                body: formData
                            });

                            if (!response.ok) {
                                throw new Error("Transcription failed");
                            }

                            const data = await response.json();
                            if (data.transcript) {
                                chatInput.value += (chatInput.value ? " " : "") + data.transcript;
                                // Auto-submit
                                chatForm.requestSubmit();
                            } else if (data.error) {
                                console.error("Transcription error:", data.error);
                                alert("Transcription failed: " + data.error);
                            }

                        } catch (err) {
                            console.error("Error sending audio:", err);
                            alert("Error sending audio: " + err);
                        } finally {
                            chatInput.disabled = false;
                            chatInput.placeholder = originalPlaceholder;
                            chatInput.focus();

                            // Revert Icon
                            micButton.innerHTML = ''; // Clear icon or text
                            micButton.textContent = "🎙️";
                            micButton.disabled = false;

                            // Stop all tracks to release microphone
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

    // Load Chat History
    async function loadChatHistory() {
        try {
            const response = await fetch(chatConfig.urls.chat, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            if (response.ok) {
                const data = await response.json();
                if (data.history && Array.isArray(data.history)) {
                    // Clear existing history to avoid duplicates if re-initialized (though safeguards exist)
                    chatHistory.innerHTML = '';

                    data.history.forEach(msg => {
                        const messageDiv = document.createElement('div');
                        // Map 'assistant' to 'tutor-message', 'user' to 'user-message'
                        const isUser = msg.role === 'user';
                        const className = isUser ? 'chat-message user-message' : 'chat-message tutor-message';
                        messageDiv.className = className;

                        const prefix = isUser ? '<strong>You:</strong> ' : '<strong>Tutor:</strong> ';

                        if (isUser) {
                            messageDiv.innerHTML = prefix;
                            messageDiv.appendChild(document.createTextNode(msg.content));
                        } else {
                            // Ensure markdownit is available
                            const md = window.markdownit ? window.markdownit({ html: false }) : { render: (t) => t };
                            const rendered = md.render(msg.content || '');
                            const safe = window.DOMPurify
                                ? window.DOMPurify.sanitize(rendered)
                                : rendered;
                            messageDiv.innerHTML = prefix + safe;
                            if (window.renderMath) {
                                window.renderMath(messageDiv);
                            }
                        }
                        chatHistory.appendChild(messageDiv);
                    });
                    chatHistory.scrollTop = chatHistory.scrollHeight;
                }
            }
        } catch (e) {
            console.error("Failed to load chat history", e);
        }
    }

    // Trigger history load
    loadChatHistory();

    // Mark as initialized to prevent duplicate event listeners
    isInitialized = true;
}
