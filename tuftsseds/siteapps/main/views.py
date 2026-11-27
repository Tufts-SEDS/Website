from copy import copy
from datetime import date
from django.shortcuts import get_object_or_404, render
from django.template.defaulttags import register
from django.http import HttpResponseBadRequest, JsonResponse
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import IntegrityError
from django.db.models import Prefetch, Q
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from django.urls import reverse

from tuftsseds.siteapps.events.models import Events
from .models import ExecMembers, YearAndRole, MailingList, AstrophotographyPhotos


@register.filter
def get_role(dictionary, key):
    # the years are given to use as a single digit (YYYYYYYY) so we parse it ourselves
    formatted_string = key[:4] + "-" + key[4:]
    return dictionary.get(formatted_string)


def index(request):
    metacontent = {
        "description": """Through social events, technical endeavors, and outreach programs, 
        Tufts SEDS aims to create a community for students who are interested in space and its advancement.""",
        "author": "",
        "keywords": "rockets, rocketry, space, weather balloon, SEDS, astrophotography, radio telescope, CubeSat, Tufts",
    }

    # fetching the first three most recent events from the database to display on homepage
    events = Events.objects.order_by("-date")[:3]

    return render(
        request, "main/index.html", {"metacontent": metacontent, "events": events}
    )


# The following functions denoted with "_hp" are views that
# send the user to the homepage of each respective project teams
# The homepages simply query events that are related to
# specific teams and display them on the project team homepages
def rocket_hp(request):
    # rocket_events = Events.objects.filter(related_proj_team="rocketry")

    # Using some indicators to figure what data-filter to apply to
    # each result when rendered in the rocket homepage
    # for result in result_list:
    #     if "Launch:" in result.title:
    #         result.filter = 2
    #     elif "project" in result.tags.names():
    #         result.filter = 1
    #     else:
    #         result.filter = 0

    metacontent = {
        "description": """Tufts SEDS Rocketry is a student-led organization dedicated to the design, 
                            construction, and launch of high-powered rockets.""",
        "author": "",
        "keywords": "rockets, rocketry, Tufts, motor, launch, explosion",
    }

    return render(
        request,
        "main/homepages/rocketry_home.html",
        {"metacontent": metacontent},
    )


def rocket_our_sponsers(request):
    metacontent = {
        "description": """Tufts SEDS Rocketry is a student-led organization dedicated to the design, 
                            construction, and launch of high-powered rockets.""",
        "author": "",
        "keywords": "rockets, rocketry, Tufts, launch, explosion, space",
    }
    return render(
        request, "main/rocketry/our_sponsors.html", {"metacontent": metacontent}
    )


def rocket_become_sponser(request):
    metacontent = {
        "description": """Tufts SEDS Rocketry is a student-led organization dedicated to the design, 
                            construction, and launch of high-powered rockets.""",
        "author": "",
        "keywords": "rockets, rocketry, Tufts, launch, explosion, space",
    }
    return render(
        request, "main/rocketry/become_a_sponsor.html", {"metacontent": metacontent}
    )


def rocket_donate(request):
    metacontent = {
        "description": """Tufts SEDS Rocketry is a student-led organization dedicated to the design, 
                            construction, and launch of high-powered rockets.""",
        "author": "",
        "keywords": "rockets, rocketry, Tufts, launch, explosion, space",
    }
    return render(
        request, "main/rocketry/donate_rocketry.html", {"metacontent": metacontent}
    )


def rocket_projects(request):
    metacontent = {
        "description": """Tufts SEDS Rocketry is a student-led organization dedicated to the design, 
                            construction, and launch of high-powered rockets.""",
        "author": "",
        "keywords": "rockets, rocketry, Tufts, launch, explosion, project, competition, space",
    }
    return render(request, "main/rocketry/projects.html", {"metacontent": metacontent})


def rocket_leadership(request):
    metacontent = {
        "description": """Tufts SEDS Rocketry is a student-led organization dedicated to the design, 
                            construction, and launch of high-powered rockets.""",
        "author": "",
        "keywords": "rockets, rocketry, Tufts, launch, explosion, leadership, space",
    }
    return render(
        request, "main/rocketry/leadership.html", {"metacontent": metacontent}
    )


