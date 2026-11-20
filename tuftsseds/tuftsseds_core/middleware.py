from django.conf import settings

# Paths that are per-user or change state, and must never be cached.
UNCACHED_PREFIXES = (
    "/admin",
    "/account",
    "/newsletter-signup",
    "/get-image-info",
)

# Vercel's CDN serves a cached copy for 5 minutes, then keeps serving it for up
# to a day while it fetches a fresh copy in the background. Browsers always
# revalidate (max-age=0), so visitors never see a page older than the CDN's.
PUBLIC_CACHE_CONTROL = "public, max-age=0, s-maxage=300, stale-while-revalidate=86400"


class PublicPageCacheMiddleware:
    """Let the CDN cache public pages.

    Only plain GET/HEAD 200 responses that set no cookies, don't vary by cookie,
    and come from visitors who aren't logged in are marked cacheable. Must be
    listed before SessionMiddleware and CsrfViewMiddleware in MIDDLEWARE so it
    sees any cookies they add to the response.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if not settings.DEBUG and self.is_cacheable(request, response):
            response["Cache-Control"] = PUBLIC_CACHE_CONTROL
        return response

    @staticmethod
    def is_cacheable(request, response):
        return (
            request.method in ("GET", "HEAD")
            and response.status_code == 200
            and not request.path.startswith(UNCACHED_PREFIXES)
            and not response.has_header("Cache-Control")
            and not response.cookies
            and "cookie" not in response.get("Vary", "").lower()
            and settings.SESSION_COOKIE_NAME not in request.COOKIES
        )
