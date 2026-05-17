import argparse
import csv
import json
from pathlib import Path
import xml.etree.ElementTree as ET


def parse_xml_file(xml_path: Path) -> list[dict]:
    tree = ET.parse(xml_path)
    root = tree.getroot()
    foods: list[dict] = []

    for food in root.findall("food"):
        item_el = food.find("item")
        price_el = food.find("price")
        description_el = food.find("description")
        calories_el = food.find("calories")

        ingredients = [
            ing.text.strip()
            for ing in food.findall("./ingredients/ingredient")
            if ing.text and ing.text.strip()
        ]

        foods.append(
            {
                "item": (item_el.text or "").strip() if item_el is not None and item_el.text else "",
                "name": item_el.get("name", "") if item_el is not None else "",
                "type": item_el.get("type", "") if item_el is not None else "",
                "price": (price_el.text or "").strip() if price_el is not None and price_el.text else "",
                "currency": price_el.get("currency", "") if price_el is not None else "",
                "description": (
                    " ".join(description_el.itertext()).strip() if description_el is not None else ""
                ),
                "calories": (calories_el.text or "").strip() if calories_el is not None and calories_el.text else "",
                "ingredients": ingredients,
            }
        )

    return foods


def save_csv(rows: list[dict], output_path: Path) -> None:
    if not rows:
        return
    fieldnames = ["item", "name", "type", "price", "currency", "description", "calories", "ingredients"]
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            row_copy = row.copy()
            row_copy["ingredients"] = " | ".join(row_copy["ingredients"])
            writer.writerow(row_copy)


def parse_pdf_file(pdf_path: Path) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise RuntimeError(
            "PDF support requires pypdf. Install with: pip install pypdf"
        ) from exc

    reader = PdfReader(str(pdf_path))
    parts: list[str] = []
    for page in reader.pages:
        parts.append(page.extract_text() or "")
    return "\n".join(parts).strip()


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse XML menu data and optionally extract PDF text.")
    parser.add_argument("--xml", type=Path, default=Path("sample.xml"), help="Path to XML file")
    parser.add_argument("--to-json", type=Path, default=None, help="Optional output JSON file")
    parser.add_argument("--to-csv", type=Path, default=None, help="Optional output CSV file")
    parser.add_argument("--pdf", type=Path, default=None, help="Optional PDF file to extract text from")
    args = parser.parse_args()

    xml_rows = parse_xml_file(args.xml)
    print(json.dumps(xml_rows, indent=2, ensure_ascii=False))

    if args.to_json:
        args.to_json.write_text(json.dumps(xml_rows, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"JSON saved to: {args.to_json}")

    if args.to_csv:
        save_csv(xml_rows, args.to_csv)
        print(f"CSV saved to: {args.to_csv}")

    if args.pdf:
        try:
            extracted = parse_pdf_file(args.pdf)
            print("PDF text preview:")
            print(extracted[:1000])
        except (RuntimeError, FileNotFoundError, OSError) as exc:
            print(f"PDF processing error: {exc}")


if __name__ == "__main__":
    main()
