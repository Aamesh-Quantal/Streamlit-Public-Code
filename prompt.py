prompts = {
  "text_prompt": """
You are analyzing a wine label image. Your task is twofold:

1. **Extract all readable text from this wine label exactly as it appears.**

### Text Extraction Rules:
- Preserve capitalization, spacing, and formatting exactly as seen.
- Do not infer, translate, or guess missing text—only extract what is clearly visible.
- If text is partially cut off, return it as-is without completion.
- For stylized or cursive fonts, extract characters as best as possible—even approximated characters are better than skipping.
- Do not merge or "correct" fragmented words.
- Maintain the vertical and visual order of lines on the label.
- Ignore decorative, non-informative elements (swirls, flourishes, etc.).
- **If spelling mistakes are obvious (like missing or incorrect characters), correct them where possible** (e.g., “Beaw Sejou” → “Beau Sejour,” “Philippe Youan” → “Philippe Jouan”).
- **Do not output any labels like "Vintage," "Producer," etc.** The goal is only to extract the raw text as seen.

---

2. **Structure the extracted text in the following format:**

Vintage:  
Producer Name:  
Fanciful Name / Vineyard Name (if present):  
Appellation:  
Grape Variety (if can be inferred):  
Size (if present, e.g., in ML):  
Additional Designations (Grand Cru, 1er Cru, Vieilles Vignes, etc.):

### Structuring Rules:
- Do not fabricate, infer, or complete missing details.
- Categorize only what is clearly visible on the label.
- **If a field cannot be confidently filled, omit that entire line (no label, no blank).**
- Only infer a field (e.g., Grape or Appellation) when logically certain and universally standardized (e.g., Châteauneuf-du-Pape = GSM blend).
- **Do not output labels or field names, only raw values.**
- **Shorten any longer terms**, such as **Denominacion De Origen** to **DO** (use standard abbreviations).
- **Do not assume or invent any data, especially vintage year**—only include it if clearly visible.
- **Do not include Size if it is 750 mL.**
- No extra explanation—return only the structured data.
""",

    "format_prompt": """
        Format the following wine data (already extracted & structured) into **one** space-separated, Title-Case filename:

        **Vintage Producer Name (Additional Designations) Appellation Classification Vineyard Name Grape Variety Size**

        ### Formatting Rules:
        - Output exactly one clean line. No commas, periods, parentheses, brackets, hyphens, ampersands or other special characters.
        - Strip all accents/diacritics (e.g., “é” → “e”).
        - Title Case each major word (e.g., “Domaine Leflaive”).
        - Never invent or assume data; use only what is explicitly provided.
        - **Omit any slot that is empty. Do not insert placeholders or field names.**
        - **Only include Vintage if the structured data contains a real four-digit year.**
        - **Do not output field labels** like "Vintage," "Producer," etc.
        - **Do not output ownership-only names** like “Famille” unless it is the actual estate name.
        - **Do not use quotes** (for Designations or anything else).
        - **If a field is missing or empty, omit it entirely.** Do not insert any placeholder or label.
        - **Do not repeat any words** in the final output, even if they appear multiple times in the extracted data (e.g., "Grand Cru Classe", "Vieilles Vignes").

        ### Classification Rules:
        - **For Grand Cru Classe**, ensure it is only included **once** even if repeated in the input.
        - Only allow these exact classification tokens:
        - **Burgundy**: “1er Cru” (not “Premier Cru”) before vineyard.
        - **Bordeaux**: “Grand Cru Classe” after the appellation if applicable.
        - **Champagne**: prepend dosage/style (e.g., Extra Brut Blanc de Noirs) before “Champagne.”
        - **Italy/Germany/Spain**: DOCG, DOC, AOC, IGT
        - **Do not include both "Premier Cru" and "1er Cru"**—keep only "1er Cru."

        ### World-Specific Conventions

        1. **New World** (Argentina, Chile, Australia, US, South Africa…):
        Vintage Producer FantasyName/Cuvee Appellation GrapeOrStyle Size-if-≠750mL


        2. **Old World** (France, Germany, Spain, Chile…):
        Vintage Producer Designations Appellation Classification FantasyName/Cuvée GrapeOrStyle Size-if-≠750mL

        - **Designations** (e.g., Vieilles Vignes) go immediately after Producer, without quotes.
        - **FantasyName/Cuvée mapping**: pull exactly from the “Fanciful/Vineyard Name” field for:
        - **Germany**: quoted estate or cru label (e.g., Hollenpfad Im Muhlenberg)
        - **Spain**: bottling’s unique name (e.g., La Iruelas, Ultreia, El Rapolao)
        - **Chile**: vineyard cuvée (e.g., Imaginador, Vinista, Miles)

        3. **Italy**: follows Old World rules; exact pattern TBD (rows highlighted in red).

        Return only the final cleaned, space-separated name.
"""
}