import re


def extract_replies_with_senders(body: str, csv_email: str) -> list[tuple[str, str]]:
    pattern = re.compile(
        r"(?=^From:|^On .+? wrote:|^-----Original Message-----)",
        re.IGNORECASE | re.MULTILINE,
    )

    chunks = pattern.split((body or "").strip())
    results: list[tuple[str, str]] = []
    last_sender = csv_email

    for i, chunk in enumerate(chunks):
        chunk = chunk.strip()
        if not chunk or len(chunk.splitlines()) < 2:
            continue

        sender = None

        if i == 0:
            sender = csv_email
        else:
            match_from = re.search(r"^From:\s*(.*)", chunk, re.IGNORECASE | re.MULTILINE)
            if match_from:
                sender = match_from.group(1).strip()
            else:
                match_wrote = re.search(
                    r"On .+? (.+?) <(.+?)> wrote:",
                    chunk,
                    re.IGNORECASE,
                )
                if match_wrote:
                    name = match_wrote.group(1).strip()
                    email_addr = match_wrote.group(2).strip()
                    sender = f"{name} <{email_addr}>"

        sender = sender or last_sender
        last_sender = sender
        results.append((sender, chunk))

    return results