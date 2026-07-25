#!/usr/bin/env bash
# Repository-wide dependency upgrader.
#
# Usage:
#   scripts/force_dependency_upgrade.sh safe
#   scripts/force_dependency_upgrade.sh latest
#
# "safe" keeps declared compatibility ranges where the package manager supports it.
# "latest" also rewrites manifests to the latest available releases and can include
# breaking major-version changes. Generated/cache/vendor/archive directories are skipped.

set -uo pipefail

MODE="${1:-safe}"
case "$MODE" in
  safe|latest) ;;
  *)
    echo "Unsupported mode: $MODE (expected safe or latest)" >&2
    exit 2
    ;;
esac

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
SUMMARY_FILE="${GITHUB_STEP_SUMMARY:-/tmp/force-dependency-upgrade-summary.md}"
SUCCESS_COUNT=0
SKIP_COUNT=0
FAILURE_COUNT=0

cd "$ROOT"

cat >"$SUMMARY_FILE" <<EOF
## Repository dependency upgrade

- Mode: \`$MODE\`
- Repository root: \`$ROOT\`

| Ecosystem | Directory | Result |
|---|---|---|
EOF

log_result() {
  local ecosystem="$1"
  local directory="$2"
  local result="$3"
  printf '| %s | `%s` | %s |\n' "$ecosystem" "${directory#"$ROOT"/}" "$result" >>"$SUMMARY_FILE"
}

run_upgrade() {
  local ecosystem="$1"
  local directory="$2"
  shift 2

  echo "::group::[$ecosystem] ${directory#"$ROOT"/}"
  if (cd "$directory" && timeout 20m "$@"); then
    SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    log_result "$ecosystem" "$directory" "✅ upgraded"
    echo "::endgroup::"
    return 0
  fi

  FAILURE_COUNT=$((FAILURE_COUNT + 1))
  log_result "$ecosystem" "$directory" "❌ command failed"
  echo "::warning title=Dependency upgrade failed::$ecosystem upgrade failed in ${directory#"$ROOT"/}"
  echo "::endgroup::"
  return 0
}

skip_upgrade() {
  local ecosystem="$1"
  local directory="$2"
  local reason="$3"
  SKIP_COUNT=$((SKIP_COUNT + 1))
  log_result "$ecosystem" "$directory" "⏭️ $reason"
}

find_manifests() {
  local name="$1"
  find "$ROOT" \
    -type d \( \
      -name .git -o -name .cache -o -name node_modules -o -name vendor -o \
      -name .venv -o -name venv -o -name dist -o -name build -o \
      -name coverage -o -name .gradle -o -name .dart_tool -o \
      -name backup -o -name backups \
    \) -prune -o \
    -type f -name "$name" -print0
}

upgrade_node_project() {
  local package_file="$1"
  local directory
  directory="$(dirname "$package_file")"

  if ! command -v node >/dev/null 2>&1 || ! command -v npm >/dev/null 2>&1; then
    skip_upgrade "Node.js" "$directory" "Node.js/npm unavailable"
    return
  fi

  if [[ "$MODE" == "latest" ]]; then
    run_upgrade "Node.js manifest" "$directory" npx --yes npm-check-updates@latest -u
  fi

  if [[ -f "$directory/pnpm-lock.yaml" ]]; then
    if command -v corepack >/dev/null 2>&1; then corepack enable >/dev/null 2>&1 || true; fi
    if command -v pnpm >/dev/null 2>&1; then
      if [[ "$MODE" == "latest" ]]; then
        run_upgrade "pnpm" "$directory" pnpm update --latest --lockfile-only --ignore-scripts
      else
        run_upgrade "pnpm" "$directory" pnpm update --lockfile-only --ignore-scripts
      fi
    else
      skip_upgrade "pnpm" "$directory" "pnpm unavailable"
    fi
  elif [[ -f "$directory/yarn.lock" ]]; then
    if command -v corepack >/dev/null 2>&1; then corepack enable >/dev/null 2>&1 || true; fi
    if command -v yarn >/dev/null 2>&1; then
      if [[ "$MODE" == "latest" ]]; then
        run_upgrade "Yarn" "$directory" yarn upgrade --latest --ignore-scripts
      else
        run_upgrade "Yarn" "$directory" yarn upgrade --ignore-scripts
      fi
    else
      skip_upgrade "Yarn" "$directory" "Yarn unavailable"
    fi
  else
    if [[ "$MODE" == "latest" ]]; then
      run_upgrade "npm" "$directory" npm install --package-lock-only --ignore-scripts --legacy-peer-deps
    else
      run_upgrade "npm" "$directory" npm update --package-lock-only --ignore-scripts --legacy-peer-deps
    fi
  fi
}

upgrade_python_project() {
  local manifest="$1"
  local directory
  directory="$(dirname "$manifest")"

  if [[ -f "$directory/uv.lock" ]] && command -v uv >/dev/null 2>&1; then
    run_upgrade "Python/uv" "$directory" uv lock --upgrade
    return
  fi

  if [[ -f "$directory/poetry.lock" ]] && command -v poetry >/dev/null 2>&1; then
    run_upgrade "Python/Poetry" "$directory" poetry update --lock
    return
  fi

  if [[ -f "$directory/Pipfile.lock" ]] && command -v pipenv >/dev/null 2>&1; then
    run_upgrade "Python/Pipenv" "$directory" pipenv update
    return
  fi

  if [[ "$MODE" == "latest" && "$(basename "$manifest")" == requirements*.txt ]] && command -v pur >/dev/null 2>&1; then
    run_upgrade "Python requirements" "$directory" pur -r "$(basename "$manifest")"
    return
  fi

  skip_upgrade "Python" "$directory" "handled by recursive Dependabot"
}

upgrade_maven_project() {
  local pom="$1"
  local directory
  directory="$(dirname "$pom")"

  if ! command -v mvn >/dev/null 2>&1; then
    skip_upgrade "Maven" "$directory" "Maven unavailable"
    return
  fi

  if [[ "$MODE" == "latest" ]]; then
    run_upgrade "Maven" "$directory" mvn -B -ntp versions:use-latest-releases versions:update-parent -DgenerateBackupPoms=false -DprocessAllModules=true
  else
    run_upgrade "Maven" "$directory" mvn -B -ntp versions:use-latest-versions -DallowMajorUpdates=false -DgenerateBackupPoms=false -DprocessAllModules=true
  fi
}

upgrade_go_project() {
  local mod="$1"
  local directory
  directory="$(dirname "$mod")"

  if ! command -v go >/dev/null 2>&1; then
    skip_upgrade "Go" "$directory" "Go unavailable"
    return
  fi

  if [[ "$MODE" == "latest" ]]; then
    run_upgrade "Go" "$directory" bash -lc 'go get -u ./... && go mod tidy'
  else
    run_upgrade "Go" "$directory" bash -lc 'go get -u=patch ./... && go mod tidy'
  fi
}

upgrade_rust_project() {
  local manifest="$1"
  local directory
  directory="$(dirname "$manifest")"

  if ! command -v cargo >/dev/null 2>&1; then
    skip_upgrade "Rust" "$directory" "Cargo unavailable"
    return
  fi

  run_upgrade "Rust" "$directory" cargo update
}

upgrade_pub_project() {
  local manifest="$1"
  local directory
  directory="$(dirname "$manifest")"

  if command -v flutter >/dev/null 2>&1; then
    if [[ "$MODE" == "latest" ]]; then
      run_upgrade "Flutter" "$directory" flutter pub upgrade --major-versions
    else
      run_upgrade "Flutter" "$directory" flutter pub upgrade
    fi
  elif command -v dart >/dev/null 2>&1; then
    if [[ "$MODE" == "latest" ]]; then
      run_upgrade "Dart" "$directory" dart pub upgrade --major-versions
    else
      run_upgrade "Dart" "$directory" dart pub upgrade
    fi
  else
    skip_upgrade "Dart/Flutter" "$directory" "Dart/Flutter unavailable"
  fi
}

# Process each project once per primary manifest.
while IFS= read -r -d '' manifest; do upgrade_node_project "$manifest"; done < <(find_manifests package.json)
while IFS= read -r -d '' manifest; do upgrade_python_project "$manifest"; done < <(find_manifests pyproject.toml)
while IFS= read -r -d '' manifest; do upgrade_python_project "$manifest"; done < <(find_manifests 'requirements*.txt')
while IFS= read -r -d '' manifest; do upgrade_maven_project "$manifest"; done < <(find_manifests pom.xml)
while IFS= read -r -d '' manifest; do upgrade_go_project "$manifest"; done < <(find_manifests go.mod)
while IFS= read -r -d '' manifest; do upgrade_rust_project "$manifest"; done < <(find_manifests Cargo.toml)
while IFS= read -r -d '' manifest; do upgrade_pub_project "$manifest"; done < <(find_manifests pubspec.yaml)

{
  echo
  echo "### Result"
  echo
  echo "- Successful commands: $SUCCESS_COUNT"
  echo "- Skipped projects: $SKIP_COUNT"
  echo "- Failed commands: $FAILURE_COUNT"
  echo
  echo "> Docker, Gradle, NuGet, Composer, Bundler, Terraform, Git submodules, and package managers without an available runner tool remain covered by recursive Dependabot updates."
} >>"$SUMMARY_FILE"

# Keep partial successful changes available for review. A strict caller can opt in to failure.
if [[ "${STRICT_UPGRADE:-false}" == "true" && "$FAILURE_COUNT" -gt 0 ]]; then
  exit 1
fi

exit 0
