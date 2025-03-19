// Deferred resource loading
function loadDeferred() {
    const resources = {
        css: [
            'assets/vendors/leaflet.awesome-markers.css',
            'assets/vendors/bootstrap-glyphicons.css',
            'assets/vendors/fontawesome-all.min.css',
            'assets/vendors/bootstrap.min.css',
            'assets/vendors/leaflet.css',
            'assets/vendors/leaflet.awesome.rotate.min.css'
        ],
        js: [
            'assets/vendors/leaflet.awesome-markers.js',
            'assets/vendors/jquery.min.js',
            'assets/vendors/bootstrap.bundle.min.js',
            'assets/vendors/leaflet.js'
        ]
    };

    // Load CSS files
    resources.css.forEach(file => {
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = file;
        document.head.appendChild(link);
    });

    // Load JS files
    let loadedScripts = 0;
    resources.js.forEach(file => {
        const script = document.createElement('script');
        script.src = file;
        script.async = true;
        script.onload = () => {
            loadedScripts++;
            if (loadedScripts === resources.js.length) {
                // Initialize deferred functionality
                if (window.initMap) window.initMap();
            }
        };
        document.body.appendChild(script);
    });
}

// Load deferred resources after initial render
if (document.readyState === 'complete') {
    loadDeferred();
} else {
    window.addEventListener('load', loadDeferred);
}