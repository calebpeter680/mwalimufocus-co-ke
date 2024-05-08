document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('changeNewPasswordBtn').addEventListener('click', function (event) {
        event.preventDefault();

        var currentPassword = document.getElementById('changeCurrentPasswordInput').value;
        var newPassword = document.getElementById('changeNewPasswordInput').value;

        var csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

        var button = document.getElementById('changeNewPasswordBtn');
        button.innerHTML = `
                <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                Changing...
            `;

        fetch('/vendors/change-password/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                current_password: currentPassword,
                new_password: newPassword
            })
        })
        .then(response => response.json())
        .then(data => {
            var alertDiv = document.createElement('div');
            alertDiv.className = 'alert alert-dark mt-2';
            alertDiv.role = 'alert';
            alertDiv.textContent = data.message;
            document.querySelector('.change-password-div-body').innerHTML = '';
            document.querySelector('.change-password-div-body').appendChild(alertDiv);

            setTimeout(function () {
                window.location.href = '/';
            }, 2000);
        });
    });
});
