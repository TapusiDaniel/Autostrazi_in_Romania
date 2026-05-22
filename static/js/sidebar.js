// Sidebar toggle logic
(function() {
    function initSidebar() {
        const sidebar = document.getElementById("highway-sidebar");
        const toggle = document.getElementById("sidebar-toggle");
        const close = document.getElementById("sidebar-close");

        if (!sidebar || !toggle) return;

        function setOpen(open) {
            sidebar.classList.toggle("open", open);
        }

        toggle.addEventListener("click", function() {
            setOpen(!sidebar.classList.contains("open"));
        });

        if (close) {
            close.addEventListener("click", function() {
                setOpen(false);
            });
        }
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initSidebar);
    } else {
        initSidebar();
    }
})();
