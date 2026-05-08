from django.shortcuts import render, get_object_or_404
from django.views.generic.list import ListView


from .models import Events


def get_substring_after_last_char(s, char):
    head, separator, tail = s.rpartition(char)
    return tail


class EventsListView(ListView):
    model = Events
    paginate_by = 24
    template_name = "events/eventlist.html"
    ordering = ["-date"]
    extra_context = {
        "metacontent": {
            "description": """Discover past events hosted and attended by our SEDS group, 
            including talks, workshops, and outreach programs. 
            Get inspired for future space-related opportunities!""",
            "author": "",
            "keywords": "events, SEDS, tufts, space, aerospace, astronomy",
        }
    }


def get_event(request, slug):
    event = get_object_or_404(Events.objects.filter(slug=slug))

    # generating urls for the static images
    image_count = event.total_images
    static_image_path = (
        "/static/images/events/" + event.folder_name + "/" + event.image_prepend_name
    )
    
    # using list comprehension bc thats faster
    event_images = [f"{static_image_path}_{i}.webp" for i in range(1, image_count + 1)]

    # Using the tags for SEO
    keywords = "tufts, Tufts, "
    for tag in event.tags.names():
        keywords += tag + ","

    metacontent = {
        "description": event.description[0:150],
        "author": event.author.author_name,
        "keywords": keywords,
    }
    return render(
        request,
        "events/single_event.html",
        {"event": event, "event_images": event_images, "metacontent": metacontent},
    )
