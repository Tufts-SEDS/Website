from unittest import mock

from django.shortcuts import render as real_render
from django.test import RequestFactory, TestCase, override_settings

from tuftsseds.siteapps.main import views
from tuftsseds.siteapps.main.models import ExecMembers, YearAndRole

CURRENT = "2026-2027"


def call_leadership():
    """Render the page and return (response, context).

    Calls the view directly instead of using the test client: Django 4.1's
    client can't copy template contexts on Python 3.14.
    """
    seen = {}

    def spy(request, template, context=None, *args, **kwargs):
        seen.update(context or {})
        return real_render(request, template, context, *args, **kwargs)

    with mock.patch.object(views, "render", side_effect=spy):
        response = views.leadership(RequestFactory().get("/leadership"))
    return response, seen


@override_settings(ACTIVE_YEAR=CURRENT)
class LeadershipPageTests(TestCase):
    def member(self, first, active=False, ordering=None):
        return ExecMembers.objects.create(first_name=first, last_name="Test", active=active, ordering=ordering)

    def role(self, member, year, role, eboard=False, lead=False):
        return YearAndRole.objects.create(
            seds_member=member, year=year, role=role, is_eboard=eboard, is_project_lead=lead
        )

    def get(self):
        response, context = call_leadership()
        self.assertEqual(response.status_code, 200)
        return context

    def test_current_members_get_this_years_roles_only(self):
        ada = self.member("Ada", active=True, ordering=1)
        self.role(ada, CURRENT, "President", eboard=True)
        self.role(ada, CURRENT, "Rocketry Lead", lead=True)
        self.role(ada, "2024-2025", "Treasurer", eboard=True)  # past year: ignored here

        [shown] = list(self.get()["active_members"])
        self.assertEqual((shown.eboard_role, shown.chapter_role), ("President", "Rocketry Lead"))

    def test_current_members_follow_their_ordering(self):
        self.member("Second", active=True, ordering=2)
        self.member("First", active=True, ordering=1)
        self.member("Inactive", active=False, ordering=0)
        names = [m.first_name for m in self.get()["active_members"]]
        self.assertEqual(names, ["First", "Second"])

    def test_past_roles_are_joined_with_the_eboard_role_first(self):
        bo = self.member("Bo")
        self.role(bo, "2024-2025", "Rocketry Lead", lead=True)
        self.role(bo, "2024-2025", "Vice President", eboard=True)
        cy = self.member("Cy")
        self.role(cy, "2024-2025", "CubeSat Lead", lead=True)
        self.role(cy, "2024-2025", "Mars Rover Lead", lead=True)
        self.role(cy, "2024-2025", "Secretary", eboard=True)

        roles = {m.first_name: m.role for m in self.get()["past_members"]["2024-2025"]}
        self.assertEqual(roles["Bo"], "Vice President and Rocketry Lead")
        self.assertEqual(roles["Cy"], "Secretary, CubeSat Lead and Mars Rover Lead")

    def test_one_person_in_several_years_keeps_each_years_role(self):
        di = self.member("Di")
        self.role(di, "2023-2024", "Treasurer", eboard=True)
        self.role(di, "2024-2025", "President", eboard=True)

        past = self.get()["past_members"]
        self.assertEqual([m.role for m in past["2023-2024"]], ["Treasurer"])
        self.assertEqual([m.role for m in past["2024-2025"]], ["President"])

    def test_past_years_skip_the_current_year_and_the_gap_years(self):
        years = self.get()["years"]
        self.assertEqual(years[0], "2025-2026")
        self.assertEqual(years[-1], "2018-2019")
        for year in (CURRENT, "2020-2021", "2021-2022"):
            self.assertNotIn(year, years)

    def test_page_uses_three_queries_however_many_members(self):
        for i in range(10):
            m = self.member(f"M{i}", active=i < 5, ordering=i)
            self.role(m, CURRENT if i < 5 else "2024-2025", "Lead", lead=True)
            self.role(m, "2023-2024", "Member at Large", eboard=True)
        # members, their current roles, and all past roles (including rendering)
        with self.assertNumQueries(3):
            call_leadership()


class ImageInfoTests(TestCase):
    def post(self, data):
        return views.image_info(RequestFactory().post("/get-image-info/", data))

    def test_bad_request_is_rejected_instead_of_crashing(self):
        self.assertEqual(self.post({}).status_code, 400)
        self.assertEqual(self.post({"action": "other", "src": "x.webp"}).status_code, 400)
        self.assertEqual(self.post({"action": "post"}).status_code, 400)

    def test_unknown_photo_is_a_404(self):
        from django.http import Http404

        with self.assertRaises(Http404):
            self.post({"action": "post", "src": "missing.webp"})

    def test_get_is_not_allowed(self):
        self.assertEqual(views.image_info(RequestFactory().get("/get-image-info/")).status_code, 405)
