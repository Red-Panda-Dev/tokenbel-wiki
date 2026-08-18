/**
 * Юнит-тест runtime worker.js: Link-заголовки главной (RFC 8288/9727)
 * и regression-контроль content negotiation.
 *
 * Запуск: node tests/check_link_headers.mjs  (входит в `make check` и build.sh).
 * env.ASSETS-биндинг заменяется стабом, реальная сеть не используется.
 */

import worker from "../worker.js";

const BASE = "https://wiki.tokenbel.info";

// Объект окружения Worker: env.ASSETS — заменяем стабом, реальная сеть не используется.
const env = {
  ASSETS: {
    async fetch(input) {
      const url =
        typeof input === "string" ? new URL(input) : new URL(input.url);
      const path = url.pathname;
      const body =
        path === "/index.md" ? "# База знаний TokenBel\n" : "<html></html>";
      const type = path.endsWith(".md")
        ? "text/markdown; charset=utf-8"
        : path.endsWith(".css")
          ? "text/css"
          : "text/html; charset=utf-8";
      return new Response(path.startsWith("/missing/") ? null : body, {
        status: path.startsWith("/missing/") ? 404 : 200,
        headers: { "content-type": type },
      });
    },
  },
};

let failures = 0;

function check(name, actual, expected) {
  const ok = actual === expected;
  if (!ok) {
    failures += 1;
    console.error(
      `FAIL ${name}: expected ${JSON.stringify(expected)}, got ${JSON.stringify(actual)}`,
    );
  }
}

function linkHeader(response) {
  // Повторяющиеся заголовки Link читаются как одно значение через запятую (fetch spec).
  return response.headers.get("link") ?? "";
}

async function get(path, accept = "text/html,application/xhtml+xml") {
  const headers = accept ? { accept } : {};
  return worker.fetch(new Request(`${BASE}${path}`, { headers }), env);
}

// --- Link-заголовки главной (RFC 8288, relation type `describedby`, RFC 6903) ---
{
  const res = await get("/");
  check("home status", res.status, 200);
  const homeLinks = linkHeader(res);
  check(
    "home llms.txt link",
    homeLinks.includes('</llms.txt>; rel="describedby"; type="text/plain"'),
    true,
  );
  check(
    "home sitemap link",
    homeLinks.includes(
      '</sitemap.xml>; rel="describedby"; type="application/xml"',
    ),
    true,
  );
  check(
    "home has only the two links",
    homeLinks.split("</llms.txt>").length - 1,
    1,
  );
}

{
  const res = await get("/index.html");
  check(
    "home /index.html has link headers",
    linkHeader(res).includes("describedby"),
    true,
  );
}

{
  // Markdown-представление главной — тот же ресурс, те же describedby-ссылки.
  const res = await get("/", "text/markdown");
  check(
    "home markdown content-type",
    res.headers.get("content-type"),
    "text/markdown; charset=utf-8",
  );
  check(
    "home markdown link present",
    linkHeader(res).includes("describedby"),
    true,
  );
}

// --- Link-заголовки НЕ добавляются вне главной ---
{
  const article = await get("/news/article/");
  check("article has no link headers", linkHeader(article), "");

  const css = await get("/css/tailwind.min.css");
  check(
    "css content-type untouched",
    css.headers.get("content-type"),
    "text/css",
  );
  check("css has no link headers", linkHeader(css), "");

  const missing = await get("/missing/", "text/markdown");
  check("markdown fallback keeps 404", missing.status, 404);
  check("missing has no link headers", linkHeader(missing), "");
}

// --- Content negotiation regression ---
{
  const md = await get("/news/article/", "text/markdown");
  check(
    "article markdown content-type",
    md.headers.get("content-type"),
    "text/markdown; charset=utf-8",
  );
  check("article markdown vary", md.headers.get("vary"), "Accept");

  const html = await get("/news/article/", null);
  check(
    "browser gets html",
    html.headers.get("content-type"),
    "text/html; charset=utf-8",
  );
  check("browser no vary", html.headers.get("vary"), null);
}

if (failures > 0) {
  console.error(`Link header validation FAILED: ${failures} assertion(s)`);
  process.exit(1);
}
console.log(
  "Link header validation passed (homepage + negotiation regression).",
);
