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
                updatePaymentStatusModal();
            },
            error: function(xhr, status, error) {
                console.error('Error occurred during STK Push:', error);
            }
        });
    });

    function updatePaymentStatusModal() {
        $.ajax({
            type: 'GET',
            url: '/payment-status/', 
            success: function(data) {
                console.log('Payment Status Data:', data);

                var state = data.state;
                var payment_status = '';
                var message = '';
                var iconHTML = '';

                if (state === 'PENDING') {
                    payment_status = 'Payment Has Started...';
                    message = 'A Prompt Has Been Sent to Your Phone to Enter Your Mpesa PIN to Complete this Transaction.';
                    iconHTML = '<div class="spinner-border ms-auto" role="status" aria-hidden="true"></div>';
                } else if (state === 'PROCESSING') {
                    payment_status = 'Payment Is Processing...';
                    message = 'Once you authorize by entering your PIN, we will redirect you to the download page and send the purchased items to your email.';
                    iconHTML = '<div class="spinner-border ms-auto" role="status" aria-hidden="true"></div>';
                } else if (state === 'RETRY') {
                    payment_status = 'Payment Failed...';
                    message = 'The payment failed. We are retrying the transaction. You can refresh the page and initiate another transaction since we have not deducted any amount.';
                    iconHTML = '<div class="ms-auto"><i class="bi bi-exclamation-triangle ms-2"></i></div>';
                    setTimeout(function() {
                        window.location.reload();
                    }, 5000);
                } else if (state === 'COMPLETE') {
                    payment_status = 'Payment Successful...';
                    message = 'Thank you. The payment has been received successfully. We\'re now redirecting you to the downloads page in less than 2 seconds...';
                    iconHTML = '<div class="ms-auto"><i class="bi bi-check-circle ms-2" style="font-size: 34px;"></i></div>';
                    setTimeout(function() {
                        window.location.href = '/session-order-detail/';
                    }, 500);
                } else if (state === 'FAILED') {
                    payment_status = 'Payment Failed...';
                    message = 'The Payment has failed. Please try again and ensure you enter your Mpesa PIN correctly and you have sufficient balance for this transaction, including transaction charges. If the problem persists, contact support.';
                    iconHTML = '<div class="ms-auto"><i class="bi bi-exclamation-triangle" style="font-size: 34px;"></i></div>';
                    setTimeout(function() {
                        window.location.reload();
                    }, 5000);
                }

                $('#paymentStatusMessage').text(message);
                $('.modal-payment-status-header .modal-title').text(payment_status);
                $('.modal-payment-status-header .spinner-border').replaceWith(iconHTML);

                setTimeout(updatePaymentStatusModal, 1000); 
            },
            error: function(xhr, status, error) {
                console.error('Error occurred while fetching payment status:', error);
                
                $('#paymentStatusMessage').text('An error occurred while processing the payment. Confirm if your phone number is correct or contact support if the problem persists!');
                $('.modal-payment-status-header .modal-title').text('Payment Failed');
                
                setTimeout(function() {
                    window.location.reload();
                }, 5000);
            }
        });
    }
});

