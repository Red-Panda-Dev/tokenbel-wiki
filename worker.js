/**
 * TokenBel Wiki — content negotiation для AI-агентов.
 *
 * Единственная runtime-обязанность Worker (см. ARCHITECTURE.md): запросы
 * с `Accept: text/markdown` получают готовую Markdown-версию страницы
 * (`/path/` → `/path/index.md`, предгенерируется Hugo output format
 * "Markdown"). Все остальные запросы, включая браузеры, проходят в
 * статические ассеты без изменений.
 *
 * Фолбэк: если Markdown-варианта нет (404, /page/N/ пагинация, статика),
 * отдаётся обычный HTML-ответ.
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

export default {
  async fetch(request, env) {
    try {
      const accept = request.headers.get("accept");
      const url = new URL(request.url);

      if (!wantsMarkdown(accept) || STATIC_EXT.test(url.pathname)) {
        return env.ASSETS.fetch(request);
      }

      const markdownUrl = new URL(url);
      markdownUrl.pathname = markdownPath(url.pathname);
      const markdownResponse = await env.ASSETS.fetch(
        new Request(markdownUrl, request),
      );

      if (markdownResponse.status < 300) {
        const headers = new Headers(markdownResponse.headers);
        headers.set("content-type", "text/markdown; charset=utf-8");
        headers.set("vary", "Accept");
        return new Response(markdownResponse.body, {
          status: markdownResponse.status,
          headers,
        });
      }
    } catch {
      // Некорректный запрос (например, неразборчивый URL) — идём в статику.
    }

    // Markdown-версии нет — прозрачный фолбэк на HTML.
    return env.ASSETS.fetch(request);
  },
};
