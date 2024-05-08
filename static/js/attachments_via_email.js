document.addEventListener('DOMContentLoaded', function() {
    function sendEmailWithAttachments(orderId) {
        const csrftoken = getCookie('csrftoken');

        $.ajax({
            type: 'POST', 
            url: `/send_attachment_via_email/${orderId}/`,  
            dataType: 'json',  
            beforeSend: function(xhr) {
                xhr.setRequestHeader('X-CSRFToken', csrftoken); 
            },
            success: function(response) {
                if (response.success) {
                    
                } else {
                    
                }
            },
            error: function(xhr, textStatus, errorThrown) {
                
            }
        });
    }

    const orderIdInput = document.getElementById('order-id');
    if (orderIdInput) {
        const orderId = orderIdInput.value;

        sendEmailWithAttachments(orderId);
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
