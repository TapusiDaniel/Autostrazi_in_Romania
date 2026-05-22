// Dark mode toggle with localStorage persistence
(function() {
    const mapBackgroundSelectors = [
        '.folium-map',
        '.leaflet-container',
        '.leaflet-map-pane',
        '.leaflet-tile-pane',
        '.leaflet-tile-container'
    ];
    const layerCache = {};

    function isDarkMode() {
        return document.documentElement.getAttribute('data-theme') === 'dark';
    }

    function applyDarkMapBackground() {
        document.querySelectorAll(mapBackgroundSelectors.join(', ')).forEach(function(el) {
            el.style.background = '#1a1a1a';
            el.style.backgroundColor = '#1a1a1a';
        });
    }

    function revertDarkMapBackground() {
        document.querySelectorAll(mapBackgroundSelectors.join(', ')).forEach(function(el) {
            el.style.background = '';
            el.style.backgroundColor = '';
        });
    }

    function getLeafletMap() {
        const mapContainer = document.querySelector('.leaflet-container');
        if (!mapContainer) return null;
        const mapKey = Object.keys(window).find(
            k => window[k] && window[k]._container === mapContainer
        );
        return mapKey ? window[mapKey] : null;
    }

    function collectLayersByClass(layer, className, matches) {
        if (!layer) return;
        if (
            layer.options &&
            layer.options.className &&
            layer.options.className.indexOf(className) !== -1 &&
            layer.setStyle
        ) {
            matches.push(layer);
        }

        if (!layer.eachLayer) return;
        layer.eachLayer(function(child) {
            collectLayersByClass(child, className, matches);
        });
    }

    function setLeafletLayerStyle(className, style) {
        let matches = layerCache[className];
        if (!matches) {
            const mapInstance = getLeafletMap();
            matches = [];
            if (mapInstance) {
                collectLayersByClass(mapInstance, className, matches);
            }
            layerCache[className] = matches;
        }
        matches.forEach(function(layer) {
            layer.setStyle(style);
        });
    }

    function applyDarkModeToSVG() {
        setLeafletLayerStyle('romania-outline', {
            fillColor: '#1a1a1a',
            color: '#333333',
            fillOpacity: 1,
            opacity: 1
        });
        setLeafletLayerStyle('city-boundary', {
            fillColor: '#2a2a2a',
            color: '#666666',
            fillOpacity: 1,
            opacity: 1
        });
        setLeafletLayerStyle('city-dot', {
            fillColor: '#444444',
            color: '#888888',
            fillOpacity: 1,
            opacity: 1
        });

        const selectors = [
            '.romania-outline',
            '.city-boundary',
            '.city-dot',
            '.leaflet-circle-marker-pane path'
        ];

        document.querySelectorAll(selectors.join(', ')).forEach(function(el) {
            const isRomania = el.classList.contains('romania-outline');
            const isCity = el.classList.contains('city-boundary');
            const isDot = el.classList.contains('city-dot') || el.closest('.leaflet-circle-marker-pane');

            if (isRomania) {
                el.style.fill = '#1a1a1a';
                el.style.stroke = '#333333';
            } else if (isCity) {
                el.style.fill = '#2a2a2a';
                el.style.stroke = '#666666';
            } else if (isDot) {
                el.style.fill = '#444444';
                el.style.stroke = '#888888';
            }
        });
    }

    function revertDarkModeFromSVG() {
        setLeafletLayerStyle('romania-outline', {
            fillColor: 'white',
            color: 'gray',
            fillOpacity: 1,
            opacity: 1
        });
        setLeafletLayerStyle('city-boundary', {
            fillColor: '#E0E0E0',
            color: '#4A4A4A',
            fillOpacity: 1,
            opacity: 1
        });
        setLeafletLayerStyle('city-dot', {
            fillColor: '#E0E0E0',
            color: '#4A4A4A',
            fillOpacity: 1,
            opacity: 1
        });

        const selectors = [
            '.romania-outline',
            '.city-boundary',
            '.city-dot',
            '.leaflet-circle-marker-pane path'
        ];

        document.querySelectorAll(selectors.join(', ')).forEach(function(el) {
            const isRomania = el.classList.contains('romania-outline');
            const isCity = el.classList.contains('city-boundary');
            const isDot = el.classList.contains('city-dot') || el.closest('.leaflet-circle-marker-pane');

            if (isRomania) {
                el.style.fill = 'white';
                el.style.stroke = 'gray';
            } else if (isCity) {
                el.style.fill = '#E0E0E0';
                el.style.stroke = '#4A4A4A';
            } else if (isDot) {
                el.style.fill = '#E0E0E0';
                el.style.stroke = '#4A4A4A';
            }
        });
    }

    function applyDarkMode() {
        document.documentElement.setAttribute('data-theme', 'dark');
        applyDarkMapBackground();
        applyDarkModeToSVG();
        setTimeout(function() {
            applyDarkMapBackground();
            applyDarkModeToSVG();
        }, 100);
    }

    function applyLightMode() {
        document.documentElement.removeAttribute('data-theme');
        revertDarkMapBackground();
        revertDarkModeFromSVG();
    }

    function watchMapChanges() {
        const mapContainer = document.querySelector('.leaflet-container');
        if (!mapContainer || mapContainer._darkModeObserver) return;

        const observer = new MutationObserver(function() {
            if (isDarkMode()) {
                applyDarkMapBackground();
                applyDarkModeToSVG();
            }
        });
        observer.observe(mapContainer, {childList: true, subtree: true});
        mapContainer._darkModeObserver = observer;
    }

    function initDarkMode() {
        const toggle = document.getElementById('dark-mode-toggle');
        if (!toggle) return;

        const savedTheme = localStorage.getItem('theme');
        const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

        if (savedTheme === 'dark' || (!savedTheme && systemPrefersDark)) {
            applyDarkMode();
            setTimeout(applyDarkMode, 1000);
        }
        setTimeout(watchMapChanges, 1000);

        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', event => {
            if (!localStorage.getItem('theme')) {
                if (event.matches) {
                    applyDarkMode();
                } else {
                    applyLightMode();
                }
            }
        });

        toggle.addEventListener('click', function() {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

            if (newTheme === 'dark') {
                applyDarkMode();
            } else {
                applyLightMode();
            }

            localStorage.setItem('theme', newTheme);
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initDarkMode);
    } else {
        initDarkMode();
    }
})();
