if ( window.history.replaceState ) {
    window.history.replaceState( null, null, window.location.href );
  }

// Toggle eye show in login form
document.addEventListener("DOMContentLoaded", function () {
    const togglePassword = document.getElementById('togglePassword_icon');
    const password = document.getElementById('password_floatingInput');


    if (password && togglePassword) {
        togglePassword.addEventListener('click', function () {
            // Toggle the type attribute
            const type = password.getAttribute('type') === 'password' ? 'text' : 'password';
            password.setAttribute('type', type);
    
            // Toggle the eye / eye slash icon
            this.classList.toggle('bi-eye');
            this.classList.toggle('bi-eye-slash');
        });
    }
    
});

// Form formating, allow reloads & prevent auto submission
document.getElementById('backend-form').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent the default form submission
    
    // Perform form submission using Fetch API or XMLHttpRequest if needed
    fetch(this.action, {
        method: this.method,
        body: new FormData(this)
    }).then(response => {
        // Optionally handle response here
        window.location.reload(); // Refresh the page
    }).catch(error => {
        // Optionally handle errors here
        console.error('Error:', error);
    });
});

// Toggle icon changing based on clicking side menue field for content field (FOR COMMENTED TOGGLE ITEM IN ADMIN_BASE TEMPLATE)
// document.getElementById('content_toggle_button').addEventListener('click', function() {
//     const icon = document.getElementById('toggleFieldIconCollapse');
//     // Check the current icon and toggle it

//     icon.classList.toggle('rotate');
//     this.classList.toggle("active");
// });

// FIX localStorage adding active class for dynamic classes}
document.addEventListener("DOMContentLoaded", function() {
    // Get the home button
    const homeButton = document.getElementById('homeButton');

    // Function to remove active class from all buttons
    function removeActiveClass() {
        const activeLinks = document.querySelectorAll('.nav_button.active');
        activeLinks.forEach(link => {
            link.classList.remove('active');
        });
    }

    // Function to set active class and redirect
    function setActiveAndRedirect(button, url) {
        button.addEventListener('click', function(e) {
            e.preventDefault(); // Prevent default anchor behavior
            removeActiveClass(); // Remove active class from all links
            button.classList.add('active'); // Add active class to the clicked button
            localStorage.setItem('activeButton', button.id); // Save active button ID to local storage
            window.location.href = url; // Redirect to the specified URL
        });
    }

    // Set up the home button
    if (homeButton) {
        setActiveAndRedirect(homeButton, '/admin'); // Redirect to '/admin' when clicked
    }

    // Check local storage for active button and set it
    const activeButtonId = localStorage.getItem('activeButton');
    if (activeButtonId) {
        const activeButton = document.getElementById(activeButtonId);
        if (activeButton) {
            removeActiveClass(); // Remove active class from all links
            activeButton.classList.add('active'); // Set the active class to the stored button
        }
    }
});