def rocket_launch(request):
    # List goes from oldest -> newest, will be switched in the template
    result_list = Events.objects.filter(related_proj_team="rocketry").order_by("date")

    metacontent = {
        "description": """Tufts SEDS Rocketry is a student-led organization dedicated to the design, 
                            construction, and launch of high-powered rockets.""",
        "author": "",
        "keywords": "rockets, rocketry, Tufts, launch, explosion, photo gallary, awesome pictures, space",
    }
    return render(
        request,
        "main/rocketry/launches.html",
        {"metacontent": metacontent, "results": result_list},
    )


def rocket_gallery(request):
    metacontent = {
        "description": """Explore our Tufts SEDS Rocketry's journey with stunning visuals. 
                        View our photo gallery showcasing the milestones and achievements of our dedicated team.""",
        "author": "",
        "keywords": "rockets, rocketry, Tufts, launch, explosion, photo gallary, awesome pictures, space",
    }
    return render(request, "main/rocketry/gallery.html", {"metacontent": metacontent})

def weatherball_hp(request):
    result_list = Events.objects.filter(related_proj_team="hab").order_by("date")
    metacontent = {
        "description": """The Tufts SEDS High Altitude Balloon team is committed to advancing our understanding of weather patterns, 
                            climate change, and the effects of high altitude conditions on biological organisms.""",
        "author": "",
        "keywords": "weather balloon, experiment, report, Tufts, environmental science, high altitude",
    }

    return render(
        request,
        "main/homepages/hab_home.html",
        {"metacontent": metacontent, "results": result_list},
    )


def astrophotography_hp(request):
    metacontent = {
        "description": """Discover the cosmos with Tufts SEDS Astrophotography! 
                            Join us as we capture the beauty of the night sky and reveal the mysteries of the universe, one snapshot at a time.""",
        "author": "",
        "keywords": "astrophotography, james-webb, Tufts, space, cosmos, astronomy, galaxy, stars",
    }

    astrophotos = AstrophotographyPhotos.objects.filter(homepage_active=True)

    return render(
        request,
        "main/homepages/astrophotography_home.html",
        {
            "metacontent": metacontent,
            "images": astrophotos,
        },
    )


def astrophotography_helper(request):
    return render(
        request,
        "main/modals/modal_photo_info.html",
    )


# csrf_exempt: pages are cached at the CDN without a CSRF cookie, and this
# view only reads public photo details.
@csrf_exempt
@require_POST
def image_info(request):
    img_link = request.POST.get("src")
    if request.POST.get("action") != "post" or not img_link:
        return HttpResponseBadRequest("Expected action=post and a photo src.")
    photo = get_object_or_404(AstrophotographyPhotos, photo=img_link)
    if photo.caption is None:
        photo.caption = ""
    return render(request, "main/modals/modal_photo_info.html", {"photo": photo})


def cubesat_hp(request):
    result_list = Events.objects.filter(related_proj_team="cubesat").order_by("date")

    metacontent = {
        "description": """Discover the Tufts SEDS CubeSat team's mission to contribute to space exploration by building innovative CubeSats for various scientific purposes. 
                        Join us in our journey of technology advancement and groundbreaking research.""",
        "author": "",
        "keywords": "CubeSat, cubesat, Tufts",
    }

    return render(
        request,
        "main/homepages/cubesat_home.html",
        {"metacontent": metacontent, "results": result_list},
    )


def radio_telescope_hp(request):
    metacontent = {
        "description": """Discover the Tufts SEDS Radio Telescope team's mission to build a public radio telescope for the Tufts community.
                        Join us in our journey of technology advancement and groundbreaking research.""",
        "author": "",
        "keywords": "CubeSat, cubesat, Tufts",
    }

    return render(
        request,
        "main/homepages/rt_home.html",
        {
            "metacontent": metacontent,
        },
    )

