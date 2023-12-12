$(document).ready(function () {
  // Listen for the modal show event
  $('#auctionModal').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget); // Button that triggered the modal
    var artworkId = button.data('artwork-id'); // Extract the artwork ID from data-* attributes

    // Load the auction details using AJAX
    $.ajax({
      url: '/get_auction_detail/' + artworkId + '/', // Replace with Ir Django URL
      type: 'GET',
      success: function (data) {
        // Update the modal content with the retrieved auction details
        $('#auction-detail-content').html(data);
      },
      error: function () {
        console.error('Error loading auction details.');
      },
    });
  });
});