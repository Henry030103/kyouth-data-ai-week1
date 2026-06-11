from email import policy
from email.parser import BytesParser
from pathlib import Path
import quopri


def extract_html_from_mhtml(mhtml_path):          # This creates a function called extract_html_from_mhtml.
    with open(mhtml_path, "rb") as file:
        message = BytesParser(policy=policy.default).parse(file) # opens the .mhtml file like an email-style archive.

    for part in message.walk():
        content_type = part.get_content_type() #checks all parts inside the .mhtml file.

        if content_type == "text/html": #finds the HTML section.
            payload = part.get_payload(decode=True)

            if payload is None:
                payload = part.get_payload()
                if isinstance(payload, str):
                    payload = payload.encode("utf-8", errors="ignore")

            html_content = quopri.decodestring(payload).decode(  #decodes quoted-printable text, because MHTML files often store HTML in an encoded format.
                "utf-8",
                errors="ignore",
            )

            return html_content

    return None


def ingest_all_mhtml(input_dir, output_dir):       # Take all .mhtml files from input_dir, Extract HTML from each one, Save the output into output_dir 
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    print("🥉 Bronze:...")

    if not input_dir.exists():
        print(f"⚠️ Source directory does not exist: {input_dir}")
        print("\n📊 Bronze Summary:")
        print("Total: 0 | Extracted: 0 | Failed: 0")
        return

    mhtml_files = list(input_dir.glob("*.mhtml"))

    if not mhtml_files:
        print(f"⚠️ No MHTML content found in: {input_dir}")
        print("\n📊 Bronze Summary:")
        print("Total: 0 | Extracted: 0 | Failed: 0")
        return

    total = len(mhtml_files)
    extracted = 0
    failed = 0

    for mhtml_file in mhtml_files:
        html_content = extract_html_from_mhtml(mhtml_file)

        if html_content is None:
            print(f"⚠️ No HTML content found in: {mhtml_file.name}")
            failed += 1
            continue

        output_file = output_dir / f"{mhtml_file.stem}.html"

        with open(output_file, "w", encoding="utf-8") as file:
            file.write(html_content)

        print(f"✅ Extracted: {mhtml_file.name}")
        extracted += 1

    print("\n📊 Bronze Summary:")
    print(f"Total: {total} | Extracted: {extracted} | Failed: {failed}")

