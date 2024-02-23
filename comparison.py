import fitz  # PyMuPDF
import json
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

def create_json_from_page(page):
    lines = json.loads(page.get_text("json"))
    json_data = []

    for block in lines["blocks"]:
        for line in block["lines"]:
            for span in line["spans"]:
                json_data.append({
                    "bbox": span["bbox"],
                    "text": span["text"]
                })

    return json_data

def highlight_differences(new_pdf_path, old_pdf_path, output_pdf_path):
    logging.debug("Opening PDF files...")
    new_pdf = fitz.open(new_pdf_path)
    old_pdf = fitz.open(old_pdf_path)

    logging.debug("Creating output PDF...")
    output_pdf = fitz.open()

    num_pages = min(len(new_pdf), len(old_pdf))

    for i in range(num_pages):
        logging.debug(f"Processing page {i + 1}...")
        new_page = new_pdf[i]
        old_page = old_pdf[i]

        logging.debug("Creating JSON representations of pages...")
        new_page_json = create_json_from_page(new_page)
        old_page_json = create_json_from_page(old_page)

        logging.debug("Comparing pages...")
        if len(new_page_json) != len(old_page_json):
            logging.warning("Page structures do not match. Skipping page comparison.")
            continue

        for new_line, old_line in zip(new_page_json, old_page_json):
            if new_line["text"] != old_line["text"]:
                logging.debug("Differences detected.")
                new_words = set(new_line["text"].split())
                old_words = set(old_line["text"].split())
                differing_words = new_words.symmetric_difference(old_words)

                for word in differing_words:
                    rects = new_page.search_for(word)
                    for rect in rects:
                        new_page.add_highlight_annot(rect)

        output_pdf.insert_pdf(new_pdf, from_page=i, to_page=i)

    logging.debug("Saving output PDF...")
    output_pdf.save(output_pdf_path)

    logging.debug("Closing PDF files...")
    new_pdf.close()
    old_pdf.close()
    output_pdf.close()

if __name__ == "__main__":
    # Provide absolute paths directly
    new_pdf_path = "pdf1 path provide here "
    old_pdf_path = "pdf2 path provide here "
    output_pdf_path = "output path where you want to see the highlighted differences"

    # Call the function to highlight differences
    logging.debug("Starting PDF comparison and highlighting...")
    highlight_differences(new_pdf_path, old_pdf_path, output_pdf_path)

    print(f"Differences highlighted and saved to {output_pdf_path}")
