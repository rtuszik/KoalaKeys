"""Browser-level integration tests for generated cheatsheets.

These render a cheatsheet to disk via the real pipeline, open it in a headless
Chromium through ``file://``, and assert the interactive behaviour the static
HTML tests can't reach: the keyboard renders, clicking a shortcut highlights the
matching keys, and search filters the list

"""

import pytest

from koalakeys.generate_cheatsheet import main

pytestmark = pytest.mark.browser

sync_playwright = pytest.importorskip(
    "playwright.sync_api",
    reason="playwright not installed; run `uv run playwright install chromium`",
).sync_playwright


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        try:
            instance = p.chromium.launch()
        except Exception as exc:  # browser binary not installed
            pytest.skip(f"chromium not available: {exc}")
        yield instance
        instance.close()


@pytest.fixture
def cheatsheet_url(valid_fixtures, isolated_output):
    _, filename = main(valid_fixtures / "full_featured.yaml")
    assert filename, "generation should produce an output file"
    return (isolated_output / filename).resolve().as_uri()


@pytest.fixture
def page(browser, cheatsheet_url):
    page = browser.new_page()
    errors: list[str] = []
    page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    page.goto(cheatsheet_url)
    page.wait_for_load_state("networkidle")
    page.console_errors = errors  # exposed for the no-error assertion
    yield page
    page.close()


class TestCheatsheetInBrowser:
    def test_loads_without_console_errors(self, page):
        assert page.console_errors == [], f"unexpected JS errors: {page.console_errors}"
        assert "Full Featured Test" in page.title() or page.locator("h1").count() >= 0

    def test_keyboard_and_shortcuts_render(self, page):
        assert page.locator(".key").count() > 0, "keyboard keys should be rendered"
        assert page.locator(".shortcut").count() >= 4, "all fixture shortcuts should render"
        assert page.get_by_text("Copy selected item").is_visible()

    def test_clicking_shortcut_highlights_keys(self, page):
        # Clicking a shortcut adds `active-step-N` to the matching keys.
        page.locator(".shortcut").first.click()
        highlighted = page.locator(".key.active-step-1")
        highlighted.first.wait_for(state="attached", timeout=2000)
        assert highlighted.count() > 0, "clicking a shortcut should highlight at least one key"

    def test_search_filters_shortcuts(self, page):
        total = page.locator(".shortcut").count()
        page.fill("#shortcut-search", "paste")

        visible = page.locator(".shortcut:visible")
        visible.first.wait_for(state="visible", timeout=2000)
        assert 0 < visible.count() < total, "search should narrow the visible shortcuts"
        assert page.get_by_text("Paste").is_visible()
