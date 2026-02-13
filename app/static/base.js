const loader = document.getElementById('loader');
const loaderText = document.getElementById('loader-text');
const factText = document.getElementById('fact-text');
const loaderBg = document.getElementById('loader-bg');

/* Uses LEARNING_FACTS from static/facts.js */
const facts = (typeof LEARNING_FACTS !== 'undefined') ? LEARNING_FACTS : [
    "Learning is a journey, not a destination.",
    "Practice makes progress."
];

const icons = ['fa-brain', 'fa-lightbulb', 'fa-book-open', 'fa-atom', 'fa-rocket', 'fa-puzzle-piece', 'fa-layer-group', 'fa-magic'];

function setupFloatingIcons() {
    if (!loaderBg || loaderBg.children.length > 0) return;

    // Create 15 floating icons
    for (let i = 0; i < 15; i++) {
        const icon = document.createElement('i');
        const randomIcon = icons[Math.floor(Math.random() * icons.length)];
        icon.className = `fas ${randomIcon} floating-icon`;

        // Randomize position and animation properties
        icon.style.left = `${Math.random() * 100}%`;
        icon.style.animationDuration = `${10 + Math.random() * 20}s`; // 10-30s
        icon.style.animationDelay = `${Math.random() * 5}s`;
        icon.style.opacity = Math.random() * 0.5 + 0.1; // Varied opacity
        icon.style.fontSize = `${1 + Math.random() * 2}rem`; // Varied size

        loaderBg.appendChild(icon);
    }
}

let hookInterval;
const hooks = ["Analyzing complexity...", "Finding resources...", "Structuring content...", "Almost there..."];

function showLoader(message = "Preparing your experience...") {
    if (loader) {
        setupFloatingIcons();
        if (loaderText) loaderText.textContent = message;

        // Set Random Fact
        if (factText) {
            factText.textContent = facts[Math.floor(Math.random() * facts.length)];
        }

        loader.style.display = 'flex';

        // Cycle hook messages if generic
        if (message === "Preparing your experience...") {
            let i = 0;
            if (hookInterval) clearInterval(hookInterval);
            hookInterval = setInterval(() => {
                if (loaderText) loaderText.textContent = hooks[i % hooks.length];
                i++;
            }, 3000);
        }

        // Set flag for next page
        localStorage.setItem('loader_active', 'true');
    }
}

function hideLoader() {
    if (loader) {
        loader.style.display = 'none';
        if (hookInterval) clearInterval(hookInterval);
    }
}

// Expose loader functions globally for use by other scripts
window.showLoader = showLoader;
window.hideLoader = hideLoader;

// Fix for bfcache (back/forward cache)
window.addEventListener('pageshow', (event) => {
    if (event.persisted || (window.performance && window.performance.navigation.type === 2)) {
        hideLoader();
    }
});

// Check for transition on load
document.addEventListener('DOMContentLoaded', () => {
    if (localStorage.getItem('loader_active') === 'true') {
        localStorage.removeItem('loader_active');

        // Show "Ready!" state manually before hiding
        if (loader && loaderText) {
            setupFloatingIcons();
            loader.style.display = 'flex';
            loaderText.textContent = "Ready!";

            // Hide fact for success state
            const factBox = document.getElementById('loader-fact');
            if (factBox) factBox.style.display = 'none';

            // Replace spinner with checkmark
            const spinner = loader.querySelector('.spinner');
            if (spinner) {
                spinner.style.display = 'none';

                const check = document.createElement('i');
                check.className = 'fas fa-check-circle';
                check.style.fontSize = '4rem';
                check.style.color = '#4ade80';
                check.style.marginBottom = '20px';
                check.style.animation = 'scaleIn 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275)';

                // Insert checkmark where spinner was
                spinner.parentNode.insertBefore(check, spinner);

                // Keep "Done" visible for 800ms
                setTimeout(() => {
                    loader.style.opacity = '0';
                    loader.style.transition = 'opacity 0.5s ease';
                    setTimeout(() => {
                        loader.style.display = 'none';
                        loader.style.opacity = '1'; // Reset for next time
                        check.remove(); // Cleanup
                        spinner.style.display = 'block'; // Restore spinner
                        if (factBox) factBox.style.display = ''; // Restore fact box
                    }, 500);
                }, 800);
            } else {
                hideLoader();
            }
        }
    } else {
        // Normal load (hide just in case)
        hideLoader(); // CSS hides it by default but good to be sure
    }

    // Theme logic...
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'light') {
        body.classList.remove('dark-mode');
    } else {
        body.classList.add('dark-mode');
    }
});

const themeSwitcher = document.getElementById('theme-switcher');
const body = document.body;

if (themeSwitcher) {
    themeSwitcher.addEventListener('click', () => {
        body.classList.toggle('dark-mode');
        localStorage.setItem('theme', body.classList.contains('dark-mode') ? 'dark' : 'light');
    });
}

// Apply the saved theme on page load
document.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'light') {
        body.classList.remove('dark-mode');
    } else {
        body.classList.add('dark-mode');
    }
});

// ===== Feedback Modal =====
const feedbackBtn = document.getElementById('feedback-btn');
const feedbackModal = document.getElementById('feedback-modal');
const feedbackClose = document.getElementById('feedback-close');
const feedbackCancel = document.getElementById('feedback-cancel');
const feedbackForm = document.getElementById('feedback-form');
const feedbackMessage = document.getElementById('feedback-message');
const starRating = document.getElementById('star-rating');
const feedbackRatingInput = document.getElementById('feedback-rating');

