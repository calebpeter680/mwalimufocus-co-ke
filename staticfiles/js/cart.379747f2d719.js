$(document).ready(function() {
    updateCartBadge();

    $('.add-to-cart-form').submit(function(e) {
        e.preventDefault();

        var form = $(this);
        var itemID = form.find('input[name="item_id"]').val();
        var csrftoken = form.find('input[name="csrfmiddlewaretoken"]').val();
        var addToCartButton = form.find('button[type="submit"]');

        if (addToCartButton.text().trim() === "Add to Cart") {
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
                    if (response.message === "Item added to cart successfully.") {
                        addToCartButton.text("Remove from Cart");
                        addToCartButton.removeClass("btn-outline-dark").addClass("btn-outline-danger");

                        playNotificationSound();
                        flashCartBadge();
                        updateCartBadge();
                        toggleCartSection();
                    }
                },
                error: function(xhr, errmsg, err) {
                    console.log(xhr.status + ": " + xhr.responseText);
                }
            });
        }
    });

    function updateCartBadge() {
        $.ajax({
            type: 'GET',
            url: '/get_cart_items/',
            success: function(data) {
                var numCartItems = data.num_items;
                $('.custom-cart-badge').text(numCartItems);
                toggleCartSection(); 
            },
            error: function(xhr, errmsg, err) {
                console.log(xhr.status + ": " + xhr.responseText);
            }
        });
    }

    function playNotificationSound() {
        var audio = new Audio('/static/audio/add_to_cart_notification.mp3');
        audio.play();
    }

    function flashCartBadge() {
        var badge = $('.custom-cart-badge');
        badge.addClass('text-bg-danger');

        setTimeout(function() {
            badge.removeClass('text-bg-danger');
        }, 1000); 
    }

    function toggleCartSection() {
        var numCartItems = parseInt($('.custom-cart-badge').text());
        var cartSection = $('.add-to-cart');

        if (numCartItems > 0) {
            cartSection.show();
        } else {
            cartSection.hide();
        }
    }
});




$(document).ready(function() {
    updateCartBadge();

    $('.add-to-cart-form').submit(function(e) {
        e.preventDefault();

        var form = $(this);
        var itemID = form.find('input[name="item_id"]').val();
        var addToCartButton = form.find('button[type="submit"]');

        if (addToCartButton.text().trim() === "Remove from Cart") {
            $.ajax({
                type: 'POST',
                url: '/remove_from_cart/' + itemID + '/',
                data: {
                    'item_id': itemID,
                },
                headers: {
                    'X-CSRFToken': getCsrfToken()
                },
                success: function(response) {
                    if (response.message === "Item removed from cart successfully.") {
                        addToCartButton.text("Add to Cart");
                        addToCartButton.removeClass("btn-outline-danger").addClass("btn-outline-dark");

                        updateCartBadge();
                        toggleCartSection();
                    }
                },
                error: function(xhr, errmsg, err) {
                    console.log(xhr.status + ": " + xhr.responseText);
                }
            });
        }
    });

    function getCsrfToken() {
        return $('input[name="csrfmiddlewaretoken"]').val();
    }

    function updateCartBadge() {
        $.ajax({
            type: 'GET',
            url: '/get_cart_items/',
            success: function(data) {
                var numCartItems = data.num_items;
                $('.custom-cart-badge').text(numCartItems);
                toggleCartSection(); 
            },
            error: function(xhr, errmsg, err) {
                console.log(xhr.status + ": " + xhr.responseText);
            }
        });
    }

    function toggleCartSection() {
        var numCartItems = parseInt($('.custom-cart-badge').text());
        var cartSection = $('.add-to-cart');

        if (numCartItems > 0) {
            cartSection.show();
        } else {
            cartSection.hide();
        }
    }
});

