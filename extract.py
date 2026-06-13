import json

transcript_path = r'C:\Users\adijd\.gemini\antigravity-ide\brain\f781be18-2332-4caf-a6e7-c08782b56ccc\.system_generated\logs\transcript.jsonl'
output_path = r'C:\Users\adijd\.gemini\antigravity-ide\brain\f781be18-2332-4caf-a6e7-c08782b56ccc\scratch\full_prompt.txt'

with open(transcript_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

with open(output_path, 'w', encoding='utf-8') as out:
    for line in lines:
        try:
            data = json.loads(line)
            if data.get('type') == 'USER_INPUT':
                out.write(f"--- STEP {data.get('step_index')} ---\n")
                out.write(data.get('content', ''))
                out.write("\n\n")
        except:
            pass
