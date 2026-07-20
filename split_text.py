import json
import re
from typing import Dict
from pydantic import BaseModel, Field, field_validator

# the AI model reads the transcript and returns the report as JSON text,
# then we convert it to a python dictionary and clean it up with pydantic


# pydantic cleans up whatever the model returns instead of rejecting it
class DailyReportData(BaseModel):
    Description: str = ""
    HardHatUsed: bool = False
    GlovesUsed: bool = False
    EyeProtectionUsed: bool = False
    EarProtectionUsed: bool = False
    FootwearUsed: bool = False
    DustMaskUsed: bool = False
    OtherPPEUsed: str = ""
    WorkerHours: Dict[str, float] = Field(default_factory=dict)

    @field_validator("WorkerHours", mode="before")
    @classmethod
    def clean_worker_hours(cls, value):
        # Make sure worker hours are stored as a clean dictionary of names and valid numbers.
        if not isinstance(value, dict):
            return {}
        cleaned = {}
        for name, hours in value.items():
            try:
                hours = float(hours)
            except (TypeError, ValueError):
                continue
            if isinstance(name, str) and name.strip() and 0 < hours <= 24:
                cleaned[name.strip().title()] = hours
        return cleaned


# This prompt tells the model exactly how to structure the report output.
PROMPT = """You extract structured data from a construction daily report transcript.

Return ONLY a JSON object with exactly these keys:
"Description", "HardHatUsed", "GlovesUsed", "EyeProtectionUsed", "EarProtectionUsed", "FootwearUsed", "DustMaskUsed", "OtherPPEUsed", "WorkerHours"

Description: a detailed summary of the work completed, in 2-4 full sentences. 
Keep every work detail from the transcript: the tasks done, where they happened (floor, room, or area), and the exact quantities, sizes, and materials mentioned (like "20 toilets" or "copper piping"). 
Never mention safety equipment, worker names, or hours here. No greetings, weather, or small talk. 
If the transcript has no construction or plumbing work at all, set it to exactly: "Non-plumbing related information was provided, so the report is incomplete."

Safety equipment checklist. Set the field to true if the transcript mentions ANY of its words, even worded slightly differently:
- HardHatUsed: hard hat, hardhat, helmet, safety hat, head protection
- GlovesUsed: gloves, work gloves, rubber gloves
- EyeProtectionUsed: safety glasses, glasses, goggles, safety goggles, face shield, eye protection
- EarProtectionUsed: ear plugs, ear muffs, hearing protection, ear protection
- FootwearUsed: boots, work boots, safety boots, steel toe, safety shoes
- DustMaskUsed: dust mask, mask, respirator, N95
Set a field to false only if none of its words appear.
OtherPPEUsed: any other safety gear, like safety vest, high-vis vest, or harness. "" if none.

WorkerHours: an object mapping each worker's name to their hours as a number. Copy names and numbers exactly from the transcript.

Example 1:
Transcript: hey so today went well. we fixed the leaking sink in the second floor kitchen and replaced two shut off valves under it. we also started running new copper piping for the third floor bathroom. the guys wore hard hats, safety glasses and steel toe boots, plus their vests. mike smith worked 5 hours.
Output: {{"Description": "Fixed the leaking sink in the second floor kitchen and replaced two shut-off valves under the sink. Started running new copper piping for the third floor bathroom.", "HardHatUsed": true, "GlovesUsed": false, "EyeProtectionUsed": true, "EarProtectionUsed": false, "FootwearUsed": true, "DustMaskUsed": false, "OtherPPEUsed": "safety vest", "WorkerHours": {{"Mike Smith": 5}}}}

Example 2:
Transcript: hey what's up, did you watch the game last night? it was so good, we should hang out this weekend.
Output: {{"Description": "Non-plumbing related information was provided, so the report is incomplete.", "HardHatUsed": false, "GlovesUsed": false, "EyeProtectionUsed": false, "EarProtectionUsed": false, "FootwearUsed": false, "DustMaskUsed": false, "OtherPPEUsed": "", "WorkerHours": {{}}}}

Transcript: {text}
Output:"""


# main method- transcript in, clean python dictionary out
def classify_text(text):
    try:
        # load the model fresh every call - no stored state anywhere
        from transformers import pipeline
        pipe = pipeline(
            "text-generation",
            model="Qwen/Qwen2.5-0.5B-Instruct",
            device=-1,
        )

        messages = [{"role": "user", "content": PROMPT.format(text=text)}]
        result = pipe(messages, max_new_tokens=300, do_sample=False)
        reply = result[0]["generated_text"][-1]["content"]

        # strip markdown fences and grab the JSON object
        reply = re.sub(r"```(?:json)?", "", reply)
        match = re.search(r"\{.*\}", reply, re.DOTALL)
        if not match:
            raise ValueError(f"No JSON found in model output: {reply[:200]}")

        data = json.loads(match.group(0))

        # safety net: if the model missed a PPE word that is clearly in the text, set it anyway
        ppe_words = {
            "HardHatUsed": ["hard hat", "hardhat", "helmet", "safety hat"],
            "GlovesUsed": ["glove"],
            "EyeProtectionUsed": ["safety glasses", "goggle", "face shield", "eye protection"],
            "EarProtectionUsed": ["ear plug", "earplug", "ear muff", "hearing protection", "ear protection"],
            "FootwearUsed": ["boot", "steel toe", "safety shoes"],
            "DustMaskUsed": ["dust mask", "respirator", "n95"],
        }
        lowered = text.lower()
        for field, words in ppe_words.items():
            if any(w in lowered for w in words):
                data[field] = True

        return DailyReportData.model_validate(data).model_dump()

    except Exception as e:
        print(f"classify_text failed: {e}")
        return {"error": True}