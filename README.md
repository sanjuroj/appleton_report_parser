This file processes the monthly financial reports we get as PDF files from Appleton.  Main functionality:
1. Uses `convert` and `tesseract` to covert PDF files to parsable text.
2. Optionally skip the conversion and just parse pre-converted text files.w
3. Convert whole directories or single files.
4. Outputs a .xlsx file with accounts in rows and dates in columns.