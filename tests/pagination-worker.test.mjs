import assert from "node:assert/strict";
import test from "node:test";

import worker from "../worker.mjs";

function createAssets() {
  let request;
  return {
    async fetch(nextRequest) {
      request = nextRequest;
      return new Response("asset");
    },
    request() {
      return request;
    },
  };
}

async function dispatch(url, options = {}) {
  const assets = createAssets();
  const request = new Request(url, options);
  const response = await worker.fetch(request, { ASSETS: assets });
  return { assets, response };
}

test("rewrites a later pager query to Hugo's static pager asset", async () => {
  const { assets, response } = await dispatch(
    "https://wiki.tokenbel.info/news/?page=2&utm_source=test",
  );

  assert.equal(await response.text(), "asset");
  assert.equal(
    assets.request().url,
    "https://wiki.tokenbel.info/news/page/2/?utm_source=test",
  );
});

test("normalizes the first pager query to the section root", async () => {
  const { assets } = await dispatch("https://wiki.tokenbel.info/news/?page=1");

  assert.equal(assets.request().url, "https://wiki.tokenbel.info/news/");
});

test("rewrites taxonomy pager queries to Hugo's static pager assets", async () => {
  const { assets } = await dispatch("https://wiki.tokenbel.info/tags/финансы/?page=2");

  assert.equal(assets.request().url, "https://wiki.tokenbel.info/tags/%D1%84%D0%B8%D0%BD%D0%B0%D0%BD%D1%81%D1%8B/page/2/");
});

test("passes requests without a page parameter through unchanged", async () => {
  const { assets } = await dispatch("https://wiki.tokenbel.info/news/?utm_source=test");

  assert.equal(assets.request().url, "https://wiki.tokenbel.info/news/?utm_source=test");
});

test("does not treat static assets as paginated lists", async () => {
  const { assets } = await dispatch("https://wiki.tokenbel.info/favicon.svg?page=2");

  assert.equal(assets.request().url, "https://wiki.tokenbel.info/favicon.svg?page=2");
});

test("rejects malformed, duplicate, and unsafe page values", async () => {
  for (const url of [
    "https://wiki.tokenbel.info/news/?page=0",
    "https://wiki.tokenbel.info/news/?page=2&page=3",
    "https://wiki.tokenbel.info/news/?page=9007199254740992",
  ]) {
    const { assets, response } = await dispatch(url);
    assert.equal(response.status, 400);
    assert.equal(assets.request(), undefined);
  }
});

test("passes non-GET requests through unchanged", async () => {
  const { assets } = await dispatch("https://wiki.tokenbel.info/news/?page=2", {
    method: "POST",
  });

  assert.equal(assets.request().url, "https://wiki.tokenbel.info/news/?page=2");
});
