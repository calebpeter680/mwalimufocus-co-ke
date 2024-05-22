function initTinyMCE() {
  tinymce.init({
    selector: '#descriptionInput, #descriptionInput_update',
    menubar: false,
    plugins: 'lists link image preview',
    toolbar: 'undo redo | formatselect | bold italic | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | link image | preview',
    height: 300
  });
}

document.getElementById('addShopItem').addEventListener('shown.bs.modal', function () {
  if (!tinymce.get('descriptionInput')) {  
    initTinyMCE();
  }
});

document.getElementById('addShopItem').addEventListener('hidden.bs.modal', function () {
  if (tinymce.get('descriptionInput')) { 
    tinymce.remove(tinymce.get('descriptionInput'));
  }
});
