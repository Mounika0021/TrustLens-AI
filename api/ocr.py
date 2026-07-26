import easyocr

reader = easyocr.Reader(["en"], gpu=True)


def extract_text(image_path):
    results = reader.readtext(image_path)

    clean_results = []

    for box, text, confidence in results:
        clean_box = [[int(x), int(y)] for x, y in box]

        clean_results.append({
            "box": clean_box,
            "text": text,
            "confidence": float(confidence)
        })

    return clean_results