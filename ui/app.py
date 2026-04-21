import io
import csv
import os

import pandas as pd
import streamlit as st

from ui.auth import get_credentials_from_tkinter
from ui.data_processing import build_grouped_dataframe, build_text_export

SEPARATOR = "\n\n-----------------------------------------------\n\n"


def render_downloads(result_df: pd.DataFrame | None) -> None:
    st.subheader("📤 Download Options")
    export_format = st.radio(
        "Choose export format:",
        ["CSV", "Excel (.xlsx)", "Notepad (.txt)"],
        horizontal=True,
    )

    if result_df is None or result_df.empty:
        return

    if export_format == "CSV":
        csv_data = result_df.to_csv(index=False, quoting=csv.QUOTE_ALL)
        st.download_button(
            "⬇️ Download CSV",
            data=csv_data,
            file_name="filtered_output.csv",
            mime="text/csv",
        )

    elif export_format == "Excel (.xlsx)":
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
            result_df.to_excel(writer, index=False, sheet_name="Emails")
        excel_buffer.seek(0)

        st.download_button(
            "⬇️ Download Excel File",
            data=excel_buffer.getvalue(),
            file_name="filtered_output.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    elif export_format == "Notepad (.txt)":
        txt_output = build_text_export(result_df)
        st.download_button(
            "⬇️ Download Notepad File",
            data=txt_output,
            file_name="filtered_output.txt",
            mime="text/plain",
        )


def handle_upload_to_council_connect(result_df: pd.DataFrame | None) -> None:
    st.subheader("🏢 Upload to Council Connect")
    launch_login = st.button("🔐 Login Credentials")

    if not launch_login:
        return

    creds = get_credentials_from_tkinter()

    if not creds:
        st.error("Login cancelled.")
        return

    if result_df is None or result_df.empty:
        st.error("Please select at least one thread before uploading.")
        return

    with st.spinner("Launching browser and submitting entries..."):
        from src.upload import upload_to_council_connect

        driver_path = os.path.join(os.getcwd(), "msedgedriver.exe")

        try:
            upload_to_council_connect(
                result_df,
                creds["username"],
                creds["password"],
                creds["auto_click"],
                driver_path,
            )
            st.success("✅ All selected threads uploaded to Council Connect.")
            st.rerun()
        except Exception as exc:
            st.error(f"❌ Upload failed: {exc}")


def main() -> None:
    st.set_page_config(page_title="📬 New Constituent Emails", layout="wide")
    st.title("📬 New Constituent Emails")
    st.markdown(
        "Upload a raw exported email CSV. This app **groups by Email + Subject** "
        "and merges bodies (and their internal replies) with a separator line."
    )

    uploaded_file = st.file_uploader("📥 Upload raw exported email CSV", type="csv")
    if not uploaded_file:
        st.warning("Please upload a raw email export file.")
        st.stop()

    df, grouped = build_grouped_dataframe(uploaded_file, separator=SEPARATOR)
    st.success(f"✅ Grouped into {len(df)} (Email + Subject) threads.")

    total_groups = len(grouped)

    if "prev_select_all" not in st.session_state:
        st.session_state["prev_select_all"] = False

    for i in range(1, total_groups + 1):
        st.session_state.setdefault(f"select_{i}", False)

    # Build result_df FIRST from current session state
    selected_groups: list[pd.DataFrame] = []

    for i, (_, group) in enumerate(grouped, start=1):
        group = group.sort_values("__order")
        if st.session_state.get(f"select_{i}", False):
            selected_groups.append(group)

    result_df = None
    if selected_groups:
        result_df = pd.concat(selected_groups, ignore_index=True).drop(
            columns=["__order"], errors="ignore"
        )

    # Show these ABOVE search/threads
    render_downloads(result_df)
    handle_upload_to_council_connect(result_df)

    st.subheader("🔍 Search Threads")
    search_query = st.text_input("Search by subject or name:", "").strip().lower()

    select_all_state = st.checkbox("🔘 Select All Threads", key="select_all_toggle")
    if select_all_state != st.session_state["prev_select_all"]:
        for i in range(1, total_groups + 1):
            st.session_state[f"select_{i}"] = select_all_state
        st.session_state["prev_select_all"] = select_all_state

    st.subheader("📑 Email Threads")
    matches_found = False

    for i, (subject, group) in enumerate(grouped, start=1):
        group = group.sort_values("__order")
        first_name = group.iloc[0].get("Name", "Unknown")
        searchable_text = f"{first_name} {subject}".lower()

        if search_query and search_query not in searchable_text:
            continue

        matches_found = True

        reply_text = group.iloc[0].get("Reply", "")
        num_replies = reply_text.count(SEPARATOR) + 1 if reply_text else 0
        expander_title = f"{i}. {first_name} | {subject} ({num_replies} replies)"

        col1, col2 = st.columns([0.05, 0.95])

        with col1:
            st.checkbox("✔", key=f"select_{i}", label_visibility="collapsed")

        with col2:
            with st.expander(expander_title, expanded=False):
                for _, row in group.iterrows():
                    st.markdown(
                        (
                            f"**Name**: {row.get('Name', '')}  \n"
                            f"**Email**: {row.get('Email', '')}  \n"
                            f"**Subject**: {row.get('Subject', '')}  \n"
                            f"**Reply:**  \n"
                            f"```text\n{row.get('Reply', '').strip()}\n```"
                        ),
                        unsafe_allow_html=True,
                    )

    if not matches_found:
        st.info("No threads matched your search.")


if __name__ == "__main__":
    main()