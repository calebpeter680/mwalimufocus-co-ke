(() => {
  'use strict';

  const forms = document.querySelectorAll('.needs-validation');

  Array.from(forms).forEach(form => {
    form.addEventListener('submit', event => {
      const instructionsCheckboxes = form.querySelectorAll('#instructions-container input[type="checkbox"]');
      const isAnyInstructionsChecked = Array.from(instructionsCheckboxes).some(checkbox => checkbox.checked);

      if (!isAnyInstructionsChecked) {
        event.preventDefault();
        event.stopPropagation();

        form.querySelector('#instructions-container').classList.add('is-invalid');
        form.querySelector('#instructions-container .invalid-feedback').style.display = 'block';
      } else {
        form.querySelector('#instructions-container').classList.remove('is-invalid');
        form.querySelector('#instructions-container .invalid-feedback').style.display = 'none';
      }

      form.classList.add('was-validated');
    }, false);

    form.querySelectorAll('#instructions-container input[type="checkbox"]').forEach(checkbox => {
      checkbox.addEventListener('change', () => {
        const checkboxes = form.querySelectorAll('#instructions-container input[type="checkbox"]');
        const isAnyCheckboxChecked = Array.from(checkboxes).some(checkbox => checkbox.checked);

        if (isAnyCheckboxChecked) {
          form.querySelector('#instructions-container').classList.remove('is-invalid');
          form.querySelector('#instructions-container .invalid-feedback').style.display = 'none';
        }
      });
    });

    form.querySelector('#instructions-container .invalid-feedback').style.display = 'none';
  });
})();






document.addEventListener('DOMContentLoaded', function() {
  'use strict';

  const forms = document.querySelectorAll('.needs-validation');

  Array.from(forms).forEach(form => {
    form.addEventListener('submit', event => {
      const topicsCheckboxes = form.querySelectorAll('#topics-container input[type="checkbox"]');
      const isAnyTopicsChecked = Array.from(topicsCheckboxes).some(checkbox => checkbox.checked);

      if (!isAnyTopicsChecked) {
        event.preventDefault();
        event.stopPropagation();

        form.querySelector('#topics-container').classList.add('is-invalid');
        form.querySelector('#topics-container .invalid-feedback').style.display = 'block';
      } else {
        form.querySelector('#topics-container').classList.remove('is-invalid');
        form.querySelector('#topics-container .invalid-feedback').style.display = 'none';
      }

      form.classList.add('was-validated');
    }, false);

    form.querySelector('#topics-container').addEventListener('change', event => {
      if (event.target.matches('input[type="checkbox"]')) {
        const checkboxes = form.querySelectorAll('#topics-container input[type="checkbox"]');
        const isAnyCheckboxChecked = Array.from(checkboxes).some(checkbox => checkbox.checked);

        if (isAnyCheckboxChecked) {
          form.querySelector('#topics-container').classList.remove('is-invalid');
          form.querySelector('#topics-container .invalid-feedback').style.display = 'none';
        }
      }
    });

    form.querySelector('#topics-container .invalid-feedback').style.display = 'none';
  });
});





(() => {
  'use strict'
  const forms = document.querySelectorAll('.needs-validation')
  Array.from(forms).forEach(form => {
    form.addEventListener('submit', event => {
      if (!form.checkValidity()) {
        event.preventDefault()
        event.stopPropagation()
      }

      form.classList.add('was-validated')
    }, false)
  })
})()