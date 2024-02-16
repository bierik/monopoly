import os
import re
import subprocess

from playwright.sync_api import expect


def test_has_title(page, live_server):
    breakpoint()

    # page.goto("https://playwright.dev/")

    # # Expect a title "to contain" a substring.
    # expect(page).to_have_title(re.compile("Playwright"))    # expect(page).to_have_title(re.compile("Playwright"))
