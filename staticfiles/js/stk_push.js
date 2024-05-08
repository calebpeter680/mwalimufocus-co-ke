$(document).ready(function() {
    $('#proceedBtn').click(function(event) {
        event.preventDefault();

        var phoneNumber = $('#phonenumber').val().trim();
        var email = $('#email').val().trim();
        var orderTotal = $('#orderTotal').val().trim();
        var orderID = $('#orderID').val().trim();
        var amount = parseFloat(orderTotal);

        console.log('Phone Number:', phoneNumber);
        console.log('Email:', email);
        console.log('Order Amount:', amount);
        console.log('Order ID:', orderID);

        var csrfToken = $('input[name="csrfmiddlewaretoken"]').val();

        $.ajax({
            type: 'POST',
            url: '/trigger_stk_push/',
            headers: {
                'X-CSRFToken': csrfToken 
            },
            data: {
                'phonenumber': phoneNumber,
                'email': email,
                'total_price': amount,
                'order_id': orderID,
            },
            success: function(data) {
                console.log('Success:', data);
            },
            error: function(xhr, status, error) {
                console.error('Error occurred during STK Push:', error);
            }
        });
    });
});
