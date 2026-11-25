"""Browser smoke test of the built site. See README for Playwright setup."""

import re
from pathlib import Path
from urllib.parse import urlsplit

from playwright.sync_api import expect, sync_playwright

PUBLIC = Path("public")
ORIGIN = "http://wiki.test"
FENCE = re.compile(r"^```mermaid\s*\n(.*?)^```", re.MULTILINE | re.DOTALL)
# Independent expectations for the simple flowchart statements used by the wiki.
# Other Mermaid constructs still get the per-fence rendering check.
NODE = re.compile(r'\b(\w+)(?:\[([^\]\n]+)\]|\{([^}\n]+)\})')
EDGE = re.compile(
    r'^\s*(\w+)(?:\[[^\]]*\]|\{[^}]*\})?\s+(?:--\s+(.*?)\s+)?-->(?:\|([^|]*)\|)?\s+(\w+)', re.M
)


def serve(route):
    """Serve local build artifacts; do not depend on CDNs or a running server."""
    if not route.request.url.startswith(ORIGIN + "/"):
        route.abort()
        return
    path = PUBLIC / urlsplit(route.request.url).path.lstrip("/")
    if path.is_dir():
        path = path / "index.html"
    if path.is_file():
        route.fulfill(path=path)
    else:
        route.fulfill(status=404, body="")


def check_labels(svg, source):
    def text(selector):
        # Wrapped SVG labels contain separate tspans without whitespace between them.
        return svg.locator(selector).evaluate("""el => {
            const lines = [...el.querySelectorAll('tspan')];
            return lines.length ? lines.map(t => t.textContent).join(' ') : el.textContent;
        }""")

    for key, rectangle, diamond in NODE.findall(source):
        assert text(f'.pele-node[data-id="{key}"] text') == (rectangle or diamond).strip('"')
    for start, inline, pipe, end in EDGE.findall(source):
        edge = f'[data-id="L_{start}_{end}_0"]'
        expect(svg.locator(f'.pele-edge{edge}')).to_have_count(1)
        if inline or pipe:
            assert text(f'.pele-edge-label{edge} text') == (inline or pipe).strip('"')


def main():
    pages = {}
    for file in Path("content").rglob("index.md"):
        blocks = FENCE.findall(file.read_text(encoding="utf-8"))
        if blocks:
            rel = file.relative_to("content")
            assert FENCE.findall((PUBLIC / rel).read_text(encoding="utf-8")) == blocks, rel
            pages[rel.parent.as_posix()] = blocks
    assert pages, "Сначала соберите сайт с Mermaid-диаграммами"

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()
        page.route("**/*", serve)
        page.goto(ORIGIN)
        expect(page.locator('script[src*="/js/diagrams."]')).to_have_count(0)
        for width in (320, 1280):
            page.set_viewport_size({"width": width, "height": 800})
            for path, blocks in pages.items():
                page.goto(f"{ORIGIN}/{path}/")
                figures = page.locator("figure.mermaid-figure")
                expect(figures).to_have_count(len(blocks))
                for i, source in enumerate(blocks):
                    figure = figures.nth(i)
                    svg = figure.locator("[data-mermaid] > svg.pele")
                    expect(svg).to_be_visible()
                    box = figure.bounding_box()
                    assert box and 0 <= box["x"] <= width - box["width"] + 1, (path, i, width)
                    if source.startswith("flowchart "):
                        check_labels(svg, source)
        # One malformed block must not consume its neighbour or erase its source.
        loader = page.locator('script[src*="/js/diagrams."]').get_attribute("src")
        assert loader
        page.set_content('<div data-mermaid>Ошибка схемы</div><div data-mermaid>flowchart TD\nA --> B</div>')
        page.add_script_tag(url=ORIGIN + loader)
        expect(page.locator('[data-mermaid]').first).to_have_text('Ошибка схемы')
        expect(page.locator('[data-mermaid]').last.locator('svg.pele')).to_be_visible()
        browser.close()
    print(f"Pele: {sum(map(len, pages.values()))} схем на {len(pages)} страницах при 320 и 1280 px.")


if __name__ == "__main__":
    main()
