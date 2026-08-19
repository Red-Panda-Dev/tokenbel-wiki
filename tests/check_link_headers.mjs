/**
 * Юнит-тест runtime worker.js: Link-заголовки главной (RFC 8288/9727),
 * канонические content-type discovery-документов (/llms.txt, /auth.md,
 * /.well-known/api-catalog — RFC 9727) и regression-контроль content
 * negotiation.
 *
 * Запуск: node tests/check_link_headers.mjs  (входит в `make check` и build.sh).
 * env.ASSETS-биндинг заменяется стабом, реальная сеть не используется.
 * Стаб повторяет production Static Assets: text/markdown и text/plain
 * отдаются БЕЗ charset, файлу без расширения (/api-catalog) content-type
 * не присваивается вовсе — worker обязан выставить его сам. Тело каталога
 * и openapi.json читаются из static/, чтобы тест проверял реальные файлы.
 */

import { readFileSync } from "node:fs";
import worker from "../worker.js";

const BASE = "https://wiki.tokenbel.info";

const apiCatalogBody = readFileSync(
  new URL("../static/.well-known/api-catalog", import.meta.url),
  "utf8",
);
const openapiBody = readFileSync(
  new URL("../static/openapi.json", import.meta.url),
  "utf8",
);

// Объект окружения Worker: env.ASSETS — заменяем стабом, реальная сеть не используется.
const env = {
  ASSETS: {
    async fetch(input) {
      const url =
        typeof input === "string" ? new URL(input) : new URL(input.url);
      const path = url.pathname;
      const body =
        path === "/index.md"
          ? "# База знаний TokenBel\n"
          : path === "/auth.md"
            ? "# auth.md — доступ агентов к TokenBel Wiki\n"
            : path === "/llms.txt" || path === "/robots.txt"
              ? "# TokenBel Wiki\n"
              : path === "/.well-known/api-catalog"
                ? apiCatalogBody
                : path === "/openapi.json"
                  ? openapiBody
                  : "<html></html>";
      const headers = {};
      if (path === "/.well-known/api-catalog") {
        // Файл без расширения: production Static Assets не определяет content-type.
      } else if (path.endsWith(".md")) {
        headers["content-type"] = "text/markdown";
      } else if (path.endsWith(".txt")) {
        headers["content-type"] = "text/plain";
      } else if (path.endsWith(".css")) {
        headers["content-type"] = "text/css";
      } else if (path.endsWith(".json")) {
        headers["content-type"] = "application/json";
      } else {
        headers["content-type"] = "text/html; charset=utf-8";
      }
      return new Response(path.startsWith("/missing/") ? null : body, {
        status: path.startsWith("/missing/") ? 404 : 200,
        headers,
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

// --- Charset discovery-документов (Static Assets в проде отдаёт их без charset) ---
{
  const auth = await get("/auth.md");
  check(
    "auth.md gains charset",
    auth.headers.get("content-type"),
    "text/markdown; charset=utf-8",
  );
  check("auth.md has no link headers", linkHeader(auth), "");

  // /auth.md — статический ассет: Accept: text/markdown не включает negotiation.
  const authMd = await get("/auth.md", "text/markdown");
  check(
    "auth.md markdown accept same content-type",
    authMd.headers.get("content-type"),
    "text/markdown; charset=utf-8",
  );
  check("auth.md static asset: no vary", authMd.headers.get("vary"), null);

  const llms = await get("/llms.txt");
  check(
    "llms.txt gains charset",
    llms.headers.get("content-type"),
    "text/plain; charset=utf-8",
  );
  check("llms.txt has no link headers", linkHeader(llms), "");

  // Отрицательный контроль: прочие text/plain Worker не трогает.
  const robots = await get("/robots.txt");
  check(
    "robots.txt content-type untouched",
    robots.headers.get("content-type"),
    "text/plain",
  );
}

// --- /.well-known/api-catalog (RFC 9727) и /openapi.json ---
{
  const res = await get("/.well-known/api-catalog");
  check("api-catalog status", res.status, 200);
  check(
    "api-catalog gains linkset+json type",
    res.headers.get("content-type"),
    "application/linkset+json",
  );
  check("api-catalog has no link headers", linkHeader(res), "");
  check("api-catalog static asset: no vary", res.headers.get("vary"), null);

  // RFC 9727 §2: HEAD тоже должен отдавать каталог.
  const head = await worker.fetch(
    new Request(`${BASE}/.well-known/api-catalog`, { method: "HEAD" }),
    env,
  );
  check(
    "api-catalog HEAD content-type",
    head.headers.get("content-type"),
    "application/linkset+json",
  );

  const entry = (await res.json()).linkset?.[0];
  check("linkset anchor", entry?.anchor, `${BASE}/`);
  check(
    "linkset service-desc href",
    entry?.["service-desc"]?.[0]?.href,
    `${BASE}/openapi.json`,
  );
  check(
    "linkset service-doc href",
    entry?.["service-doc"]?.[0]?.href,
    `${BASE}/llms.txt`,
  );
  check(
    "linkset service-meta href",
    entry?.["service-meta"]?.[0]?.href,
    `${BASE}/auth.md`,
  );

  const specRes = await get("/openapi.json");
  check(
    "openapi.json content-type untouched",
    specRes.headers.get("content-type"),
    "application/json",
  );
  check("openapi.json has no link headers", linkHeader(specRes), "");
}

// --- Исходник openapi.json в static/ ---
{
  const spec = JSON.parse(openapiBody);
  check("openapi version", spec.openapi, "3.1.0");
  check("openapi server", spec.servers?.[0]?.url, BASE);
  check(
    "openapi documents the catalog path",
    Object.hasOwn(spec.paths, "/.well-known/api-catalog"),
    true,
  );
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
  "Link header validation passed (homepage + discovery docs + api-catalog + negotiation regression).",
);
