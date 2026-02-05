# Homebrew Distribution

This document explains how to set up Founder OS for Homebrew distribution.

## For Users

Once the tap is published, users can install with:

```bash
# Option 1: Add tap then install
brew tap jermaine-craig/os
brew install founder-os

# Option 2: One-liner
brew install jermaine-craig/os/founder-os
```

After installation:

```bash
# Run the setup wizard
founder-os-setup

# Then use with Claude Code
cd $(brew --prefix)/Founder-OS && claude
```

## For Maintainers

### Setting Up the Homebrew Tap

1. **Create a new repo for the tap**

   Create a repo named `homebrew-os` at:
   `https://github.com/jermaine-craig/homebrew-os`

2. **Add the formula**

   Copy `Formula/founder-os.rb` to the tap repo:
   ```
   homebrew-os/
   └── Formula/
       └── founder-os.rb
   ```

3. **Create a release**

   Tag a release on the main Founder-OS repo:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

4. **Update the formula SHA**

   Download the release tarball and get its SHA:
   ```bash
   curl -sL https://github.com/jermaine-craig/Founder-OS/archive/refs/tags/v1.0.0.tar.gz | shasum -a 256
   ```

   Update the `sha256` in the formula.

5. **Update Python dependency SHAs**

   Get the SHA for each Python package:
   ```bash
   pip download google-auth google-auth-oauthlib google-api-python-client --no-deps -d /tmp/deps
   cd /tmp/deps
   shasum -a 256 *.tar.gz
   ```

   Update the resource blocks in the formula.

### Updating the Formula

When releasing a new version:

1. Tag the release: `git tag v1.1.0 && git push origin v1.1.0`
2. Update the URL version in the formula
3. Update the SHA256 hash
4. Push to the homebrew-os repo

### Testing Locally

```bash
# Test the formula
brew install --build-from-source ./Formula/founder-os.rb

# Run tests
brew test founder-os

# Audit the formula
brew audit --strict founder-os
```

## Alternative: Homebrew Core

For wider distribution, you can submit to Homebrew core. Requirements:
- 30+ GitHub stars (or notable)
- Stable release
- No vendored dependencies that can use system versions
- Passes `brew audit --strict`

See: https://docs.brew.sh/Formula-Cookbook
