document.addEventListener('DOMContentLoaded', function() {
    const loginBtn = document.getElementById('loginBtn');

    if (loginBtn) {
        loginBtn.addEventListener('click', function(event) {
            event.preventDefault(); 

            loginBtn.innerHTML = `
                <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                Logging In...
            `;

            const email = document.getElementById('InputEmail2').value;
            const password = document.getElementById('InputPassword2').value;


            const formData = {
                email: email,
                password: password
            };

            const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;


            fetch('/accounts/login/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify(formData)
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                console.log(data);
                const modalBody = document.querySelector('.login-modal');

                if (data.success) {
                    modalBody.innerHTML = `
                        <div class="alert alert-success" role="alert">
                            <i class="bi bi-check-circle-fill"></i> ${data.success}
                        </div>`;
                    setTimeout(() => {
                        window.location.href = '/accounts/dashboard/';
                    }, 2000);
                } else {
                    modalBody.innerHTML = `
                        <div class="alert alert-danger" role="alert">
                            <i class="bi bi-exclamation-triangle-fill"></i> ${data.error}
                        </div>`;
                    console.error('Login failed:', data.error);
                    setTimeout(() => {
                        window.location.reload();
                    }, 2000);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                setTimeout(() => {
                    window.location.reload();
                }, 2000);
            });
        });
    }
});
