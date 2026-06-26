from transformers import pipeline
from typer import prompt

pipe = pipeline("text-generation", model="mistralai/Mistral-7B-Instruct-v0.2")

def classify_text(text):
        prompt = f"""
            You are filling out a structured report.

            Read the transcript and answer the following fields clearly:
            you will return a python dictionary with the following keys:
            #Description, HardHatUsed, GlovesUsed, EyeProtectionUsed, EarProtectionUsed, FootwareUsed, DustMaskUsed, OtherPPEUsed
            - "Description" this is text format 
            - "HardHatUsed" this is a boolean value (True or False)
            - "GlovesUsed" this is a boolean value (True or False)
            - "EyeProtectionUsed" this is a boolean value (True or False)
            - "EarProtectionUsed" this is a boolean value (True or False)
            - "FootwareUsed" this is a boolean value (True or False)
            - "DustMaskUsed" this is a boolean value (True or False)
            - "OtherPPEUsed" this is a boolean value (True or False)
            - "WorkerHours" (this should be a dictionary inside the dictionary with the keys "worker_name" and values "hours_worked")

            Transcript:
            {text}
            Please provide the output in a valid Python dictionary format.
        """
        return pipe(prompt)

print(classify_text("Today we had four guys on site. Mike Rodriguez worked 9 hours running new copper supply lines on the second floor bathroom rough-in. He was wearing his hard hat, gloves, and steel toe boots the whole time. Carlos Mendez put in 8 hours sweating fittings and installing the shower valve, had his hard hat and safety glasses on. We also had Danny Park for 6 hours doing demo on the old cast iron drain lines — he had full PPE, hard hat, gloves, eye protection, ear protection, dust mask, and boots because of the demo work. Lastly Jose Vega came in for 4 hours to help with material staging, he had his hard hat and boots on but no gloves or eye protection. Overall it was a productive day, we got the second floor rough-in about 70 percent complete and expect to finish the drain lines tomorrow. No incidents or injuries to report."))

