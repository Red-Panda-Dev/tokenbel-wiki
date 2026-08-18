/**
 * TokenBel Wiki — агент-oriented runtime для Cloudflare Worker.
 *
 * Две runtime-обязанности Worker (см. ARCHITECTURE.md):
 *
 * 1. Content negotiation: запросы с `Accept: text/markdown` получают готовую
 *    Markdown-версию страницы (`/path/` → `/path/index.md`, предгенерируется
 *    Hugo output format "Markdown"). Браузеры и прочие запросы проходят в
 *    статические ассеты без изменений. Если Markdown-варианта нет (404,
 *    /page/N/ пагинация, статика) — прозрачный фолбэк на HTML.
 *
 * 2. Обогащение обнаружения (RFC 8288/9727): ответы главной получают
 *    `Link` с зарегистрированным relation type `describedby` (RFC 6903) на
 *    машиночитаемые описания сайта — /llms.txt и /sitemap.xml. Relation types
 *    из RFC 9727/8631 (api-catalog, service-desc, service-doc) не применяются:
 *    у сайта нет API. Кроме того, discovery-документы с кириллицей (/llms.txt,
 *    /auth.md) получают явный `charset=utf-8`: Static Assets не добавляет
 *    charset к text/markdown и text/plain, и клиенты без него неверно
 *    декодируют UTF-8 (CP1252-моджибейк); файл _headers тут не вариант — его
 *    правила не применяются к ответам, прошедшим через Worker при
 *    run_worker_first (документация Cloudflare Static Assets).
 */

const STATIC_EXT =
  /\.(?:css|js|mjs|map|json|png|jpe?g|webp|gif|svg|ico|xml|txt|md|pdf|zip|gz|avif|wasm|webmanifest|woff2?)$/i;

function wantsMarkdown(accept) {
  return accept !== null && accept.includes("text/markdown");
}

function markdownPath(pathname) {
  let path = pathname;
  if (path.endsWith(".html")) {
    path = path.slice(0, -5);
  }
  if (!path.endsWith("/")) {
    path += "/";
  }
  return `${path}index.md`;
}

// Машиночитаемые описания сайта для Link-заголовков главной (RFC 8288).
const HOMEPAGE_LINKS = [
  '</llms.txt>; rel="describedby"; type="text/plain"',
  '</sitemap.xml>; rel="describedby"; type="application/xml"',
];

function isHomepage(pathname) {
  return pathname === "/" || pathname === "/index.html";
}

function withHomepageLinks(response) {
  const headers = new Headers(response.headers);
  for (const link of HOMEPAGE_LINKS) {
    headers.append("link", link);
  }
  return new Response(response.body, {
    status: response.status,
    headers,
  });
}

// Discovery-документы с кириллицей: Static Assets отдаёт text/markdown и
// text/plain без charset — выставляем его явно (см. шапку файла, п. 2).
const DISCOVERY_TYPES = {
  "/auth.md": "text/markdown; charset=utf-8",
  "/llms.txt": "text/plain; charset=utf-8",
};

function withDiscoveryCharset(response, pathname) {
  const type = DISCOVERY_TYPES[pathname];
  if (type === undefined || response.status !== 200) {
    return response;
  }
  const headers = new Headers(response.headers);
  headers.set("content-type", type);
  return new Response(response.body, {
    status: response.status,
    headers,
  });
}

async function serve(url, request, env) {
  const accept = request.headers.get("accept");

  if (!wantsMarkdown(accept) || STATIC_EXT.test(url.pathname)) {
    return env.ASSETS.fetch(request);
  }

  url.pathname = markdownPath(url.pathname);
  const markdownResponse = await env.ASSETS.fetch(new Request(url, request));

  if (markdownResponse.status < 300) {
    const headers = new Headers(markdownResponse.headers);
    headers.set("content-type", "text/markdown; charset=utf-8");
    headers.set("vary", "Accept");
    return new Response(markdownResponse.body, {
      status: markdownResponse.status,
      headers,
    });
  }

  // Markdown-версии нет — прозрачный фолбэк на HTML.
  return env.ASSETS.fetch(request);
}

export default {
  async fetch(request, env) {
    let response;
    try {
      response = await serve(new URL(request.url), request, env);
    } catch {
      // Некорректный запрос (например, неразборчивый URL) — идём в статику.
      response = await env.ASSETS.fetch(request);
    }

    try {
      const { pathname } = new URL(request.url);
      if (isHomepage(pathname)) {
        response = withHomepageLinks(response);
      }
      response = withDiscoveryCharset(response, pathname);
    } catch {
      // URL неразборчив — оставляем ответ как есть.
    }
    return response;
  },
};
