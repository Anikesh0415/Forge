import json
from src.macro_orchestrator import macro_orchestrator

prompts = [
    """Open "client_list.xlsx" in Excel. Process the top 10 rows sequentially (Rows 2 through 11):
For EACH row:
1. Click Column A for that row and copy the Client ID.
2. Switch to Chrome and click the search bar in the CRM tab.
3. Paste the Client ID, press Enter, and wait for the profile card to load.
4. Verify visually that the status indicator says "Active".
5. Use OCR to click the "Export Summary" button on the profile card.
6. Copy the generated summary text from the modal popup.
7. Switch back to Excel, paste the summary into Column D for that row.
8. Type "VERIFIED" into Column E for that row.
9. Press Down Arrow to move to the next row.
After all 10 rows are processed, save the Excel workbook, close Chrome, and type a summary notification message into WhatsApp stating "10 records verified and updated." """,

    """Navigate to the folder "C:\Logs\Daily". There are 12 text files named log_1.txt through log_12.txt.
Perform the following sequence for EVERY file from log_1.txt to log_12.txt:
1. Open the file in Notepad.
2. Select all text (Ctrl+A), copy it to the clipboard, and close Notepad.
3. Open the "Text Cleaner Utility" web app in your browser.
4. Paste the text into the raw input box.
5. Click the "Clean & Format" button.
6. Wait for the green "Processing Complete" banner to visually appear.
7. Click the "Download Formatted Text" button.
8. Copy the generated summary snippet from the preview panel.
9. Open a master document "Daily_Report.docx" in Word, paste the snippet at the end, and press Enter twice.
Once all 12 files are processed, save "Daily_Report.docx", minimize all windows, and open the Downloads folder.""",

    """Open WhatsApp Desktop. I need to audit and send updates to 10 contacts listed in "contacts.txt".
For EACH contact from 1 to 10:
1. Open "contacts.txt", copy contact line N, switch to WhatsApp.
2. Click the search bar, paste the contact name, and press Enter.
3. Verify via screen check that the active chat header matches the searched contact name.
4. Click the message input field.
5. Type: "Hello, this is an automated system check #N. Please ignore." and press Enter.
6. Wait for the message bubble to show the sent mark (single or double checkmark).
7. Right-click the sent message, select "Copy Text".
8. Switch back to an open Notepad file "Audit_Log.txt".
9. Paste the copied text, type " - SENT & CONFIRMED", and hit Enter.
Repeat this exact workflow until all 10 contacts in the file have been messaged and logged."""
]

def run_tests():
    print("# Macro Orchestrator Stress Test Results\n", flush=True)
    for i, prompt in enumerate(prompts):
        print(f"## Test {i+1}: Macro Loop Detection", flush=True)
        try:
            plan = macro_orchestrator.analyze_instruction(prompt)
            print("### Macro JSON Output:", flush=True)
            print(json.dumps(plan, indent=2), flush=True)
        except Exception as e:
            print(f"### Error:\n{e}", flush=True)
        print("\n---\n", flush=True)

if __name__ == "__main__":
    run_tests()
