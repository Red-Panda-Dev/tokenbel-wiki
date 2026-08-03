---
type: Build Script
title: Build Script
description: Pinned Cloudflare production build script for TokenBel Wiki
---

# Build Script

File: `build.sh`

The **pinned Cloudflare production build script** that downloads, verifies, and runs specific versions of Hugo and Node.js to produce a reproducible `public/` directory. It is **restricted to Linux x86_64** and is the authoritative build entrypoint for Cloudflare Workers Builds.

## Platform Requirement

```bash
require_linux_x64() {
  if [[ "$(uname -s)" != "Linux" || "$(uname -m)" != "x86_64" ]]; then
    printf 'build.sh supports the Cloudflare Linux x86_64 build environment. Use make dev or make build locally.\n' >&2
    exit 1
  fi
}
```

**Constraint**: Script exits with error on non-Linux or non-x86_64 systems.
**Fallback**: Use `make dev` or `make build` for local development on other platforms.

## Pinned Versions

```bash
HUGO_VERSION="0.164.0"
NODE_VERSION="24.18.1"
TZ="Europe/Amsterdam"
```

**Hugo**: Standard edition 0.164.0 (not Extended)
**Node.js**: 24.18.1 (LTS version matching Cloudflare environment)
**Timezone**: Europe/Amsterdam (matches production timezone)

## Directory Configuration

```bash
HUGO_CACHEDIR="${PWD}/.cache/hugo"
TOOLS_DIR="${PWD}/.cache/tools"
HUGO_BIN="${TOOLS_DIR}/hugo-${HUGO_VERSION}/hugo"
NODE_DIR="${TOOLS_DIR}/node-v${NODE_VERSION}-linux-x64"
```

