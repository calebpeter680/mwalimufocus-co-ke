function removeCartItem(itemId) {
    $.ajax({
        type: 'POST',
        url: '/remove_from_cart_at_checkout/', 
        data: {
            'item_id': itemId,
            'csrfmiddlewaretoken': getCSRFToken(), 
        },
        success: function(data) {
            if (data.success) {
                location.reload();
            } else {
                console.error('Failed to remove item from cart.');
            }
        },
        error: function(xhr, status, error) {
            console.error('Error occurred during item removal:', error);
        }
    });
}

function getCSRFToken() {
    return $('input[name="csrfmiddlewaretoken"]').val();
}

$(document).ready(function() {
    $(document).on('click', '.bi-trash-fill', function() {
        const itemId = $(this).closest('tr').attr('id').replace('item-', '');
        removeCartItem(itemId);
    });

    $(document).on('click', '.bi-arrow-counterclockwise', function() {
        const itemId = $(this).closest('tr').attr('id').replace('item-', '');
        restoreCartItem(itemId);
    });
});
