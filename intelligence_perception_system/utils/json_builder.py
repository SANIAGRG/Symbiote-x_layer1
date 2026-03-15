import json
from datetime import datetime
import config


class JSONBuilder:

    @staticmethod
    def calculate_combined_threat(text_result, image_result):
        """Combine text and image threat scores"""
        # Base threat from text
        threat_map = {"low": 0.2, "medium": 0.5, "high": 0.7, "critical": 0.9}
        base_score = threat_map.get(text_result["threat_level"], 0.2)

        # Boost from image detections
        counts = image_result["counts"]
        boost = 0

        if counts["person"] > 5:
            boost += 0.2
        if counts["vehicle"] > 2:
            boost += 0.1
        if counts["aircraft"] > 0:
            boost += 0.15

        # Combined score
        combined_score = min(base_score + boost, 1.0)

        # Determine level
        if combined_score >= 0.8:
            level = "critical"
        elif combined_score >= 0.6:
            level = "high"
        elif combined_score >= 0.4:
            level = "medium"
        else:
            level = "low"

        return {
            "level": level,
            "score": round(combined_score, 3),
            "text_score": base_score,
            "image_boost": boost
        }

    @staticmethod
    def build_output(text_result, image_result):
        """Build final JSON output"""
        combined_threat = JSONBuilder.calculate_combined_threat(
            text_result, image_result
        )

        output = {
            "timestamp": datetime.now().isoformat(),
            "analysis": {
                "text": text_result,
                "image": image_result,
            },
            "detections": {
                "humans": image_result["counts"]["person"],
                "vehicles": image_result["counts"]["vehicle"],
                "aircraft": image_result["counts"]["aircraft"],
            },
            "threat_assessment": combined_threat,
            "confidence": {
                "overall": round((text_result["confidence"] +
                                  image_result["confidence"]) / 2, 3)
            }
        }

        return output

    @staticmethod
    def save(output, filename=None):
        """Save to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"report_{timestamp}.json"

        filepath = config.OUTPUTS_DIR / filename

        with open(filepath, 'w') as f:
            json.dump(output, f, indent=2)

        print(f"Saved: {filepath}")
        return str(filepath)