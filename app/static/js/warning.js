// ============================================
// PhishGuard Warning Page Scripts
// Countdown timer, proceed confirmation, analytics ping
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    // Countdown timer (optional, for stricter safety)
    const proceedBtn = document.getElementById('proceedBtn');
    const countdownSpan = document.getElementById('countdown');
    let secondsLeft = 5;  // 5-second delay before "Proceed" becomes active
    
    if (proceedBtn && countdownSpan) {
        proceedBtn.disabled = true;
        const timer = setInterval(() => {
            secondsLeft--;
            countdownSpan.textContent = secondsLeft;
            if (secondsLeft <= 0) {
                clearInterval(timer);
                proceedBtn.disabled = false;
                countdownSpan.textContent = '0';
            }
        }, 1000);
    }
    
    // Log warning view to backend (optional analytics)
    logWarningView();
    
    // "Proceed Anyway" double confirmation
    if (proceedBtn) {
        proceedBtn.addEventListener('click', (e) => {
            if (!confirm('⚠️ This site is reported as malicious. Proceeding may compromise your security. Are you absolutely sure?')) {
                e.preventDefault();
                return false;
            }
            // Additional client-side bypass flag (optional)
            document.cookie = 'bypass_intent=true; path=/; max-age=300';
        });
    }
    
    // Go back button – ensure user goes to previous page
    const backBtn = document.getElementById('backBtn');
    if (backBtn) {
        backBtn.addEventListener('click', () => {
            if (document.referrer) {
                window.location.href = document.referrer;
            } else {
                window.history.back();
            }
        });
    }
});

/**
 * Send an asynchronous request to log that warning page was shown
 * (helps track how many users see warnings vs bypass)
 */
async function logWarningView() {
    const urlParams = new URLSearchParams(window.location.search);
    const targetUrl = urlParams.get('url') || 'unknown';
    const category = urlParams.get('category') || 'unknown';
    try {
        // Use a beacon or fetch to log warning view
        navigator.sendBeacon('/api/v1/log_warning_view', JSON.stringify({
            url: targetUrl,
            category: category
        }));
    } catch (e) {
        // Fallback – do nothing
    }
}

/**
 * Simple bypass token setter (if not already set by backend)
 * This ensures the user can proceed without being re-blocked immediately
 */
function setBypassToken(url, durationSeconds = 300) {
    const token = btoa(JSON.stringify({ url: url, exp: Date.now() + durationSeconds * 1000 }));
    document.cookie = `bypass_token=${token}; path=/; max-age=${durationSeconds}`;
}

// If the user proceeds via form, the backend already sets the cookie.
// But we also expose a helper for client-side logic.
window.setBypassToken = setBypassToken;