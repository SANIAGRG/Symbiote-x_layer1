import sys
import argparse
from pathlib import Path
from models.text_analyzer import TextAnalyzer
from models.image_analyzer import ImageAnalyzer
from utils.json_builder import JSONBuilder
import config


class IntelligenceSystem:
    def __init__(self):
        print("="*60)
        print("Intelligence Perception System")
        print("="*60)

        self.text_analyzer = TextAnalyzer()
        self.image_analyzer = ImageAnalyzer()
        self.json_builder = JSONBuilder()

        print("System ready!\n")

    def analyze(self, text=None, image_path=None, output_name=None):
        """Analyze text and/or image"""

        # Text Analysis
        if text:
            print("\n[1/3] Analyzing text...")
            text_result = self.text_analyzer.analyze(text)
        else:
            text_result = {
                "text": "",
                "threat_level": "low",
                "threat_score": 0.1,
                "confidence": 0.0
            }

        # Image Analysis
        if image_path:
            print("\n[2/3] Analyzing image...")
            image_result = self.image_analyzer.analyze(image_path)
        else:
            image_result = {
                "image_path": "",
                "total_detections": 0,
                "detections": [],
                "counts": {"person": 0, "vehicle": 0, "aircraft": 0},
                "confidence": 0.0
            }

        # Build Output
        print("\n[3/3] Building report...")
        output = self.json_builder.build_output(text_result, image_result)

        # Save
        filepath = self.json_builder.save(output, output_name)

        # Print Summary
        self._print_summary(output)

        return output

    def _print_summary(self, output):
        """Print results"""
        print("\n" + "="*60)
        print("RESULTS")
        print("="*60)

        threat = output["threat_assessment"]
        counts = output["detections"]

        print(f"\n🎯 THREAT: {threat['level'].upper()}")
        print(f"   Score: {threat['score']}")

        print(f"\n📊 DETECTIONS:")
        print(f"   Humans: {counts['humans']}")
        print(f"   Vehicles: {counts['vehicles']}")
        print(f"   Aircraft: {counts['aircraft']}")

        print(f"\n✅ Confidence: {output['confidence']['overall']:.2%}")
        print("\n" + "="*60)


def list_input_files() -> tuple[list[Path], list[Path]]:
    """List all available input files"""
    print("\n" + "="*60)
    print("AVAILABLE INPUT FILES")
    print("="*60)

    # List reports
    report_files = list(config.REPORTS_DIR.glob("*.txt"))
    print(f"\n📄 Reports in {config.REPORTS_DIR}:")
    if report_files:
        for i, f in enumerate(report_files, 1):
            print(f"  {i}. {f.name}")
    else:
        print("  (No .txt files found)")

    # List images
    image_files = (list(config.IMAGES_DIR.glob("*.jpg")) +
                   list(config.IMAGES_DIR.glob("*.png")) +
                   list(config.IMAGES_DIR.glob("*.jpeg")))
    print(f"\n🖼️  Images in {config.IMAGES_DIR}:")
    if image_files:
        for i, f in enumerate(image_files, 1):
            print(f"  {i}. {f.name}")
    else:
        print("  (No .jpg/.png files found)")

    print("\n" + "="*60)
    return report_files, image_files


