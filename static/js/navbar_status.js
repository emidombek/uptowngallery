$(document).ready(function () {
  // Function to update the active class on the current page's nav link
  function updateActiveNav() {
    // Remove 'active' class from all nav links
    $('.nav-item .nav-link').removeClass('active');

    // Get current page URL path
    var currentPath = window.location.pathname;

    // Add 'active' class to the nav link that corresponds to the current page
    $('.nav-item .nav-link').each(function () {
      if ($(this).attr('href') === currentPath) {
        $(this).addClass('active');
      }
    });
  }

  // Run the function on page load
  updateActiveNav();

  $(window).on('popstate', function () {
    updateActiveNav();
  });
});