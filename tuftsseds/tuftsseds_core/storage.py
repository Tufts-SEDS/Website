from django.conf import settings
from whitenoise.storage import CompressedStaticFilesStorage

# Browsers keep CSS/JS for a day (vercel.json) and file names aren't hashed, so
# without a version a returning visitor could get new HTML with old CSS/JS.
VERSIONED_EXTENSIONS = (".css", ".js")


class VersionedStaticFilesStorage(CompressedStaticFilesStorage):
    """Add ?v=<STATIC_VERSION> to CSS and JS URLs made by {% static %}.

    STATIC_VERSION is the deployed commit, so every deploy gives CSS/JS new
    URLs. Images keep plain URLs and their long cache. With no version set
    (local development), URLs are unchanged.
    """

    def url(self, name):
        url = super().url(name)
        version = getattr(settings, "STATIC_VERSION", "")
        if version and name and name.lower().endswith(VERSIONED_EXTENSIONS):
            url += ("&" if "?" in url else "?") + f"v={version}"
        return url
