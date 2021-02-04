import pytest
from flask_babel import force_locale
from flask_babel import _


def test_finnish_translations(app):
    """ Test that translations exists for finnish. """

    # For flask_babel to work, we need to run in app context
    with app.app_context():
        # Setup locale to finnish
        with force_locale('fi_FI'):
            assert _("Hello World") == "Hei Maailma", "Message is not translated"

