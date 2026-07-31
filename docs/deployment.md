# Cloudflare deployment

TokenBel Wiki is deployed as a **Cloudflare Worker with Static Assets**. It is not a Cloudflare Pages project, has no Worker runtime script, KV namespace, or origin server.

## Pinned build tools

| Tool | Version | Purpose |
| --- | --- | --- |
| Hugo | `0.164.0` (standard Linux x86_64 release) | Static-site build |
| Node.js | `24.18.1` | Runs npm and Wrangler |
| Wrangler | `4.118.0` | Validates and deploys the Worker |

The Hugo standard edition is intentional: the site has plain CSS and only uses Hugo's built-in `minify` and `fingerprint` Pipes, so it does not need Dart Sass or the Extended edition.

`build.sh` downloads Hugo and Node only when the pinned local cache is absent, validates each download against the upstream SHA-256 checksum list, sets `TZ=Europe/Amsterdam` and `HUGO_CACHEDIR=.cache/hugo`, runs `npm ci`, then runs Hugo in the `production` environment. It deliberately does not fetch Git history because `enableGitInfo: false` in `hugo.yaml`.

## Repository configuration

- Worker name: `tokenbel-wiki`
- Production branch: `main`
- Production domain (not connected by this change): `wiki.tokenbel.info`
- Configured Worker route hostname: `wi.tokenbel.info`
- Static asset directory: `./public`
- Missing URL behavior: nearest Hugo `404.html` with HTTP `404`
- Preview URLs: enabled in `wrangler.toml`

`wrangler.toml` has no `main`, bindings, account ID, token, secret, or custom `build` hook. It declares the `wi.tokenbel.info` routes and enables Workers observability logs and traces. Omitting the `build` hook is intentional: current Workers Builds documentation does not honor Wrangler Custom Builds as its dashboard build step. It also prevents `npx` from resolving an unpinned Wrangler before `build.sh` has executed `npm ci`. Workers Builds runs `./build.sh` as its explicit build command, then runs `npm run deploy` using the lockfile-installed Wrangler.

## Local validation

Docker and GNU Make are the normal local Hugo workflow:

```bash
make dev
make build
make check
```

The Makefile also wraps the package scripts for the Cloudflare Linux build flow:

```bash
make cloudflare-build
make deploy-dry-run
make deploy
```

`make deploy-dry-run` builds first and validates without publishing. `make deploy` builds first and publishes, so use it only after staging approval.

Validate the Cloudflare deployment configuration and its pinned npm dependency with:

```bash
npm ci
./build.sh
npm run deploy:dry-run

test -f public/index.html
test -f public/404.html
test ! -d public/public
git status --short
```

`build.sh` targets the Cloudflare Linux x86_64 build environment. On other local platforms, use the Docker-based Make targets for site development; the dry-run requires a Linux x86_64 environment (for example, the same Docker/Linux CI environment).

`public/`, `.cache/`, and `.wrangler/` are ignored and must never be committed.

## Cloudflare Workers Builds setup

Perform these dashboard actions after this configuration is merged. They cannot be represented safely as repository files and must be confirmed in the target Cloudflare account.

1. In **Workers & Pages**, create a Worker from Git and grant the Cloudflare GitHub App access only to `Red-Panda-Dev/tokenbel-wiki`.
2. Select the repository and set the Worker/project name to `tokenbel-wiki`.
3. In **Settings → Builds**, set the production branch to `main` and root directory to the repository root.
4. Set **Build command** to `./build.sh`. This downloads the pinned Hugo/Node tools when needed and runs the authoritative `npm ci`.
5. Set **Deploy command** to `npm run deploy`. This uses `node_modules/.bin/wrangler` installed by the preceding build command and therefore honors the lockfile pin.
6. Add build variable `SKIP_DEPENDENCY_INSTALL=true`, because `build.sh` runs the authoritative `npm ci`.
7. Enable non-production branch builds, preview URLs, and GitHub pull-request build status/comments. For the non-production deploy command, retain the Workers Builds default `npx wrangler versions upload` unless an explicit preview deployment policy is agreed.
8. Run the first build and retain the build log.

