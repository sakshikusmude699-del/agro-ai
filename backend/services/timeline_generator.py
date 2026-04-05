"""
Crop lifecycle timeline generator.
Returns a day-wise task schedule based on crop type.
"""

from datetime import date, timedelta
from typing import List

# ─── Crop Lifecycle Definitions ───────────────────────────────────────────────
# Each entry: (day_offset, task_type, title, description)

CROP_TIMELINES = {
    "rice": [
        (1,   "sowing",     "Seed Sowing",           "Sow pre-germinated rice seeds in nursery beds. Maintain 2–3 cm water depth."),
        (7,   "irrigation", "First Irrigation",      "Irrigate nursery beds. Keep soil moist but not waterlogged."),
        (21,  "sowing",     "Transplanting",         "Transplant seedlings to main field. Spacing: 20×15 cm."),
        (28,  "fertilizer", "Basal Fertilizer",      "Apply NPK (60:40:40 kg/ha). Mix well into soil before transplanting."),
        (35,  "irrigation", "Regular Irrigation",    "Maintain 5 cm standing water. Check for water stress signs."),
        (45,  "pest_check", "Pest Monitoring",       "Check for brown plant hopper, leaf folder. Apply pesticide if needed."),
        (60,  "fertilizer", "Top Dressing",          "Apply urea (40 kg/ha) for better tillering."),
        (75,  "pest_check", "Disease Check",         "Monitor for blast, sheath blight. Apply fungicide if spotted."),
        (90,  "irrigation", "Drainage",              "Drain fields 10 days before harvest for better grain quality."),
        (110, "harvest",    "Harvest Time",          "Harvest when 80% grains are golden yellow. Use combine or manually."),
    ],
    "wheat": [
        (1,   "sowing",     "Seed Sowing",           "Sow wheat seeds at 100 kg/ha. Depth: 5–6 cm. Row spacing: 20 cm."),
        (10,  "irrigation", "Crown Root Irrigation", "First critical irrigation at crown root initiation stage."),
        (21,  "fertilizer", "Basal Dose",            "Apply DAP (100 kg/ha) and potash before sowing."),
        (30,  "irrigation", "Tillering Irrigation",  "Irrigate at tillering stage. Avoid waterlogging."),
        (40,  "pest_check", "Aphid Check",           "Monitor for aphids and rust disease. Apply as needed."),
        (55,  "fertilizer", "Top Dressing",          "Apply urea (50 kg/ha) at jointing stage."),
        (65,  "irrigation", "Booting Irrigation",    "Irrigate at booting stage for grain filling."),
        (80,  "pest_check", "Yellow Rust Check",     "Inspect for yellow rust. Apply fungicide if required."),
        (100, "irrigation", "Milky Grain Irrigation","Light irrigation at milky grain stage. Don't over-irrigate."),
        (120, "harvest",    "Harvest",               "Harvest when crop turns golden yellow. Moisture <14%."),
    ],
    "maize": [
        (1,   "sowing",     "Seed Sowing",           "Sow treated seeds at 20 kg/ha. Spacing: 60×25 cm."),
        (7,   "irrigation", "Germination Water",     "Light irrigation to ensure uniform germination."),
        (15,  "fertilizer", "Basal Fertilizer",      "Apply NPK (120:60:40 kg/ha) in furrows."),
        (25,  "pest_check", "Stem Borer Check",      "Monitor for fall armyworm and stem borer. Apply Bt spray."),
        (30,  "irrigation", "Knee-High Irrigation",  "Irrigate when plant is knee-high. Critical growth stage."),
        (45,  "fertilizer", "Side Dressing",         "Apply urea (60 kg/ha) when plant is 45 cm tall."),
        (60,  "irrigation", "Tasseling Irrigation",  "Most critical stage. Ensure good moisture during tasseling."),
        (70,  "pest_check", "Silk Stage Monitor",    "Check for earworm at silk stage. Protect silks."),
        (85,  "irrigation", "Grain Fill Irrigation", "Light irrigation during grain filling stage."),
        (100, "harvest",    "Harvest",               "Harvest when husks turn brown and dry. Moisture 20–25%."),
    ],
    "cotton": [
        (1,   "sowing",     "Seed Sowing",           "Sow Bt cotton seeds. Spacing: 90×60 cm. Depth: 3 cm."),
        (10,  "irrigation", "Pre-emergence Water",   "Light irrigation to ensure seedling emergence."),
        (20,  "fertilizer", "Basal Dose",            "Apply NPK (90:45:45 kg/ha) in rows."),
        (35,  "pest_check", "Whitefly Check",        "Monitor for whitefly, jassids, and mealybug."),
        (50,  "fertilizer", "Top Dressing 1",        "Apply urea (45 kg/ha) at squaring stage."),
        (60,  "irrigation", "Flowering Irrigation",  "Critical irrigation at flowering. Avoid water stress."),
        (75,  "pest_check", "Bollworm Check",        "Monitor for bollworm. Use pheromone traps."),
        (90,  "fertilizer", "Top Dressing 2",        "Apply MOP (30 kg/ha) at boll development stage."),
        (110, "pest_check", "Boll Weevil Check",     "Final pest check before harvest. Monitor boll weevil."),
        (150, "harvest",    "First Picking",         "Start picking when 60% bolls open. Do 3–4 pickings."),
    ],
    "default": [
        (1,   "sowing",     "Seed Sowing",           "Prepare seedbed and sow seeds at recommended spacing."),
        (7,   "irrigation", "First Irrigation",      "Water the field to support seedling establishment."),
        (14,  "fertilizer", "Basal Fertilizer",      "Apply NPK fertilizer as per soil test recommendation."),
        (21,  "pest_check", "First Pest Check",      "Scout for pests and diseases. Record observations."),
        (35,  "irrigation", "Regular Irrigation",    "Irrigate based on crop water requirements."),
        (45,  "fertilizer", "Top Dressing",          "Apply nitrogen top dressing for vegetative growth."),
        (60,  "pest_check", "Mid-Season Check",      "Monitor for diseases, insects, and weeds."),
        (75,  "irrigation", "Critical Irrigation",   "Ensure adequate moisture at flowering/fruiting stage."),
        (90,  "pest_check", "Pre-harvest Check",     "Final crop health assessment before harvest."),
        (100, "harvest",    "Harvest",               "Harvest at maturity. Follow crop-specific guidelines."),
    ],
}

