import subprocess
import json

out = subprocess.run(
    ["python", "-c", "from hey_cli.llm import *; print(generate_command('is my docker running', 'Context:\\n[Output of docker info]:\\nDocker is not running.'))"],
    capture_output=True,
    text=True,
    cwd="/Users/mohit/github/hey-cli"
)
print("OUT:", out.stdout)
print("ERR:", out.stderr)
