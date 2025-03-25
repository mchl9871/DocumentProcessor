import re
import ollama  # Import ollama library

def extract_author_recipient(text):
    author = recipient = "Unknown"

    from_match = re.search(r"\b(From|Sent by|Author):\s*([\w\s.,&'-]+)", text, re.IGNORECASE)
    to_match = re.search(r"\b(To|Recipient):\s*([\w\s.,&'-]+)", text, re.IGNORECASE)

    def extract_name(match):
        if match:
            name = match.group(2).strip()
            # If it has multiple words & no digits, treat as a name
            if len(name.split()) > 1 and not any(c.isdigit() for c in name):
                return name
        return None

    def extract_email(txt):
        email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", txt)
        return email_match.group(0) if email_match else None

    # Existing extraction logic
    extracted_author = extract_name(from_match) or extract_email(text)
    author = extracted_author or "Unknown"

    extracted_recipient = extract_name(to_match) or extract_email(text)
    recipient = extracted_recipient or "Unknown"

    # Enhance with Llama3
    llama3_author, llama3_recipient = extract_author_recipient_llama3(text)
    if llama3_author:
        author = llama3_author
    if llama3_recipient:
        recipient = llama3_recipient

    return author, recipient

def extract_author_recipient_llama3(text):
    """
    Uses Llama3 to identify the author and recipient from the text.
    Returns the identified author and recipient.
    """
    # Define the prompt for Llama3
    prompt = f"Identify the author and recipient from the following text:\n\n{text}"

    try:
        # Use ollama.chat(...) to interact with the Llama3 model
        response = ollama.chat(
            model="llama3",
            messages=[{"role": "user", "content": prompt}]
        )
        # Extract the author and recipient from the response
        result = response["message"]["content"].strip().split("\n")
        author = result[0].replace("Author:", "").strip() if len(result) > 0 else "Unknown"
        recipient = result[1].replace("Recipient:", "").strip() if len(result) > 1 else "Unknown"
    except Exception as e:
        author = "Unknown"
        recipient = "Unknown"

    # Define document types and associated keywords
    document_types = {
        "court_document": ["statement of claim", "court document", "court order", "judgment"],
        "government_document": ["notice of fine", "compliance notice", "regulatory notice", "government policy"],
        "corporate_document": ["company policy", "board meeting minutes", "shareholder agreement"],
        "personal_document": ["will and testament", "power of attorney", "divorce decree"],
        "letter": ["demand letter", "cease and desist letter", "offer letter"],
        "email": ["@example.com"],  # Add more email domains as needed
        "handwritten_note": ["handwritten note", "personal note"]
    }

    # Check for document type keywords
    for doc_type, keywords in document_types.items():
        if any(keyword in text.lower() for keyword in keywords):
            if doc_type == "court_document":
                author = "Party"
                recipient = "Court"
            elif doc_type == "government_document":
                author = identify_government_entity(text)
                recipient = "Recipient"
            elif doc_type == "corporate_document":
                author = "Corporate Entity"
                recipient = "Recipient"
            elif doc_type == "personal_document":
                author = "Individual"
                recipient = "Recipient"
            elif doc_type == "letter":
                author = "Sender"
                recipient = "Recipient"
            elif doc_type == "email":
                author = "Email Sender"
                recipient = "Email Recipient"
            elif doc_type == "handwritten_note":
                author = "Note Author"
                recipient = "Recipient"
            break

    return author, recipient

def identify_government_entity(text):
    """
    Identifies the specific government entity from the text.
    """
    government_entities = [
        "Department of Transport and Main Roads",
        "Department of Education",
        "Queensland Health",
        "Department of Environment and Science",
        "Department of Justice and Attorney-General",
        "Australian Taxation Office",
        "Department of Home Affairs",
        "Department of Defence",
        "Department of Foreign Affairs and Trade",
        "Department of Agriculture and Fisheries",
        "Department of Employment, Small Business and Training",
        "Department of State Development, Manufacturing, Infrastructure and Planning"
    ]

    for entity in government_entities:
        if entity.lower() in text.lower():
            return entity

    return "Government Entity"