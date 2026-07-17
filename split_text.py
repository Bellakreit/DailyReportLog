from pydantic import BaseModel, Field, ValidationError, ConfigDict, field_validator
from typing import Dict
import re
import ast

# we used a combination of rule-based and AI-based methods to extract structured data from the text. 
# The AI model is used to improve the accuracy of the extraction, but we also have rule-based methods to ensure that we can still extract data even if the AI model fails or returns unexpected results.
# this way the output is the most accurate it can be

_generation_pipeline = None

# making the pipeline method and this way it is reusable instead of reloading each time
def get_generation_pipeline():
    global _generation_pipeline

    if _generation_pipeline is None:
        from transformers import pipeline

        try:
            _generation_pipeline = pipeline(
                "text-generation",
                model="Qwen/Qwen2.5-0.5B-Instruct",
                device=-1,
                temperature=0.0,
                do_sample=False,
                max_new_tokens=100,
            )
        except Exception:
            _generation_pipeline = None

    return _generation_pipeline


# using pydanctic to define the data model for the daily report so that we can validate the output from the AI model
class DailyReportData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    Description: str = Field(default="")
    HardHatUsed: bool = False
    GlovesUsed: bool = False
    EyeProtectionUsed: bool = False
    EarProtectionUsed: bool = False
    FootwearUsed: bool = False
    DustMaskUsed: bool = False
    OtherPPEUsed: str = Field(default="")
    WorkerHours: Dict[str, float] = Field(default_factory=dict)

    @field_validator("WorkerHours")
    @classmethod
    def validate_worker_hours(cls, value):
        for worker, hours in value.items():
            if not worker or len(worker.strip().split()) < 2:
                raise ValueError(f"Worker name must be a full name: {worker}")

            if hours < 0 or hours > 24:
                raise ValueError(f"Invalid hours for {worker}: {hours}")

        return value


# method for finding PPE mentions in the text
def detect_ppe_from_text(text):
    normalized_text = re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()

    ppe_words = {
        "HardHatUsed": [
            "hard hat", "hardhat", "helmet", "safety helmet", "safety helmets"
        ],
        "GlovesUsed": [
            "gloves", "work gloves", "cut gloves", "rubber gloves"
        ],
        "EyeProtectionUsed": [
            "eye protection", "safety glasses", "glasses", "goggles",
            "face shield", "safety goggles"
        ],
        "EarProtectionUsed": [
            "ear protection", "ear plugs", "earplugs", "ear muffs",
            "earmuffs", "hearing protection"
        ],
        "FootwearUsed": [
            "boots", "work boots", "steel toe", "steel toe", "steel-toe",
            "safety shoes", "foot protection"
        ],
        "DustMaskUsed": [
            "dust mask", "mask", "respirator", "n95"
        ],
        "OtherPPEUsed": [
            "vest", "safety vest", "high vis", "hi vis",
            "high visibility", "harness", "fall protection"
        ]
    }

    detected = {}

    for field, words in ppe_words.items():
        if field == "OtherPPEUsed":
            matched_items = [word for word in words if word in normalized_text]
            detected[field] = ", ".join(matched_items) if matched_items else ""
        else:
            detected[field] = any(word in normalized_text for word in words)

    return detected

# method for extracting the dictionary from the model output with error handling
def extract_dict_from_model_output(output):
    if not output:
        raise ValueError("AI did not return a valid dictionary.")

    match = re.search(r"\{.*\}", output, re.DOTALL)
    if not match:
        raise ValueError("AI did not return a valid dictionary.")

    raw_dict = match.group(0)

    try:
        parsed = ast.literal_eval(raw_dict)
        if isinstance(parsed, dict):
            return parsed
        raise ValueError("Parsed output was not a dictionary.")
    except Exception:
        raise ValueError("AI returned a dictionary, but it could not be parsed.")

# method for making the description from the text and scoring the sentences based on keywords to find the most accurate and best one
def build_description_from_text(text):
    cleaned = re.sub(r"\s+", " ", text or "").strip()
    if not cleaned:
        return ""

    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", cleaned) if s.strip()]
    if not sentences:
        return cleaned[:250]

    preferred_keywords = [
        "installed", "fixed", "replaced", "connected", "inspected", "checked",
        "tested", "cleaned", "patched", "plumb", "pipe", "valve", "drain",
        "toilets", "sinks", "faucets", "showers", "tubs", "pipes", "piping",
        "water heater", "floor", "finished", "completed", "work", "project",
        "site", "crew", "team", "built", "ran", "setup", "started"
    ]
    ignored_keywords = ["safety", "helmet", "glasses", "gloves", "boots", "vest", "mask"]
    worker_keywords = ["worker", "workers", "worked", "worked for", "hours", "hours worked"]
    personal_keywords = ["hi", "thanks", "personal", "good day", "weather", "productive"]

    scored = []
    for sentence in sentences:
        lower = sentence.lower()
        score = 0

        score += sum(2 for keyword in preferred_keywords if keyword in lower)
        score += sum(1 for keyword in ["day", "today", "work", "job"] if keyword in lower)

        if any(keyword in lower for keyword in ignored_keywords):
            score -= 2
        if any(keyword in lower for keyword in worker_keywords):
            score -= 2
        if any(keyword in lower for keyword in personal_keywords):
            score -= 1

        scored.append((score, sentence))

    scored.sort(reverse=True)

    selected_sentences = []
    for score, sentence in scored:
        if score >= 2:
            selected_sentences.append(sentence)
        elif selected_sentences:
            break

    if selected_sentences:
        return " ".join(selected_sentences)

    return " ".join(sentences[:2])

