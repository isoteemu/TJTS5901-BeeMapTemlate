import os
import unittest

import pytest
import requests

# Module requires website_staging environment variable to be defined, and it should be url pointing to staging website.

if not os.getenv("WEBSITE_STAGING"):
    pytest.skip(
        "No $WEBSITE_STAGING defined, skipping availability tests",
        allow_module_level=True,
    )


# Only run tests when "staging" has been marked. See: https://docs.pytest.org/en/latest/mark.html
@pytest.mark.staging
class AvailabilityTest(unittest.TestCase):
    def test_availability(self):
        """Fetch web page and check "200" is returned as status code.

        See explanation for status codes:
        https://en.wikipedia.org/wiki/List_of_HTTP_status_codes#2xx_success
        """

        # Get the webpage, and check status code
        url = os.getenv("WEBSITE_STAGING")
        status_code = requests.get(url).status_code

        self.assertEqual(
            status_code,
            200,
            f"Website {url!r} availability failed. Returned code was {status_code!r}.",
        )

        # TODO: Check that pages that shouldn't exists, won't.
