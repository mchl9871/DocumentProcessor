import re

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

    extracted_author = extract_name(from_match) or extract_email(text)
    author = extracted_author or "Unknown"

    extracted_recipient = extract_name(to_match) or extract_email(text)
    recipient = extracted_recipient or "Unknown"

    return author, recipient