def radio_telescope_news(request):
    metacontent = {
        "description": """Discover the Tufts SEDS Radio Telescope team's mission to build a public radio telescope for the Tufts community.
                        Join us in our journey of technology advancement and groundbreaking research.""",
        "author": "",
        "keywords": "CubeSat, cubesat, Tufts",
    }

    return render(
        request,
        "main/radio-telescope/news.html",
        {
            "metacontent": metacontent,
        },
    )


# Current board members + past board members
def leadership(request):
    metacontent = {
        "description": """Meet the current and past members of our SEDS group's executive board, 
            the driving force behind our success. Learn about the achievements and 
            contributions of past members and get inspired by the future leaders of the space industry""",
        "author": "",
        "keywords": "Tufts, executive members, important people, geniuses",
    }

    curr_year = settings.ACTIVE_YEAR

    # One query for the members plus one for all of their roles this year.
    # (Querying roles per member made this page take 15+ seconds.)
    active_members = (
        ExecMembers.objects.filter(active=True)
        .order_by("ordering")
        .prefetch_related(
            Prefetch(
                "yearandrole_set",
                queryset=YearAndRole.objects.filter(year=curr_year).order_by("id"),
                to_attr="current_roles",
            )
        )
    )

    for member in active_members:
        for item in member.current_roles:
            if item.is_eboard:
                member.eboard_role = item.role

            if item.is_project_lead:
                member.chapter_role = item.role

    # Get the past years of exes of seds in a dict
    ## target year range, when Tufts SEDS chapter was founded
    target_year_range = "2018-2019"
    year_list = []
    # Convert the year ranges to integer values
    current_year, target_year = map(int, settings.ACTIVE_YEAR.split("-"))
    target_year = int(target_year_range.split("-")[0])

    # Loop to continuously decrease the years
    while current_year > target_year:
        # Generate the year range string
        current_year_range = f"{current_year}-{current_year + 1}"
        year_list.append(current_year_range)
        # Decrease the year range
        current_year -= 1
    year_list.append(target_year_range)
    year_list.pop(0)  # the active year was added first so we get rid of it
    year_list.remove("2020-2021")  # the dark ages
    year_list.remove(
        "2021-2022"
    )  # this was the year the 1st gen seds eboard were handing the keys to us 2nd gens we dont know wtf happened here

    # Organizes past members by year: {year: [member, ...]}, in the order their
    # roles were entered. Each member gets a "role" attribute; someone with more
    # than one role that year shows as "Eboard Role and Project Role".
    # All years come from a single query.
    roles_by_year = {year: {} for year in year_list}

    past_roles = (
        YearAndRole.objects.filter(year__in=year_list, seds_member__isnull=False)
        .select_related("seds_member")
        .order_by("id")
    )
    for item in past_roles:
        members_that_year = roles_by_year[item.year]
        if item.seds_member_id not in members_that_year:
            # Separate copy per year, since the same person can appear in several years
            members_that_year[item.seds_member_id] = (copy(item.seds_member), [])
        members_that_year[item.seds_member_id][1].append(item)

    past_members_dict = {}
    for year, members_that_year in roles_by_year.items():
        past_members_dict[year] = []
        for member, roles in members_that_year.values():
            roles.sort(key=lambda r: not r.is_eboard)  # eboard role first
            names = [r.role for r in roles]
            member.role = (
                ", ".join(names[:-1]) + " and " + names[-1] if len(names) > 1 else names[0]
            )
            past_members_dict[year].append(member)

    return render(
        request,
        "main/members.html",
        {
            "metacontent": metacontent,
            "active_members": active_members,
            "past_members": past_members_dict,
            "years": year_list,
            "curr": curr_year,
        },
    )


def media(request):
    metacontent = {
        "description": """Tufts SEDS in the News!""",
        "author": "",
        "keywords": "astrophotography, james-webb, Tufts, space, cosmos, astronomy, galaxy, stars",
    }

    return render(request, "main/media.html")