**Cache directories:**
- `.cache/hugo` — Hugo cache (separate from Hugo's default)
- `.cache/tools` — Downloaded tool binaries

**Binary locations:**
- `.cache/tools/hugo-0.164.0/hugo` — Hugo binary
- `.cache/tools/node-v24.18.1-linux-x64/` — Node.js installation

## Logging

```bash
log() {
  printf '[build] %s\n' "$*"
}
```

All build steps are logged with `[build]` prefix for visibility in Cloudflare Workers Builds logs.

## Installation Functions

### install_hugo()

Downloads and installs Hugo 0.164.0 standard edition:

```bash
install_hugo() {
  if [[ -x "${HUGO_BIN}" ]] && [[ "$(${HUGO_BIN} version | awk '{print $2}')" == "v${HUGO_VERSION}"* ]]; then
    return  # Already installed and correct version
  fi

  # Download Hugo archive and checksums
  local archive="hugo_${HUGO_VERSION}_linux-amd64.tar.gz"
  local release_url="https://github.com/gohugoio/hugo/releases/download/v${HUGO_VERSION}"
  local download_dir="$(mktemp -d)"

  curl --fail --location --silent --show-error --output "${download_dir}/${archive}" "${release_url}/${archive}"
  curl --fail --location --silent --show-error --output "${download_dir}/checksums.txt" "${release_url}/hugo_${HUGO_VERSION}_checksums.txt"

  # Verify SHA-256 checksum
  (
    cd "${download_dir}"
    grep "  ${archive}$" checksums.txt | sha256sum --check --status -
  )

  # Extract and install
  rm -rf "${HUGO_BIN%/*}"
  mkdir -p "${HUGO_BIN%/*}"
  tar --extract --gzip --file "${download_dir}/${archive}" --directory "${HUGO_BIN%/*}" hugo
  rm -rf "${download_dir}"
}
```

**Steps:**
1. Check if Hugo is already installed and correct version
2. Download Hugo archive and checksum file from GitHub releases
3. Verify SHA-256 checksum against official checksums
4. Extract `hugo` binary to tools directory
5. Clean up temporary files

**Security**: SHA-256 verification ensures binary integrity.

### install_node_if_required()

Downloads and installs Node.js 24.18.1:

```bash
install_node_if_required() {
  if command -v node >/dev/null 2>&1 && [[ "$(node --version)" == "v${NODE_VERSION}" ]]; then
    return  # Already installed and correct version
  fi

  if [[ -x "${NODE_DIR}/bin/node" ]]; then
    export PATH="${NODE_DIR}/bin:${PATH}"
    return  # Already installed in tools directory
  fi

  # Download Node.js archive and checksums
  local archive="node-v${NODE_VERSION}-linux-x64.tar.xz"
  local release_url="https://nodejs.org/dist/v${NODE_VERSION}"
  local download_dir="$(mktemp -d)"

  curl --fail --location --silent --show-error --output "${download_dir}/${archive}" "${release_url}/${archive}"
  curl --fail --location --silent --show-error --output "${download_dir}/SHASUMS256.txt" "${release_url}/SHASUMS256.txt"

  # Verify SHA-256 checksum
  (
    cd "${download_dir}"
    grep "  ${archive}$" SHASUMS256.txt | sha256sum --check --status -
  )

  # Extract and install
  rm -rf "${NODE_DIR}"
  mkdir -p "${TOOLS_DIR}"
  tar --extract --xz --file "${download_dir}/${archive}" --directory "${TOOLS_DIR}"
  rm -rf "${download_dir}"
  export PATH="${NODE_DIR}/bin:${PATH}"
}
```

**Steps:**
1. Check if Node.js is already installed and correct version
2. Check if Node.js is already installed in tools directory
3. Download Node.js archive and checksum file from Node.js distribution
4. Verify SHA-256 checksum
5. Extract to tools directory
6. Add to PATH

**Security**: SHA-256 verification ensures binary integrity.

### install_node_dependencies()

Installs Node.js dependencies:

```bash
install_node_dependencies() {
  npm ci
}
```

Runs `npm ci` to install exact versions from `package-lock.json`.

**Purpose**: Install Tailwind CSS CLI and Wrangler.

### log_versions()

Logs installed versions for debugging:

```bash
log_versions() {
  log "Hugo: $(${HUGO_BIN} version)"
  log "Node.js: $(node --version)"
  log "npm: $(npm --version)"
  log "TZ: ${TZ}"
}
```

**Output**:
```
[build] Hugo: hugo v0.164.0+extended linux/amd64 BuildDate=unknown
[build] Node.js: v24.18.1
[build] npm: 10.8.2
[build] TZ: Europe/Amsterdam
```

### build_site()

Builds the Hugo site:

```bash
build_site() {
  "${HUGO_BIN}" --gc --minify --cleanDestinationDir --environment production
}
```

**Flags:**
- `--gc` — Remove unused files
- `--minify` — Minify output
- `--cleanDestinationDir` — Clean `public/` before build
- `--environment production` — Set environment to production

**Output**: Complete `public/` directory with all static files.

## Main Function

```bash
main() {
  require_linux_x64
  install_hugo
  install_node_if_required
  install_node_dependencies
  log_versions
  build_site
}
```

**Execution order:**
1. Verify Linux x86_64 platform
2. Install Hugo (if needed)
3. Install Node.js (if needed)
4. Install Node.js dependencies
5. Log versions
6. Build site

## Environment Variables

The script exports `TZ=Europe/Amsterdam` for consistent timezone handling during build.

## Relationships

* [Makefile](makefile.md) — Local development wrapper that calls this script
* [Tailwind Build](tailwind-build.md) — CSS compilation (called via `npm run css:build`)

## Citations

[1] `build.sh:1-10` — Script header and version configuration
[2] `build.sh:12-20` — require_linux_x64 function
[3] `build.sh:22-50` — install_hugo function with SHA-256 verification
[4] `build.sh:52-85` — install_node_if_required function with SHA-256 verification
[5] `build.sh:87-89` — install_node_dependencies function
[6] `build.sh:91-95` — log_versions function
[7] `build.sh:97-99` — build_site function
[8] `build.sh:101-107` — main function with execution order
[9] `package.json:8-9` — css:build script called by Node.js
[10] `package.json:5-7` — Tailwind and Wrangler dependencies
