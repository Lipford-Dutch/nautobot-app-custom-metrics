r"""Headless screenshot capture for the Lipford Nautobot Metrics UI.

Runs inside a Playwright container attached to the lab's docker network so it can
reach the app by service name (``http://nautobot:8080``) over plain HTTP, avoiding
host HTTPS-upgrade issues. Saves PNGs to ``/out`` (mounted to ``audits/screenshots``).

Usage (from the repo root, with the dev stack running)::

    docker run --rm --network lipford-nautobot-metrics_default \\
      -v "$PWD/development/screenshots.py:/screenshots.py:ro" \\
      -v "$PWD/audits/screenshots:/out" \\
      mcr.microsoft.com/playwright/python:v1.47.0-jammy \\
      sh -c "pip install --quiet playwright==1.47.0 && python /screenshots.py"

Credentials default to the dev superuser (``admin``/``admin`` from
``creds.example.env``) and may be overridden via the ``SCREENSHOT_*`` env vars.
"""

import os
import sys

from playwright.sync_api import sync_playwright

BASE = os.getenv("SCREENSHOT_BASE_URL", "http://nautobot:8080")
USERNAME = os.getenv("SCREENSHOT_USERNAME", "admin")
CREDENTIAL = os.getenv("SCREENSHOT_PASSWORD", "admin")

PAGES = (
    ("01-dashboard", "/plugins/lipford-nautobot-metrics/"),
    ("02-metric-definitions", "/plugins/lipford-nautobot-metrics/metric-definitions/"),
    ("03-metric-values", "/plugins/lipford-nautobot-metrics/metric-values/"),
    ("04-navigation-home", "/"),
)


def main() -> int:
    """Log in, capture each page to /out, and return a process exit code."""
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_context(viewport={"width": 1600, "height": 1000}).new_page()

        page.goto(f"{BASE}/login/", wait_until="networkidle")
        page.fill("input[name='username']", USERNAME)
        page.fill("input[name='password']", CREDENTIAL)
        page.click("button[type='submit'], input[type='submit']")
        page.wait_for_load_state("networkidle")

        if "/login" in page.url:
            print("LOGIN FAILED, still at", page.url)
            return 2
        print("LOGIN OK ->", page.url)

        for name, path in PAGES:
            page.goto(f"{BASE}{path}", wait_until="networkidle")
            page.wait_for_timeout(800)
            out = f"/out/{name}.png"
            page.screenshot(path=out, full_page=True)
            print(f"SAVED {out}  (url={page.url}, title={page.title()!r})")

        page.goto(f"{BASE}/plugins/lipford-nautobot-metrics/metric-definitions/", wait_until="networkidle")
        link = page.query_selector("table tbody tr td a")
        if link:
            link.click()
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(600)
            page.screenshot(path="/out/05-metric-definition-detail.png", full_page=True)
            print(f"SAVED /out/05-metric-definition-detail.png (url={page.url})")
        else:
            print("NO definition rows found for detail screenshot")

        browser.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
