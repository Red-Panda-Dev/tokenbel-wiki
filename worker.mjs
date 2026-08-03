const PAGE_NUMBER_PATTERN = /^[1-9]\d*$/;
const PAGINATED_PATH_PREFIXES = [
  "/about/",
  "/guides/",
  "/news/",
  "/policies/",
  "/statistics/",
  "/tags/",
];

function supportsPagination(pathname) {
  return (
    !pathname.includes("/page/") &&
    PAGINATED_PATH_PREFIXES.some((prefix) => pathname.startsWith(prefix))
  );
}

function paginationAssetPath(pathname, pageNumber) {
  const basePath = pathname.endsWith("/") ? pathname : `${pathname}/`;
  return pageNumber === 1 ? basePath : `${basePath}page/${pageNumber}/`;
}

function badPageRequest() {
  return new Response("Недопустимый номер страницы.", {
    status: 400,
    headers: { "content-type": "text/plain; charset=UTF-8" },
  });
}

export default {
  async fetch(request, env) {
    if (request.method !== "GET" && request.method !== "HEAD") {
      return env.ASSETS.fetch(request);
    }

    const url = new URL(request.url);
    if (!supportsPagination(url.pathname)) {
      return env.ASSETS.fetch(request);
    }

    const pageParameters = url.searchParams.getAll("page");
    if (pageParameters.length === 0) {
      return env.ASSETS.fetch(request);
    }

    const pageParameter = pageParameters[0];
    if (
      pageParameters.length !== 1 ||
      !PAGE_NUMBER_PATTERN.test(pageParameter) ||
      !Number.isSafeInteger(Number(pageParameter))
    ) {
      return badPageRequest();
    }

    url.pathname = paginationAssetPath(url.pathname, Number(pageParameter));
    url.searchParams.delete("page");
    return env.ASSETS.fetch(new Request(url, request));
  },
};
