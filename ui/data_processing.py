import csv
import io
import re

import pandas as pd

from ui.emailParser import extract_replies_with_senders


def recover_exchange_email(email: str, body: str) -> str:
    if email.lower().startswith("/o=nycc/ou=exchange"):
        match_emails = re.findall(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
            body,
        )
        return match_emails[0] if match_emails else "/o=NYCC/ou=Exchange Administrative"
    return email


def build_grouped_dataframe(uploaded_file, separator: str):
    reader = csv.DictReader(
        io.StringIO(uploaded_file.getvalue().decode("ISO-8859-1"))
    )

    grouped_threads: dict[tuple[str, str], dict[str, str]] = {}

    for row in reader:
        name = (row.get("To: (Name)", "") or "").strip(" '\"")
        email = (row.get("To: (Address)", "") or "").strip(" '\"")
        subject = (row.get("Subject", "") or "").strip(" '\"")
        body = (row.get("Body", "") or "").strip()

        email = recover_exchange_email(email, body)

        if not subject and not body:
            continue

        replies = extract_replies_with_senders(body, email)

        if replies:
            combined_reply_this_row = separator.join(reply.strip() for _, reply in replies)
        else:
            combined_reply_this_row = body

        subj_key = subject if subject else "No Subject"
        key = (email.lower(), subj_key)

        if key not in grouped_threads:
            grouped_threads[key] = {
                "Name": name,
                "Email": email,
                "Subject": subj_key,
                "Reply": combined_reply_this_row,
            }
        else:
            grouped_threads[key]["Reply"] += separator + combined_reply_this_row

    df = pd.DataFrame(grouped_threads.values())
    df["__order"] = range(len(df))
    grouped = df.groupby("Subject", sort=False)

    return df, grouped


def build_text_export(result_df: pd.DataFrame) -> str:
    txt_output = ""

    for _, row in result_df.iterrows():
        txt_output += f"Name: {row.get('Name', '')}\n"
        txt_output += f"Email: {row.get('Email', '')}\n"
        txt_output += f"Subject: {row.get('Subject', '')}\n"
        txt_output += f"Reply:\n{row.get('Reply', '').strip()}\n"
        txt_output += "-" * 40 + "\n"

    return txt_output