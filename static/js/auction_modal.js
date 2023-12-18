console.log('Script loaded');

$(function () {
  console.log('Modal script loaded');

  $('#auctionModal').on('show.bs.modal', function (event) {
    console.log('Modal event triggered');

    let button = $(event.relatedTarget);
    let artworkId = button.data('artwork-id');
    let auctionId = button.data('auction-id');

    console.log('Artwork ID:', artworkId, 'Auction ID:', auctionId);

    $.ajax({
      url: '/auction_detail/' + artworkId + '/' + auctionId + '/',
      type: 'GET',
      success: function (data) {
        // Update the modal content
        $('#auction-detail-content').html(data);

        // Extract the title from the loaded content and set it as the modal title
        var title = $('#auction-detail-content').find('h1').first().text();
        $('#auctionModalLabel').text(title);
      },
      error: function (jqXHR, textStatus, errorThrown) {
        console.error('AJAX error:', textStatus, errorThrown);
        $('#auction-detail-content').html('<p>An error occurred while loading the details. Please try again later.</p>');
      }
    });
  });
});