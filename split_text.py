from transformers import pipeline
from pydantic import BaseModel, Field, ValidationError, ConfigDict, field_validator
from typing import Dict
import re
import ast


pipe = pipeline(
    "text-generation",
    model="Qwen/Qwen2.5-0.5B-Instruct",
    device=-1,
    temperature=0.2
)


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
    OtherPPEUsed: bool = False
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
    text = text.lower()

    ppe_words = {
        "HardHatUsed": [
            "hard hat", "hardhat", "helmet", "safety helmet"
        ],
        "GlovesUsed": [
            "gloves", "work gloves", "cut gloves", "rubber gloves"
        ],
        "EyeProtectionUsed": [
            "eye protection", "safety glasses", "glasses", "goggles",
            "face shield"
        ],
        "EarProtectionUsed": [
            "ear protection", "ear plugs", "earplugs", "ear muffs",
            "earmuffs", "hearing protection"
        ],
        "FootwearUsed": [
            "boots", "work boots", "steel toe", "steel-toe",
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
        detected[field] = any(word in text for word in words)

    return detected

# method for extracting the dictionary from the model output with error handling
def extract_dict_from_model_output(output):
    match = re.search(r"\{.*\}", output, re.DOTALL)

    if not match:
        raise ValueError("AI did not return a valid dictionary.")

    raw_dict = match.group(0)

    try:
        return ast.literal_eval(raw_dict)
    except Exception:
        raise ValueError("AI returned a dictionary, but it could not be parsed.")


# method for classifying the text and returning the structured data
def classify_text(text):
    prompt = f"""
You extract information from construction daily reports.

Fill in the provided Python dictionary using ONLY information from the transcript.

Rules:
- Return ONLY the completed Python dictionary.
- Do not use markdown.
- Do not explain anything.
- Do not add text before or after the dictionary.
- Fill in every field.
- Description must ONLY include plumbing work or safety-related information.
- Do not include weather, personal comments, unrelated conversations, or general notes.
- PPE fields are True if ANY worker used that PPE; otherwise False.
- If PPE is not mentioned, use False.
- WorkerHours maps each worker's full name to the number of hours worked.
- If no workers are mentioned, return an empty WorkerHours dictionary.

Dictionary:

{{
    "Description": "",
    "HardHatUsed": False,
    "GlovesUsed": False,
    "EyeProtectionUsed": False,
    "EarProtectionUsed": False,
    "FootwearUsed": False,
    "DustMaskUsed": False,
    "OtherPPEUsed": False,
    "WorkerHours": {{}}
}}

Transcript:
{text}

Output:
"""

    result = pipe(prompt)[0]["generated_text"]
    output = result.replace(prompt, "").strip()

    raw_data = extract_dict_from_model_output(output)

    ppe_detected = detect_ppe_from_text(text)

    for field, was_found in ppe_detected.items():
        if was_found:
            raw_data[field] = True

    try:
        validated_data = DailyReportData.model_validate(raw_data)
        return validated_data.model_dump()

    except ValidationError as e:
        return {
            "error": True,
            "message": "The report data could not be validated.",
            "details": e.errors(),
            "raw_ai_output": raw_data
        }