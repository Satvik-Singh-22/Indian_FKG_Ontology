"""
SPARQL Regression Tests for the Indian Food Knowledge Graph.

These queries serve as baseline validation checks to ensure data integrity
after any KG modification (dedup, scaling, alt-label injection, etc.).

Usage:
    python -m pipeline.sparql_tests
"""

from rdflib import Graph
from rdflib.namespace import RDF, RDFS, SKOS
from pipeline.config import FKG, HEALS, HEALS_ING, OUTPUT_TTL


# ── Namespace URIs ────────────────────────────────────────────────────
HEALS_NS = str(HEALS)       # http://purl.org/heals/food/
FKG_NS   = str(FKG)         # http://fkg.iiitd.ac.in/ontology#
ING_NS   = str(HEALS_ING)   # http://purl.org/heals/ingredient/


# ══════════════════════════════════════════════════════════════════════
#  QUERY DEFINITIONS
# ══════════════════════════════════════════════════════════════════════

QUERIES = {

    # ── 4.1 SPARQL Regression Tests ───────────────────────────────────

    "test_1_preparation_time": {
        "name": "Preparation Time (< 45 min)",
        "sparql": f"""
            SELECT (COUNT(?recipe) AS ?cnt)
            WHERE {{
                ?recipe a <{HEALS_NS}Recipe> ;
                        <{FKG_NS}preparationTime> ?time .
                FILTER(?time < 45)
            }}
        """,
        "validate": lambda rows: int(rows[0][0]) > 0,
        "format":   lambda rows: f"Recipes under 45 min: {int(rows[0][0])}",
    },

    "test_2_north_indian_vegetarian": {
        "name": "Multi-Constraint: North Indian Vegetarian",
        "sparql": f"""
            SELECT (COUNT(?recipe) AS ?cnt)
            WHERE {{
                ?recipe a <{HEALS_NS}Recipe> ;
                        <{FKG_NS}hasCuisine> ?cuisine ;
                        <{FKG_NS}hasDietType> ?diet .
                ?cuisine rdfs:label ?cuisineLabel .
                ?diet rdfs:label ?dietLabel .
                FILTER(STR(?cuisineLabel) = 'NorthIndian'
                    && STR(?dietLabel) = 'Vegetarian')
            }}
        """,
        "validate": lambda rows: int(rows[0][0]) > 0,
        "format":   lambda rows: f"North Indian Vegetarian recipes: {int(rows[0][0])}",
    },

    "test_3_top_ingredients": {
        "name": "Aggregation / Top 5 Ingredients",
        "sparql": f"""
            SELECT ?ingredientLabel (COUNT(?recipe) AS ?cnt)
            WHERE {{
                ?recipe a <{HEALS_NS}Recipe> ;
                        <{FKG_NS}hasIngredient> ?ingredient .
                ?ingredient rdfs:label ?ingredientLabel .
            }}
            GROUP BY ?ingredientLabel
            ORDER BY DESC(?cnt)
            LIMIT 5
        """,
        "validate": lambda rows: len(rows) == 5 and int(rows[0][1]) > 0,
        "format":   lambda rows: ", ".join(
            f"{r[0]} ({int(r[1])})" for r in rows
        ),
    },

    "test_4_co_occurrence_tomato_paneer": {
        "name": "Multi-Ingredient Co-occurrence: Tomatoes + Paneer",
        "sparql": f"""
            SELECT (COUNT(?recipe) AS ?cnt)
            WHERE {{
                ?recipe a <{HEALS_NS}Recipe> ;
                        <{FKG_NS}hasIngredient> ?ing1 ;
                        <{FKG_NS}hasIngredient> ?ing2 .
                ?ing1 rdfs:label 'Tomatoes' .
                ?ing2 rdfs:label 'Paneer' .
            }}
        """,
        "validate": lambda rows: int(rows[0][0]) > 0,
        "format":   lambda rows: f"Recipes with both Tomatoes and Paneer: {int(rows[0][0])}",
    },

    "test_5_cuisine_distribution": {
        "name": "Cuisine Distribution (top 10)",
        "sparql": f"""
            SELECT ?cuisineLabel (COUNT(?recipe) AS ?cnt)
            WHERE {{
                ?recipe a <{HEALS_NS}Recipe> ;
                        <{FKG_NS}hasCuisine> ?cuisine .
                ?cuisine rdfs:label ?cuisineLabel .
            }}
            GROUP BY ?cuisineLabel
            ORDER BY DESC(?cnt)
            LIMIT 10
        """,
        "validate": lambda rows: len(rows) > 0,
        "format":   lambda rows: ", ".join(
            f"{r[0]} ({int(r[1])})" for r in rows
        ),
    },

    # ── 4.2 Transliteration / Vernacular Query ────────────────────────

    "test_6_transliteration": {
        "name": "Transliteration / Vernacular Lookup",
        "sparql": f"""
            SELECT ?canonicalLabel ?altLabel
            WHERE {{
                ?ingredient a <{ING_NS}Ingredient> ;
                            rdfs:label ?canonicalLabel ;
                            skos:altLabel ?altLabel .
                FILTER(STR(?altLabel) IN ("jeera", "haldi", "hing", "vendakkai"))
            }}
        """,
        "validate": lambda rows: len(rows) == 4,
        "format":   lambda rows: ", ".join(
            f'"{r[1]}" → {r[0]}' for r in rows
        ),
    },

    # ── 4.3 Structural Integrity ──────────────────────────────────────

    "test_7_orphaned_recipes": {
        "name": "Orphaned Recipes (0 ingredients)",
        "sparql": f"""
            SELECT (COUNT(?recipe) AS ?cnt)
            WHERE {{
                ?recipe a <{HEALS_NS}Recipe> .
                FILTER NOT EXISTS {{
                    ?recipe <{FKG_NS}hasIngredient> ?ing
                }}
            }}
        """,
        "validate": lambda rows: int(rows[0][0]) == 0,
        "format":   lambda rows: f"Orphaned recipes: {int(rows[0][0])}",
    },

    "test_8_dangling_ingredients": {
        "name": "Dangling Ingredient References",
        "sparql": f"""
            SELECT (COUNT(?ing) AS ?cnt)
            WHERE {{
                ?recipe <{FKG_NS}hasIngredient> ?ing .
                FILTER NOT EXISTS {{
                    ?ing a <{ING_NS}Ingredient>
                }}
            }}
        """,
        "validate": lambda rows: int(rows[0][0]) == 0,
        "format":   lambda rows: f"Dangling references: {int(rows[0][0])}",
    },
}


