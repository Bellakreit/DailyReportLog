from transformers import pipeline
import re
import ast

pipe = pipeline(
    "text-generation",
    model="Qwen/Qwen2.5-0.5B-Instruct",  # 0.5B instead of 1.5B/3B, much faster on CPU
    device=-1,
    temperature=0.2
)

def classify_text(text):
    prompt = f"""You extract information from construction daily reports.

Fill in the provided Python dictionary using ONLY information from the transcript.

Rules:
- Return ONLY the completed Python dictionary.
- Do not use markdown.
- Do not do any explanation only the python dictionary.
- Do not add any text before or after the dictionary!.
- Fill in every field.
- Description: summarize the work performed in 2-3 sentences, add specific details.
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

    # Extract just the dict from whatever the model returns

    match = re.search(r'\{.*\}', output, re.DOTALL)
    output = match.group(0) if match else "{}"
    return ast.literal_eval(output)  # returns actual dict


# print(classify_text("today on the project we installed 20 toilets and 4 sinks. we finished floor 2 and 50 percent done with floor 3. workers john smith and jane doe were on site. john worked 8 hours and jane worked 6 hours. everyone wore hard hats, gloves, and eye protection. john also wore a dust mask."))
