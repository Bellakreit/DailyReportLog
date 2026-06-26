from transformers import pipeline

pipe = pipeline(
    "text-generation",
    model="Qwen/Qwen2.5-0.5B-Instruct",  # 0.5B instead of 3B, much faster on CPU
    device=-1,
    temperature=0.2
)

def classify_text(text):
    prompt = f"""
You are filling out a structured safety report.

Extract the following fields and return ONLY a valid Python dictionary.

Rules:
only hours should be specific for each worker
Use True or False for booleans
Do not include extra text
WorkerHours must be a dictionary inside the dictionary: {{ "Name": hours }}

ALL Keys(so each key is in the dictionary with a value):
Description (string)
HardHatUsed (bool)
GlovesUsed (bool)
EyeProtectionUsed (bool)
EarProtectionUsed (bool)
FootwareUsed (bool)
DustMaskUsed (bool)
OtherPPEUsed (bool)
WorkerHours (dict)

do it like this but based on the input given not this fake example:

    {{
        "Description": "description of the work done based on the input",
        "HardHatUsed": boolean based on the input,
        "GlovesUsed": boolean based on the input,
        "EyeProtectionUsed": boolean based on the input,
        "EarProtectionUsed": boolean based on the input,
        "FootwareUsed": boolean based on the input,
        "DustMaskUsed": boolean based on the input,
        "OtherPPEUsed": boolean based on the input,
        "WorkerHours": {{
            "name of worker": hours,
            "Carlos Mendez example name": 8 example hours,
        }}
    }}


Transcript:
{text}

Output:
"""

    result = pipe(prompt)[0]["generated_text"]

    # remove prompt from output (Qwen may echo it)
    output = result.replace(prompt, "").strip()

    return output


print(classify_text("Today we had four guys on site. Mike Rodriguez worked 9 hours running new copper supply lines on the second floor bathroom rough-in. He was wearing his hard hat, gloves, and steel toe boots the whole time. Carlos Mendez put in 8 hours sweating fittings and installing the shower valve, had his hard hat and safety glasses on. We also had Danny Park for 6 hours doing demo on the old cast iron drain lines — he had full PPE, hard hat, gloves, eye protection, ear protection, dust mask, and boots because of the demo work. Lastly Jose Vega came in for 4 hours to help with material staging, he had his hard hat and boots on but no gloves or eye protection. Overall it was a productive day, we got the second floor rough-in about 70 percent complete and expect to finish the drain lines tomorrow. No incidents or injuries to report."))