Do not add a Cloudflare API token to GitHub or this repository for this Git-connected workflow. Build variables are not runtime secrets; do not place credentials in them. Preview deployments are public and are not a security boundary.

## Staging and validation

Do **not** attach `wiki.tokenbel.info` for the first deployment. First validate the Worker preview URL or `workers.dev` URL, then preferably attach temporary custom domain `wiki-next.tokenbel.info`.

Replace `<staging-domain>` after the first successful build and run:

```bash
curl -I https://<staging-domain>/
curl -I https://<staging-domain>/guides/
curl -I https://<staging-domain>/non-existent-page/
curl -I https://<staging-domain>/favicon.svg
curl --silent --show-error https://<staging-domain>/non-existent-page/ | grep -q 'Страница не найдена'
curl -fsS https://<staging-domain>/robots.txt
curl -fsS https://<staging-domain>/sitemap.xml
```

Expected status codes are `200`, `200`, `404`, and `200`. Also review keyboard navigation, focus state, mobile layout, fingerprinted CSS, favicon, section links, and PR-preview URL. The canonical URL intentionally remains `https://wiki.tokenbel.info/` even on staging; verify it has no `localhost` references.

A repeated `./build.sh` from the same commit must succeed and must not modify tracked files.

## Production cutover (separate approval)

The `wi.tokenbel.info` route and custom domain are declared in `wrangler.toml`; publishing this configuration still requires the Cloudflare account and DNS state to be confirmed separately. The production hostname `wiki.tokenbel.info` remains unchanged by this change.

Before a separately approved cutover:

1. Make a fresh BookStack database backup and preserve uploads/attachments.
2. Record the current `wiki` DNS record and BookStack origin in the change ticket, including the exact rollback value.
3. Keep BookStack available, preferably read-only once the final content migration starts.
4. Complete the staging checklist and prepare smoke-test URLs.
5. Choose an owner and a short cutover window.

During cutover, remove or change the conflicting `wiki` DNS record, then add Worker Custom Domain `wiki.tokenbel.info` in the Cloudflare dashboard. Do not use `wiki.tokenbel.info/*`: Worker Custom Domains are hostnames. Wait for the certificate, then test homepage, section pages, 404, CSS, favicon, canonical URL, sitemap, and robots.txt. Do not delete BookStack after cutover; remove its public exposure only after validation.

## Rollback

Rollback immediately if the homepage fails, TLS is not issued, static assets return widespread 404 responses, content is missing, redirect loops occur, or the custom domain does not serve the Worker.

1. Remove or disable the Worker Custom Domain.
2. Restore the exact pre-cutover DNS record saved in the change ticket.
3. Check the BookStack homepage and TLS certificate.
4. Purge only the necessary Cloudflare cache entries.
5. Record the incident and do not repeat deployments until the fault is understood.

## Checklists

### Before merge

- [ ] `npm ci` passes.
- [ ] `./build.sh` passes.
- [ ] `npm run deploy:dry-run` passes.
- [ ] `public/index.html` and `public/404.html` exist.
- [ ] `public/public` does not exist.
- [ ] Hugo, Node, and Wrangler are pinned; `package-lock.json` is committed.
- [ ] `public/`, `.cache/`, and `.wrangler/` are untracked.
- [ ] A preview build has succeeded.

### Before production cutover

- [ ] Staging is validated.
- [ ] BookStack backup is complete.
- [ ] DNS rollback values are recorded.
- [ ] Smoke-test URLs and rollback owner are ready.
- [ ] 404, sitemap, robots.txt, and certificate work.

### After cutover

- [ ] Homepage and section pages return `200`.
- [ ] Unknown URLs return `404` with Hugo's 404 page.
- [ ] CSS and favicon return `200`.
- [ ] Canonical URL is correct.
- [ ] Dashboard links work.
- [ ] Workers Builds status is green.
- [ ] BookStack backup is retained.