def process_single():
    """Process single report and image"""
    report_files, image_files = list_input_files()

    if not report_files and not image_files:
        print("\n❌ No input files found!")
        print(f"\nAdd files to:")
        print(f"  Reports: {config.REPORTS_DIR}")
        print(f"  Images:  {config.IMAGES_DIR}")
        return

    # Select report
    text = None
    if report_files:
        print("\nSelect report (or press Enter to skip):")
        choice = input("Enter number: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(report_files):
            report_file = report_files[int(choice) - 1]
            with open(report_file, 'r') as f:
                text = f.read()
            print(f"✓ Using report: {report_file.name}")

    # Select image
    image_path = None
    if image_files:
        print("\nSelect image (or press Enter to skip):")
        choice = input("Enter number: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(image_files):
            image_path = str(image_files[int(choice) - 1])
            print(f"✓ Using image: {image_files[int(choice) - 1].name}")

    if not text and not image_path:
        print("\n❌ No files selected!")
        return

    # Process
    system = IntelligenceSystem()
    system.analyze(text=text, image_path=image_path)


def process_batch():
    """Process all files in input folders"""
    report_files, image_files = list_input_files()

    if not report_files and not image_files:
        print("\n❌ No input files found!")
        print(f"\nAdd files to:")
        print(f"  Reports: {config.REPORTS_DIR}")
        print(f"  Images:  {config.IMAGES_DIR}")
        return

    print(f"\n🚀 Processing {len(image_files)} images...")

    system = IntelligenceSystem()

    # Process each image with matching report
    for i, image_file in enumerate(image_files):
        print(f"\n{'='*60}")
        print(f"Processing {i+1}/{len(image_files)}: {image_file.name}")
        print(f"{'='*60}")

        # Find matching report (same name)
        report_text = None
        report_name = image_file.stem  # filename without extension

        for report_file in report_files:
            if report_file.stem == report_name:
                with open(report_file, 'r') as f:
                    report_text = f.read()
                print(f"✓ Found matching report: {report_file.name}")
                break

        # If no matching report, use first available or None
        if report_text is None and report_files:
            if i < len(report_files):
                with open(report_files[i], 'r') as f:
                    report_text = f.read()
                print(f"✓ Using report: {report_files[i].name}")

        # Create output name based on image name
        output_name = f"report_{image_file.stem}.json"

        # Analyze
        system.analyze(
            text=report_text,
            image_path=str(image_file),
            output_name=output_name
        )

    print(f"\n{'='*60}")
    print(f"✅ Batch processing complete!")
    print(f"📁 Check {config.OUTPUTS_DIR} for results")
    print(f"{'='*60}")


def process_all_pairs():
    """Process all report-image pairs with matching names"""
    report_files, image_files = list_input_files()

    if not report_files or not image_files:
        print("\n⚠️  Need both reports and images for pair mode!")
        return

    # Find matching pairs
    pairs = []
    for image_file in image_files:
        for report_file in report_files:
            if image_file.stem == report_file.stem:
                pairs.append((report_file, image_file))

    if not pairs:
        print("\n❌ No matching pairs found!")
        print("\nTip: Name files the same (e.g., routineAlpha1.txt + report1.jpg)")
        return

    print(f"\n✓ Found {len(pairs)} matching pairs")
    print("\nPairs:")
    for i, (report, image) in enumerate(pairs, 1):
        print(f"  {i}. {report.name} + {image.name}")

    system = IntelligenceSystem()

    for report_file, image_file in pairs:
        print(f"\n{'='*60}")
        print(f"Processing pair: {report_file.stem}")
        print(f"{'='*60}")

        with open(report_file, 'r') as f:
            text = f.read()

        output_name = f"report_{report_file.stem}.json"
        system.analyze(
            text=text,
            image_path=str(image_file),
            output_name=output_name
        )

    print(f"\n✅ All pairs processed!")


def main():
    print("\n" + "="*60)
    print("INTELLIGENCE PERCEPTION SYSTEM")
    print("="*60)
    print(f"\nInput folders:")
    print(f"  📄 Reports: {config.REPORTS_DIR}")
    print(f"  🖼️  Images:  {config.IMAGES_DIR}")
    print(f"  📁 Outputs: {config.OUTPUTS_DIR}")

    print("\n" + "="*60)
    print("SELECT MODE:")
    print("="*60)
    print("1. Process single file (select from list)")
    print("2. Process all images (batch)")
    print("3. Process matching pairs (routineAlpha1.txt + report1.jpg)")
    print("4. List available files")
    print("5. Exit")

    choice = input("\nEnter choice (1-5): ").strip()

    if choice == "1":
        process_single()
    elif choice == "2":
        process_batch()
    elif choice == "3":
        process_all_pairs()
    elif choice == "4":
        list_input_files()
    elif choice == "5":
        print("Goodbye!")
        sys.exit(0)
    else:
        print("Invalid choice!")


if __name__ == "__main__":
    print("@@@@@@@@@@@@@@@@Code Execution Starts here...")
    main()