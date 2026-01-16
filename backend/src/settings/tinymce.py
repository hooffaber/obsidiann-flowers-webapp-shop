# TinyMCE Settings

TINYMCE_DEFAULT_CONFIG = {
    'theme': 'silver',
    'height': 400,
    'menubar': True,
    'plugins': [
        'advlist', 'autolink', 'lists', 'link', 'image', 'charmap',
        'preview', 'anchor', 'searchreplace', 'visualblocks', 'code',
        'fullscreen', 'insertdatetime', 'media', 'table', 'help', 'wordcount'
    ],
    'toolbar': (
        'undo redo | formatselect | bold italic underline strikethrough | '
        'forecolor backcolor | alignleft aligncenter alignright alignjustify | '
        'bullist numlist outdent indent | link image | removeformat | code'
    ),
    'language': 'ru',
    'content_css': 'default',
    'branding': False,
}
