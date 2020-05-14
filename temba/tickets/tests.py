from django.test.utils import override_settings
from django.urls import reverse

from temba.tests import CRUDLTestMixin, TembaTest

from .models import Ticket, Ticketer
from .types import reload_ticketer_types
from .types.mailgun import MailgunType


class TicketerTest(TembaTest):
    def test_release(self):
        ticketer = Ticketer.create(self.org, self.user, MailgunType.slug, "Email (bob@acme.com)", {})

        contact = self.create_contact("Bob", twitter="bobby")

        ticket = Ticket.objects.create(
            org=self.org,
            ticketer=ticketer,
            contact=contact,
            subject="Need help",
            body="Where are my cookies?",
            status="O",
        )

        # release it
        ticketer.release()
        ticketer.refresh_from_db()
        self.assertFalse(ticketer.is_active)

        # ticket should be closed too
        ticket.refresh_from_db()
        self.assertEqual("C", ticket.status)

        # reactivate
        ticketer.is_active = True
        ticketer.save()

        # add a dependency and try again
        flow = self.create_flow()
        flow.ticketer_dependencies.add(ticketer)

        with self.assertRaises(AssertionError):
            ticketer.release()

        ticketer.refresh_from_db()
        self.assertTrue(ticketer.is_active)


class TicketerCRUDLTest(TembaTest, CRUDLTestMixin):
    def test_connect(self):
        connect_url = reverse("tickets.ticketer_connect")

        with override_settings(TICKETER_TYPES=[]):
            reload_ticketer_types()

            response = self.assertListFetch(connect_url, allow_viewers=False, allow_editors=False)

            self.assertEqual([], response.context["ticketer_types"])
            self.assertContains(response, "No ticketing services are available.")

        with override_settings(TICKETER_TYPES=["temba.tickets.types.mailgun.MailgunType"], MAILGUN_API_KEY="123"):
            reload_ticketer_types()

            response = self.assertListFetch(connect_url, allow_viewers=False, allow_editors=False)

            self.assertNotContains(response, "No ticketing services are available.")
            self.assertContains(response, reverse("tickets.types.mailgun.connect"))
