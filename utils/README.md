# New Constituent Automation Platform

## Overview
This project is a Python-based automation platform designed to streamline constituent workflow processing by extracting, organizing, and preparing email thread data for structured submission into an external system.

It combines a Streamlit interface, Selenium-based browser automation, and data processing pipelines to transform unstructured email content into structured datasets for backend analytics and operational workflows.

The system was built to operate under real-world constraints such as authentication, dynamic web interfaces, large record volumes, and inconsistent email thread formatting.

---

## Features
- Upload raw exported email CSV files through a Streamlit interface
- Parse and reconstruct email threads from unstructured message bodies
- Group conversations by email address and subject
- Export processed threads as CSV, Excel, or text files
- Launch authenticated automation workflows for submission into Council Connect
- Handle changing page structures and interactive browser-based workflows

---


## Architecture

The project is organized into modular layers:

### `app.py`
Main Streamlit application and user interface.  
Handles:
- file upload
- thread selection
- search and filtering
- export options
- triggering the automation workflow

### `parser.py`
Parses raw email bodies and reconstructs reply threads using regex-based chunking.  
Responsible for identifying reply boundaries and preserving sender context.

### `data_processing.py`
Processes uploaded CSV data into structured thread records.  
Handles:
- email cleanup
- grouping by email + subject
- thread merging
- export formatting

### `auth.py`
Provides a Tkinter-based credentials popup used to collect login information securely before launching the upload workflow.

### `src/upload.py`
Executes the automation workflow that submits processed thread data into Council Connect.

### `automation.py`
Contains the Selenium automation logic used for authenticated browser interaction, navigation, and workflow execution.

## How to run
Install the requirements
py -m pip install -r utils/requirements.txt

Run the Streamlit app
py -m streamlit run ui/app.py 