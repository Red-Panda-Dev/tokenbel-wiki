#!/usr/bin/env bash
set -euo pipefail

HUGO_VERSION="0.164.0"
NODE_VERSION="24.18.1"
TZ="Europe/Amsterdam"
HUGO_CACHEDIR="${PWD}/.cache/hugo"
TOOLS_DIR="${PWD}/.cache/tools"
HUGO_BIN="${TOOLS_DIR}/hugo-${HUGO_VERSION}/hugo"
NODE_DIR="${TOOLS_DIR}/node-v${NODE_VERSION}-linux-x64"

export TZ HUGO_CACHEDIR

log() {
  printf '[build] %s\n' "$*"
}

require_linux_x64() {
  if [[ "$(uname -s)" != "Linux" || "$(uname -m)" != "x86_64" ]]; then
    printf 'build.sh supports the Cloudflare Linux x86_64 build environment. Use make dev or make build locally.\n' >&2
    exit 1
  fi
}

install_hugo() {
  if [[ -x "${HUGO_BIN}" ]] && [[ "$("${HUGO_BIN}" version | awk '{print $2}')" == "v${HUGO_VERSION}"* ]]; then
    return
  fi

  local archive="hugo_${HUGO_VERSION}_linux-amd64.tar.gz"
  local release_url="https://github.com/gohugoio/hugo/releases/download/v${HUGO_VERSION}"
  local download_dir
  download_dir="$(mktemp -d)"

  log "Downloading Hugo v${HUGO_VERSION} standard edition"
  curl --fail --location --silent --show-error --output "${download_dir}/${archive}" "${release_url}/${archive}"
  curl --fail --location --silent --show-error --output "${download_dir}/checksums.txt" "${release_url}/hugo_${HUGO_VERSION}_checksums.txt"
  (
    cd "${download_dir}"
    grep "  ${archive}$" checksums.txt | sha256sum --check --status -
  )

  rm -rf "${HUGO_BIN%/*}"
  mkdir -p "${HUGO_BIN%/*}"
  tar --extract --gzip --file "${download_dir}/${archive}" --directory "${HUGO_BIN%/*}" hugo
  rm -rf "${download_dir}"
}

install_node_if_required() {
  if command -v node >/dev/null 2>&1 && [[ "$(node --version)" == "v${NODE_VERSION}" ]]; then
    return
  fi

  if [[ -x "${NODE_DIR}/bin/node" ]]; then
    export PATH="${NODE_DIR}/bin:${PATH}"
    return
  fi

  local archive="node-v${NODE_VERSION}-linux-x64.tar.xz"
  local release_url="https://nodejs.org/dist/v${NODE_VERSION}"
  local download_dir
  download_dir="$(mktemp -d)"

  log "Downloading Node.js v${NODE_VERSION}"
  curl --fail --location --silent --show-error --output "${download_dir}/${archive}" "${release_url}/${archive}"
  curl --fail --location --silent --show-error --output "${download_dir}/SHASUMS256.txt" "${release_url}/SHASUMS256.txt"
  (
    cd "${download_dir}"
    grep "  ${archive}$" SHASUMS256.txt | sha256sum --check --status -
  )

  rm -rf "${NODE_DIR}"
  mkdir -p "${TOOLS_DIR}"
  tar --extract --xz --file "${download_dir}/${archive}" --directory "${TOOLS_DIR}"
  rm -rf "${download_dir}"
  export PATH="${NODE_DIR}/bin:${PATH}"
}

install_node_dependencies() {
  npm ci
}

log_versions() {
  log "Hugo: $("${HUGO_BIN}" version)"
  log "Node.js: $(node --version)"
  log "npm: $(npm --version)"
  log "TZ: ${TZ}"
}

build_site() {
  "${HUGO_BIN}" --gc --minify --cleanDestinationDir --environment production
  python3 tests/check_seo.py public content
  python3 tests/check_pagination.py public content hugo.yaml
  python3 tests/check_markdown.py public
  node --disable-warning=MODULE_TYPELESS_PACKAGE_JSON tests/check_link_headers.mjs
  test -f public/auth.md
  head -n 1 public/auth.md | grep -q 'auth\.md'
}

main() {
  require_linux_x64
  install_hugo
  install_node_if_required
  install_node_dependencies
  log_versions
  build_site
}

main "$@"
