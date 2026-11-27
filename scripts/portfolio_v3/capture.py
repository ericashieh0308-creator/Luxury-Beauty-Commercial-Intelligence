"""Capture verified public demo states from a running local Streamlit app."""
import argparse
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "portfolio/v3/evidence"


def capture(url, executable):
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path=executable)
        page = browser.new_page(viewport={"width": 1540, "height": 990}, device_scale_factor=1)
        page.goto(url)
        page.get_by_text("PUBLIC DEMO", exact=False).wait_for()

        def snap(name, visible):
            page.get_by_text(visible, exact=True).first.wait_for()
            page.wait_for_timeout(700)
            assert page.get_by_test_id("stException").count() == 0
            assert "PRIVATE LOCAL MODE" not in page.locator("body").inner_text()
            page.screenshot(path=EVIDENCE / f"{name}.png", animations="disabled")

        page.get_by_test_id("stMetricValue").first.get_by_text("36", exact=True).wait_for()
        page.get_by_text("Representative products by category", exact=True).wait_for(state="attached")
        snap("01-executive", "Catalog snapshot")
        page.get_by_text("Commercial intelligence", exact=True).click()
        snap("02-commercial", "Brand and category portfolio")
        page.get_by_text("Financial performance", exact=True).click()
        snap("03-base", "USD 155,493")
        page.get_by_text("Bull", exact=True).click()
        snap("04-bull", "USD 204,022")
        page.get_by_text("Promotion & scenario simulator", exact=True).click()
        snap("05-offer", "Breakeven units 1,218.0")
        uplift = page.get_by_role("slider", name="Assumed volume response (%)")
        uplift.focus()
        for _ in range(10):
            uplift.press("ArrowRight")
        page.get_by_text("Promotion ROI", exact=False).wait_for()
        page.get_by_text("Profit impact $2,067", exact=False).wait_for()
        snap("06-uplift", "Breakeven units 1,218.0")
        browser.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:8501")
    parser.add_argument("--chromium")
    args = parser.parse_args()
    capture(args.url, args.chromium)
