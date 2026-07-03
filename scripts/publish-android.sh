#!/usr/bin/env bash
# Publishes the Android package to GitHub Packages, taking the credentials from
# your existing gh login. Run this once to grant the scope:
#   gh auth refresh -h github.com -s write:packages
set -euo pipefail
cd "$(dirname "$0")/../packages/android"

export JAVA_HOME="${JAVA_HOME:-$(/usr/libexec/java_home -v 17)}"
export ANDROID_HOME="${ANDROID_HOME:-$HOME/Library/Android/sdk}"
export GITHUB_ACTOR="${GITHUB_ACTOR:-$(gh api user --jq .login)}"
export GITHUB_TOKEN="${GITHUB_TOKEN:-$(gh auth token)}"

./gradlew publish
