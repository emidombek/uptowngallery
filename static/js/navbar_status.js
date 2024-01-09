/**
 This script dynamically updates the navigation bar to highlight the active link
 based on the current page URL. It runs on document ready and performs the following actions:

 Defines the `updateActiveNav` function to manage the active state of navigation links.
 It first removes the 'active' class from all navigation links.

 Then, it compares each navigation link's href attribute with the current window location.
 If a match is found, it adds the 'active' class to that link, highlighting it as active.
 
 Invokes the `updateActiveNav` function immediately to set the correct active link when the page loads.
 Binds the `updateActiveNav` function to the window's 'popstate' event.
 This ensures that the active link is updated correctly when navigating through browser history (back/forward buttons).
 */
$(document).ready(function () {
  function updateActiveNav() {
    $('.nav-item .nav-link').removeClass('active');
    let currentPath = window.location.pathname;
    $('.nav-item .nav-link').each(function () {
      if ($(this).attr('href') === currentPath) {
        $(this).addClass('active');
      }
    });
  }
  updateActiveNav();

  $(window).on('popstate', function () {
    updateActiveNav();
  });
});