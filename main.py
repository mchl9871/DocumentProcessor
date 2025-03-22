import sys
import os
import time
import pandas as pd

from text_extraction import (
    extract_text_from_pdf,
    extract_text_from_docx,
    extract_text_from_excel,
    extract_text_from_image,
    extract_text_from_email,
    extract_text_from_eml
)
from date_extraction import extract_document_date
from summarization import generate_summary
from excel_output import save_to_excel, remove_invalid_xml_chars
from author_recipient_extraction import extract_author_recipient  # Import the function

def process_folder(folder_path):
    """
    Scans the folder for supported file types,
    extracts text, date, author, recipient,
    and ALWAYS generates a 'concise' summary.
    Returns a DataFrame with columns matching
    the 11 custom headers.
    """
    data = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            text = ""

            ext_lower = file.lower()
            if ext_lower.endswith(".pdf"):
                text = extract_text_from_pdf(file_path)
            elif ext_lower.endswith(".docx"):
                text = extract_text_from_docx(file_path)
            elif ext_lower.endswith((".xls", ".xlsx")):
                text = extract_text_from_excel(file_path)
            elif ext_lower.endswith((".png", ".jpg", ".jpeg", ".tiff")):
                text = extract_text_from_image(file_path)
            elif ext_lower.endswith(".msg"):
                text = extract_text_from_email(file_path)
            elif ext_lower.endswith(".eml"):
                text = extract_text_from_eml(file_path)
            else:
                # Unsupported file type
                print(f"Skipping file '{file}' (unsupported extension).")
                continue

            # Extract date
            doc_date = extract_document_date(text, file_path)

            # Extract author & recipient
            author, recipient = extract_author_recipient(text)

            # ALWAYS generate a "concise" summary
            summary = generate_summary(text, summary_type="concise")

            data.append({
                "File Name": file,
                "File Path": file_path,
                "File Type": ext_lower.split('.')[-1],
                "Document Date": doc_date,
                "Author": author,
                "Recipient": recipient,
                "Summary": summary,
            })

    df = pd.DataFrame(data)
    df = df.applymap(remove_invalid_xml_chars)

    if df.empty:
        return df

    # Insert "Document ID" as auto-increment
    df.insert(0, "Document ID", range(1, len(df) + 1))

    # Create blank columns for "Category" & "Host Document ID"
    df["Category"] = ""
    df["Host Document ID"] = ""

    # Rename columns
    df.rename(columns={
        "File Name": "Document Title",
        "File Type": "Document Type",
        "File Path": "Filename (including extension)"
    }, inplace=True)

    # Create "Hyperlink" from the file path
    if "Filename (including extension)" in df.columns:
        df["Hyperlink"] = df["Filename (including extension)"].apply(lambda p: f"file://{p}")
    else:
        df["Hyperlink"] = ""

    # Reorder to final 11 columns
    final_columns = [
        "Document ID",
        "Document Date",
        "Category",
        "Document Title",
        "Summary",
        "Document Type",
        "Host Document ID",
        "Author",
        "Recipient",
        "Filename (including extension)",
        "Hyperlink"
    ]
    existing_cols = [c for c in final_columns if c in df.columns]
    df = df[existing_cols]

    return df

if __name__ == "__main__":
    start_time = time.time()

    # 1) Check if user provided a path as an argument
    import sys
    if len(sys.argv) < 2:
        print("Usage: python main.py /path/to/folder")
        sys.exit(1)

    folder_path = sys.argv[1]

    # 2) Verify folder exists
    if not os.path.exists(folder_path):
        print(f"Folder not found: {folder_path}")
        sys.exit(1)

    # 3) Process folder & create DataFrame
    df = process_folder(folder_path)

    # 4) Save to Excel
    if not df.empty:
        save_to_excel(df, output_filename="Document Register.xlsx")
    else:
        print("No documents processed.")

    elapsed_time = time.time() - start_time
    print(f"⏳ Script completed in {int(elapsed_time // 60)} minutes and {int(elapsed_time % 60)} seconds.")