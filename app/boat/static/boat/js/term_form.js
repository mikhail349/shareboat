$(document).ready(function() {
    $('textarea[name="content"]').summernote({
        height: 360,
        lang: 'ru-RU',
        toolbar: [
            ['style', ['style']],
            ['font', ['bold', 'underline', 'clear']],
            ['color', ['color']],
            ['para', ['ul', 'ol', 'paragraph']],
            ['table', ['table']],
            ['insert', ['link',]],
            ['view', ['fullscreen', 'help']]
          ]
    });
  });