import os
import sys

def generate_formula(tap_path, version, checksums_dir):
    print(f"Generating Binary Formula for version {version}")
    
    # helper to read checksum
    def get_sha(filename):
        path = os.path.join(checksums_dir, f"{filename}.sha256")
        if not os.path.exists(path):
            print(f"Warning: Checksum file not found: {path}")
            return "MISSING_SHA"
        with open(path, "r") as f:
            return f.read().strip()

    sha_arm64 = get_sha("hey-macos-arm64")
    sha_x86_64 = get_sha("hey-macos-x86_64")
    sha_linux = get_sha("hey-linux-x86_64")

    base_url = f"https://github.com/sinsniwal/hey-cli/releases/download/{version}"

    ruby_template = f"""class HeyCli < Formula
  desc "A secure, zero-bloat CLI companion powered by Ollama"
  homepage "https://github.com/sinsniwal/hey-cli"
  version "{version}"
  license "MIT"

  on_macos do
    if Hardware::CPU.arm?
      url "{base_url}/hey-macos-arm64"
      sha256 "{sha_arm64}"
    else
      url "{base_url}/hey-macos-x86_64"
      sha256 "{sha_x86_64}"
    end
  end

  on_linux do
    if Hardware::CPU.is_64_bit?
      url "{base_url}/hey-linux-x86_64"
      sha256 "{sha_linux}"
    end
  end

  def install
    if OS.mac?
      bin.install Hardware::CPU.arm? ? "hey-macos-arm64" : "hey-macos-x86_64" => "hey"
    elsif OS.linux?
      bin.install "hey-linux-x86_64" => "hey"
    end
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
    assert_match "hey-cli", shell_output("#{{bin}}/hey --help")
  end
end
"""

    tap_dir = os.path.join(tap_path, "Formula")
    os.makedirs(tap_dir, exist_ok=True)
    
    formula_path = os.path.join(tap_dir, "hey-cli.rb")
    with open(formula_path, "w") as f:
        f.write(ruby_template)
        
    print(f"\nSuccessfully generated Binary Homebrew Formula at:\n{formula_path}")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python generate_brew.py <tap_path> <version> <checksums_dir>")
        sys.exit(1)
    
    generate_formula(sys.argv[1], sys.argv[2], sys.argv[3])
