from pathlib import Path

# Directories
BASE_DIR = Path(__file__).parent
MODELS_DIR = BASE_DIR / "pretrained_models"
OUTPUTS_DIR = BASE_DIR / "outputs"
INPUTS_DIR = BASE_DIR / "inputs"
REPORTS_DIR = INPUTS_DIR / "reports"
IMAGES_DIR = INPUTS_DIR / "images"

# Create all directories
MODELS_DIR.mkdir(exist_ok=True)
OUTPUTS_DIR.mkdir(exist_ok=True)
INPUTS_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)
IMAGES_DIR.mkdir(exist_ok=True)

print(f"✓ Folders created:")
print(f"  Input Reports: {REPORTS_DIR}")
print(f"  Input Images:  {IMAGES_DIR}")
print(f"  Outputs:       {OUTPUTS_DIR}")

# Model Settings
YOLO_CONFIDENCE = 0.25
TEXT_MODEL_NAME = "all-MiniLM-L6-v2"

# Detection Categories
DETECTION_CLASSES = {
    "person": ["person", "human", "people"],
    "vehicle": ["car", "truck", "bus", "vehicle"],
    "aircraft": ["airplane", "helicopter", "drone"],
}

# Threat Levels
THREAT_KEYWORDS = {
    "critical": ["attack", "explosion", "weapon", "hostile"],
    "high": ["armed", "military", "suspicious"],
    "medium": ["unusual", "monitoring"],
    "low": ["routine", "normal"],
}