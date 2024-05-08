$(document).ready(function() {
    $('#add-to-cart').click(function(e) {
        e.preventDefault();

        var itemID = $(this).val();

        function getCookie(name) {
            var cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                var cookies = document.cookie.split(';');
                for (var i = 0; i < cookies.length; i++) {
                    var cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
        
        var csrftoken = getCookie('csrftoken');

        $.ajax({
            type: 'POST',
            url: '/add_to_cart/',  
            data: {
                'item_id': itemID,
            },
            headers: {
                'X-CSRFToken': csrftoken  
            },
            success: function(response) {
                alert(response.message);
            },
            error: function(xhr, errmsg, err) {
                console.log(xhr.status + ": " + xhr.responseText);
            }
        });
    });
});
