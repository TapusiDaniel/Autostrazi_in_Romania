document.addEventListener('DOMContentLoaded', function() {
    var mapButtons = document.querySelectorAll('.map-button[data-map]');
    var overlays = document.querySelector('.leaflet-control-layers-overlays');
    var minimizeButton = document.querySelector('.minimize-button');
    var mapControls = document.querySelector('.map-controls');
    
    if(overlays) {
        overlays.style.display = 'none';
    }
    
    if (minimizeButton && mapControls) {
        minimizeButton.addEventListener('click', function() {
            mapControls.classList.toggle('minimized');
            minimizeButton.textContent = mapControls.classList.contains('minimized') ? '+' : '−';
        });
    }

    var labels = document.querySelectorAll('.city-label');
    
    function updateMapStyle(activeButton, skipButtonUpdate = false) {
        if (!skipButtonUpdate) {
            mapButtons.forEach(button => button.classList.remove('active'));
            activeButton.classList.add('active');
        }
        
        var mapStyle = activeButton.getAttribute('data-map');
        
        // Only hide the white background element, not all overlay paths
        document.querySelectorAll('.leaflet-overlay-pane .romania-outline, .leaflet-overlay-pane .white-background').forEach(function(element) {
            element.style.display = mapStyle === 'white' ? 'block' : 'none';
        });
        
        if (!skipButtonUpdate) {
            // Find and click the correct base layer radio button
            var baseLayerName = {
                'white': 'White Map',
                'osm': 'OpenStreetMap',
                'satellite': 'Satellite'
            }[mapStyle];
            
            var baseInput = Array.from(document.querySelectorAll('.leaflet-control-layers-base input'))
                .find(input => input.nextElementSibling.textContent.trim() === baseLayerName);
            if (baseInput) baseInput.click();
        }
        
        var isWhiteMap = mapStyle === 'white';
        var isSatellite = mapStyle === 'satellite';
        
        // Add/remove satellite-view class on body for CSS targeting
        if (isSatellite) {
            document.body.classList.add('satellite-view');
        } else {
            document.body.classList.remove('satellite-view');
        }
        
        // Update labels (custom city labels only on the White Map)
        labels.forEach(function(label) {
            label.style.display = isWhiteMap ? 'block' : 'none';
        });
        
        // Update city boundaries
        document.querySelectorAll('.city-boundary').forEach(function(element) {
            element.style.display = isWhiteMap ? 'block' : 'none';
            element.style.visibility = isWhiteMap ? 'visible' : 'hidden';
        });
        
    }
    
    // Event listeners for map buttons
    mapButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            updateMapStyle(this);
        });
    });
    
    // Initial setup - set white map as default
    var whiteMapButton = document.querySelector('.map-button[data-map="white"]');
    if (whiteMapButton) {
        updateMapStyle(whiteMapButton);
    }
});
