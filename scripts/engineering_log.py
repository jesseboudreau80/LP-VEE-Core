from openai import OpenAI
import os
from datetime import datetime, UTC
import argparse

LOG_PATH = "ENGINEERING_LOG.md"
client = OpenAI()


def read_log():
    if not os.path.exists(LOG_PATH):
        return ""
    with open(LOG_PATH, "r") as f:
        return f.read()


def append_log(entry_text):
    with open(LOG_PATH, "a") as f:
        f.write(entry_text)


def summarize_log():
    log_text = read_log()

    prompt = f"""
You are reviewing an engineering log.

Summarize:
- Current phase
- Implemented components
- Open TODOs
- Risks or inconsistencies

Engineering Log:
{log_text}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a senior engineering reviewer."},
            {"role": "user", "content": prompt}
        ],
    )

    print("\n--- ENGINEERING SUMMARY ---\n")
    print(response.choices[0].message.content)


def update_log(message):
    today = datetime.now(UTC).strftime("%Y-%m-%d")

    prompt = f"""
Create a concise engineering log entry summarizing the following change:

{message}

Keep it short and professional.
Do not include headers other than plain text summary.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a precise engineering documentation assistant."},
            {"role": "user", "content": prompt}
        ],
    )

    summary = response.choices[0].message.content.strip()

    formatted_entry = f"""

---

## {today}

{summary}
"""

    append_log(formatted_entry)

    print("\nENGINEERING_LOG.md safely appended.\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["summarize", "update"])
    parser.add_argument("--message", "-m", type=str)

    args = parser.parse_args()

    if args.action == "summarize":
        summarize_log()

    elif args.action == "update":
        if not args.message:
            print("Provide a message with --message")
        else:
            update_log(args.message)
