from datetime import date
from itertools import chain
from django.shortcuts import get_object_or_404, render
from django.template.defaulttags import register
from django.http import JsonResponse
from django.db.models import Q
from django.conf import settings

from tuftsseds.siteapps.events.models import Events
from tuftsseds.siteapps.blog.models import Blog, Author, Category
from .models import ExecMembers, YearAndRole, MailingList, AstrophotographyPhotos


def get_date_attr(value):
    try:
        return value.publish_date
    except AttributeError:
        return value.date


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
# The homepages simply query events and blogs that are related to
# specific teams and display them on the project team homepages
def rocket_hp(request):
    # rocket_events = Events.objects.filter(related_proj_team="rocketry")
    # rocket_blogs = Blog.objects.filter(related_proj_team="rocketry")

    # Gets blog and events related to rocketry
    # Aggregates the data from both models into one big queryset sorted by date bc that their common field
    # List goes from oldest -> newest, will be switched in the template
    # result_list = sorted(
    #     chain(rocket_blogs, rocket_events), key=lambda instance: get_date_attr(instance)
    # )

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
    rocket_events = Events.objects.filter(related_proj_team="rocketry")
    rocket_blogs = Blog.objects.filter(related_proj_team="rocketry")

    # Gets blog and events related to rocketry
    # Aggregates the data from both models into one big queryset sorted by date bc that their common field
    # List goes from oldest -> newest, will be switched in the template
    result_list = sorted(
        chain(rocket_blogs, rocket_events), key=lambda instance: get_date_attr(instance)
    )

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

# delete when done
def burner(request):
    metacontent = {
        "description": """Explore our Tufts SEDS Rocketry's journey with stunning visuals. 
                        View our photo gallery showcasing the milestones and achievements of our dedicated team.""",
        "author": "",
        "keywords": "rockets, rocketry, Tufts, launch, explosion, photo gallary, awesome pictures, space",
    }
    return render(request, "main/burner.html", {"metacontent": metacontent})


def weatherball_hp(request):
    hab_events = Events.objects.filter(related_proj_team="hab")
    hab_blogs = Blog.objects.filter(related_proj_team="hab")

    result_list = sorted(
        chain(hab_blogs, hab_events), key=lambda instance: get_date_attr(instance)
    )
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


def image_info(request):
    if request.POST.get("action") == "post":
        img_link = request.POST.get("src")
        photo = AstrophotographyPhotos.objects.get(photo=img_link)
        if photo.caption == None:
            photo.caption = ""
        return render(request, "main/modals/modal_photo_info.html", {"photo": photo})


def cubesat_hp(request):
    cubesat_events = Events.objects.filter(related_proj_team="cubesat")
    cubesat_blogs = Blog.objects.filter(related_proj_team="cubesat")

    result_list = sorted(
        chain(cubesat_blogs, cubesat_events),
        key=lambda instance: get_date_attr(instance),
    )

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
    active_members = (
        ExecMembers.objects.filter(active=True).order_by("ordering").values()
    )

    for member in active_members:
        year_and_roles = YearAndRole.objects.filter(
            seds_member=member["id"], year=curr_year
        )
        for item in year_and_roles:
            if item.is_eboard:
                member["eboard_role"] = item.role

            if item.is_project_lead:
                member["chapter_role"] = item.role

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

    # Creates a dictionary that organizes past members into a key:value pair with the key
    # being their active years and the value being a queryset that contains member who were
    # active that year
    past_members_dict = {}

    for year in year_list:
        # past_eboard_members = ExecMembers.objects.filter(yearandrole__year=year, yearandrole__is_eboard=True).annotate(
        #         role = Subquery(YearAndRole.objects.filter(seds_member=OuterRef('id'), year=year).values("role"))).values()
        past_members = (
            ExecMembers.objects.filter(yearandrole__year=year).distinct().values()
        )
        for member in past_members:
            year_and_roles = YearAndRole.objects.filter(
                seds_member=member["id"], year=year
            )
            # you can only be on the eboard and be a chapter lead in a single year so
            if year_and_roles.count() > 1:
                member["role"] = (
                    year_and_roles[0].role + " and " + year_and_roles[1].role
                )
            else:
                member["role"] = year_and_roles[0].role
        past_members_dict[year] = past_members

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


# Handles signing up new people for newsletter
def newsletter_signup(request):
    email = str(request.POST.get("email"))
    try:
        MailingList.objects.create(user_email=email)
        return JsonResponse(
            {
                "status": "success",
                "statusText": "You have been added to our mailing list!",
            },
            safe=False,
        )
    except:
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


def search(request):
    if request.method == "POST":
        searched = request.POST.get("s")

        blogresults = (
            Blog.objects.filter(
                (Q(title__icontains=searched))
                | (Q(short_description__icontains=searched))
                | (Q(tags__name__in=[searched]))
                | (Q(author__author_name__icontains=searched))
            )
            .distinct()
            .order_by("-publish_date")
        )
        eventresults = (
            Events.objects.filter(
                (Q(title__icontains=searched))
                | (Q(description__icontains=searched))
                | (Q(tags__name__in=[searched]))
                | (Q(author__author_name__icontains=searched))
            )
            .distinct()
            .order_by("-date")
        )
    return render(
        request,
        "main/search/results.html",
        {
            "searched": searched,
            "blogresults": blogresults,
            "eventresults": eventresults,
        },
    )


def search_category(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)

    blogresults = Blog.objects.filter(category=category)
    eventresults = Events.objects.filter(
        (Q(title__icontains=category.name))
        | (Q(description__icontains=category.name))
        | (Q(tags__name__in=[category.name]))
    ).distinct()

    return render(
        request,
        "main/search/results.html",
        {
            "searched": category.name,
            "blogresults": blogresults,
            "eventresults": eventresults,
        },
    )
