document.addEventListener('DOMContentLoaded', function() {
    const deleteButtons = document.querySelectorAll('[id^="productDeleteConfirm"]');
    
    deleteButtons.forEach(deleteButton => {
        deleteButton.addEventListener('click', function(event) {
            event.preventDefault();

            deleteButton.innerHTML = `
                <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                Deleting...
            `;
    
            const itemID = deleteButton.dataset.itemid; 
    
            const csrftoken = getCookie('csrftoken');

            fetch(`/vendors/delete-item/${itemID}/`, {
                method: 'POST',  
                headers: {
                    'X-CSRFToken': csrftoken,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ item_id: itemID })  
            })
            .then(response => response.json())
            .then(data => {
                const modalBody = deleteButton.closest('.modal-content').querySelector('.delete-product-modal-body');
    
                if (data.status === 'success') {
                    modalBody.innerHTML = `
                        <div class="alert alert-success" role="alert">
                            ${data.message}
                        </div>
                    `;
                } else {
                    modalBody.innerHTML = `
                        <div class="alert alert-danger" role="alert">
                            ${data.message}
                        </div>
                    `;
                }
                setTimeout(function() {
                    window.location.reload();
                }, 500);
            })
            .catch(error => {
                console.error('Error:', error);
                const modalBody = deleteButton.closest('.modal-content').querySelector('.delete-product-modal-body');
                modalBody.innerHTML = `
                    <div class="alert alert-danger" role="alert">
                        An error occurred. Please try again.
                    </div>
                `;

                setTimeout(function() {
                    window.location.reload();
                }, 500);
            });
        });
    });

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
