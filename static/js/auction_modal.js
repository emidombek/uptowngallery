/* Initializes a modal popup for auction details. When the modal is triggered, it performs an AJAX request 
to fetch and display details about a specific auction. The auction's ID and artwork's ID are extracted from
the button that triggered the modal. It then updates the modal content with the fetched data and sets
the modal title. In case of an AJAX error, it displays an error message within the modal.*/
$(function () {
  $('#auctionModal').on('show.bs.modal', function (event) {
    let button = $(event.relatedTarget);
    let artworkId = button.data('artwork-id');
    let auctionId = button.data('auction-id');
    $.ajax({
      url: '/auction_detail/' + artworkId + '/' + auctionId + '/',
      type: 'GET',
      success: function (data) {
        $('#auction-detail-content').html(data);
        let title = $('#auction-detail-content').find('h1').first().text();
        $('#auctionModalLabel').text(title);
      },
      error: function (jqXHR, textStatus, errorThrown) {
        console.error('AJAX error:', textStatus, errorThrown);
        $('#auction-detail-content').html('<p>An error occurred while loading the details. Please try again later.</p>');
      }
    });
  });
});