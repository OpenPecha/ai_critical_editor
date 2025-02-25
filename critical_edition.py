import time
import re
from antx import transfer
from tqdm import tqdm
from config import LLM
from utils import read_json_file, write_json_file
from pydantic import BaseModel, Field




class Critical_edition(BaseModel):
    critical_edition: str = Field(
         description="The critical edition of the verse with the resolved spelling variants.",
    )
    footnote: dict = Field(
        description="The footnote for all the resolved spelling variants in the critical edition with its corresponding note number as key of the dictionary and notes as value of dictionary in a string.",
    )

def get_critical_editor():
    critical_editor=LLM.with_structured_output(Critical_edition)
    return critical_editor

def has_spelling_variants(collated_verse):
    if re.search(r'<.+?>', collated_verse):
        return True
    return False

def get_critical_edition(verse, editor):
    critical_edition = ''
    collated_verse = verse.get('collated_verse', "")
    sanskrit_verse = verse.get('sanskrit_verse', "")
    verse_commentary_1 = verse.get('verse_commentary_1', "")
    verse_commentary_2 = verse.get('verse_commentary_2', "")
    verse_commentary_3 = verse.get('verse_commentary_3', "")
    verse_commentary_4 = verse.get('verse_commentary_4', "")
    if has_spelling_variants(collated_verse) == False:
        critical_edition, critical_apparatus = collated_verse, ""
        return critical_edition, critical_apparatus
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
- Choose the best reading based on both internal evidence and external witnesses (Sanskrit and commentaries)
- Format variant readings consistently: lemma ] witness-sigla variant
- Number footnotes consecutively
- Provide clear philological reasoning for each choice
- Maintain proper Tibetan Unicode formatting
- Include punctuation (shad ། ) in the main text but not in the apparatus
- When referring to the Sanskrit or commentaries, cite the specific terms that support your choice

Inputs :

Collated edition: {collated_verse}

Sanskrit source: {sanskrit_verse}

Commentary by Kunsang Palden(KP): {verse_commentary_1}

Commentary by Gyaltsab Dharma Rinchen(GDR): {verse_commentary_2}

Commentary by Khenpo Shenga(KS): {verse_commentary_3}

Commentary by Thokmey Sangpo(TS): {verse_commentary_4}

Please generate the critical edition following these specifications.
"""
    critical_editon_info = editor.invoke(prompt)
    critical_edition = critical_editon_info.critical_edition
    critical_apparatus = critical_editon_info.footnote
        
    return critical_edition, critical_apparatus

def get_critical_edition_with_marker(critical_edition, collated_verse):
    collated_verse = re.sub(r'<.+?>', '#', collated_verse)
    patterns = [['marker', r'(#)',]]
    critical_edition_with_marker =  transfer(collated_verse, patterns, critical_edition)
    chunks = re.split(r'(#)', critical_edition_with_marker)
    critical_edition_with_marker = ""
    marker = 1
    for chunk in chunks:
        if chunk == '#':
            critical_edition_with_marker += f"[{marker}]"
            marker += 1
        else:
            critical_edition_with_marker += chunk
    return critical_edition_with_marker





if __name__ == "__main__":
    start_time = time.time()
    chojuk_with_ce = []
    seg_walker = 1
    chojuk_mapping = read_json_file('./data/chojuk_mapping.json')
    
    critical_editor = get_critical_editor()
    for chojuk_verse in tqdm(chojuk_mapping, desc="Processing Verses"):
        collated_verse = chojuk_verse.get('collated_verse', "")
        try:
            critical_edition, critical_apparatus = get_critical_edition(chojuk_verse, critical_editor)
        except:
            critical_edition = re.sub(r'<.+?>', '', collated_verse)
            critical_apparatus = ""
        clean_critical_edition = re.sub(r'\d+', '', critical_edition)
        if critical_apparatus:
            critical_edition_with_marker = get_critical_edition_with_marker(critical_edition, collated_verse)
        else:
            critical_edition_with_marker = critical_edition
        cur_verse = {
            'collated_edition': collated_verse,
            'critical_edition': clean_critical_edition,
            'critical_edition_with_marker': critical_edition_with_marker,
            'critical_apparatus': critical_apparatus
        }
        write_json_file(f'./data/chojuk/seg_{seg_walker:03}.json', cur_verse)
        seg_walker += 1
        chojuk_with_ce.append(cur_verse)
    write_json_file('./data/chojuk_with_ce.json', chojuk_with_ce)
    end_time = time.time()
    print(f"Task completed in {end_time - start_time:.2f} seconds")