# Handles signing up new people for newsletter. csrf_exempt because public
# pages are cached at the CDN without a CSRF cookie; the view only stores a
# validated email address.
@csrf_exempt
@require_POST
def newsletter_signup(request):
    email = (request.POST.get("email") or "").strip()
    try:
        validate_email(email)
    except ValidationError:
        return JsonResponse(
            {"status": "fail", "errors": "Please enter a valid email address."},
            safe=False,
        )
    try:
        MailingList.objects.create(user_email=email)
        return JsonResponse(
            {
                "status": "success",
                "statusText": "You have been added to our mailing list!",
            },
            safe=False,
        )
    except IntegrityError:
        return JsonResponse(
            {"status": "fail", "errors": "This email has already been used."},
            safe=False,
        )


def about_us(request):
    metadescription = "Temporary metadescription"

    return render(
        request,
        "main/about-us.html",
        {
            "metadescription": metadescription,
        },
    )


def support_us(request):
    metadescription = "Temporary metadescription"

    return render(
        request,
        "main/support-us.html",
        {
            "metadescription": metadescription,
        },
    )


# Pages the search bar can find. The keywords are what the search matches against,
# so add a line here (and relevant keywords) whenever a new public page is added.
SEARCHABLE_PAGES = [
    ("Home", "main:home", "tufts seds students exploration development space"),
    ("About Us", "main:about_us", "about mission chapter join members contact"),
    ("Leadership", "main:leadership", "leadership executive board eboard officers president project leads members"),
    ("Support Us", "main:support_us", "support donate sponsor sponsorship"),
    ("Media", "main:media", "media news press photos videos"),
    ("Events", "events:events", "events launches meetings outreach"),
    ("Event Calendar", "events:calendar", "calendar schedule events dates meetings"),
    ("Rocketry", "main:rocket_hp", "rocketry rockets rocket launch high power"),
    ("Rocketry Projects", "main:rocket_projects", "rocketry projects rockets carm"),
    ("Rocketry Launches", "main:rocket_launch", "rocketry launches launch rockets"),
    ("Rocketry Leadership", "main:rocket_leadership", "rocketry leadership leads team"),
    ("Rocketry Sponsors", "main:rocket_our_sponsers", "rocketry sponsors sponsorship"),
    ("Become a Rocketry Sponsor", "main:rocket_become_sponser", "rocketry sponsor sponsorship become"),
    ("Donate to Rocketry", "main:rocket_donate", "rocketry donate donation support"),
    ("CubeSat", "main:cubesat_hp", "cubesat satellite space debris team members"),
    ("Radio Telescope", "main:radio_telescope_hp", "radio telescope srt astronomy hydrogen"),
    ("Radio Telescope News", "main:radio_telescope_news", "radio telescope news updates srt"),
    ("Astrophotography", "main:astrophotography_hp", "astrophotography photos photography night sky"),
]


def search(request):
    # GET so result pages can be bookmarked or shared; POST kept for any old forms
    searched = (request.GET.get("s") or request.POST.get("s") or "").strip()
    words = searched.split()

    eventresults = Events.objects.none()
    pageresults = []
    memberresults = ExecMembers.objects.none()

    if words:
        # Every word has to appear somewhere, but not necessarily as one phrase
        event_query = Q()
        member_query = Q()
        for word in words:
            event_query &= (
                Q(title__icontains=word)
                | Q(description__icontains=word)
                | Q(tags__name__icontains=word)
                | Q(author__author_name__icontains=word)
                | Q(related_proj_team__icontains=word)
            )
            member_query &= (
                Q(first_name__icontains=word)
                | Q(last_name__icontains=word)
                | Q(yearandrole__role__icontains=word)
            )

        eventresults = Events.objects.filter(event_query).distinct().order_by("-date")
        memberresults = (
            ExecMembers.objects.filter(member_query)
            .distinct()
            .order_by("-active", "ordering", "last_name")
        )

        lowered = [word.lower() for word in words]
        for title, url_name, keywords in SEARCHABLE_PAGES:
            haystack = f"{title} {keywords}".lower()
            if all(word in haystack for word in lowered):
                pageresults.append({"title": title, "url": reverse(url_name)})

    return render(
        request,
        "main/search/results.html",
        {
            "searched": searched,
            "eventresults": eventresults,
            "pageresults": pageresults,
            "memberresults": memberresults,
        },
    )

