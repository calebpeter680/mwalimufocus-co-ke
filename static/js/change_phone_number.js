$(document).ready(function() {
    $('#phoneNumberChangeBtn').click(function(event) {
        event.preventDefault();  

        $(this).html(`
            <div class="spinner-border spinner-border-sm" role="status">
                <span class="visually-hidden">Updating...</span>
            </div>
            Updating...
        `);

        var newPhoneNumber = document.getElementById('phoneNumberChangeInput').value.trim(); 

        console.log('New Phone Number:', newPhoneNumber);

        if (!newPhoneNumber) {
            alert('Please enter a valid phone number.');
            $('#phoneNumberChangeBtn').html('Update');
            return;
        }

        var dataToSend = {
            'phone_number': newPhoneNumber
        };

        $.ajax({
            type: 'POST',
            url: '/vendors/update_phone_number/',
            data: JSON.stringify(dataToSend),
            contentType: 'application/json', 
            success: function(response) {
                $('.phone-number-change-body').html('<div class="alert alert-dark" role="alert">Phone number updated successfully.</div>');
                setTimeout(function() {
                    window.location.reload();
                }, 1000); 
            },
            error: function(xhr, status, error) {
                $('.phone-number-change-body').html('<div class="alert alert-dark" role="alert">An error occurred. Please try again.</div>');
                setTimeout(function() {
                    window.location.reload();
                }, 1000);
            },
            complete: function() {
                $('#phoneNumberChangeBtn').html('Update');
            }
        });
    });
});
