import unittest
from unittest import mock

from scripts import conference_agent


class ConferenceAgentExtractionTests(unittest.TestCase):
    def test_extracts_space_conference_fields_from_labeled_lines(self) -> None:
        record = {
            "name": "IEEE Smart World Congress",
            "acronym": "SWC",
            "conference_start": "07.09.2026",
            "conference_end": "11.09.2026",
            "early_bird_deadline": "",
            "registration_price": "TBD",
            "location": "Rende, Italy",
            "website": "https://swc-ieee-2026.github.io/swc/",
        }
        lines = [
            "Important Dates",
            "Conference dates: September 7-11, 2026",
            "Early bird registration deadline: May 1, 2026",
            "Registration fees: Early bird EUR 540 / Regular EUR 690",
            "Venue: Rende, Italy",
        ]
        snapshot = conference_agent.PageSnapshot(
            url=record["website"],
            final_url=record["website"],
            text=" ".join(lines),
            ok=True,
            status_code=200,
            lines=lines,
        )

        extracted = conference_agent.extract_structured_updates_from_snapshot(record, snapshot)

        self.assertIsNotNone(extracted)
        updates, _, _ = extracted
        self.assertEqual(updates.get("conference_start"), "07.09.2026")
        self.assertEqual(updates.get("conference_end"), "11.09.2026")
        self.assertEqual(updates.get("early_bird_deadline"), "01.05.2026")
        self.assertEqual(
            updates.get("registration_price"),
            "Early bird EUR 540 / Regular EUR 690",
        )
        self.assertEqual(updates.get("location"), "Rende, Italy")

    def test_single_day_event_is_normalized_to_start_and_end_date(self) -> None:
        record = {
            "name": "EO Summit",
            "acronym": "EOS",
            "conference_start": "12.10.2026",
            "conference_end": "12.10.2026",
            "early_bird_deadline": "",
            "registration_price": "TBD",
            "location": "Berlin, Germany",
            "website": "https://eo.example/summit",
        }
        lines = [
            "Event date: October 12, 2026",
            "Registration fee: EUR 320",
        ]
        snapshot = conference_agent.PageSnapshot(
            url=record["website"],
            final_url=record["website"],
            text=" ".join(lines),
            ok=True,
            status_code=200,
            lines=lines,
        )

        extracted = conference_agent.extract_structured_updates_from_snapshot(record, snapshot)

        self.assertIsNotNone(extracted)
        updates, _, _ = extracted
        self.assertEqual(updates.get("conference_start"), "12.10.2026")
        self.assertEqual(updates.get("conference_end"), "12.10.2026")

    def test_prepare_conference_fetches_linked_details_page(self) -> None:
        record = {
            "name": "International Conference on Service-Oriented System Engineering",
            "acronym": "SOSE",
            "conference_start": "27.07.2026",
            "conference_end": "30.07.2026",
            "early_bird_deadline": "",
            "registration_price": "TBD",
            "location": "Fukuoka, Japan",
            "website": "https://cisose.fit.ac.jp/sose/",
        }
        details_url = "https://cisose.fit.ac.jp/sose/index.php/registration/"
        homepage_snapshot = conference_agent.PageSnapshot(
            url=record["website"],
            final_url=record["website"],
            text="IEEE SOSE 2026 Registration and Important Dates",
            ok=True,
            status_code=200,
            links=[conference_agent.PageLink(url=details_url, text="Registration and Important Dates")],
            lines=["IEEE SOSE 2026"],
        )
        details_snapshot = conference_agent.PageSnapshot(
            url=details_url,
            final_url=details_url,
            text=(
                "Registration Important Dates Conference dates: July 27-30, 2026 "
                "Early bird deadline: April 21, 2026 Registration fee: EUR 650"
            ),
            ok=True,
            status_code=200,
            lines=[
                "Registration",
                "Conference dates: July 27-30, 2026",
                "Early bird deadline: April 21, 2026",
                "Registration fee: EUR 650",
            ],
        )

        with mock.patch.object(
            conference_agent,
            "fetch_page",
            side_effect=[homepage_snapshot, details_snapshot],
        ) as fetch_page:
            prepared = conference_agent.prepare_conference(
                record,
                timeout=25,
                search_fallback=False,
            )

        self.assertEqual(fetch_page.call_count, 2)
        self.assertEqual([snapshot.final_url for snapshot in prepared.snapshots], [record["website"], details_url])
        self.assertEqual(prepared.heuristic["status"], "review")
        self.assertEqual(prepared.heuristic["selected_url"], details_url)
        self.assertEqual(prepared.heuristic["record"]["early_bird_deadline"], "21.04.2026")
        self.assertEqual(prepared.heuristic["record"]["registration_price"], "EUR 650")


if __name__ == "__main__":
    unittest.main()
