document.addEventListener('DOMContentLoaded', function() {
    const updateButtons = document.querySelectorAll('[id^="updateShopItemBtn"]');
    
    updateButtons.forEach(updateButton => {
        updateButton.addEventListener('click', function(event) {
            event.preventDefault();

            updateButton.innerHTML = `
                <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                Updating...
            `;

            const modalId = updateButton.dataset.itemid;
            const modal = document.querySelector(`#updateShopItem${modalId}`);
            const modalBody = modal.querySelector('.update-shop-item-modal');

            const title = modal.querySelector('#titleInput_update').value;
            const category = modal.querySelector('#categoryInput_update').value;
            const educationLevel = modal.querySelector('#educationLevelInput_update').value;
            const subject = modal.querySelector('#subjectInput_update').value;
            const description = modal.querySelector('#descriptionInput_update').value;
            const oldPrice = modal.querySelector('#oldPriceInput_update').value;
            const newPrice = modal.querySelector('#newPriceInput_update').value;
            const itemId = modal.querySelector('#itemID').value;

            const requestData = {
                item_id: itemId,
                title: title,
                category: category,
                education_level: educationLevel,
                subject: subject,
                description: description,
                old_price: oldPrice,
                new_price: newPrice
            };

            const csrfToken = modal.querySelector('input[name="csrfmiddlewaretoken"]').value;

            fetch('/vendors/update-shop-item/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify(requestData)
            })
            .then(response => response.json())
            .then(data => {
                // Handle the response
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
            });
        });
    });
});






document.addEventListener('DOMContentLoaded', function() {
    const updateButtons = document.querySelectorAll('[data-bs-target^="#updateShopItem"]');

    updateButtons.forEach(updateButton => {
        updateButton.addEventListener('click', function(event) {
            event.preventDefault();
            const itemID = updateButton.dataset.itemid;
            
            fetch(`/vendors/api/get-product-details/${itemID}/`)
                .then(response => response.json())
                .then(data => {
                    const modal = document.querySelector(updateButton.dataset.bsTarget);
                    
                    modal.querySelector('#titleInput_update').value = data.title;
                    modal.querySelector('#categoryInput_update').value = data.category_id;
                    modal.querySelector('#educationLevelInput_update').value = data.education_level_id;
                    modal.querySelector('#subjectInput_update').value = data.subject_id;
                    modal.querySelector('#descriptionInput_update').value = data.description;
                    modal.querySelector('#oldPriceInput_update').value = data.old_price;
                    modal.querySelector('#newPriceInput_update').value = data.new_price;
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        });
    });
});





