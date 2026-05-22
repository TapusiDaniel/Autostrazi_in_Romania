// Manage delimiter visibility and high-detail layer toggling
(function() {
    function loadLayerData() {
        const el = document.getElementById('highway-layer-data');
        if (!el) return null;
        try {
            return JSON.parse(el.textContent);
        } catch (e) {
            return null;
        }
    }

    const data = loadLayerData();
    if (!data || !data.statusLayers) return;

    function getLeafletMap() {
        const mapContainer = document.querySelector('.leaflet-container');
        if (!mapContainer) return null;
        const mapKey = Object.keys(window).find(
            k => window[k] && window[k]._container === mapContainer
        );
        return mapKey ? window[mapKey] : null;
    }

    function waitForMap(retries) {
        const mapInstance = getLeafletMap();
        if (mapInstance) {
            init(mapInstance);
            return;
        }
        if (retries <= 0) return;
        setTimeout(() => waitForMap(retries - 1), 250);
    }

    // Build { highwayCode: { status: true } } from the section layers, whose
    // classNames carry both the highway code and status. Used to decide which
    // highway logos to show: a logo appears only if its highway has at least
    // one section of a currently-selected status.
    let highwayStatusesCache = null;
    function collectHighwayStatusCodes(layer, statusKey, result) {
        if (layer && layer.options && layer.options.className) {
            const m = layer.options.className.match(/highway-section-([a-z0-9-]+)/);
            if (m) {
                (result[m[1]] = result[m[1]] || {})[statusKey] = true;
            }
        }
        if (layer && layer.eachLayer) {
            layer.eachLayer(function(child) {
                collectHighwayStatusCodes(child, statusKey, result);
            });
        }
    }
    function getHighwayStatuses() {
        if (highwayStatusesCache) return highwayStatusesCache;
        const result = {};
        if (data && data.statusLayers) {
            Object.keys(data.statusLayers).forEach(function(statusKey) {
                const grp = window[data.statusLayers[statusKey].low];
                if (grp && grp.eachLayer) {
                    grp.eachLayer(function(child) {
                        collectHighwayStatusCodes(child, statusKey, result);
                    });
                }
            });
        }
        if (Object.keys(result).length) highwayStatusesCache = result;
        return result;
    }
    function logoHighwayCode(logoEl) {
        const d = logoEl.querySelector('[data-highway]');
        const h = d ? d.getAttribute('data-highway') : '';
        return h.toLowerCase().replace(/ /g, '-');
    }
    function logoStatusKey(logoEl) {
        const d = logoEl.querySelector('[data-status]');
        return d ? d.getAttribute('data-status') : '';
    }

    function syncDelimiterVisibility() {
        const layerControls = document.querySelectorAll(
            '.leaflet-control-layers-overlays input[type="checkbox"]'
        );
        if (!layerControls.length) return false;

        const highwayLogos = document.querySelectorAll('.highway-logo-marker');
        let checkedStatusSections = 0;
        let totalStatusSections = 0;

        layerControls.forEach(control => {
            const labelText = control.nextElementSibling.textContent.trim();

            if (['Finished', 'In Construction', 'Tendered', 'Planned'].includes(labelText)) {
                totalStatusSections++;
                if (control.checked) {
                    checkedStatusSections++;
                }
            }

            if (labelText === '_logos') {
                control.checked = true;
                if (control.onchange) control.onchange();
                control.parentElement.style.display = 'none';
            }

            const delimiterControl = Array.from(layerControls).find(
                c =>
                    c.nextElementSibling.textContent.trim() ===
                    `_delimiters_${labelText.toLowerCase().replace(' ', '_')}`
            );
            // Toggle the delimiter layer to match its status. Leaflet's layer
            // control responds to click events, not a programmatic .checked
            // change or the onchange property, so click only when state differs.
            if (delimiterControl && delimiterControl.checked !== control.checked) {
                delimiterControl.click();
            }
        });

        // Prefer the logo marker's own section status; older generated pages
        // without data-status fall back to highway-level status matching.
        const selectedKeys = {};
        layerControls.forEach(function(c) {
            const lbl = c.nextElementSibling.textContent.trim();
            if (['Finished', 'In Construction', 'Tendered', 'Planned'].indexOf(lbl) !== -1 && c.checked) {
                selectedKeys[lbl.toLowerCase().replace(' ', '_')] = true;
            }
        });
        const highwayStatuses = getHighwayStatuses();
        const haveStatusData = Object.keys(highwayStatuses).length > 0;
        const allOrNoneSelected =
            checkedStatusSections === totalStatusSections || checkedStatusSections === 0;
        highwayLogos.forEach(logo => {
            if (allOrNoneSelected) {
                logo.style.display = 'block';
                return;
            }
            const logoStatus = logoStatusKey(logo);
            if (logoStatus) {
                logo.style.display = selectedKeys[logoStatus] ? 'block' : 'none';
                return;
            }
            if (!haveStatusData) {
                logo.style.display = 'block';
                return;
            }
            const statuses = highwayStatuses[logoHighwayCode(logo)] || {};
            const show = Object.keys(selectedKeys).some(function(k) {
                return statuses[k];
            });
            logo.style.display = show ? 'block' : 'none';
        });

        const logoControl = Array.from(layerControls).find(
            c => c.nextElementSibling.textContent.trim() === '_logos'
        );
        if (logoControl) {
            logoControl.parentElement.style.display = 'none';
        }

        return true;
    }

    function waitForControls(retries) {
        if (syncDelimiterVisibility()) {
            const sectionControls = document.querySelectorAll(
                '.leaflet-control-layers-overlays input[type="checkbox"]'
            );
            sectionControls.forEach(control => {
                control.addEventListener('change', syncDelimiterVisibility);
            });
            document.querySelectorAll('.section-button').forEach(function(button) {
                button.addEventListener('click', function() {
                    setTimeout(syncDelimiterVisibility, 0);
                });
            });
            return;
        }
        if (retries <= 0) return;
        setTimeout(() => waitForControls(retries - 1), 250);
    }

    function initHighDetail(mapInstance) {
        const statusLayers = data.statusLayers || {};
        if (Object.keys(statusLayers).length === 0) return;

        const HIGH_DETAIL_ZOOM = data.highDetailZoom || 9;
        let highDetailEnabled = false;
        let highDetailInitialized = false;
        let transitionId = 0;
        const DETAIL_FADE_MS = 180;

        function getLayer(pair, key) {
            if (!pair || !pair[key]) return null;
            return window[pair[key]];
        }

        function ensureHighLayer(pair) {
            return Promise.resolve(getLayer(pair, 'high'));
        }

        function setGroupOpacity(layer, opacity) {
            if (!layer || !layer.eachLayer) return;
            layer.eachLayer(function(child) {
                if (child && child.setStyle) {
                    child.setStyle({opacity: opacity});
                }
                setGroupOpacity(child, opacity);
            });
        }

        function setGroupInteraction(layer, interactive) {
            if (!layer) return;
            if (layer.options && layer.options.className) {
                layer.options.interactive = interactive;
                layer.options.bubblingMouseEvents = interactive;
            }
            if (!layer.eachLayer) return;
            layer.eachLayer(function(child) {
                setGroupInteraction(child, interactive);
            });
        }

        function bringGroupToFront(layer) {
            if (!layer) return;
            if (layer.bringToFront) {
                layer.bringToFront();
            }
            if (!layer.eachLayer) return;
            layer.eachLayer(function(child) {
                bringGroupToFront(child);
            });
        }

        // Section delimiters are black, weight-5 polylines (no reliable
        // className on every build). After high-detail layers are brought to
        // front they would cover the delimiters, so re-raise them on top.
        function bringDelimitersToFront() {
            mapInstance.eachLayer(function(layer) {
                if (
                    layer &&
                    layer.options &&
                    layer.options.color === 'black' &&
                    layer.options.weight === 5 &&
                    layer.bringToFront &&
                    typeof layer.getRadius !== 'function'
                ) {
                    layer.bringToFront();
                }
            });
        }

        function suppressLowDetail(layer, suppress) {
            setGroupOpacity(layer, suppress ? 0 : 1);
            setGroupInteraction(layer, !suppress);
        }

        function setAllLowDetailSuppressed(suppress) {
            Object.values(statusLayers).forEach(function(pair) {
                const lowLayer = getLayer(pair, 'low');
                if (lowLayer) {
                    suppressLowDetail(lowLayer, suppress);
                }
            });
        }

        function animateDetailSwitch(enable, layerPairs, onComplete) {
            const currentTransition = ++transitionId;
            const startedAt = performance.now();
            let finished = false;

            function finish() {
                if (finished || currentTransition !== transitionId) return;
                finished = true;

                layerPairs.forEach(function(pair) {
                    setGroupOpacity(pair.lowLayer, enable ? 0 : 1);
                    setGroupOpacity(pair.highLayer, enable ? 1 : 0);
                });

                if (onComplete) {
                    onComplete();
                }
            }

            function frame(now) {
                if (currentTransition !== transitionId) return;

                const progress = Math.min(1, (now - startedAt) / DETAIL_FADE_MS);
                const lowOpacity = enable ? 1 - progress : progress;
                const highOpacity = enable ? progress : 1 - progress;

                layerPairs.forEach(function(pair) {
                    setGroupOpacity(pair.lowLayer, lowOpacity);
                    setGroupOpacity(pair.highLayer, highOpacity);
                });

                if (progress < 1) {
                    requestAnimationFrame(frame);
                    return;
                }

                finish();
            }

            requestAnimationFrame(frame);
            setTimeout(finish, DETAIL_FADE_MS + 80);
        }

        function refreshTimelineIfNeeded() {
            if (window.refreshTimelineFilter) {
                window.refreshTimelineFilter();
            }
        }

        function refreshHighwayHighlightIfNeeded() {
            if (window.refreshHighwayHighlight) {
                window.refreshHighwayHighlight();
            }
        }

        function updateHighDetailMode() {
            const shouldEnable = mapInstance.getZoom() >= HIGH_DETAIL_ZOOM;
            if (highDetailInitialized && shouldEnable === highDetailEnabled) return;
            highDetailInitialized = true;
            if (shouldEnable !== highDetailEnabled) {
                highDetailEnabled = shouldEnable;
                document.body.classList.toggle('high-detail-mode', highDetailEnabled);
            } else {
                document.body.classList.toggle('high-detail-mode', highDetailEnabled);
            }

            const layerPairs = [];
            const activeLowLayerCount = Object.values(statusLayers).filter(function(pair) {
                const lowLayer = getLayer(pair, 'low');
                return lowLayer && mapInstance.hasLayer(lowLayer);
            }).length;
            Object.values(statusLayers).forEach(pair => {
                const lowLayer = getLayer(pair, 'low');
                if (!lowLayer) return;

                if (highDetailEnabled) {
                    if (!mapInstance.hasLayer(lowLayer)) return;
                    ensureHighLayer(pair).then(function(highLayer) {
                        if (!highDetailEnabled || !highLayer) return;
                        if (!mapInstance.hasLayer(highLayer)) {
                            mapInstance.addLayer(highLayer);
                        }
                        setGroupOpacity(highLayer, 0);
                        bringGroupToFront(highLayer);
                        layerPairs.push({lowLayer: lowLayer, highLayer: highLayer});
                        if (layerPairs.length === activeLowLayerCount) {
                            animateDetailSwitch(true, layerPairs, function() {
                                setAllLowDetailSuppressed(true);
                                bringDelimitersToFront();
                                refreshTimelineIfNeeded();
                                refreshHighwayHighlightIfNeeded();
                            });
                        }
                    });
                } else {
                    const highLayer = getLayer(pair, 'high');
                    if (highLayer && mapInstance.hasLayer(highLayer)) {
                        suppressLowDetail(lowLayer, true);
                        layerPairs.push({lowLayer: lowLayer, highLayer: highLayer});
                    }
                }
            });
            if (!highDetailEnabled) {
                animateDetailSwitch(false, layerPairs, function() {
                    layerPairs.forEach(function(pair) {
                        if (mapInstance.hasLayer(pair.highLayer)) {
                            mapInstance.removeLayer(pair.highLayer);
                        }
                    });
                    setAllLowDetailSuppressed(false);
                    refreshTimelineIfNeeded();
                    refreshHighwayHighlightIfNeeded();
                });
            }
            refreshTimelineIfNeeded();
        }

        // Toggling a status overlay triggers a cascade of overlayadd/overlayremove
        // events (section filter buttons re-toggle every overlay, and delimiter
        // sync adds more). Reacting per-event races and can leave high-detail
        // layers removed. Instead, debounce and reconcile the whole state once.
        function reconcileActiveLayers() {
            Object.values(statusLayers).forEach(pair => {
                const lowLayer = getLayer(pair, 'low');
                const highLayer = getLayer(pair, 'high');
                if (!lowLayer) return;

                const lowActive = mapInstance.hasLayer(lowLayer);
                if (highDetailEnabled && lowActive && highLayer) {
                    if (!mapInstance.hasLayer(highLayer)) {
                        mapInstance.addLayer(highLayer);
                    }
                    setGroupOpacity(highLayer, 1);
                    bringGroupToFront(highLayer);
                    suppressLowDetail(lowLayer, true);
                } else {
                    if (highLayer && mapInstance.hasLayer(highLayer)) {
                        mapInstance.removeLayer(highLayer);
                    }
                    suppressLowDetail(lowLayer, false);
                }
            });
            bringDelimitersToFront();
            refreshTimelineIfNeeded();
            refreshHighwayHighlightIfNeeded();
        }

        let reconcileTimer = null;
        function scheduleReconcile() {
            if (reconcileTimer) clearTimeout(reconcileTimer);
            reconcileTimer = setTimeout(function() {
                reconcileTimer = null;
                reconcileActiveLayers();
            }, 60);
        }

        mapInstance.on('zoomend', updateHighDetailMode);
        mapInstance.on('overlayadd', scheduleReconcile);
        mapInstance.on('overlayremove', scheduleReconcile);

        updateHighDetailMode();
    }

    function getActiveBaseLayerName(mapInstance) {
        let baseName = null;
        if (!window.L || !mapInstance) return baseName;
        mapInstance.eachLayer(function(layer) {
            if (!layer || !mapInstance.hasLayer(layer) || layer._url === undefined) return;
            if (layer._url === '') {
                baseName = 'White Map';
            } else if (layer._url.indexOf('openstreetmap') !== -1) {
                baseName = 'OpenStreetMap';
            } else if (layer._url.indexOf('google') !== -1) {
                baseName = 'Satellite';
            }
        });
        return baseName;
    }

    function findLayerByClass(layer, className) {
        if (!layer) return null;
        if (layer.options && layer.options.className === className) {
            return layer;
        }
        if (!layer.eachLayer) return null;

        let found = null;
        layer.eachLayer(function(child) {
            if (!found) {
                found = findLayerByClass(child, className);
            }
        });
        return found;
    }

    function initOutlineToggle(mapInstance) {
        const outlineLayer = findLayerByClass(mapInstance, 'romania-outline');
        if (!outlineLayer) return;

        function updateOutlineVisibility(baseName) {
            const shouldShow = baseName === 'White Map';
            if (shouldShow && !mapInstance.hasLayer(outlineLayer)) {
                mapInstance.addLayer(outlineLayer);
                if (outlineLayer.bringToBack) outlineLayer.bringToBack();
            } else if (!shouldShow && mapInstance.hasLayer(outlineLayer)) {
                mapInstance.removeLayer(outlineLayer);
            }

            document.querySelectorAll('.romania-outline').forEach(function(el) {
                el.style.display = shouldShow ? '' : 'none';
            });
        }

        const initialBase = getActiveBaseLayerName(mapInstance);
        if (initialBase) {
            updateOutlineVisibility(initialBase);
        }

        mapInstance.on('baselayerchange', function(e) {
            const name = e && e.name ? e.name : getActiveBaseLayerName(mapInstance);
            updateOutlineVisibility(name);
        });

        document.querySelectorAll('.map-button[data-map]').forEach(function(button) {
            button.addEventListener('click', function() {
                setTimeout(function() {
                    updateOutlineVisibility(getActiveBaseLayerName(mapInstance));
                }, 0);
            });
        });
    }

    function initCityOverlayToggle(mapInstance) {
        // City boundaries / dots are canvas layers toggled via the layer API
        // (labels are DOM markers handled in map_controls.js). Boundaries are
        // GeoJson polygons (className 'city-boundary'); dots are the only
        // CircleMarkers (detected by getRadius, since folium does not reliably
        // emit a className for CircleMarker).
        //   - Boundaries: shown only on the White Map.
        //   - Dots: shown only on the White Map AND when all status categories
        //     are selected (matches the highway logo behaviour).
        const boundaries = [];
        const dots = [];
        mapInstance.eachLayer(function(layer) {
            if (!layer || !layer.options) return;
            if (layer.options.className === 'city-boundary') {
                boundaries.push(layer);
            } else if (typeof layer.getRadius === 'function') {
                dots.push(layer);
            }
        });

        function allStatusesSelected() {
            const controls = document.querySelectorAll(
                '.leaflet-control-layers-overlays input[type="checkbox"]'
            );
            let checked = 0;
            let total = 0;
            controls.forEach(function(c) {
                const label = c.nextElementSibling.textContent.trim();
                if (['Finished', 'In Construction', 'Tendered', 'Planned'].indexOf(label) !== -1) {
                    total++;
                    if (c.checked) checked++;
                }
            });
            return total > 0 && checked === total;
        }

        function setLayersOnMap(layers, on) {
            layers.forEach(function(layer) {
                if (on && !mapInstance.hasLayer(layer)) {
                    mapInstance.addLayer(layer);
                } else if (!on && mapInstance.hasLayer(layer)) {
                    mapInstance.removeLayer(layer);
                }
            });
        }

        function updateCityVisibility() {
            const white = getActiveBaseLayerName(mapInstance) === 'White Map';
            setLayersOnMap(boundaries, white);
            setLayersOnMap(dots, white && allStatusesSelected());
        }

        let updateTimer = null;
        function scheduleUpdate() {
            if (updateTimer) clearTimeout(updateTimer);
            updateTimer = setTimeout(function() {
                updateTimer = null;
                updateCityVisibility();
            }, 60);
        }

        updateCityVisibility();

        mapInstance.on('baselayerchange', updateCityVisibility);
        mapInstance.on('overlayadd', scheduleUpdate);
        mapInstance.on('overlayremove', scheduleUpdate);

        document.querySelectorAll('.map-button[data-map]').forEach(function(button) {
            button.addEventListener('click', function() {
                setTimeout(updateCityVisibility, 0);
            });
        });
    }

    function init(mapInstance) {
        waitForControls(40);
        initHighDetail(mapInstance);
        initOutlineToggle(mapInstance);
        initCityOverlayToggle(mapInstance);
    }

    waitForMap(40);
})();
