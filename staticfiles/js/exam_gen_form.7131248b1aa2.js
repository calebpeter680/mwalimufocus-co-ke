$(document).ready(function() {
    function getRelevantEducationLevels(selectedLevel) {
        const levelMapping = {
            'PP1': ['PP1'],
            'PP2': ['PP1', 'PP2'],
            'Grade 1': ['Grade 1'],
            'Grade 2': ['Grade 1', 'Grade 2'],
            'Grade 3': ['Grade 1', 'Grade 2', 'Grade 3'],
            'Grade 4': ['Grade 4'],
            'Grade 5': ['Grade 4', 'Grade 5'],
            'Grade 6': ['Grade 4', 'Grade 5', 'Grade 6'],
            'Grade 7': ['Grade 7'],
            'Grade 8': ['Grade 7', 'Grade 8'],
            'Grade 9': ['Grade 7', 'Grade 8', 'Grade 9'],
            'Grade 10': ['Grade 10'],
            'Grade 11': ['Grade 10', 'Grade 11'],
            'Grade 12': ['Grade 10', 'Grade 11', 'Grade 12'],
            'Form 1': ['Form 1'],
            'Form 2': ['Form 1', 'Form 2'],
            'Form 3': ['Form 1', 'Form 2', 'Form 3'],
            'Form 4': ['Form 1', 'Form 2', 'Form 3', 'Form 4']
        };

        return levelMapping[selectedLevel] || [];
    }

    function fetchTopics() {
        var educationLevelId = $('#education_level').val();
        var subjectId = $('#subjects').val();

        if (educationLevelId && subjectId) {
            var selectedLevelText = $('#education_level option:selected').text();
            var relevantLevels = getRelevantEducationLevels(selectedLevelText);

            $.ajax({
                url: '{% url "fetch_topics" %}',
                data: {
                    'education_level_ids': relevantLevels,
                    'subject_id': subjectId
                },
                success: function(data) {
                    var topicsContainer = $('#topics-container');
                    topicsContainer.empty();
                    var noTopics = true;

                    relevantLevels.forEach(function(level) {
                        var levelHeader = `<h6><b>${level}</b></h6>`;
                        topicsContainer.append(levelHeader);
                        var levelTopics = data.topics.filter(topic => topic.education_level === level);
                        if (levelTopics.length > 0) {
                            noTopics = false;
                            levelTopics.forEach(function(topic) {
                                var checkbox = `
                                    <div class="form-check form-check-inline">
                                        <input class="form-check-input" type="checkbox" id="topic${topic.id}" value="${topic.id}">
                                        <label class="form-check-label" for="topic${topic.id}">${topic.name}</label>
                                    </div>`;
                                topicsContainer.append(checkbox);
                            });
                        } else {
                            topicsContainer.append(`<p>No topics yet!</p>`);
                        }
                    });

                    if (noTopics) {
                        topicsContainer.append(`<p><i class="bi bi-patch-exclamation"></i> No topics yet for ${selectedLevelText} ${$('#subjects option:selected').text()}. Please try again soon!</p>`);
                        $('#submit_btn').prop('disabled', true);
                    } else {
                        $('#submit_btn').prop('disabled', false);
                    }
                }
            });
        }
    }

    fetchTopics();

    $('#education_level, #subjects').change(function() {
        fetchTopics();
    });
});




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