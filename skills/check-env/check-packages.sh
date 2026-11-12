#!/usr/bin/env bash
# Read-only inventory. Bash 3.2+; no distro-specific installation assumptions.
skip_python=false
requested_python=''
while [ "$#" -gt 0 ]; do
    case "$1" in
        --skip-python-packages) skip_python=true; shift ;;
        --python)
            if [ "$#" -lt 2 ] || [ -z "$2" ]; then
                printf '%s\n' 'Usage: check-packages.sh [--python PATH] [--skip-python-packages]' >&2
                exit 2
            fi
            requested_python=$2; shift 2 ;;
        *) printf 'Unknown argument: %s\n' "$1" >&2; exit 2 ;;
    esac
done

script_dir=$(CDPATH='' cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd) || exit 2
missing_cli=()
python_exe=''
python_found=false

find_application() {
    type -P -- "$1" 2>/dev/null
}

check_cli() {
    local name=$1 arg=$2 candidate exe='' result status
    shift 2
    for candidate in "$@"; do
        exe=$(find_application "$candidate")
        [ -n "$exe" ] && break
    done
    if [ -z "$exe" ]; then
        printf '[MISSING] %s\n' "$name"
        missing_cli+=("$name")
        return
    fi
    result=$("$exe" "$arg" 2>&1); status=$?
    if [ "$status" -eq 0 ]; then
        printf '[OK] %s %s (%s)\n' "$name" "${result%%$'\n'*}" "$exe"
    else
        printf '[UNKNOWN] %s found, version probe failed: exit %s (%s)\n' "$name" "$status" "$exe"
    fi
}

printf '%s\n' '=== CLI tools (inventory, not mandatory dependencies) ==='
if [ -n "$requested_python" ]; then
    python_candidates=("$requested_python")
else
    python_candidates=(python3 python)
fi
for candidate in "${python_candidates[@]}"; do
    exe=$(find_application "$candidate")
    [ -z "$exe" ] && continue
    python_found=true
    result=$("$exe" --version 2>&1); status=$?
    if [ "$status" -eq 0 ]; then
        python_exe=$exe
        printf '[OK] python %s (%s)\n' "${result%%$'\n'*}" "$exe"
        break
    fi
    printf '[UNKNOWN] Python candidate found, version probe failed (%s)\n' "$exe"
done
if [ -z "$python_exe" ]; then
    if [ "$python_found" = true ]; then
        printf '%s\n' '[UNKNOWN] No usable Python selected; its probe failed.'
    else
        printf '%s\n' '[MISSING] Python executable not found.'
    fi
fi

for name in node git curl jq gh rg; do check_cli "$name" --version "$name"; done
check_cli fd --version fd fdfind
check_cli ffmpeg -version ffmpeg
check_cli bat --version bat batcat
check_cli uv --version uv

if [ "$skip_python" = false ]; then
    printf '\n%s\n' '=== Python distributions (selected interpreter only) ==='
    if [ -n "$python_exe" ]; then
        "$python_exe" "$script_dir/check-python-packages.py"
        status=$?
        if [ "$status" -ne 0 ]; then printf '%s\n' '[UNKNOWN] Python metadata check did not complete.'; fi
    else
        printf '%s\n' '[UNKNOWN] Python packages were not checked; no usable interpreter.'
    fi
fi

if [ "${#missing_cli[@]}" -gt 0 ]; then
    printf '\n%s\n' '=== Suggestions only; install only what the task needs ==='
    printf '%s\n' 'Use project instructions and your platform package manager (for example apt, dnf, or brew).'
    for name in "${missing_cli[@]}"; do
        case "$name" in
            gh) printf '%s\n' 'GitHub CLI: https://cli.github.com/' ;;
            uv) printf '%s\n' 'uv: https://docs.astral.sh/uv/getting-started/installation/' ;;
            *) printf 'Check the appropriate package for: %s\n' "$name" ;;
        esac
    done
fi
exit 0
