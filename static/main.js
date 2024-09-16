const placeholderText = ["Search for your perfect dress...", "Find your dream dress..."];
let placeholderIndex = 0;
let charIndex = 0;
const searchBar = document.getElementById('searchBar');

function typePlaceholder() {
    if (charIndex < placeholderText[placeholderIndex].length) {
        searchBar.setAttribute('placeholder', placeholderText[placeholderIndex].substring(0, charIndex + 1));
        charIndex++;
        setTimeout(typePlaceholder, 100);
    } else {
        setTimeout(erasePlaceholder, 3000); // Wait before erasing
    }
}

function erasePlaceholder() {
    if (charIndex > 0) {
        searchBar.setAttribute('placeholder', placeholderText[placeholderIndex].substring(0, charIndex - 1));
        charIndex--;
        setTimeout(erasePlaceholder, 100);
    } else {
        placeholderIndex = (placeholderIndex + 1) % placeholderText.length;
        setTimeout(typePlaceholder, 500);
    }
}

typePlaceholder();

document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector('form');
    const buttonText = document.querySelector('.button-text');
    const loader = document.querySelector('.loader');

    // Reset the state when the page is loaded or navigated back
    buttonText.style.display = 'inline'; // Show "Search" text
    loader.style.display = 'none'; // Hide the loader

    // Handle form submission
    form.addEventListener('submit', function (event) {
        // Immediately hide the text and show the loader
        buttonText.style.display = 'none';
        loader.style.display = 'inline-block';

        // Allow the form to submit after showing the loader
        setTimeout(() => {
            form.submit(); // Submit the form after showing loader
        }, 100); // Small delay to ensure loader is visible before form submission
    });
});

document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector('form');
    const buttonText = document.querySelector('.button-text');
    const loader = document.querySelector('.loader');
    const searchBar = document.querySelector('#searchBar'); // Get the search bar input

    // Reset the button state and clear the search bar on page load
    function resetForm() {
        buttonText.style.display = 'inline'; // Show "Search" text
        loader.style.display = 'none'; // Hide the loader
        searchBar.value = ''; // Clear the search bar input
    }

    resetForm(); // Reset on page load

    // Handle form submission
    form.addEventListener('submit', function () {
        // Hide the button text and show the loader
        buttonText.style.display = 'none';
        loader.style.display = 'inline-block';
    });

    // Detect if the user navigates back and reset the form
    window.addEventListener('pageshow', function (event) {
        if (event.persisted) { // If the page was loaded from cache
            resetForm(); // Reset form on back navigation
        }
    });
});



