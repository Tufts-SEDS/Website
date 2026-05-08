import base64
import json
import zipfile
import xml.etree.ElementTree as ET

from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.core.files.base import ContentFile
from django.core.paginator import Paginator
from django.utils.text import slugify

# from utils import ork_parser
from tuftsseds.siteapps.main.models import BaseSEDSMember
from tuftsseds.siteapps.events.models import Events
from .forms import BaseRegistrationForm, LoginForm
from .token import account_activation_token

# Create your views here.


def account_register(request):
    if request.user.is_authenticated:
        return redirect("/account/dashboard/")

    if request.method == "POST":
        register_form = BaseRegistrationForm(request.POST)
        if register_form.is_valid():
            user = register_form.save(commit=False)
            user.email = register_form.cleaned_data["email"]
            user.name = register_form.cleaned_data["name"]
            user.set_password(register_form.cleaned_data["password"])
            user.is_active = False
            user.save()

            # Setting up the fields necessary to email the user the account activation url
            current_site = get_current_site(request)
            subject = "Activate your Account"
            message = render_to_string(
                "complete_activation.html",
                {
                    "user": user,
                    "domain": current_site.domain,
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": account_activation_token.make_token(user),
                },
            )
            user.email_user(subject=subject, message=message)
            return render(request, "main/index.html", {"form": register_form})
        else:
            # If form wasn't valid, sends user back to register page with the errors in the form
            return render(
                request, "account/login_register.html", {"form": register_form}
            )
    else:
        register_form = BaseRegistrationForm()
    return render(request, "account/login_register.html", {"form": register_form})


def login_register(request):
    # Fresh login/register forms to use if the user needs to reinput their info
    register_form = BaseRegistrationForm()
    login_form = LoginForm()

    if request.user.is_authenticated:
        return redirect("/account/dashboard/")

    if request.method == "POST":
        completed_register_form = BaseRegistrationForm(request.POST)
        completed_login_form = LoginForm(request.POST)

        # Perform user registration if the registration form is completed and the login form isnt
        if completed_register_form.is_valid() and not completed_login_form.is_valid():
            user = completed_register_form.save(commit=False)
            user.email = completed_register_form.cleaned_data["email"]
            user.name = completed_register_form.cleaned_data["name"]
            user.set_password(completed_register_form.cleaned_data["password"])
            user.is_active = False
            user.save()

            # Setting up the fields necessary to email the user the account activation url
            current_site = get_current_site(request)
            subject = "Activate your Account"
            message = render_to_string(
                "account/complete_activation.html",
                {
                    "user": user,
                    "domain": current_site.domain,
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": account_activation_token.make_token(user),
                },
            )
            user.email_user(subject=subject, message=message)
            return render(request, "main/index.html")

        # Login the user if they input the correct account info
        if not completed_register_form.is_valid() and completed_login_form.is_valid():
            user = authenticate(
                username=completed_login_form.cleaned_data["email"],
                password=completed_login_form.cleaned_data["password"],
            )
            if user is not None:
                login(request, user)
                return redirect("/account/dashboard/")
            else:
                message = "Login failed, user does not exist"
                return render(
                    request, "account/login_register.html", {"form": login_form}
                )

    # If both forms were invalid, return back to the login/register page with fresh forms and an error message
    return render(
        request,
        "account/login_register.html",
        {
            "register_form": register_form,
            "login_form": login_form,
        },
    )


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = BaseSEDSMember.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, user.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        return HttpResponse("Account activated")
    else:
        return HttpResponse("Account not activated")


@login_required
def dashboard(request):
    return render(request, "account/dashboard/dashboard-base.html")


@login_required
def event_image_manager(request):
    contact_list = Events.objects.all()
    paginator = Paginator(contact_list, 25)  # Show 25 events per page.

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(
        request,
        "account/dashboard/events/event-image-manager.html",
        {"page_obj": page_obj},
    )


@login_required
def edit_event(request, slug):
    event = get_object_or_404(
        Events.objects.prefetch_related("event_images").filter(slug=slug)
    )

    return render(
        request, "account/dashboard/events/single-event-images.html", {"event": event}
    )


# @login_required
# def rocketmodel_upload(request):
#     import zipfile
#     if request.method == 'POST':
#         uploaded_files = request.FILES.getlist('file')
#         for file in uploaded_files:
#             filename = file.name
#             file_extension = filename.split('.')[-1].lower()
#             if "ork" in file_extension:
#                 with zipfile.ZipFile(file, "r") as zip_file:
#                     # Extract the XML file from the ZIP archive
#                     rocket_file = zip_file.read("rocket.ork")
#                     tree = ET.ElementTree(ET.fromstring(rocket_file))
#                     root = tree.getroot()

#                     sim_data = ork_parser.dragco_vs_machnum(root)

#                     # Read the XML file
#                     tree = ET.parse("rocket.ork")
#                     root = tree.getroot()
#                     print(ET.tostring(root, encoding="utf-8").decode())

# for file in files:
#     # Check file extension
#     filename = file.name
#     print(filename)
#     file_extension = filename.split('.')[-1].lower()
#     if file_extension not in valid_extensions:
#         return render(request, 'account/dashboard/rocketry/model_upload.html', {'form' : form, 'error' : True})

# return render(request, 'account/dashboard/rocketry/model_upload.html', {'form' : form})

# return render(request, 'account/dashboard/rocketry/model_upload.html')
