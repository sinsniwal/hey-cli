import json
import urllib.request
import os
import sys

def generate_formula():
    package_name = "hey-cli-python"
    url = f"https://pypi.org/pypi/{package_name}/json"
    
    print(f"Fetching latest PyPI metadata for {package_name}...")
    try:
        response = urllib.request.urlopen(url)
        data = json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"Error fetching from PyPI: {e}")
        sys.exit(1)

    version = data["info"]["version"]
    releases = data["releases"][version]
    
    # Find the tar.gz release
    tar_url = None
    sha256 = None
    for release in releases:
        if release["filename"].endswith(".tar.gz"):
            tar_url = release["url"]
            sha256 = release["digests"]["sha256"]
            break
            
    if not tar_url or not sha256:
        print("Error: Could not find .tar.gz release on PyPI.")
        sys.exit(1)
        
    print(f"Found version: {version}")
    print(f"Tarball URL: {tar_url}")
    print(f"SHA256: {sha256}")

    ruby_template = f"""class HeyCli < Formula
  include Language::Python::Virtualenv

  desc "A secure, zero-bloat CLI companion powered by Ollama"
  homepage "https://github.com/sinsniwal/hey-cli"
  url "{tar_url}"
  sha256 "{sha256}"
  license "MIT"

  depends_on "python@3.12"

  resource "markdown-it-py" do
    url "https://files.pythonhosted.org/packages/5b/f5/4ec618ed16cc4f8fb3b701563655a69816155e79e24a17b651541804721d/markdown_it_py-4.0.0.tar.gz"
    sha256 "cb0a2b4aa34f932c007117b194e945bd74e0ec24133ceb5bac59009cda1cb9f3"
  end

  resource "mdurl" do
    url "https://files.pythonhosted.org/packages/d6/54/cfe61301667036ec958cb99bd3efefba235e65cdeb9c84d24a8293ba1d90/mdurl-0.1.2.tar.gz"
    sha256 "bb413d29f5eea38f31dd4754dd7377d4465116fb207585f97bf925588687c1ba"
  end

  resource "Pygments" do
    url "https://files.pythonhosted.org/packages/c3/b2/bc9c9196916376152d655522fdcebac55e66de6603a76a02bca1b6414f6c/pygments-2.20.0.tar.gz"
    sha256 "6757cd03768053ff99f3039c1a36d6c0aa0b263438fcab17520b30a303a82b5f"
  end

  resource "rich" do
    url "https://files.pythonhosted.org/packages/b3/c6/f3b320c27991c46f43ee9d856302c70dc2d0fb2dba4842ff739d5f46b393/rich-14.3.3.tar.gz"
    sha256 "b8daa0b9e4eef54dd8cf7c86c03713f53241884e814f4e2f5fb342fe520f639b"
  end

  def install
    virtualenv_install_with_resources
  end

  def caveats
    <<~EOS
      hey-cli requires a local language model to function.
      If you do not have Ollama installed, please download it from:
      https://ollama.com/download/mac

      Once Ollama is installed, gracefully pull the default model:
      ollama pull gpt-oss:20b-cloud
    EOS
  end

  test do
    # Verify the native bash execution connects to the entry handler
    assert_match "hey-cli", shell_output("#{{bin}}/hey --help")
  end
end
"""

    tap_dir = os.path.expanduser("~/github/homebrew-hey-cli/Formula")
    os.makedirs(tap_dir, exist_ok=True)
    
    formula_path = os.path.join(tap_dir, "hey-cli.rb")
    with open(formula_path, "w") as f:
        f.write(ruby_template)
        
    print(f"\nSuccessfully generated Homebrew Formula at:\n{formula_path}")

if __name__ == "__main__":
    generate_formula()
