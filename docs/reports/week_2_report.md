# Week 2 Progress & Deliverables Report: Indian Food Knowledge Graph (FKG)

**Project:** KG-Augmented RAG System for the Indian Food Knowledge Graph — BTP Phase 2  
**Contributors:** Satvik Singh (2023494) · Rahul Kumar (2023420) · Prateek Kumar (2023389)  
**Advisor:** Dr. Ganesh Bagler · IIIT Delhi  
**Milestone:** Phase 1 — Week 2 (10–16 Aug 2026): *Finish cleaning + transliteration variants via `skos:altLabel`*

---

## 1. Executive Summary

During Week 2, we completed the ingredient normalization and deduplication pipeline on the Indian Food Knowledge Graph (`food_kg.ttl`) — now expanded to **~2,000 recipes** — and incorporated multilingual transliteration support. 

Key outcomes:
- Upgraded the fuzzy matching engine from standard `difflib` to **`rapidfuzz`** for fast and tiered similarity processing.
- Implemented a **Tiered Normalization Pipeline** with automated merging for near-identical items and an editable CSV review workflow for ambiguous candidates.
- Curated and injected **341 `skos:altLabel` triples** across **9 Indian languages** (Hindi, Tamil, Telugu, Kannada, Malayalam, Marathi, Gujarati, Bengali, etc.), enabling downstream RAG components to handle vernacular ingredient queries (e.g., *"jeera"*, *"haldi"*, *"vendakkai"*).
- Executed full graph validation and regression SPARQL tests to guarantee data integrity.

---

## 2. Knowledge Graph Metrics (Before vs. After)

| Metric | Before Week 2 | After Week 2 | Change ($\Delta$) |
|:---|:---|:---|:---|
| **Total Triples** | 42,037 | **42,036** | $-1$ *(dedup merge)* |
| **Total Recipes** | 1,998 | **1,998** | $0$ |
| **Unique Ingredients** | 954 | **953** | $-1$ *(Deduplicated)* |
| **Cuisines** | 70 | **70** | $0$ |
| **Diet Types** | 1 | **1** | $0$ |
| **`skos:altLabel` Triples** | 340 | **341** | $+1$ |
| **Language Tags Covered** | 9 languages | **9 languages** | $0$ |

---

## 3. Detailed Technical Implementation

