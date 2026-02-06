#!/usr/bin/env bash
#
# Founder OS Installer
# https://os.engineering
#
# Usage:
#   curl -fsSL https://os.engineering/install | bash
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Config
REPO_URL="https://github.com/jermaine-craig/Founder-OS.git"
INSTALL_DIR="$PWD/founder-os"
MIN_PYTHON_VERSION="3.8"

print_banner() {
    echo ""
    echo -e "${BOLD}"
    echo "  ╔═══════════════════════════════════════╗"
    echo "  ║           Founder OS Installer        ║"
    echo "  ╚═══════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""
}

print_step() {
    echo -e "${BLUE}==>${NC} ${BOLD}$1${NC}"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}!${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Compare version strings
version_gte() {
    [ "$(printf '%s\n' "$1" "$2" | sort -V | head -n1)" = "$2" ]
}

# Get Python version
get_python_version() {
    "$1" -c 'import sys; print(".".join(map(str, sys.version_info[:2])))'
}

# Find suitable Python
find_python() {
    for cmd in python3 python; do
        if command_exists "$cmd"; then
            version=$(get_python_version "$cmd" 2>/dev/null || echo "0.0")
            if version_gte "$version" "$MIN_PYTHON_VERSION"; then
                echo "$cmd"
                return 0
            fi
        fi
    done
    return 1
}

# Check prerequisites
check_prerequisites() {
    print_step "Checking prerequisites..."

    local missing=()

    # Check git
    if ! command_exists git; then
        missing+=("git")
    else
        print_success "git found"
    fi

    # Check Python
    PYTHON_CMD=$(find_python) || true
    if [ -z "$PYTHON_CMD" ]; then
        missing+=("python3.8+")
    else
        version=$(get_python_version "$PYTHON_CMD")
        print_success "Python $version found ($PYTHON_CMD)"
    fi

    # Check pip
    if ! "$PYTHON_CMD" -m pip --version >/dev/null 2>&1; then
        missing+=("pip")
    else
        print_success "pip found"
    fi

    # Check Claude Code (optional but recommended)
    if command_exists claude; then
        print_success "Claude Code found"
    else
        print_warning "Claude Code not found (install from https://claude.ai/code)"
    fi

    if [ ${#missing[@]} -ne 0 ]; then
        echo ""
        print_error "Missing required dependencies: ${missing[*]}"
        echo ""
        echo "Please install the missing dependencies:"

        if [[ " ${missing[*]} " =~ " git " ]]; then
            echo "  - git: https://git-scm.com/downloads"
        fi

        if [[ " ${missing[*]} " =~ " python3.8+ " ]]; then
            echo "  - Python 3.8+: https://www.python.org/downloads/"
        fi

        if [[ " ${missing[*]} " =~ " pip " ]]; then
            echo "  - pip: $PYTHON_CMD -m ensurepip --upgrade"
        fi

        exit 1
    fi

    echo ""
}

# Clone or update the repository
install_repo() {
    print_step "Installing Founder OS..."

    if [ -d "$INSTALL_DIR" ]; then
        print_warning "Directory $INSTALL_DIR already exists"
        read -p "Remove and reinstall? [y/N] " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "$INSTALL_DIR"
        else
            print_warning "Keeping existing installation"
            return 0
        fi
    fi

    git clone --depth 1 "$REPO_URL" "$INSTALL_DIR"
    print_success "Cloned to $INSTALL_DIR"
    echo ""
}

# Install Python dependencies
install_dependencies() {
    print_step "Installing Python dependencies..."

    cd "$INSTALL_DIR"

    "$PYTHON_CMD" -m pip install --quiet --upgrade --user \
        google-auth \
        google-auth-oauthlib \
        google-api-python-client

    print_success "Dependencies installed"
    echo ""
}

# Print next steps
print_next_steps() {
    echo ""
    echo "  Files downloaded to $INSTALL_DIR"
    echo ""
    echo "  To finish setting up, run:"
    echo ""
    echo "    cd $INSTALL_DIR && ./setup"
    echo ""
    echo "  This will connect your Google account"
    echo "  (Gmail and Calendar) and configure your timezone."
    echo ""
    echo "  Need help? Visit https://os.engineering"
    echo ""
}

# Main
main() {
    print_banner
    check_prerequisites
    install_repo
    install_dependencies
    print_next_steps
}

main "$@"
