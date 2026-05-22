// Hide loading overlay when map is ready
(function() {
    function hideOverlay() {
        const overlay = document.getElementById('loading-overlay');
        if (!overlay) return;

        overlay.classList.add('hidden');
        setTimeout(function() {
            overlay.remove();
        }, 500);
    }

    function init() {
        setTimeout(hideOverlay, 1500);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
