document.addEventListener('DOMContentLoaded', function() {
    var sectionButtons = document.querySelectorAll('.section-button');

    function isWhiteMapActive() {
        var checkedBaseLayer = document.querySelector(
            '.leaflet-control-layers-base input[type="radio"]:checked'
        );
        if (checkedBaseLayer && checkedBaseLayer.nextElementSibling) {
            return checkedBaseLayer.nextElementSibling.textContent.trim() === 'White Map';
        }

        var activeMapButton = document.querySelector('.map-button.active');
        return activeMapButton && activeMapButton.getAttribute('data-map') === 'white';
    }

    function selectSection(button) {
        // Toggle active class instead of removing from all
        button.classList.toggle('active');
        
        // Get all currently active sections
        var activeSections = Array.from(document.querySelectorAll('.section-button.active'))
            .map(btn => btn.getAttribute('data-section'));
        
        var isWhiteMap = isWhiteMapActive();
        
        // Handle the "all" section specially
        if (button.getAttribute('data-section') === 'all') {
            // If "all" was clicked, deactivate other sections
            sectionButtons.forEach(btn => {
                if (btn.getAttribute('data-section') !== 'all') {
                    btn.classList.remove('active');
                }
            });
            activeSections = ['all'];
        } else {
            // If a specific section was clicked, deactivate "all"
            var allButton = document.querySelector('.section-button[data-section="all"]');
            if (allButton) {
                allButton.classList.remove('active');
            }
            // Remove 'all' from activeSections if it exists
            activeSections = activeSections.filter(section => section !== 'all');
        }
        
        // If no sections are active, activate "all"
        if (activeSections.length === 0) {
            var allButton = document.querySelector('.section-button[data-section="all"]');
            if (allButton) {
                allButton.classList.add('active');
                activeSections = ['all'];
            }
        }
        
        // Update overlay visibility based on active sections
        var overlayInputs = document.querySelectorAll('.leaflet-control-layers-overlays input[type="checkbox"]');
        overlayInputs.forEach(function(input) {
            var label = input.nextElementSibling.textContent.trim();
            
            // Skip internal overlays (outline '_', '_logos', '_delimiters_*').
            // These are managed by their own sync logic, not the status filter.
            if (label.charAt(0) === '_') {
                return;
            }

            // Handle highway sections
            if (activeSections.includes('all')) {
                if (!input.checked) input.click();
            } else if (activeSections.includes(label)) {
                if (!input.checked) input.click();
            } else {
                if (input.checked) input.click();
            }
        });

        // For white map, ensure all elements remain visible
        if (isWhiteMap) {
            // Ensure Romania outline and white background are visible
            document.querySelectorAll('.leaflet-overlay-pane .romania-outline, .leaflet-overlay-pane .white-background').forEach(function(element) {
                element.style.display = 'block';
            });
            
            // Explicitly ensure city boundaries are visible
            document.querySelectorAll('.city-boundary').forEach(function(element) {
                element.style.display = 'block';
                element.style.visibility = 'visible';
                element.style.opacity = 0.99;
                setTimeout(() => {
                    element.style.opacity = 1;
                }, 10);
            });
            
            // Ensure labels are visible
            document.querySelectorAll('.city-label').forEach(function(label) {
                label.style.display = 'block';
            });
            
        }
    }
    
    // Event listeners for section buttons
    sectionButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            selectSection(this);
        });
    });
    
    // Show all sections initially
    var allButton = document.querySelector('.section-button[data-section="all"]');
    if (allButton) {
        selectSection(allButton);
    }
});