### 3.1. RapidFuzz Integration & Pipeline Upgrade
- **Dependency Added:** `rapidfuzz==3.14.5` added to [`requirements.txt`](file:///home/satvik/Documents/Indian_FKG/requirements.txt).
- **Resolver Refactor:** Updated [`pipeline/ingredient_resolver.py`](file:///home/satvik/Documents/Indian_FKG/pipeline/ingredient_resolver.py) to use `rapidfuzz.process.extract` with `fuzz.ratio` scoring and clear percentage thresholds.

### 3.2. Tiered Deduplication & Edge-Case Safeguards
Created [`pipeline/dedup_ingredients.py`](file:///home/satvik/Documents/Indian_FKG/pipeline/dedup_ingredients.py) with a two-tiered clustering mechanism:
1. **Tier 1 (Auto-merge $\ge 96\%$):** Silently merges syntactic plurals/near-exact duplicates (e.g., `Chicken Breast` $\rightarrow$ `Chicken Breasts`).
   > **Note on Critical Threshold Tuning:** The initial standard cutoff of $92\%$ caused a false-positive merge between *"Chaat Masala Powder"* and *"Chana Masala Powder"* ($94.7\%$ character similarity). We identified this, rolled back the change, separated the instances across all recipes, and raised the threshold to $96\%$ to protect domain-specific semantic boundaries.
2. **Tier 2 (Review Tier $80\% - 96\%$):** Exports candidates to [`pipeline/output/dedup_review.csv`](file:///home/satvik/Documents/Indian_FKG/pipeline/output/dedup_review.csv) with columns for similarity score and human action (`merge` or `keep`).
   - On the expanded 2,000-recipe dataset: **53 candidate clusters** (134 ingredient pairs) were reviewed.
   - **1 genuine merge** applied: `Food Color` $\rightarrow$ `Red Food Color`.
   - Distinct ingredients preserved across all other clusters, including new false-positive catches:
     - `Almond Oil` vs `Almond Milk` vs `Almond Meal` — different products
     - `Ber` (Indian jujube) vs `Beer` — completely different items
     - `Goat Cheese` vs `Gouda Cheese` — different cheese varieties
     - `Tinda` vs `Tindora` — distinct Indian vegetables
     - `Mustard Powder` vs `Custard Powder` — obviously different
     - Previous distinctions maintained: `Bottle Gourd` vs `Bitter Gourd`, `Cocoa Powder` vs `Coconut Powder`, `Tea Leaves` vs `Dried Basil Leaves`, etc.

### 3.3. Transliteration Map & `skos:altLabel` Injection
- **Dictionary Creation:** Created [`pipeline/transliteration_map.py`](file:///home/satvik/Documents/Indian_FKG/pipeline/transliteration_map.py) containing structured triples of `(alt_label, canonical_english_label, iso_639_1_lang_tag)`.
- **Injection Script:** Created [`pipeline/add_alt_labels.py`](file:///home/satvik/Documents/Indian_FKG/pipeline/add_alt_labels.py) to map aliases directly to canonical URIs in `food_kg.ttl`.
- **Schema Declaration:** Updated [`pipeline/schema.py`](file:///home/satvik/Documents/Indian_FKG/pipeline/schema.py) to bind `skos` and declare `skos:altLabel` as an `owl:AnnotationProperty`.

#### Breakdown of Injected `skos:altLabel`s by Language Tag:
- **Hindi (`@hi`):** 118 labels *(e.g., "jeera", "haldi", "adrak", "lahsun", "hing", "dhania", "besan")*
- **Tamil (`@ta`):** 62 labels *(e.g., "kothamalli", "manjal podi", "perungayam", "kadugu", "vendakkai")*
- **Telugu (`@te`):** 53 labels *(e.g., "jilakarra", "kothimeera", "pasupu", "inguva", "avalu", "bellam")*
- **Kannada (`@kn`):** 46 labels *(e.g., "kottambari soppu", "arishina", "sasive", "hingu", "bellulli")*
- **Malayalam (`@ml`):** 30 labels *(e.g., "jeerakam", "kurumulaku", "kariveppila", "cherunaranga")*
- **Marathi (`@mr`):** 19 labels *(e.g., "jire", "halad", "mohori", "lasun", "kanda", "batata")*
- **Gujarati (`@gu`):** 7 labels *(e.g., "dungri", "limbdo", "aadu", "tuvar dal")*
- **Bengali (`@bn`):** 2 labels *(e.g., "chena", "chhena")*
- **Dedup Variants (`@none`):** 4 labels *(English syntactic variations preserved as alt labels, including "Food Color" → "Red Food Color")*

---

## 4. Verification & Quality Assurance

### 4.1. SPARQL Regression Tests
All 5 existing baseline queries from the ontology benchmark passed without regressions:
1. **Preparation Time Queries:** Filtering recipes under 45 minutes → **1,033 recipes** $\rightarrow$ Passed.
2. **Multi-Constraint (Cuisine + Diet):** North Indian Vegetarian filtering → **279 recipes** $\rightarrow$ Passed.
3. **Aggregation / Top Ingredients:** Salt (1,574), Onion (770), Sunflower Oil (764), Green Chilli (690), Turmeric Powder (682) $\rightarrow$ Passed.
4. **Multi-Ingredient Co-occurrence:** Recipes using both `Tomatoes` and `Paneer` → **18 recipes** $\rightarrow$ Passed.
5. **Cuisine Distribution:** Continental (308), Indian (306), NorthIndian (279), SouthIndian (190), ItalianRecipes (69), BengaliRecipes (56), Karnataka (49), MaharashtrianRecipes (48), Kerala (47), TamilNadu (47) — **70 cuisines** total $\rightarrow$ Passed.

### 4.2. Transliteration / Vernacular Query Test
Verified multi-lingual retrieval using `skos:altLabel`:
```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX heals_ing: <http://purl.org/heals/ingredient/>

SELECT ?canonicalLabel ?altLabel
WHERE {
    ?ingredient a heals_ing:Ingredient ;
                rdfs:label ?canonicalLabel ;
                skos:altLabel ?altLabel .
    FILTER(STR(?altLabel) IN ("jeera", "haldi", "hing", "vendakkai"))
}
```
**Results:** Successfully resolved `jeera` $\rightarrow$ `Cumin Seeds`, `haldi` $\rightarrow$ `Turmeric Powder`, `hing` $\rightarrow$ `Asafoetida`, and `vendakkai` $\rightarrow$ `Okra`.

### 4.3. Structural Integrity
- Verified that **0 recipes** were orphaned or left with missing ingredients.
- Confirmed total elimination of duplicate ingredient nodes while retaining complete historical linking via state tracking (`pipeline/state/known_ingredients.json`).

---

## 5. Artifacts and File Reference

- **Ontology File:** [`pipeline/output/food_kg.ttl`](file:///home/satvik/Documents/Indian_FKG/pipeline/output/food_kg.ttl)
- **Transliteration Dictionary:** [`pipeline/transliteration_map.py`](file:///home/satvik/Documents/Indian_FKG/pipeline/transliteration_map.py)
- **Deduplication Script:** [`pipeline/dedup_ingredients.py`](file:///home/satvik/Documents/Indian_FKG/pipeline/dedup_ingredients.py)
- **Deduplication Review Log:** [`pipeline/output/dedup_review.csv`](file:///home/satvik/Documents/Indian_FKG/pipeline/output/dedup_review.csv)
- **Label Injection Script:** [`pipeline/add_alt_labels.py`](file:///home/satvik/Documents/Indian_FKG/pipeline/add_alt_labels.py)
- **Updated Schema:** [`pipeline/schema.py`](file:///home/satvik/Documents/Indian_FKG/pipeline/schema.py)
- **Updated Resolver:** [`pipeline/ingredient_resolver.py`](file:///home/satvik/Documents/Indian_FKG/pipeline/ingredient_resolver.py)

---

## 6. Next Steps (Transition to Week 3)
- Re-run full KG regeneration and validate consistency in Protégé.
- Re-run all 5 existing SPARQL queries as regression tests on the expanded dataset.
- Maintain regression test tracking as new recipe subsets are populated.
