import time
from tqdm import tqdm
from config import LLM
from utils import read_json_file, write_json_file
from pydantic import BaseModel, Field




class Critical_edition(BaseModel):
    critical_edition: str = Field(
         description="The critical edition of the verse",
    )
    footnote: str = Field(
        description="The footnote for the critical edition.",
    )

def get_critical_editor():
    critical_editor=LLM.with_structured_output(Critical_edition)
    return critical_editor

def get_critical_edition(verse, editor):
    critical_edition = ''
    collated_verse = verse.get('collated_verse', "")
    sanskrit_verse = verse.get('sanskrit_verse', "")
    verse_commentary = verse.get('verse_commentary', "")
    prompt = f"""
You are a skilled philologist specializing in Buddhist texts. Your task is to create a critical edition of a Tibetan text following academic conventions. You will receive:

Please produce:

1. A critical edition of the Tibetan text
2. A critical apparatus in footnotes that:
   - Uses Arabic numerals for footnotes
   - Lists variants using the lemma followed by square bracket (])
   - Lists witness sigla for each variant
   - Justifies the chosen reading based on the Sanskrit and/or commentary
   - Uses proper philological abbreviations and conventions

Rules:
- Choose the best reading based on both internal evidence and external witnesses (Sanskrit and commentary)
- Format variant readings consistently: lemma ] witness-sigla variant
- Number footnotes consecutively
- Provide clear philological reasoning for each choice
- Maintain proper Tibetan Unicode formatting
- Include punctuation (shad ། ) in the main text but not in the apparatus
- When referring to the Sanskrit or commentary, cite the specific terms that support your choice

Inputs :

Collated edition: {collated_verse}

Sanskrit source: {sanskrit_verse}

Commentary by TS: {verse_commentary}

Please generate the critical edition following these specifications.
"""
    critical_editon_info = editor.invoke(prompt)
    critical_edition = critical_editon_info.critical_edition
    critical_apparatus = critical_editon_info.footnote
        
    return critical_edition, critical_apparatus




if __name__ == "__main__":
    start_time = time.time()
    chojuk_with_ce = []
    chojuk_mapping = read_json_file('./data/chojuk_mapping.json')
    critical_editor = get_critical_editor()
    for chojuk_verse in tqdm(chojuk_mapping, desc="Processing Verses"):
        
        critical_edition, critical_apparatus = get_critical_edition(chojuk_verse, critical_editor)
        cur_verse = chojuk_verse
        cur_verse['critical_edition'] = critical_edition
        cur_verse['critical_apparatus'] = critical_apparatus
        chojuk_with_ce.append(cur_verse)
    write_json_file('./data/chojuk_with_ce.json', chojuk_with_ce)
    end_time = time.time()
    print(f"Task completed in {end_time - start_time:.2f} seconds")
