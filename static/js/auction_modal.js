$(function () {
  // Listen for the modal show event
  $('#auctionModal').on('show.bs.modal', function (event) {
    let button = $(event.relatedTarget); // Button that triggered the modal
    let artworkId = button.data('artwork-id'); // Extract the artwork ID from data-* attributes
    let auctionId = button.data('auction-id'); // Extract the auction ID from data-* attributes

    // Load the auction and artwork details using AJAX
    $.ajax({
      url: '/auction_detail/' + artworkId + '/' + auctionId + '/',
      type: 'GET',
      success: function (data) {
        // Update the modal content
        $('#auction-detail-content').html(data);
      },
      error: function (jqXHR, textStatus, errorThrown) {
        console.error('AJAX error: ' + textStatus + ' : ' + errorThrown);
        $('#auction-detail-content').html('<p>An error occurred while loading the details. Please try again later.</p>');
      },
    });
  });
});