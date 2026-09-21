from hey_cli.llm import generate_command

resp = generate_command("is my docker running", "Context:\n[Output of docker info]:\nDocker is not running.")
print(resp.model_dump_json(indent=2))