# Crop duration in days (for display purposes)
CROP_DURATION = {
    "rice": 110, "wheat": 120, "maize": 100, "cotton": 150,
    "sugarcane": 300, "chickpea": 100, "soybean": 90,
    "groundnut": 120, "mustard": 90, "default": 100,
}


def generate_timeline(crop: str, sowing_date: date) -> List[dict]:
    """
    Generate a full day-wise task list for a crop starting from sowing_date.
    Returns list of task dicts with absolute dates.
    """
    crop_lower = crop.lower()
    schedule = CROP_TIMELINES.get(crop_lower, CROP_TIMELINES["default"])

    tasks = []
    for day_offset, task_type, title, description in schedule:
        task_date = sowing_date + timedelta(days=day_offset - 1)
        tasks.append({
            "day": day_offset,
            "task_type": task_type,
            "title": title,
            "description": description,
            "scheduled_date": task_date.isoformat(),
            "completed": False,
            "skipped": False,
            "skip_reason": None,
        })

    return tasks


def get_total_days(crop: str) -> int:
    return CROP_DURATION.get(crop.lower(), CROP_DURATION["default"])


def get_todays_tasks(tasks: List[dict], sowing_date_str: str) -> List[dict]:
    """Return tasks scheduled for today based on sowing date."""
    today = date.today()
    return [t for t in tasks if t.get("scheduled_date") == today.isoformat()]