# method for getting teh workers and hours
def extract_worker_hours_from_text(text):
    patterns = [
        r"\b([A-Za-z]+(?:\s+[A-Za-z]+){0,2})\s*(?:worked|worked for|spent|put in|did)\s*(?:for)?\s*(\d+(?:\.\d+)?)\s*(?:hours?|hrs?)\b",
        r"\b([A-Za-z]+(?:\s+[A-Za-z]+){0,2})\s*(\d+(?:\.\d+)?)\s*(?:hours?|hrs?)\b",
        r"\b(\d+(?:\.\d+)?)\s*(?:hours?|hrs?)\s*(?:for|by)\s*([A-Za-z]+(?:\s+[A-Za-z]+){0,2})\b",
    ]

    worker_hours = {}

    for pattern in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            if pattern.startswith(r"\b(\d"):
                hours = float(match.group(1))
                name = match.group(2)
            else:
                name = match.group(1)
                hours = float(match.group(2))

            if not name:
                continue

            cleaned_name = re.sub(r"\s+", " ", name).strip().title()
            cleaned_name = cleaned_name.replace("And ", "")
            cleaned_name = cleaned_name.strip()

            if len(cleaned_name.split()) >= 2 and cleaned_name.lower() not in {"and", "the", "a", "for"}:
                worker_hours[cleaned_name] = hours

    return worker_hours

# merging the rules output and the ai ouput to get the most accurate outcome
def merge_extracted_data(rule_data, model_data):
    merged = dict(rule_data or {})

    if not isinstance(model_data, dict):
        return merged

    description = str(model_data.get("Description", "") or "").strip()
    if description and not description.lower().startswith(("none", "n/a", "unknown", "not sure")):
        merged["Description"] = description

    for field in [
        "HardHatUsed",
        "GlovesUsed",
        "EyeProtectionUsed",
        "EarProtectionUsed",
        "FootwearUsed",
        "DustMaskUsed",
    ]:
        rule_value = merged.get(field)
        model_value = model_data.get(field)

        if isinstance(model_value, bool):
            merged[field] = model_value
        elif isinstance(rule_value, bool):
            merged[field] = rule_value

    other_ppe = str(model_data.get("OtherPPEUsed", "") or "").strip()
    if other_ppe:
        merged["OtherPPEUsed"] = other_ppe
    elif not merged.get("OtherPPEUsed"):
        merged["OtherPPEUsed"] = ""

    merged_hours = dict(rule_data.get("WorkerHours", {}) or {})
    model_hours = model_data.get("WorkerHours", {}) or {}
    if isinstance(model_hours, dict):
        for worker, hours in model_hours.items():
            if isinstance(worker, str) and worker.strip() and isinstance(hours, (int, float)):
                merged_hours[worker.strip().title()] = float(hours)

        for worker, hours in rule_data.get("WorkerHours", {}).items():
            if worker not in merged_hours:
                merged_hours[worker] = hours

    merged["WorkerHours"] = merged_hours
    return merged


# method for classifying the text and returning the structured data
def classify_text(text):
    base_description = build_description_from_text(text)
    ppe_detected = detect_ppe_from_text(text)
    worker_hours = extract_worker_hours_from_text(text)

    raw_data = {
        "Description": base_description,
        "HardHatUsed": ppe_detected.get("HardHatUsed", False),
        "GlovesUsed": ppe_detected.get("GlovesUsed", False),
        "EyeProtectionUsed": ppe_detected.get("EyeProtectionUsed", False),
        "EarProtectionUsed": ppe_detected.get("EarProtectionUsed", False),
        "FootwearUsed": ppe_detected.get("FootwearUsed", False),
        "DustMaskUsed": ppe_detected.get("DustMaskUsed", False),
        "OtherPPEUsed": ppe_detected.get("OtherPPEUsed", "") or "",
        "WorkerHours": worker_hours,
    }

    prompt = f"""
You extract information from construction daily reports.

Return ONLY a Python dictionary with these exact keys:
Description, HardHatUsed, GlovesUsed, EyeProtectionUsed, EarProtectionUsed, FootwearUsed, DustMaskUsed, OtherPPEUsed, WorkerHours.

Rules:
- Use only information from the transcript.
- Description should be a short summary of the plumbing or safety work.
- Do not include weather, personal comments, or unrelated talk.
- PPE values must be booleans or empty strings.
- WorkerHours must be a dictionary of full names to numbers.
- Return plain Python syntax only. No markdown.

Transcript:
{text}

Output:
"""

    model_data = None
    pipe = get_generation_pipeline()
    if pipe is not None:
        try:
            result = pipe(prompt)[0]["generated_text"]
            output = result.replace(prompt, "").strip()
            parsed = extract_dict_from_model_output(output)
            if isinstance(parsed, dict):
                model_data = {}
                for key, value in parsed.items():
                    if key in raw_data:
                        if key == "Description" and value:
                            model_data[key] = str(value)
                        elif key == "WorkerHours" and isinstance(value, dict):
                            model_data[key] = {
                                worker: hours for worker, hours in value.items()
                                if isinstance(worker, str) and len(worker.strip().split()) >= 2 and isinstance(hours, (int, float))
                            }
                        elif key in {"HardHatUsed", "GlovesUsed", "EyeProtectionUsed", "EarProtectionUsed", "FootwearUsed", "DustMaskUsed"}:
                            model_data[key] = bool(value)
                        elif key == "OtherPPEUsed":
                            model_data[key] = str(value or "")
        except Exception:
            pass

    combined_data = merge_extracted_data(raw_data, model_data)

    try:
        validated_data = DailyReportData.model_validate(combined_data)
        return validated_data.model_dump()
    except ValidationError:
        return combined_data