// ============================================
// PhishGuard URL Manager (AJAX)
// Add/Edit/Delete blacklist and whitelist entries without page reload
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    // Blacklist AJAX support
    const blacklistAddForm = document.getElementById('blacklist-add-form');
    if (blacklistAddForm) {
        blacklistAddForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(blacklistAddForm);
            const data = Object.fromEntries(formData.entries());
            try {
                await apiPost('/blacklist/add', data);
                showToast('URL added to blacklist', 'success');
                blacklistAddForm.reset();
                location.reload(); // or reload table via AJAX
            } catch (err) {
                showToast(err.message, 'danger');
            }
        });
    }
    
    // Blacklist delete buttons (dynamic)
    document.querySelectorAll('.delete-blacklist-btn').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            const id = btn.dataset.id;
            if (confirm('Are you sure you want to delete this URL from blacklist?')) {
                try {
                    await apiGet(`/blacklist/delete/${id}`);
                    showToast('Deleted', 'success');
                    btn.closest('tr').remove();
                } catch (err) {
                    showToast(err.message, 'danger');
                }
            }
        });
    });
    
    // Whitelist AJAX
    const whitelistAddForm = document.getElementById('whitelist-add-form');
    if (whitelistAddForm) {
        whitelistAddForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(whitelistAddForm);
            const data = Object.fromEntries(formData.entries());
            try {
                await apiPost('/whitelist/add', data);
                showToast('URL added to whitelist', 'success');
                whitelistAddForm.reset();
                location.reload();
            } catch (err) {
                showToast(err.message, 'danger');
            }
        });
    }
    
    // Whitelist delete buttons
    document.querySelectorAll('.delete-whitelist-btn').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            const id = btn.dataset.id;
            if (confirm('Remove from whitelist?')) {
                try {
                    await apiGet(`/whitelist/delete/${id}`);
                    showToast('Removed', 'success');
                    btn.closest('tr').remove();
                } catch (err) {
                    showToast(err.message, 'danger');
                }
            }
        });
    });
});