// Open modal
if (feedbackBtn && feedbackModal) {
    feedbackBtn.addEventListener('click', () => {
        feedbackModal.classList.add('active');
    });
}

// Close modal
function closeFeedbackModal() {
    if (feedbackModal) {
        feedbackModal.classList.remove('active');
        // Reset form
        if (feedbackForm) feedbackForm.reset();
        if (feedbackMessage) {
            feedbackMessage.className = 'feedback-message';
            feedbackMessage.textContent = '';
        }
        // Reset stars
        if (starRating) {
            starRating.querySelectorAll('.star').forEach(s => s.classList.remove('selected', 'hovered'));
        }
        if (feedbackRatingInput) feedbackRatingInput.value = '0';
    }
}

if (feedbackClose) feedbackClose.addEventListener('click', closeFeedbackModal);
if (feedbackCancel) feedbackCancel.addEventListener('click', closeFeedbackModal);

// Close on backdrop click
if (feedbackModal) {
    feedbackModal.addEventListener('click', (e) => {
        if (e.target === feedbackModal) closeFeedbackModal();
    });
}

// Star rating interaction
if (starRating) {
    const stars = starRating.querySelectorAll('.star');

    stars.forEach(star => {
        star.addEventListener('mouseenter', () => {
            const val = parseInt(star.dataset.value);
            stars.forEach(s => {
                s.classList.toggle('hovered', parseInt(s.dataset.value) <= val);
            });
        });

        star.addEventListener('mouseleave', () => {
            stars.forEach(s => s.classList.remove('hovered'));
        });

        star.addEventListener('click', () => {
            const val = parseInt(star.dataset.value);
            feedbackRatingInput.value = val;
            stars.forEach(s => {
                s.classList.toggle('selected', parseInt(s.dataset.value) <= val);
            });
        });
    });
}

// Form submission
if (feedbackForm) {
    feedbackForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const feedbackType = document.getElementById('feedback-type').value;
        const rating = parseInt(feedbackRatingInput.value) || 0;
        const comment = document.getElementById('feedback-comment').value;

        if (!feedbackType) {
            feedbackMessage.textContent = 'Please select a feedback type.';
            feedbackMessage.className = 'feedback-message error';
            return;
        }

        try {
            const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;
            const jweToken = document.querySelector('meta[name="jwe-token"]')?.content;
            const response = await fetch('/api/feedback', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken || '',
                    'X-JWE-Token': jweToken || ''
                },
                body: JSON.stringify({
                    feedback_type: feedbackType,
                    rating: rating,
                    comment: comment
                })
            });

            const data = await response.json();

            if (response.ok) {
                feedbackMessage.textContent = 'Thank you for your feedback! 🎉';
                feedbackMessage.className = 'feedback-message success';
                setTimeout(closeFeedbackModal, 2000);
            } else {
                feedbackMessage.textContent = data.error || 'Failed to submit feedback.';
                feedbackMessage.className = 'feedback-message error';
            }
        } catch (err) {
            feedbackMessage.textContent = 'Network error. Please try again.';
            feedbackMessage.className = 'feedback-message error';
        }
    });
}

// ===== Input Validation (Length & Value) =====
function setupInputValidation() {
    // Select inputs with validation constraints
    const inputs = document.querySelectorAll('input[maxlength], textarea[maxlength], input[min], input[max]');

    const validateInput = (input) => {
        // Generate valid ID for error message
        const inputId = input.id || input.name || Math.random().toString(36).substr(2, 9);
        const errorId = `error-${inputId}`;
        let errorMsg = document.getElementById(errorId);

        let message = null;

        // 1. Length Check
        if (input.hasAttribute('maxlength')) {
            const maxLength = parseInt(input.getAttribute('maxlength'));
            if (input.value.length >= maxLength) {
                message = `Maximum length of ${maxLength} characters reached.`;
            }
        }

        // 2. Value Check (for numbers)
        // Only check if no length error yet, and value is present
        if (!message && input.type === 'number' && input.value !== '') {
            const val = parseFloat(input.value);

            if (input.hasAttribute('min')) {
                const minVal = parseFloat(input.getAttribute('min'));
                if (val < minVal) {
                    message = `Value must be at least ${minVal}.`;
                }
            }

            if (!message && input.hasAttribute('max')) {
                const maxVal = parseFloat(input.getAttribute('max'));
                if (val > maxVal) {
                    message = `Value must be at most ${maxVal}.`;
                }
            }
        }

        // Display or remove error
        if (message) {
            if (!errorMsg) {
                errorMsg = document.createElement('div');
                errorMsg.id = errorId;
                errorMsg.className = 'input-limit-error';
                input.insertAdjacentElement('afterend', errorMsg);
            }
            errorMsg.textContent = message;

            // Apply invalid state
            input.classList.add('input-invalid');
            input.setAttribute('aria-invalid', 'true');
            input.setAttribute('aria-describedby', errorId);
        } else {
            if (errorMsg) {
                errorMsg.remove();
            }
            // Remove invalid state
            input.classList.remove('input-invalid');
            input.removeAttribute('aria-invalid');
            input.removeAttribute('aria-describedby');
        }
    };

    inputs.forEach(input => {
        // Check initial state
        validateInput(input);

        // Listen for updates
        input.addEventListener('input', function () {
            validateInput(this);
        });
    });
}

document.addEventListener('DOMContentLoaded', setupInputValidation);
