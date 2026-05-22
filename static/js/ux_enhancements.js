// UX enhancements: highlight, fullscreen, share, toast
(function() {
    window.activeHighway = null;
    window.activeHighwayLayers = [];
    window.activeHighwayBlinkTimer = null;
    window.activeHighwayBlinkOn = true;
    let highwayLayerIndex = null;
    let delimiterLayers = null;

    function loadLayerData() {
        const el = document.getElementById('highway-layer-data');
        if (!el) return null;
        try {
            return JSON.parse(el.textContent);
        } catch (e) {
            return null;
        }
    }

    function getLeafletMap() {
        const mapContainer = document.querySelector('.leaflet-container');
        if (!mapContainer) return null;
        const mapKey = Object.keys(window).find(
            k => window[k] && window[k]._container === mapContainer
        );
        return mapKey ? window[mapKey] : null;
    }

    function resetLayerHighlights() {
        if (window.activeHighwayBlinkTimer) {
            clearInterval(window.activeHighwayBlinkTimer);
            window.activeHighwayBlinkTimer = null;
        }
        window.activeHighwayBlinkOn = true;

        if (!window.activeHighwayLayers) return;
        window.activeHighwayLayers.forEach(layer => {
            if (layer && layer.setStyle) {
                layer.setStyle({weight: 4, opacity: getResetOpacity(layer)});
            }
        });
        window.activeHighwayLayers = [];
        bringDelimitersToFront();
    }

    function getResetOpacity(layer) {
        const className = layer && layer.options && layer.options.className;
        if (
            className &&
            document.body.classList.contains('high-detail-mode') &&
            className.split(/\s+/).includes('low-detail')
        ) {
            return 0;
        }
        return 1;
    }

    function collectMatchingLayers(layer, targetClass, matches) {
        if (!layer) return;
        if (
            layer.options &&
            layer.options.className &&
            layer.options.className.split(/\s+/).includes(targetClass) &&
            layer.setStyle
        ) {
            matches.push(layer);
        }

        if (!layer.eachLayer) return;
        layer.eachLayer(function(child) {
            collectMatchingLayers(child, targetClass, matches);
        });
    }

    function collectDelimiterLayers(layer, matches) {
        if (!layer) return;
        if (
            layer.options &&
            layer.options.className === 'highway-delimiter' &&
            layer.bringToFront
        ) {
            matches.push(layer);
        }

        if (!layer.eachLayer) return;
        layer.eachLayer(function(child) {
            collectDelimiterLayers(child, matches);
        });
    }

    function bringDelimitersToFront() {
        if (!delimiterLayers) {
            delimiterLayers = [];
            const mapInstance = getLeafletMap();
            if (mapInstance) {
                collectDelimiterLayers(mapInstance, delimiterLayers);
            }
        }

        delimiterLayers.forEach(function(layer) {
            layer.bringToFront();
        });
    }

    function indexHighwayLayers(layer, index) {
        if (!layer) return;
        if (
            layer.options &&
            layer.options.className &&
            layer.options.className.indexOf('highway-section-') !== -1 &&
            layer.setStyle
        ) {
            const layerId = layer._leaflet_id;
            layer.options.className.split(/\s+/).forEach(function(className) {
                if (className.indexOf('highway-section-') === 0) {
                    if (!index[className]) index[className] = [];
                    if (!index[className].some(function(item) { return item._leaflet_id === layerId; })) {
                        index[className].push(layer);
                    }
                }
            });
        }

        if (!layer.eachLayer) return;
        layer.eachLayer(function(child) {
            indexHighwayLayers(child, index);
        });
    }

    function getHighwayLayerIndex() {
        if (highwayLayerIndex) return highwayLayerIndex;

        highwayLayerIndex = {};
        const mapInstance = getLeafletMap();
        if (mapInstance) {
            indexHighwayLayers(mapInstance, highwayLayerIndex);
        }
        const layerData = loadLayerData();
        if (layerData && layerData.statusLayers) {
            Object.values(layerData.statusLayers).forEach(function(pair) {
                ['low', 'high'].forEach(function(key) {
                    if (pair[key] && window[pair[key]]) {
                        indexHighwayLayers(window[pair[key]], highwayLayerIndex);
                    }
                });
            });
        }
        return highwayLayerIndex;
    }

    window.invalidateHighwayLayerIndex = function() {
        highwayLayerIndex = null;
    };

    function addHighlightClass(layer) {
        if (!layer) return;

        const element = layer.getElement ? layer.getElement() : layer._path;
        if (element && element.classList) {
            element.classList.add('highlighted-path');
        }

        if (!layer.eachLayer) return;
        layer.eachLayer(function(child) {
            addHighlightClass(child);
        });
    }

    function startLayerBlink(layers) {
        if (!layers.length) return;

        window.activeHighwayBlinkTimer = setInterval(function() {
            window.activeHighwayBlinkOn = !window.activeHighwayBlinkOn;
            const opacity = window.activeHighwayBlinkOn ? 1 : 0.8;

            layers.forEach(function(layer) {
                if (layer && layer.setStyle) {
                    layer.setStyle({weight: 6, opacity: opacity});
                }
            });
        }, 1400);
    }

    window.resetHighwayHighlight = function() {
        document.querySelectorAll('.highlighted-path').forEach(path => {
            path.classList.remove('highlighted-path');
        });
        resetLayerHighlights();
        window.activeHighway = null;
    };

    window.refreshHighwayHighlight = function() {
        const code = window.activeHighway;
        if (!code) return;
        window.activeHighway = null;
        window.highlightHighway(code);
    };

    window.highlightHighway = function(code) {
        document.querySelectorAll('.highlighted-path').forEach(path => {
            path.classList.remove('highlighted-path');
        });
        resetLayerHighlights();

        if (window.activeHighway === code) {
            window.activeHighway = null;
            return;
        }
        window.activeHighway = code;

        const mapInstance = getLeafletMap();
        const targetClass = 'highway-section-' + code.toLowerCase().replace(/ /g, '-');

        const indexedLayers = getHighwayLayerIndex()[targetClass] || [];
        let matchingLayers = indexedLayers.slice();
        const detailClass = document.body.classList.contains('high-detail-mode') ? 'high-detail' : 'low-detail';
        const detailLayers = matchingLayers.filter(function(layer) {
            return layer.options.className.split(/\s+/).includes(detailClass);
        });
        if (detailLayers.length > 0) {
            matchingLayers = detailLayers;
        }
        if (matchingLayers.length === 0 && mapInstance) {
            collectMatchingLayers(mapInstance, targetClass, matchingLayers);
        }

        if (matchingLayers.length > 0) {
            matchingLayers.forEach(function(layer) {
                layer.setStyle({weight: 6, opacity: 1});
                addHighlightClass(layer);
                if (layer.bringToFront) layer.bringToFront();
            });
            window.activeHighwayLayers = matchingLayers;
            startLayerBlink(matchingLayers);
        } else {
            document.querySelectorAll('path.' + targetClass).forEach(function(el) {
                el.classList.add('highlighted-path');
            });
        }
    };

    window.zoomToHighwayCenter = function(code) {
        const centers = {
            'A0': {lat: 44.45, lng: 26.1, zoom: 10},
            'A1': {lat: 45.8, lng: 23.5, zoom: 7},
            'A2': {lat: 44.3, lng: 27.5, zoom: 8},
            'A3': {lat: 46.5, lng: 24.0, zoom: 7},
            'A4': {lat: 44.17, lng: 28.55, zoom: 11},
            'A6': {lat: 45.85, lng: 21.8, zoom: 10},
            'A7': {lat: 46.5, lng: 27.0, zoom: 7},
            'A8': {lat: 47.1, lng: 26.0, zoom: 7},
            'A10': {lat: 46.2, lng: 23.8, zoom: 9},
            'A11': {lat: 46.16, lng: 21.3, zoom: 11},
            'DEx12': {lat: 44.4, lng: 24.0, zoom: 8},
            'DEx4': {lat: 46.6, lng: 23.5, zoom: 10},
            'DEx6': {lat: 45.4, lng: 27.9, zoom: 9},
            'DEx16': {lat: 47.0, lng: 21.9, zoom: 11}
        };

        if (centers[code]) {
            const mapContainer = document.querySelector('.leaflet-container');
            if (mapContainer) {
                const mapKey = Object.keys(window).find(k => window[k] && window[k]._container === mapContainer);
                if (mapKey && window[mapKey]) {
                    window[mapKey].setView([centers[code].lat, centers[code].lng], centers[code].zoom);
                }
            }
        }
    };

    function initUX() {
        const fullscreenBtn = document.getElementById('fullscreen-btn');

        if (fullscreenBtn) {
            const newFullscreenBtn = fullscreenBtn.cloneNode(true);
            fullscreenBtn.parentNode.replaceChild(newFullscreenBtn, fullscreenBtn);

            newFullscreenBtn.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                if (!document.fullscreenElement) {
                    document.documentElement.requestFullscreen().catch(err => console.log(err));
                } else if (document.exitFullscreen) {
                    document.exitFullscreen().catch(err => console.log(err));
                }
            });

            document.addEventListener('fullscreenchange', function() {
                if (document.fullscreenElement) {
                    newFullscreenBtn.textContent = '✕';
                    newFullscreenBtn.title = 'Ieșire ecran complet';
                    document.body.classList.add('fullscreen-mode');
                } else {
                    newFullscreenBtn.textContent = '⛶';
                    newFullscreenBtn.title = 'Ecran complet';
                    document.body.classList.remove('fullscreen-mode');
                }
            });
        }

        const shareBtn = document.getElementById('share-btn');
        const modalOverlay = document.getElementById('share-modal-overlay');
        const closeBtn = document.getElementById('share-close');
        const fbBtn = document.getElementById('share-facebook');
        const twBtn = document.getElementById('share-twitter');
        const waBtn = document.getElementById('share-whatsapp');
        const copyBtn = document.getElementById('share-copy');

        function openModal() {
            if (modalOverlay) {
                modalOverlay.style.display = 'flex';
                modalOverlay.offsetHeight;
                modalOverlay.classList.add('show');

                const url = encodeURIComponent("https://tapusidaniel.github.io/Autostrazi_in_Romania/");
                const title = encodeURIComponent("Autostrăzi în România - Hartă Interactivă");

                if (fbBtn) fbBtn.href = "https://www.facebook.com/sharer/sharer.php?u=" + url;
                if (twBtn) twBtn.href = "https://twitter.com/intent/tweet?text=" + title + "&url=" + url;
                if (waBtn) waBtn.href = "https://api.whatsapp.com/send?text=" + title + " " + url;
            }
        }

        function closeModal() {
            if (modalOverlay) {
                modalOverlay.classList.remove('show');
                setTimeout(function() {
                    modalOverlay.style.display = 'none';
                }, 300);
            }
        }

        if (shareBtn) {
            const newShareBtn = shareBtn.cloneNode(true);
            shareBtn.parentNode.replaceChild(newShareBtn, shareBtn);
            newShareBtn.addEventListener('click', function(e) {
                e.preventDefault();
                openModal();
            });
        }

        if (closeBtn) closeBtn.addEventListener('click', closeModal);
        if (modalOverlay) {
            modalOverlay.addEventListener('click', function(e) {
                if (e.target === modalOverlay) closeModal();
            });
        }

        if (copyBtn) {
            copyBtn.addEventListener('click', function() {
                const url = window.location.href.split('?')[0];
                navigator.clipboard.writeText(url).then(function() {
                    window.showToast('Link copiat!');
                    closeModal();
                }).catch(function() {
                    window.showToast('Nu s-a putut copia');
                });
            });
        }
    }

    window.showToast = function(msg) {
        const t = document.getElementById('toast');
        if (t) {
            t.textContent = msg;
            t.classList.add('show');
            setTimeout(function() { t.classList.remove('show'); }, 2000);
        }
    };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initUX);
    } else {
        initUX();
    }
})();
