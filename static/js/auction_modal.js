$(document).ready(function () {
  // Listen for the modal show event
  $('#auctionModal').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget); // Button that triggered the modal
    var artworkId = button.data('artwork-id'); // Extract the artwork ID from data-* attributes
    var auctionId = button.data('auction-id'); // Extract the auction ID from data-* attributes

    // Load the auction and artwork details using AJAX
    $.ajax({
      url: '/auction_detail/' + artworkId + '/' + auctionId + '/', // Updated URL format
      type: 'GET',
      success: function (data) {
        // Update the modal content
        $('#auction-detail-content').html(data);
      },
      error: function () {
        console.error('Error loading details.');
      },
    });
  });
});