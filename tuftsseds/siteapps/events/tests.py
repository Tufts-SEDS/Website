import os
import tempfile
import time
from pathlib import Path

from django.test import SimpleTestCase

from tuftsseds.siteapps.events.images import cover_stem, thumb_name
from tuftsseds.siteapps.events.management.commands.make_cover_thumbs import plan_thumbs
from tuftsseds.siteapps.events.models import Events


class CoverStemTests(SimpleTestCase):
    def test_bare_name_is_kept(self):
        self.assertEqual(cover_stem("kidsday_4"), "kidsday_4")

    def test_webp_extension_is_dropped(self):
        self.assertEqual(cover_stem("kidsday_4.webp"), "kidsday_4")
        self.assertEqual(cover_stem("kidsday_4.WEBP"), "kidsday_4")

    def test_path_or_url_gives_the_file_name(self):
        self.assertEqual(cover_stem("images/events/kids_day/kidsday_4.webp"), "kidsday_4")
        self.assertEqual(
            cover_stem("https://sedstufts.org/static/images/events/kids_day/kidsday_4.webp?x=1#top"),
            "kidsday_4",
        )
        self.assertEqual(cover_stem("kids_day/kidsday_4/"), "kidsday_4")

    def test_whitespace_is_trimmed(self):
        self.assertEqual(cover_stem("  kidsday_4\n"), "kidsday_4")

    def test_empty_values_give_none(self):
        for value in (None, "", "   ", "/", ".webp"):
            with self.subTest(value=value):
                self.assertIsNone(cover_stem(value))


class CoverUrlTests(SimpleTestCase):
    def test_urls_point_at_the_photo_and_its_thumbnail(self):
        event = Events(folder_name="kids_day", cover_image="kidsday_4")
        self.assertEqual(event.cover_url, "/static/images/events/kids_day/kidsday_4.webp")
        self.assertEqual(event.cover_thumb_url, "/static/images/events/kids_day/kidsday_4_thumb.webp")

    def test_cover_stored_with_extension_does_not_double_it(self):
        event = Events(folder_name="kids_day", cover_image="kidsday_4.webp")
        self.assertEqual(event.cover_url, "/static/images/events/kids_day/kidsday_4.webp")

    def test_missing_cover_or_folder_falls_back_to_the_logo(self):
        for event in (Events(folder_name="kids_day", cover_image=""), Events(folder_name=None, cover_image="kidsday_4")):
            with self.subTest(event=event):
                self.assertEqual(event.cover_url, "/static/images/logo.png")
                self.assertEqual(event.cover_thumb_url, "/static/images/logo.png")


class PlanThumbsTests(SimpleTestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def touch(self, rel, mtime=None):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"x")
        if mtime is not None:
            os.utime(path, (mtime, mtime))
        return path

    def test_writes_a_missing_cover_thumbnail_only(self):
        photo = self.touch("kids_day/kidsday_4.webp")
        self.touch("kids_day/kidsday_1.webp")  # not a cover: gets no thumbnail
        to_write, to_delete, missing = plan_thumbs(self.root, [("kids_day", "kidsday_4")])
        self.assertEqual(to_write, [(photo, photo.with_name(thumb_name("kidsday_4")))])
        self.assertEqual((to_delete, missing), ([], []))

    def test_up_to_date_thumbnail_is_left_alone_and_stale_one_rewritten(self):
        now = time.time()
        self.touch("a/fresh.webp", now - 100)
        self.touch("a/fresh_thumb.webp", now)
        stale_photo = self.touch("a/stale.webp", now)
        self.touch("a/stale_thumb.webp", now - 100)
        to_write, _, _ = plan_thumbs(self.root, [("a", "fresh"), ("a", "stale")])
        self.assertEqual([photo for photo, _ in to_write], [stale_photo])

    def test_thumbnails_of_non_covers_are_deleted_in_every_folder(self):
        self.touch("kids_day/kidsday_4.webp")
        keep = self.touch("kids_day/kidsday_4_thumb.webp")
        stray = self.touch("kids_day/kidsday_1_thumb.webp")
        orphan = self.touch("no_event_folder/photo_7_thumb.webp")
        _, to_delete, _ = plan_thumbs(self.root, [("kids_day", "kidsday_4")])
        self.assertEqual(set(to_delete), {stray, orphan})
        self.assertNotIn(keep, to_delete)

    def test_cover_without_a_photo_is_reported(self):
        _, _, missing = plan_thumbs(self.root, [("kids_day", "nope")])
        self.assertEqual(missing, [("kids_day", "nope")])
