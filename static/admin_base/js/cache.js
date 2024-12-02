document.addEventListener('DOMContentLoaded', function() {
    // Function to reset all caches and clear storage
    function resetAllCaches() {
        // Clear cached images, CSS & JS files by forcing a reload
        const elements = [...document.getElementsByTagName('img'), ...document.getElementsByTagName('link'), ...document.getElementsByTagName('script')];

        elements.forEach((element) => {
            // For resetting image sources
            if (element.tagName === 'IMG') {
                const oldSrc = element.src;
                element.src = ''; // Clear the old image
                element.src = `${oldSrc}?v=${new Date().getTime()}`; // Append a timestamp
            }

            // CSS & JS Cache Busting Diabled For Now
            // // For resetting CSS files (link elements with rel="stylesheet")
            // if (element.tagName === 'LINK' && element.rel === 'stylesheet') {
            //     const oldHref = element.href;
            //     element.href = ''; // Clear the old stylesheet
            //     element.href = `${oldHref}?v=${new Date().getTime()}`; // Append a timestamp
            // }

            // // For resetting JavaScript files (script elements)
            // if (element.tagName === 'SCRIPT' && element.src) {
            //     const oldSrc = element.src;
            //     element.src = ''; // Clear the old script
            //     element.src = `${oldSrc}?v=${new Date().getTime()}`; // Append a timestamp
            // }
        });

        // Optionally, reload the page to ensure fresh loading of all assets
        

        // Clear local storage (DISABLED FOR LIVE TOASTS)
        // localStorage.clear();
        // console.log('Local storage cleared.');

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
            // Set the cache reset flag to prevent repeated reloads

            // Clear all cache data
            resetAllCaches();

            // Reload the page to apply the changes and bypass cache
            setTimeout(function() {
                if (!localStorage.getItem('cache_reset_done')) {
                    location.reload(true);
                }
            }, 1000); // Short delay to ensure caches are cleared

            localStorage.setItem('cache_reset_done', 'true');

            // Clean up the URL by removing the 'cache_reset' parameter if cache reset is done
            cleanUpUrl();

            window.location.reload(true);
        }
    }

    // Remove 'cache_reset=true' parameter from the URL after cache reset
    function cleanUpUrl() {
        if (localStorage.getItem('cache_reset_done')) {
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

});