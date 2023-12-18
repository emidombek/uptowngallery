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
        console.log("AJAX Response:", data);
        $('#auction-detail-content').html(data);
      },
      error: function (jqXHR, textStatus, errorThrown) {
        console.error('AJAX error:', textStatus, errorThrown);
      }
    });
  });
});