# ══════════════════════════════════════════════════════════════════════
#  RUNNER
# ══════════════════════════════════════════════════════════════════════

def load_graph() -> Graph:
    """Load the KG from the default output path."""
    g = Graph()
    g.bind("fkg", FKG)
    g.bind("heals", HEALS)
    g.bind("heals-ing", HEALS_ING)
    g.bind("skos", SKOS)
    g.parse(str(OUTPUT_TTL), format="turtle")
    return g


def run_all(g: Graph | None = None, verbose: bool = True) -> bool:
    """
    Run all regression tests against the graph.

    Returns True if all tests pass, False otherwise.
    """
    if g is None:
        print("  Loading KG…")
        g = load_graph()
        print(f"  Loaded {len(g)} triples\n")

    passed = 0
    failed = 0

    for test_id, test in QUERIES.items():
        name = test["name"]
        rows = list(g.query(test["sparql"]))

        ok = test["validate"](rows)
        detail = test["format"](rows)

        if ok:
            passed += 1
            if verbose:
                print(f"  ✓ {name}")
                print(f"    {detail}")
        else:
            failed += 1
            if verbose:
                print(f"  ✗ {name}  ← FAILED")
                print(f"    {detail}")

    if verbose:
        print(f"\n  {'─' * 40}")
        print(f"  Results: {passed} passed, {failed} failed, {passed + failed} total")

    return failed == 0


def main():
    print("\n🧪 SPARQL Regression Tests")
    print("=" * 60)

    all_ok = run_all()

    if all_ok:
        print("\n  ✅ ALL TESTS PASSED")
    else:
        print("\n  ❌ SOME TESTS FAILED")
        exit(1)


if __name__ == "__main__":
    main()
