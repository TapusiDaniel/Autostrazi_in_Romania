// Timeline slider logic (data injected via #timeline-data JSON)
(function() {
    function loadTimelineData() {
        const el = document.getElementById('timeline-data');
        if (!el) return null;
        try {
            return JSON.parse(el.textContent);
        } catch (e) {
            return null;
        }
    }

    const data = loadTimelineData();
    if (!data) return;

    const timelineData = data.timelineData || {};
    const yearlyAdditions = data.yearlyAdditions || {};
    const currentStateTotal = data.currentStateTotal || 0;

    let isTimelineActive = false;
    let currentFilterYear = null;
    let currentFilterMode = null;
    let cachedHighwayLayers = null;
    let cachedDelimiterLayers = null;

    function loadHighwayLayerData() {
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

    function collectHighwayLayers(layer, matches) {
        if (!layer) return;
        if (
            layer.options &&
            layer.options.className &&
            layer.options.className.split(/\s+/).includes('highway-section') &&
            layer.setStyle
        ) {
            matches.push(layer);
        }

        if (!layer.eachLayer) return;
        layer.eachLayer(function(child) {
            collectHighwayLayers(child, matches);
        });
    }

    function getHighwayLayers() {
        if (cachedHighwayLayers) return cachedHighwayLayers;

        const mapInstance = getLeafletMap();
        const layers = [];
        if (mapInstance) {
            collectHighwayLayers(mapInstance, layers);
        }
        const layerData = loadHighwayLayerData();
        if (layerData && layerData.statusLayers) {
            Object.values(layerData.statusLayers).forEach(function(pair) {
                ['low', 'high'].forEach(function(key) {
                    if (pair[key] && window[pair[key]]) {
                        collectHighwayLayers(window[pair[key]], layers);
                    }
                });
            });
        }
        cachedHighwayLayers = layers.filter(function(layer, index) {
            return layers.findIndex(function(item) {
                return item._leaflet_id === layer._leaflet_id;
            }) === index;
        });
        return cachedHighwayLayers;
    }

    window.invalidateTimelineLayerCache = function() {
        cachedHighwayLayers = null;
    };

    // Delimiters are black, weight-5 polylines. Match by that signature rather
    // than a className, because some folium builds do not emit a className for
    // PolyLine/CircleMarker layers.
    function isDelimiterLayer(layer) {
        if (!layer || !layer.options || !layer.setStyle) return false;
        if (layer.options.className === 'highway-delimiter') return true;
        return (
            layer.options.color === 'black' &&
            layer.options.weight === 5 &&
            typeof layer.getRadius !== 'function'
        );
    }

    function collectDelimiterLayers(layer, matches) {
        if (!layer) return;
        if (isDelimiterLayer(layer)) {
            matches.push(layer);
        }

        if (!layer.eachLayer) return;
        layer.eachLayer(function(child) {
            collectDelimiterLayers(child, matches);
        });
    }

    // Delimiters are drawn on the Leaflet canvas renderer (preferCanvas),
    // so they are not DOM nodes and cannot be hidden via CSS. Toggle their
    // opacity through the layer API instead.
    function setDelimitersVisible(visible) {
        getDelimiterLayers().forEach(function(layer) {
            layer.setStyle({opacity: visible ? 1 : 0});
        });
    }

    function getDelimiterLayers() {
        if (cachedDelimiterLayers) return cachedDelimiterLayers;

        const mapInstance = getLeafletMap();
        const delimiters = [];
        if (mapInstance) {
            collectDelimiterLayers(mapInstance, delimiters);
        }
        cachedDelimiterLayers = delimiters;
        return cachedDelimiterLayers;
    }

    function getLayerYear(layer) {
        if (!layer || !layer.options || !layer.options.className) return NaN;
        const match = layer.options.className.match(/section-year-(\d+)/);
        return match ? parseInt(match[1]) : NaN;
    }

    function getDefaultOpacity(layer) {
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

    function isFinishedLayer(layer) {
        const className = layer && layer.options && layer.options.className;
        return (
            className &&
            className.split(/\s+/).includes('section-status-finished')
        );
    }

    function setElementVisible(el, isVisible) {
        if (isVisible) {
            el.style.opacity = '1';
            el.style.strokeOpacity = '1';
            el.style.pointerEvents = 'auto';
            el.style.display = 'block';
        } else {
            el.style.opacity = '0';
            el.style.strokeOpacity = '0';
            el.style.pointerEvents = 'none';
        }
    }

    function positionToYear(pos) {
        const segments = [
            {pos: 0, year: 1970},
            {pos: 20, year: 2000},
            {pos: 40, year: 2010},
            {pos: 60, year: 2020},
            {pos: 75, year: 2025},
            {pos: 88, year: 2031},
            {pos: 100, year: 2036}
        ];

        for (let i = 0; i < segments.length - 1; i++) {
            if (pos >= segments[i].pos && pos <= segments[i + 1].pos) {
                const ratio = (pos - segments[i].pos) / (segments[i + 1].pos - segments[i].pos);
                return Math.round(segments[i].year + ratio * (segments[i + 1].year - segments[i].year));
            }
        }
        return 2036;
    }

    function getTimelineSelection(year) {
        if (year === 2026) {
            return {displayText: 'În prezent', dataYear: null, isPresent: true};
        }
        if (year >= 2027) {
            const actualYear = year - 1;
            return {
                displayText: actualYear.toString(),
                dataYear: actualYear,
                isPresent: false
            };
        }
        return {
            displayText: year.toString(),
            dataYear: year,
            isPresent: false
        };
    }

    function toggleTimeline() {
        const container = document.getElementById('timeline-container');
        const btn = document.getElementById('timeline-toggle');
        if (!container || !btn) return;

        container.classList.toggle('hidden');
        isTimelineActive = !container.classList.contains('hidden');
        btn.textContent = isTimelineActive ? '✕ Închide' : '📅 Evoluție în timp';

        if (isTimelineActive) {
            if (window.resetHighwayHighlight) {
                window.resetHighwayHighlight();
            }

            const sliderPos = parseInt(document.getElementById('timeline-slider').value);
            const year = positionToYear(sliderPos);
            const selection = getTimelineSelection(year);

            if (selection.isPresent) {
                filterCurrentState();
            } else {
                filterMapByYear(selection.dataYear);
            }

            document.body.classList.add('timeline-mode');

            setDelimitersVisible(false);
        } else {
            resetMapFilter();
            document.body.classList.remove('timeline-mode');

            setDelimitersVisible(true);
        }
    }

    function filterCurrentState() {
        currentFilterMode = 'current';
        currentFilterYear = null;
        const layers = getHighwayLayers();
        if (layers.length > 0) {
            layers.forEach(function(layer) {
                layer.setStyle({opacity: isFinishedLayer(layer) ? getDefaultOpacity(layer) : 0});
            });
            return;
        }

        const sections = document.querySelectorAll('path.highway-section');
        sections.forEach(function(el) {
            setElementVisible(el, el.classList.contains('section-status-finished'));
        });
    }

    function filterMapByYear(year) {
        currentFilterMode = 'year';
        currentFilterYear = year;
        const layers = getHighwayLayers();
        if (layers.length > 0) {
            layers.forEach(function(layer) {
                const sectionYear = getLayerYear(layer);
                const isVisible = !isNaN(sectionYear) && sectionYear <= year;
                layer.setStyle({opacity: isVisible ? getDefaultOpacity(layer) : 0});
            });
            return;
        }

        const sections = document.querySelectorAll('path.highway-section');
        sections.forEach(function(el) {
            let isVisible = false;
            const classes = Array.from(el.classList);
            const yearClass = classes.find(c => c.startsWith('section-year-'));

            if (yearClass) {
                const sectionYear = parseInt(yearClass.replace('section-year-', ''));
                if (!isNaN(sectionYear) && sectionYear <= year) {
                    isVisible = true;
                }
            }

            setElementVisible(el, isVisible);
        });
    }

    function resetMapFilter() {
        currentFilterMode = null;
        currentFilterYear = null;
        const layers = getHighwayLayers();
        if (layers.length > 0) {
            layers.forEach(function(layer) {
                layer.setStyle({opacity: getDefaultOpacity(layer)});
            });
            return;
        }

        const sections = document.querySelectorAll('path.highway-section');
        sections.forEach(function(el) {
            el.style.opacity = '';
            el.style.strokeOpacity = '';
            el.style.pointerEvents = '';
            el.style.display = '';
        });
    }

    window.refreshTimelineFilter = function() {
        if (isTimelineActive && currentFilterMode === 'current') {
            filterCurrentState();
            setDelimitersVisible(false);
        } else if (isTimelineActive && currentFilterYear !== null) {
            filterMapByYear(currentFilterYear);
            setDelimitersVisible(false);
        }
    };

    window.getTimelineFilteredOpacity = function(layer, opacity) {
        if (!isTimelineActive) return opacity;

        if (currentFilterMode === 'current') {
            return isFinishedLayer(layer) ? opacity : 0;
        }

        if (currentFilterYear === null) return opacity;

        const sectionYear = getLayerYear(layer);
        if (isNaN(sectionYear) || sectionYear > currentFilterYear) {
            return 0;
        }
        return opacity;
    };

    function initTimeline() {
        const slider = document.getElementById('timeline-slider');
        const yearDisplay = document.getElementById('timeline-year');
        const kmDisplay = document.getElementById('timeline-km');

        if (!slider || !yearDisplay || !kmDisplay) return;

        slider.addEventListener('input', function() {
            const sliderPos = parseInt(this.value);
            const year = positionToYear(sliderPos);
            const selection = getTimelineSelection(year);

            const cumulativeKm = selection.isPresent
                ? currentStateTotal
                : timelineData[selection.dataYear] || 0;
            const yearlyKm = selection.isPresent
                ? 0
                : yearlyAdditions[selection.dataYear] || 0;

            yearDisplay.innerHTML = selection.displayText;

            if (yearlyKm > 0 && !selection.isPresent) {
                kmDisplay.innerHTML = parseFloat(cumulativeKm).toFixed(3).replace(/\.?0+$/, '') +
                    ' <span style="color: #4CAF50; font-weight: bold;">(+' +
                    parseFloat(yearlyKm).toFixed(3).replace(/\.?0+$/, '') + ' km)</span>';
            } else {
                kmDisplay.textContent = parseFloat(cumulativeKm).toFixed(3).replace(/\.?0+$/, '');
            }

            if (isTimelineActive) {
                if (selection.isPresent) {
                    filterCurrentState();
                } else {
                    filterMapByYear(selection.dataYear);
                }
            }
        });

        window.addEventListener('load', function() {
            if (kmDisplay) {
                kmDisplay.textContent = parseFloat(currentStateTotal).toFixed(3).replace(/\.?0+$/, '');
            }
        });
    }

    window.toggleTimeline = toggleTimeline;

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initTimeline);
    } else {
        initTimeline();
    }
})();
