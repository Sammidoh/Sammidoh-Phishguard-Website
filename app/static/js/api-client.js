// ============================================
// PhishGuard API Client
// Handles all AJAX requests to backend
// ============================================

const API_BASE = '/api/v1';

/**
 * Generic fetch wrapper with error handling
 * @param {string} endpoint - API endpoint (starts with / or relative)
 * @param {object} options - Fetch options (method, body, headers)
 * @returns {Promise<any>} - Parsed JSON response
 */
async function apiFetch(endpoint, options = {}) {
    // Normalize endpoint
    let url = endpoint;
    if (!endpoint.startsWith('http')) {
        url = endpoint.startsWith('/') ? endpoint : `${API_BASE}/${endpoint}`;
    }
    
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        }
    };
    
    const finalOptions = { ...defaultOptions, ...options };
    
    // Don't set Content-Type for FormData
    if (finalOptions.body && finalOptions.body instanceof FormData) {
        delete finalOptions.headers['Content-Type'];
    }
    
    try {
        const response = await fetch(url, finalOptions);
        
        // Handle non-JSON responses (e.g., redirects)
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.error || data.message || `HTTP ${response.status}`);
            }
            return data;
        }
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        return response;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

/**
 * Helper for GET requests
 */
async function apiGet(endpoint) {
    return apiFetch(endpoint, { method: 'GET' });
}

/**
 * Helper for POST requests (JSON)
 */
async function apiPost(endpoint, data) {
    return apiFetch(endpoint, {
        method: 'POST',
        body: JSON.stringify(data)
    });
}

/**
 * Helper for PUT requests
 */
async function apiPut(endpoint, data) {
    return apiFetch(endpoint, {
        method: 'PUT',
        body: JSON.stringify(data)
    });
}

/**
 * Helper for DELETE requests
 */
async function apiDelete(endpoint) {
    return apiFetch(endpoint, { method: 'DELETE' });
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(str) {
    if (!str) return '';
    return str
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

/**
 * Show toast notification (requires Bootstrap Toasts or simple alert fallback)
 */
function showToast(message, type = 'danger') {
    // Simple alert fallback – you can replace with Bootstrap toast
    const toastContainer = document.getElementById('toast-container');
    if (toastContainer) {
        const toastHtml = `
            <div class="toast align-items-center text-white bg-${type} border-0" role="alert">
                <div class="d-flex">
                    <div class="toast-body">${escapeHtml(message)}</div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        `;
        toastContainer.insertAdjacentHTML('beforeend', toastHtml);
        const toastEl = toastContainer.lastElementChild;
        const toast = new bootstrap.Toast(toastEl, { autohide: true, delay: 3000 });
        toast.show();
        toastEl.addEventListener('hidden.bs.toast', () => toastEl.remove());
    } else {
        alert(message);
    }
}

// Export for global use
window.apiFetch = apiFetch;
window.apiGet = apiGet;
window.apiPost = apiPost;
window.apiPut = apiPut;
window.apiDelete = apiDelete;
window.escapeHtml = escapeHtml;
window.showToast = showToast;