# Homebrew formula for Founder OS
# Install: brew tap jermaine-craig/os && brew install founder-os
# Or:      brew install jermaine-craig/os/founder-os

class FounderOs < Formula
  desc "Personal operating system for email, calendar, and meeting prep using Claude"
  homepage "https://os.engineering"
  url "https://github.com/jermaine-craig/Founder-OS/archive/refs/tags/v1.0.0.tar.gz"
  sha256 "PLACEHOLDER_SHA256" # Update with: shasum -a 256 v1.0.0.tar.gz
  license "MIT"
  head "https://github.com/jermaine-craig/Founder-OS.git", branch: "main"

  depends_on "python@3.11"

  resource "google-auth" do
    url "https://files.pythonhosted.org/packages/google-auth/google-auth-2.28.0.tar.gz"
    sha256 "PLACEHOLDER" # Update with actual sha256
  end

  resource "google-auth-oauthlib" do
    url "https://files.pythonhosted.org/packages/google-auth-oauthlib/google-auth-oauthlib-1.2.0.tar.gz"
    sha256 "PLACEHOLDER" # Update with actual sha256
  end

  resource "google-api-python-client" do
    url "https://files.pythonhosted.org/packages/google-api-python-client/google-api-python-client-2.118.0.tar.gz"
    sha256 "PLACEHOLDER" # Update with actual sha256
  end

  def install
    # Install Python dependencies
    venv = virtualenv_create(libexec, "python3.11")
    venv.pip_install resources

    # Install all files to prefix
    prefix.install Dir["*"]

    # Create setup command
    (bin/"founder-os-setup").write <<~EOS
      #!/bin/bash
      cd "#{prefix}"
      exec "#{libexec}/bin/python3" setup.py "$@"
    EOS
  end

  def post_install
    ohai "Founder OS installed!"
    ohai ""
    ohai "To complete setup, run:"
    ohai "  founder-os-setup"
    ohai ""
    ohai "Then open Claude Code in the Founder OS directory:"
    ohai "  cd #{prefix} && claude"
  end

  def caveats
    <<~EOS
      Founder OS requires Claude Code to function.
      Install Claude Code from: https://claude.ai/code

      To complete setup:
        founder-os-setup

      To start using Founder OS:
        cd #{prefix} && claude

      Then try:
        "Help me with my emails"
        "What's on my calendar this week?"
    EOS
  end

  test do
    # Test that Python dependencies are installed
    system libexec/"bin/python3", "-c", "import google.auth"
    system libexec/"bin/python3", "-c", "import googleapiclient"

    # Test that setup.py exists
    assert_predicate prefix/"setup.py", :exist?
  end
end
