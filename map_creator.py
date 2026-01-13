import folium
from components.base_map import create_base_map
from components.map_layers import add_tile_layers
from components.city_elements import add_cities_to_map
from components.highway_elements import add_highways_to_map, add_totals_table
from utils.resource_manager import add_css_file, add_js_file, add_external_css
from utils.html_optimizer import optimize_template
from highway_data import HIGHWAYS

def create_highways_map(labels_position="below"):
    """Create a Folium map displaying highways in Romania."""
    # Create base map
    m = create_base_map()
    
    # Add HTML lang attribute for accessibility and SEO
    html_lang = """
    <script>
        document.documentElement.setAttribute('lang', 'ro');
    </script>
    """
    m.get_root().html.add_child(folium.Element(html_lang))
    
    # Add meta tags for SEO and responsiveness
    meta_tags = """
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes">
        <meta name="description" content="Hartă interactivă a autostrăzilor și drumurilor expres din România. Vizualizați progresul construcției, secțiunile finalizate, în lucru și planificate. Actualizat regulat cu date oficiale.">
        <meta name="keywords" content="Romania, highways, motorways, autostrăzi, drumuri expres, infrastructure, harta autostrazilor, retea rutiera">
        <meta name="author" content="Daniel Tapusi">
        <meta name="robots" content="index, follow">
        <title>Autostrăzi în România - Hartă Interactivă</title>
        
        <!-- Resource Hints for Performance -->
        <link rel="preconnect" href="https://cdnjs.cloudflare.com" crossorigin>
        <link rel="dns-prefetch" href="https://mt1.google.com">
        <link rel="dns-prefetch" href="https://tile.openstreetmap.org">
        <link rel="preconnect" href="https://unpkg.com" crossorigin>
    """
    m.get_root().header.add_child(folium.Element(meta_tags))
    
    # Add Font Awesome for icons
    add_external_css(m, "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css")
    
    # Add CSS files
    add_css_file(m, "static/css/critical.css")
    add_css_file(m, "static/css/controls.css")
    add_css_file(m, "static/css/totals_table.css")
    add_css_file(m, "static/css/markers.css")
    add_css_file(m, "static/css/ux_enhancements.css")
    
    # Add tile layers and Romania outline
    add_tile_layers(m)
    
    # Add cities and boundaries
    add_cities_to_map(m, labels_position)
    
    # Add highways
    add_highways_to_map(m)
    
    # Add skip link for keyboard navigation
    skip_link_html = """
    <a href="#map" class="skip-link" style="position: absolute; left: -9999px; z-index: 999999; 
       padding: 1em; background: #000; color: #fff; text-decoration: none;">
        Sari la hartă
    </a>
    <style>
        .skip-link:focus {
            left: 0;
            top: 0;
        }
    </style>
    """
    m.get_root().html.add_child(folium.Element(skip_link_html))
    
    # Add map controls HTML
    controls_html = """
    <div class="map-controls" role="navigation" aria-label="Controale hartă">
        <button class="minimize-button" aria-label="Minimizează panoul" title="Minimizează">−</button>
        <div class="map-button-group">
            <div class="map-button-group-title">Stil hartă</div>
            <button class="map-button active" data-map="white">Hartă Albă</button>
            <button class="map-button" data-map="osm">OpenStreetMap</button>
            <button class="map-button" data-map="satellite">Satelit</button>
        </div>

        <div class="map-button-group">
            <div class="map-button-group-title">Secțiuni</div>
            <button class="section-button section-all active" data-section="all">
                <span class="section-indicator"></span>
                Toate secțiunile
            </button>
            <button class="section-button section-finished" data-section="Finished">
                <span class="section-indicator"></span>
                Finalizate
            </button>
            <button class="section-button section-in-construction" data-section="In Construction">
                <span class="section-indicator"></span>
                În construcție
            </button>
            <button class="section-button section-tendered" data-section="Tendered">
                <span class="section-indicator"></span>
                În licitație
            </button>
            <button class="section-button section-planned" data-section="Planned">
                <span class="section-indicator"></span>
                Planificate
            </button>
        </div>
    </div>
    """
    m.get_root().html.add_child(folium.Element(controls_html))
    
    # Add dark mode toggle button
    dark_mode_html = """
    <button class="dark-mode-toggle" id="dark-mode-toggle" aria-label="Comută modul întunecat" title="Comută modul întunecat">
        <span class="icon-moon">🌙</span>
        <span class="icon-sun">☀️</span>
    </button>
    <script>
        // Dark mode toggle with localStorage persistence
        (function() {
            const toggle = document.getElementById('dark-mode-toggle');
            const html = document.documentElement;
            
            // Check for saved preference or system preference
            const savedTheme = localStorage.getItem('theme');
            const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            
            // Function to update SVG fills for dark mode
            function applyDarkModeToSVG() {
                // Target specific classes we added: romania-outline, city-boundary, city-dot
                // Note: Folium applies class_name to the path element directly
                const selectors = [
                    '.romania-outline', 
                    '.city-boundary', 
                    '.city-dot',
                    '.leaflet-circle-marker-pane path' // Fallback for dots if class missing
                ];
                
                document.querySelectorAll(selectors.join(', ')).forEach(function(el) {
                    // Check if it's one of our target elements
                    const isRomania = el.classList.contains('romania-outline');
                    const isCity = el.classList.contains('city-boundary');
                    const isDot = el.classList.contains('city-dot') || el.closest('.leaflet-circle-marker-pane');
                    
                    if (isRomania) {
                        el.style.fill = '#1a1a1a'; // Match background
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
            
            // Function to revert SVG fills
            function revertDarkModeFromSVG() {
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
            
            if (savedTheme === 'dark' || (!savedTheme && systemPrefersDark)) {
                html.setAttribute('data-theme', 'dark');
                // Apply SVG dark mode after map fully loads
                setTimeout(applyDarkModeToSVG, 1000);
            }
            
            // Listen for system preference changes
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', event => {
                if (!localStorage.getItem('theme')) { // Only if user hasn't manually overridden
                    if (event.matches) {
                        html.setAttribute('data-theme', 'dark');
                        applyDarkModeToSVG();
                    } else {
                        html.removeAttribute('data-theme');
                        revertDarkModeFromSVG();
                    }
                }
            });
            
            toggle.addEventListener('click', function() {
                const currentTheme = html.getAttribute('data-theme');
                const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
                
                if (newTheme === 'dark') {
                    html.setAttribute('data-theme', 'dark');
                    applyDarkModeToSVG();
                } else {
                    html.removeAttribute('data-theme');
                    revertDarkModeFromSVG();
                }
                
                localStorage.setItem('theme', newTheme);
            });
        })();
    </script>
    """
    m.get_root().html.add_child(folium.Element(dark_mode_html))
    
    # Add JavaScript files
    add_js_file(m, "static/js/map_controls.js")
    add_js_file(m, "static/js/section_filters.js")
    add_js_file(m, "static/js/resource_loader.js")
    
    # Add highway totals table
    add_totals_table(m)
    
    # Add loading overlay
    loading_html = """
    <div id="loading-overlay" class="loading-overlay">
        <div class="loading-spinner"></div>
        <div class="loading-text">Se încarcă harta...</div>
    </div>
    <script>
        // Hide loading overlay when map is ready
        document.addEventListener('DOMContentLoaded', function() {
            // Wait for tiles to load
            setTimeout(function() {
                var overlay = document.getElementById('loading-overlay');
                if (overlay) {
                    overlay.classList.add('hidden');
                    // Remove from DOM after fade animation
                    setTimeout(function() {
                        overlay.remove();
                    }, 500);
                }
            }, 1500);
        });
    </script>
    """
    m.get_root().html.add_child(folium.Element(loading_html))
    
    
    # Generate Sidebar HTML dynamically
    sidebar_items_html = ""
    # Sort highways by ID (A0, A1, A2...)
    sorted_highways = sorted(HIGHWAYS.items(), key=lambda x: int(x[0].split(' ')[1].replace('A', '').replace('DEx', '100')) if x[0].split(' ')[1][0].isdigit() or x[0].startswith('Autostrada') else 999)
    
    for highway_key, data in sorted_highways:
        code = highway_key.split(' ')[1] if ' ' in highway_key else highway_key
        name = data.get('name', '')
        length = data.get('total_length', 'N/A')
        
        # Determine status class roughly
        has_finished = False
        has_construction = False
        for s in data.get('sections', {}).values():
            if s['status'] == 'finished': has_finished = True
            if s['status'] == 'in_construction': has_construction = True
            
        dot_class = 'mixed'
        if has_finished and not has_construction: dot_class = 'finished'
        elif not has_finished and has_construction: dot_class = 'in-construction'
        elif not has_finished and not has_construction: dot_class = 'planned'
        
        sidebar_items_html += f"""
            <div class="highway-item" onclick="highlightHighway('{code}')">
                <div class="highway-status-dot {dot_class}"></div>
                <div style="display:flex; flex-direction:column;">
                    <span style="font-weight:bold;">{code} - {name}</span>
                    <span style="font-size:11px; color:#666;">{length}</span>
                </div>
            </div>
        """

    # Add UX Enhancements
    ux_enhancements_html = """
    <!-- Full Screen Button -->
    <button class="fullscreen-btn" id="fullscreen-btn" title="Ecran complet">
        ⛶
    </button>
    
    <!-- Share Button -->
    <button class="share-btn" id="share-btn" title="Distribuie / Copiază link">
        ➦
    </button>


    <!-- Share Modal -->
    <div class="share-modal-overlay" id="share-modal-overlay">
        <div class="share-modal">
            <div class="share-header">
                <h3 class="share-title">Distribuie Harta</h3>
                <button class="share-close" id="share-close">✕</button>
            </div>
            <div class="share-options-grid">
                <!-- Facebook -->
                <a href="#" class="share-option facebook" id="share-facebook" target="_blank">
                    <span class="share-option-icon">f</span>
                    <span class="share-option-label">Facebook</span>
                </a>
                
                <!-- Twitter/X -->
                <a href="#" class="share-option twitter" id="share-twitter" target="_blank">
                    <span class="share-option-icon">𝕏</span>
                    <span class="share-option-label">Twitter</span>
                </a>
                
                <!-- WhatsApp -->
                <a href="#" class="share-option whatsapp" id="share-whatsapp" target="_blank">
                    <span class="share-option-icon">💬</span>
                    <span class="share-option-label">WhatsApp</span>
                </a>
                
                <!-- Copy Link -->
                <div class="share-option copy" id="share-copy">
                    <span class="share-option-icon">📋</span>
                    <span class="share-option-label">Copiază Link</span>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Toast Notification -->
    <div class="toast" id="toast">Link copiat!</div>
    
    
    <script>
        // Global state for active highlighted highway
        window.activeHighway = null;

        // Highlight Highway Function (Global for onclick access)
        window.highlightHighway = function(code) {
            // 1. Clear ALL existing highlights first
            document.querySelectorAll('.highlighted-path').forEach(path => {
                path.classList.remove('highlighted-path');
            });
             
            // 2. Toggle logic
            if (window.activeHighway === code) {
                window.activeHighway = null;
                return;
            }
            window.activeHighway = code;
            
            // 3. Extract short code
            var shortCode = code;
            var match = code.match(/(A\d+)|(DEx\d+)/i);
            if (match) {
                shortCode = match[0].toUpperCase();
            }
            
            // 4. Highlight
            var targetClass = 'highway-section-' + code.toLowerCase().replace(/ /g, '-');
            var sections = document.querySelectorAll('path.' + targetClass);
            
            if (sections.length > 0) {
                sections.forEach(function(el) {
                    el.classList.add('highlighted-path');
                });
            } else {
                 document.querySelectorAll('.leaflet-pane path').forEach(path => {
                    const parentElement = path.closest('.leaflet-interactive');
                    if (parentElement && parentElement.classList.contains(targetClass)) {
                        path.classList.add('highlighted-path');
                    }
                });
            }
            
            // User requested to disable zoom on click ("keep you in the same place")
            // zoomToHighwayCenter(shortCode);
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

        // Initialize UI (Robust Pattern)
        function initUX() {
            console.log('Initializing UX buttons...');
            
            // Fullscreen toggle
            var fullscreenBtn = document.getElementById('fullscreen-btn');
            
            if (fullscreenBtn) {
                var newFullscreenBtn = fullscreenBtn.cloneNode(true);
                fullscreenBtn.parentNode.replaceChild(newFullscreenBtn, fullscreenBtn);
                fullscreenBtn = newFullscreenBtn;
                
                fullscreenBtn.addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    if (!document.fullscreenElement) {
                        document.documentElement.requestFullscreen().catch(err => console.log(err));
                    } else {
                        if (document.exitFullscreen) document.exitFullscreen().catch(err => console.log(err));
                    }
                });
            }

            document.addEventListener('fullscreenchange', function() {
                if (document.fullscreenElement) {
                    if(fullscreenBtn) {
                        fullscreenBtn.textContent = '✕';
                        fullscreenBtn.title = 'Ieșire ecran complet';
                    }
                    document.body.classList.add('fullscreen-mode');
                } else {
                    if(fullscreenBtn) {
                        fullscreenBtn.textContent = '⛶';
                        fullscreenBtn.title = 'Ecran complet';
                    }
                    document.body.classList.remove('fullscreen-mode');
                }
            });
            
            // Share Modal Logic
            var shareBtn = document.getElementById('share-btn');
            var modalOverlay = document.getElementById('share-modal-overlay');
            var closeBtn = document.getElementById('share-close');
            var fbBtn = document.getElementById('share-facebook');
            var twBtn = document.getElementById('share-twitter');
            var waBtn = document.getElementById('share-whatsapp');
            var copyBtn = document.getElementById('share-copy');

            function openModal() {
                if(modalOverlay) {
                    modalOverlay.style.display = 'flex';
                    modalOverlay.offsetHeight;
                    modalOverlay.classList.add('show');
                    
                    var url = encodeURIComponent("https://tapusidaniel.github.io/Autostrazi_in_Romania/");
                    var title = encodeURIComponent("Autostrăzi în România - Hartă Interactivă");
                    
                    if(fbBtn) fbBtn.href = "https://www.facebook.com/sharer/sharer.php?u=" + url;
                    if(twBtn) twBtn.href = "https://twitter.com/intent/tweet?text=" + title + "&url=" + url;
                    if(waBtn) waBtn.href = "https://api.whatsapp.com/send?text=" + title + " " + url;
                }
            }

            function closeModal() {
                if(modalOverlay) {
                    modalOverlay.classList.remove('show');
                    setTimeout(function() {
                        modalOverlay.style.display = 'none';
                    }, 300);
                }
            }

            if (shareBtn) {
                var newShareBtn = shareBtn.cloneNode(true);
                shareBtn.parentNode.replaceChild(newShareBtn, shareBtn);
                shareBtn = newShareBtn;
                shareBtn.addEventListener('click', function(e) {
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
                    var url = window.location.href.split('?')[0];
                    navigator.clipboard.writeText(url).then(function() {
                        showToast('Link copiat!');
                        closeModal();
                    }).catch(function() {
                        showToast('Nu s-a putut copia');
                    });
                });
            }
        }

        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', initUX);
        } else {
            initUX();
        }
        
        // Define showToast globally
        window.showToast = function(msg) {
            var t = document.getElementById('toast');
            if (t) {
                t.textContent = msg;
                t.classList.add('show');
                setTimeout(function() { t.classList.remove('show'); }, 2000);
            }
        };
    </script>
    """
    m.get_root().html.add_child(folium.Element(ux_enhancements_html))
    
    # Generate timeline data from actual highway sections
    def calculate_km_by_year():
        """Calculate cumulative km of highways by year including future projections."""
        yearly_km = {}
        
        def parse_completion_year(section):
            """Calculate projected completion year based on section status."""
            status = section.get('status')
            
            # Check if there's an explicit projected completion date first
            projected_date = section.get('projected_completion_date')
            if projected_date:
                try:
                    # Handle "~ 2030" or "2030" formats
                    clean_date = str(projected_date).replace('~', '').strip()
                    return int(clean_date[:4])
                except (ValueError, TypeError):
                    pass
            
            if status == 'finished' or status == 'in_construction':
                completion_date = section.get('completion_date', '')
                try:
                    return int(str(completion_date)[:4])
                except (ValueError, TypeError):
                    return None
                    
            elif status == 'tendered':
                try:
                    tender_year = int(section.get('tender_end_date', '2026'))
                    duration_str = section.get('construction_duration', '0 de luni')
                    months = int(duration_str.split()[0])
                    years = months / 12
                    return int(tender_year + years)
                except (ValueError, TypeError, AttributeError):
                    return 2035
                    
            elif status == 'planned':
                return 2035
                
            return None
        
        for highway in HIGHWAYS.values():
            for section_name, section in highway.get('sections', {}).items():
                year = parse_completion_year(section)
                if year:
                    length_str = section.get('length', '0 km')
                    try:
                        length = float(length_str.replace(' km', '').replace(',', '.'))
                        yearly_km[year] = yearly_km.get(year, 0) + length
                    except (ValueError, TypeError):
                        continue
        
        return yearly_km
    
    yearly_km = calculate_km_by_year()
    
    # Calculate cumulative km by year
    cumulative_data = {}
    cumulative = 0
    for year in range(1970, 2036):
        if year in yearly_km:
            cumulative += yearly_km[year]
        cumulative_data[year] = round(cumulative, 2)
    
    # Generate JavaScript objects from data
    timeline_data_js = ", ".join([f"{y}: {km}" for y, km in sorted(cumulative_data.items()) if y >= 1970])
    # Also pass yearly additions for delta display
    yearly_additions_js = ", ".join([f"{y}: {km}" for y, km in sorted(yearly_km.items()) if y >= 1970])
    current_total = cumulative_data.get(2026, 0)
    current_state_total = cumulative_data.get(2025, 0)  # What's open NOW (end of 2025)
    
    # Add Timeline Slider
    timeline_html = f"""
    <!-- Timeline Toggle Button -->
    <button class="timeline-toggle" id="timeline-toggle" onclick="toggleTimeline()">
        📅 Evoluție în timp
    </button>
    
    <!-- Timeline Slider -->
    <div class="timeline-container hidden" id="timeline-container">
        <div class="timeline-title">Evoluția construcției autostrăzilor</div>
        <div class="timeline-year" id="timeline-year">În prezent</div>
        <div class="timeline-slider-wrapper">
            <input type="range" class="timeline-slider" id="timeline-slider" 
                   min="0" max="100" value="78" step="1">
        </div>
        <div class="timeline-labels">
            <span>1970</span>
            <span>2000</span>
            <span>2010</span>
            <span>2020</span>
            <span>2025</span>
            <span>2030</span>
            <span>2035</span>
        </div>
        <div class="timeline-stats" id="timeline-stats">
            Finalizat: <span id="timeline-km">{current_state_total}</span> km
        </div>
    </div>
    
    <script>
        // Timeline data (calculated from actual highway sections)
        var timelineData = {{{timeline_data_js}}};
        var yearlyAdditions = {{{yearly_additions_js}}};
        var isTimelineActive = false;
        
        // Position-to-year mapping (matches visual label distribution)
        // Labels: 0%=1970, 20%=2000, 40%=2010, 60%=2020, 75%=2025, 88%=2030, 100%=2035
        function positionToYear(pos) {{
            var segments = [
                {{pos: 0, year: 1970}},
                {{pos: 20, year: 2000}},
                {{pos: 40, year: 2010}},
                {{pos: 60, year: 2020}},
                {{pos: 75, year: 2025}},
                {{pos: 88, year: 2031}}, // 2031 mapped becomes 2030
                {{pos: 100, year: 2036}} // 2036 mapped becomes 2035
            ];
            
            for (var i = 0; i < segments.length - 1; i++) {{
                if (pos >= segments[i].pos && pos <= segments[i+1].pos) {{
                    var ratio = (pos - segments[i].pos) / (segments[i+1].pos - segments[i].pos);
                    return Math.round(segments[i].year + ratio * (segments[i+1].year - segments[i].year));
                }}
            }}
            return 2036;
        }}
        
        // Year-to-position mapping (for initial positioning)
        function yearToPosition(year) {{
            var segments = [
                {{pos: 0, year: 1970}},
                {{pos: 20, year: 2000}},
                {{pos: 40, year: 2010}},
                {{pos: 60, year: 2020}},
                {{pos: 75, year: 2025}},
                {{pos: 88, year: 2031}},
                {{pos: 100, year: 2036}}
            ];
            
            for (var i = 0; i < segments.length - 1; i++) {{
                if (year >= segments[i].year && year <= segments[i+1].year) {{
                    var ratio = (year - segments[i].year) / (segments[i+1].year - segments[i].year);
                    return Math.round(segments[i].pos + ratio * (segments[i+1].pos - segments[i].pos));
                }}
            }}
            return 100;
        }}
        
        function toggleTimeline() {{
            var container = document.getElementById('timeline-container');
            var btn = document.getElementById('timeline-toggle');
            container.classList.toggle('hidden');
            
            isTimelineActive = !container.classList.contains('hidden');
            btn.textContent = isTimelineActive ? '✕ Închide' : '📅 Evoluție în timp';
            
            if (isTimelineActive) {{
                // Apply current filter with correct mapping
                var sliderPos = parseInt(document.getElementById('timeline-slider').value);
                var year = positionToYear(sliderPos);
                
                // Remap 2026 (În prezent) to 2025 data
                var dataYear = year;
                if (year === 2026) {{
                    dataYear = 2025;
                }} else if (year >= 2027) {{
                    dataYear = year - 1;
                }}
                
                filterMapByYear(dataYear);
                
                // Hide delimiters and logos in timeline mode via CSS class
                document.body.classList.add('timeline-mode');
                
                // Fallback for delimiters: hide by checking SVG attributes (since class might be missing on PolyLine)
                document.querySelectorAll('path').forEach(el => {{
                    if (el.getAttribute('stroke') === 'black' && el.getAttribute('stroke-width') === '5') {{
                        el.style.display = 'none';
                    }}
                }});
                
            }} else {{
                // Reset map to show everything
                resetMapFilter();
                
                // Show delimiters and logos again
                document.body.classList.remove('timeline-mode');
                
                // Fallback: show delimiters again
                document.querySelectorAll('path').forEach(el => {{
                    if (el.getAttribute('stroke') === 'black' && el.getAttribute('stroke-width') === '5') {{
                        el.style.display = '';
                    }}
                }});
            }}
        }}
        
        var slider = document.getElementById('timeline-slider');
        var yearDisplay = document.getElementById('timeline-year');
        var kmDisplay = document.getElementById('timeline-km');
        
        slider.addEventListener('input', function() {{
            var sliderPos = parseInt(this.value);
            var year = positionToYear(sliderPos);
            var displayText, dataYear;
            
            // Remap values to insert "În prezent" between 2025 and 2026
            if (year === 2026) {{
                // Show "În prezent" (current moment)
                displayText = 'În prezent';
                dataYear = 2025;  // Use 2025 data (what's open NOW)
            }} else if (year >= 2027) {{
                // Shift years: 2027 displays as "2026", 2028 as "2027", etc.
                var actualYear = year - 1;
                displayText = actualYear.toString();
                dataYear = actualYear;
            }} else {{
                // 2025 and below: normal mapping
                displayText = year.toString();
                dataYear = year;
            }}
            
            var cumulativeKm = timelineData[dataYear] || 0;
            var yearlyKm = yearlyAdditions[dataYear] || 0;
            
            // Update display
            yearDisplay.innerHTML = displayText;
            
            // Show cumulative + yearly addition in different color (remove trailing zeros)
            // For "În prezent", don't show yearly additions since nothing opened in 2026 yet
            if (yearlyKm > 0 && year !== 2026) {{
                kmDisplay.innerHTML = parseFloat(cumulativeKm).toFixed(3).replace(/\.?0+$/, '') + ' <span style="color: #4CAF50; font-weight: bold;">(+' + parseFloat(yearlyKm).toFixed(3).replace(/\.?0+$/, '') + ' km)</span>';
            }} else {{
                kmDisplay.textContent = parseFloat(cumulativeKm).toFixed(3).replace(/\.?0+$/, '');
            }}
            
            if (isTimelineActive) {{
                filterMapByYear(dataYear);
            }}
        }});
        
        // Initialize display on page load
        // Initialize display on page load
        window.addEventListener('load', function() {{
            var initialValue = 2026;  // În prezent
            var dataYear = 2025;
            var cumulativeKm = timelineData[dataYear] || 0;
            if(kmDisplay) {{
                kmDisplay.textContent = parseFloat(cumulativeKm).toFixed(3).replace(/\.?0+$/, '');
            }}
        }});
        
        function filterMapByYear(year) {{
            // Select all highway sections
            var sections = document.querySelectorAll('path.highway-section');
            
            sections.forEach(function(el) {{
                var isVisible = false;
                
                // Find the year class (works for all statuses now)
                var classes = Array.from(el.classList);
                var yearClass = classes.find(c => c.startsWith('section-year-'));
                
                if (yearClass) {{
                    var sectionYear = parseInt(yearClass.replace('section-year-', ''));
                    // Show if completed by this year
                    if (!isNaN(sectionYear) && sectionYear <= year) {{
                        isVisible = true;
                    }}
                }}
                
                // Apply visibility
                if (isVisible) {{
                    el.style.opacity = '1';
                    el.style.strokeOpacity = '1';
                    el.style.pointerEvents = 'auto';
                    el.style.display = 'block';
                }} else {{
                    el.style.opacity = '0';
                    el.style.strokeOpacity = '0';
                    el.style.pointerEvents = 'none';
                }}
            }});
        }}
        
        function resetMapFilter() {{
            var sections = document.querySelectorAll('path.highway-section');
            sections.forEach(function(el) {{
                el.style.opacity = '';
                el.style.strokeOpacity = '';
                el.style.pointerEvents = '';
                el.style.display = '';
            }});
        }}
        
        // Initialize
        kmDisplay.textContent = timelineData[2026] || 0;
    </script>
    """
    m.get_root().html.add_child(folium.Element(timeline_html))
    
    # Add layer control
    
    
    
    # Add last update date footer
    from datetime import datetime
    
    # Romanian month names
    romanian_months = {
        1: 'ianuarie', 2: 'februarie', 3: 'martie', 4: 'aprilie',
        5: 'mai', 6: 'iunie', 7: 'iulie', 8: 'august',
        9: 'septembrie', 10: 'octombrie', 11: 'noiembrie', 12: 'decembrie'
    }
    
    now = datetime.now()
    day = now.day
    month = romanian_months[now.month]
    year = now.year
    last_update = f"{day} {month} {year}"
    
    update_footer_html = f"""
    <div style="position: fixed; bottom: 10px; left: 10px; z-index: 1000; 
                background: var(--bg-overlay, rgba(255,255,255,0.9)); 
                padding: 5px 10px; border-radius: 5px; font-size: 11px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.2);
                color: var(--text-primary, #333);">
        Ultima actualizare: {last_update}
    </div>
    """
    m.get_root().html.add_child(folium.Element(update_footer_html))
    
    # Add layer control
    folium.LayerControl(position='topright').add_to(m)
    
    # Override save method to optimize HTML
    original_save = m.save
    
    def optimized_save(path, **kwargs):
        original_save(path, **kwargs)
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        optimized_content = optimize_template(content)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(optimized_content)
    
    m.save = optimized_save
    
    return m

if __name__ == "__main__":
    # Create the map
    m = create_highways_map()
    
    # Save the map to an HTML file
    m.save('index.html')