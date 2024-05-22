document.addEventListener('DOMContentLoaded', function() {
    const addShopItemBtn = document.getElementById('addShopItemBtn');
    
    addShopItemBtn.addEventListener('click', function(event) {
        event.preventDefault();

        // Ensure TinyMCE content is saved to the textarea
        if (tinymce.get('descriptionInput')) {
            tinymce.get('descriptionInput').save();
        }

        const descriptionContent = document.getElementById('descriptionInput').value;
        console.log('Description Content:', descriptionContent);  // Debug log

        addShopItemBtn.innerHTML = `
            <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
            Adding...
        `;

        const addShopItemForm = document.getElementById('addShopItemForm');
        const formData = new FormData(addShopItemForm);
        const csrfToken = formData.get('csrfmiddlewaretoken');

        fetch('/vendors/add-shop-item/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': csrfToken
            }
        }).then(response => response.json()).then(data => {
            const modalBody = document.querySelector('.add-shop-item-modal');
            if (data.status === 'success') {
                modalBody.innerHTML = `
                    <div class="alert alert-success" role="alert">
                        ${data.message}
                    </div>
                `;
                setTimeout(function() {
                    window.location.reload();
                }, 2000);
            } else {
                modalBody.innerHTML = `
                    <div class="alert alert-danger" role="alert">
                        ${data.message}
                    </div>
                `;
                setTimeout(function() {
                    window.location.reload();
                }, 4000);
            }
        }).catch(error => {
            console.error('Error:', error);
            alert('An error occurred. Please try again.');
        });
    });
});
