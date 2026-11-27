from django.templatetags.static import static
from django.test import SimpleTestCase, override_settings


class VersionedStaticUrlTests(SimpleTestCase):
    @override_settings(STATIC_VERSION="abc12345")
    def test_css_and_js_get_the_version(self):
        self.assertEqual(static("css/style.min.css"), "/static/css/style.min.css?v=abc12345")
        self.assertEqual(static("js/apolo.init.js"), "/static/js/apolo.init.js?v=abc12345")

    @override_settings(STATIC_VERSION="abc12345")
    def test_images_keep_plain_urls(self):
        self.assertEqual(static("images/logo.png"), "/static/images/logo.png")

    @override_settings(STATIC_VERSION="")
    def test_no_version_leaves_urls_unchanged(self):
        self.assertEqual(static("css/style.min.css"), "/static/css/style.min.css")
