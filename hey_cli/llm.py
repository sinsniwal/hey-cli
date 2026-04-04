import json
import os
import platform
import ollama
from .models import CommandResponse, TroubleshootResponse

DEFAULT_MODEL = "gpt-oss:20b-cloud"

SYSTEM_PROMPT = r"""You are hey-cli, an autonomous, minimalist CLI companion and terminal expert. 
Your primary goal is to turn natural language objectives and error logs into actionable shell commands.
Your user intends to execute the command you provide.
Do NOT output markdown blocks or conversational text outside the required JSON schema.
Only output valid JSON matching the requested schema exactly.
You MUST provide "command", "explanation", and "needs_context" fields in your JSON output.
WARNING: Ensure any quotes inside your command (e.g. echo 'text') are single quotes, or properly escaped double quotes, to maintain valid JSON string structure.
CRITICAL PARSING RULE: If the user provides a specific filename, directory name, string, or port, you MUST preserve it EXACTLY as written. Do not autocorrect spelling, abbreviate, or drop extensions (e.g., if asked to make 'temporarily', do not output 'temporay').

IMPORTANT AGENTIC INSTRUCTION:
If the user asks ANY question about their system state, files, or environment (e.g., "is docker running?", "what is my IP?", "explain this folder"), you MUST set `needs_context = true` and target a bash command to silently gather the data.
ONLY set `needs_context = false` when you are providing the FINAL answer. 
If your final answer is an explanation or simply answering a question, leave the `command` field empty `""` and put a high-quality Markdown response in the `explanation` field. Do NOT write bash `echo` or `printf` statements.
If your final answer requires an action to be ran (e.g., "start docker", "delete the folder"), put the executable bash string in `command`.
CRITICAL JSON REQUIREMENT: If your bash command contains any backslashes (e.g. for regex like `\.` or escaping spaces), you MUST double-escape them (`\\\\.`) so the output remains valid JSON!
"""

from .skills import get_compiled_skills

def get_system_context() -> str:
    os_name = platform.system()
    os_release = platform.release()
    arch = platform.machine()
    shell = os.environ.get("SHELL", "unknown")
    
    skills_block = f"\n\n{get_compiled_skills()}"
         
    return f"Operating System: {os_name} {os_release} ({arch})\nCurrent Shell: {shell}{skills_block}"

TROUBLESHOOT_PROMPT = r"""You are acting as an iterative troubleshooter. 
You will be provided with an objective, the previous commands attempted, and the stdout/stderr.
Determine the next command to run to resolve the issue, OR if the issue is resolved, indicate it.
Keep your explanation brief and chill. If a file or tests do not exist, do not try to aggressively brute-force create configurations. Just explain the situation and set is_resolved=True to gracefully stop.
"""

def generate_command(prompt: str, context: str = "", model_name: str = DEFAULT_MODEL, history: list = None) -> CommandResponse:
    content = prompt
    if context:
        content = f"Context (e.g. error logs or piped data):\n{context}\n\nObjective:\n{prompt}"
        
    sys_context = f"--- ENVIRONMENT ---\n{get_system_context()}\n-------------------\n"
    msgs = [{"role": "system", "content": SYSTEM_PROMPT + "\n\n" + sys_context}]
    if history:
        msgs.extend(history)
    msgs.append({"role": "user", "content": content})
    
    max_retries = 3
    last_error = None
    raw_val = "None"

    for attempt in range(max_retries):
        try:
            response = ollama.chat(
                model=model_name,
                messages=msgs,
                format="json",
                options={"temperature": 0.0}
            )
            
            raw_val = response["message"]["content"]
            content_str = raw_val

            if content_str.startswith("```json"):
                content_str = content_str[7:-3].strip()
            elif content_str.startswith("```"):
                content_str = content_str[3:-3].strip()
                
            data = json.loads(content_str)
            return CommandResponse(**data)
            
        except Exception as e:
            last_error = e
            if "refusal" in raw_val.lower() or "sorry" in raw_val.lower():
                return CommandResponse(
                    command="",
                    explanation=f"LLM Safety Trigger: The model refused to generate this command.\n\nRaw output: {raw_val.strip()}",
                    needs_context=False
                )
            
            msgs.append({"role": "assistant", "content": raw_val})
            msgs.append({"role": "user", "content": f"Your JSON output failed validation: {str(e)}\nPlease strictly follow the schema and output ONLY valid JSON without markdown wrapping."})

    return CommandResponse(
        command="", 
        explanation=f"Error generating command from LLM after {max_retries} retries: {str(last_error)}\nRaw Output:\n{raw_val}"
    )

def generate_troubleshoot_step(objective: str, history: list, model_name: str = DEFAULT_MODEL) -> TroubleshootResponse:
    history_text = "\n".join([
        f"Cmd: {h['cmd']}\nExit: {h['exit_code']}\nOut/Err:\n{h['output']}"
        for h in history
    ])
    
    content = f"Objective:\n{objective}\n\nHistory of execution:\n{history_text}\n\nAnalyze the specific error and provide the NEXT logical command to test or fix. Re-read logs carefully."
    
    sys_context = f"--- ENVIRONMENT ---\n{get_system_context()}\n-------------------\n"
    msgs = [
        {"role": "system", "content": SYSTEM_PROMPT + "\n" + TROUBLESHOOT_PROMPT + "\n\n" + sys_context},
        {"role": "user", "content": content}
    ]
    
    max_retries = 3
    last_error = None
    raw_val = "None"

    for attempt in range(max_retries):
        try:
            response = ollama.chat(
                model=model_name,
                messages=msgs,
                format="json",
                options={"temperature": 0.0}
            )
            
            raw_val = response["message"]["content"].strip()
            if not raw_val:
                raise ValueError("LLM returned empty JSON object.")
                
            content_str = raw_val
            if content_str.startswith("```json"):
                content_str = content_str[7:-3].strip()
            elif content_str.startswith("```"):
                content_str = content_str[3:-3].strip()
                
            data = json.loads(content_str)
            return TroubleshootResponse(**data)
            
        except Exception as e:
            last_error = e
            msgs.append({"role": "assistant", "content": raw_val})
            msgs.append({"role": "user", "content": f"Your JSON output failed validation: {str(e)}\nFix the syntax and output ONLY strict JSON schema."})

    return TroubleshootResponse(
        command=None,
        explanation=f"Error analyzing execution after {max_retries} retries: {str(last_error)}\nRaw Output:\n{raw_val}",
        is_resolved=False
    )
