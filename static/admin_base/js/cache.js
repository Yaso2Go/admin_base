document.addEventListener('DOMContentLoaded', function() {
    // Function to reset all caches and clear storage
    function resetAllCaches() {
        console.log('Resetting all caches...');
        
        // Clear cached images, CSS & JS files by forcing a reload
        const elements = [...document.getElementsByTagName('img'), ...document.getElementsByTagName('link'), ...document.getElementsByTagName('script')];

        elements.forEach((element) => {
            // For resetting image sources
            if (element.tagName === 'IMG') {
                const oldSrc = element.src.split('?')[0]; // Remove any existing query parameters
                element.src = ''; // Clear the old image
                element.src = `${oldSrc}?v=${new Date().getTime()}`; // Append a single timestamp
            }
        });

        // Clear session storage
        sessionStorage.clear();
        console.log('Session storage cleared.');

        // Clear service worker caches
        if ('caches' in window) {
            caches.keys().then(function(cacheNames) {
                cacheNames.forEach(function(cacheName) {
                    caches.delete(cacheName).then(function() {
                        console.log(`Cache ${cacheName} deleted.`);
                    });
                });
            });
        }
        console.log('Cache storage cleared.');

        // Unregister all service workers
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.getRegistrations().then(function(registrations) {
                registrations.forEach(function(registration) {
                    registration.unregister().then(function() {
                        console.log('Service worker unregistered.');
                    });
                });
            });
        }
        console.log('Service workers unregistered.');
    }

    // Function to check for cache_reset parameter and reload if needed
    function checkCacheReset() {
        const urlParams = new URLSearchParams(window.location.search);

        // Only proceed if 'cache_reset=true' is in the URL and we haven't already reloaded
        if (urlParams.has('cache_reset') && urlParams.get('cache_reset') === 'true') {
            console.log('Cache reset parameter found in URL.');

            // Clear all cache data
            resetAllCaches();

            console.log(localStorage.getItem('cache_reset_done'))

            // Force reload the page to apply the changes and bypass cache
            if (localStorage.getItem('cache_reset_done') === "false" || localStorage.getItem('cache_reset_done') === null) {
                localStorage.setItem('cache_reset_done', 'true');
                console.log('Reloading page to apply cache reset.');
                window.location.reload(true); // Force reload the page
            }
        }
    }

    // Remove 'cache_reset=true' parameter from the URL after cache reset
    function cleanUpUrl() {
        if (localStorage.getItem('cache_reset_done') === 'true') {
            console.log('Cleaning up URL after cache reset.');
            const urlParams = new URLSearchParams(window.location.search);
            urlParams.delete('cache_reset');  // Remove the cache_reset parameter

            // Redirect the page to the same URL without the 'cache_reset' parameter
            const newUrl = window.location.pathname + (urlParams.toString() ? '?' + urlParams.toString() : '');
            history.replaceState(null, '', newUrl);  // Update the URL without reloading the page

            // Reset cache reset status in localStorage
            localStorage.setItem('cache_reset_done', 'false');
        }
    }

    // Check immediately if the page was loaded with the cache_reset parameter
    checkCacheReset();

    // Clean up the URL after cache reset
    window.addEventListener('load', cleanUpUrl);
});




// // For resetting CSS files (link elements with rel="stylesheet")
// if (element.tagName === 'LINK' && element.rel === 'stylesheet') {
//     const oldHref = element.href.split('?')[0]; // Remove any existing query parameters
//     element.href = ''; // Clear the old stylesheet
//     element.href = `${oldHref}?v=${new Date().getTime()}`; // Append a single timestamp
// }

// // For resetting JavaScript files (script elements)
// if (element.tagName === 'SCRIPT' && element.src) {
//     const oldSrc = element.src.split('?')[0]; // Remove any existing query parameters
//     element.src = ''; // Clear the old script
//     element.src = `${oldSrc}?v=${new Date().getTime()}`; // Append a single timestamp
// }