from collections import deque
from pathlib import Path
from urllib.parse import urljoin, urlparse
from playwright.sync_api import sync_playwright


def safe_name(url: str) -> str:
    name = url.replace("https://", "").replace("http://", "")
    name = "".join(c if c.isalnum() or c in "-._" else "_" for c in name)
    return (name[:180] or "page") + ".mhtml"


def crawl_and_save(start_url: str, output_dir: str = "mhtml_output", max_pages: int = 10) -> None:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    start_origin = urlparse(start_url).netloc
    visited = set()
    queue = deque([start_url])

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        while queue and len(visited) < max_pages:
            url = queue.popleft()
            if url in visited:
                continue

            try:
                print(f"Visiting: {url}")
                page.goto(url, wait_until="networkidle", timeout=60000)
                visited.add(url)

                cdp = context.new_cdp_session(page)
                snapshot = cdp.send("Page.captureSnapshot", {"format": "mhtml"})
                (output_path / safe_name(url)).write_text(snapshot["data"], encoding="utf-8")

                links = page.eval_on_selector_all(
                    "a[href]",
                    """els => els.map(a => a.href)"""
                )

                for link in links:
                    parsed = urlparse(link)
                    if parsed.scheme in ("http", "https") and parsed.netloc == start_origin:
                        if link not in visited:
                            queue.append(link)

            except Exception as e:
                print(f"Failed on {url}: {e}")

        browser.close()


if __name__ == "__main__":
    crawl_and_save("https://www.thanhle.it.com/", max_pages=5)