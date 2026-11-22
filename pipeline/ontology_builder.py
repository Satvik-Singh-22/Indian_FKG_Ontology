"""
RDF ontology graph builder.
Handles graph initialization, recipe insertion, and serialization.
"""

import pandas as pd
from pathlib import Path
from rdflib import Graph, Literal
from rdflib.namespace import RDF, OWL, RDFS, XSD

from pipeline.config import FKG, HEALS, HEALS_ING
from pipeline.schema import (
    build_schema, slugify, norm_cuisine, norm_diet, norm_course, parse_time,
    infer_diet_from_ingredients,
)


def init_graph() -> Graph:
    """Create a fresh RDF graph with namespace bindings and schema."""
    g = Graph()
    g.bind("fkg", FKG)
    g.bind("heals", HEALS)
    g.bind("heals-ing", HEALS_ING)
    g.bind("owl", OWL)
    build_schema(g)
    print(f"  Initialized fresh ontology graph with schema ({len(g)} triples).")
    return g


def load_graph(ttl_path: str | Path) -> Graph:
    """Load an existing Turtle file into a graph."""
    g = Graph()
    g.bind("fkg", FKG)
    g.bind("heals", HEALS)
    g.bind("heals-ing", HEALS_ING)
    g.bind("owl", OWL)
    g.parse(str(ttl_path), format="turtle")
    print(f"  Loaded existing ontology from {ttl_path} ({len(g)} triples).")
    return g


def recipe_exists(g: Graph, recipe_name: str) -> bool:
    """Check if a recipe already exists in the graph."""
    recipe_uri = HEALS[slugify(recipe_name)]
    return (recipe_uri, RDF.type, HEALS.Recipe) in g


def remove_recipe_from_graph(g: Graph, recipe_name: str):
    """Remove a recipe node and its direct triples from the RDF graph."""
    recipe_uri = HEALS[slugify(recipe_name)]
    g.remove((recipe_uri, None, None))


def add_recipe_to_graph(g: Graph, recipe: dict, resolved_ingredients: list[str]):
    """Add a single recipe and its relationships to the RDF graph."""
    name = recipe.get("name", "").strip()
    if not name:
        return

    recipe_uri = HEALS[slugify(name)]
    g.add((recipe_uri, RDF.type, HEALS.Recipe))
    g.add((recipe_uri, RDFS.label, Literal(name)))

    # Cuisine
    c_slug = norm_cuisine(recipe.get("cuisine"))
    c_uri = FKG[c_slug]
    g.add((c_uri, RDF.type, FKG.Cuisine))
    g.add((c_uri, RDFS.label, Literal(c_slug)))
    g.add((recipe_uri, FKG.hasCuisine, c_uri))

    # Diet — use source value if available, otherwise infer from ingredients
    raw_diet = recipe.get("diet")
    if raw_diet and not pd.isna(raw_diet):
        d_slug = norm_diet(raw_diet)
    else:
        d_slug = infer_diet_from_ingredients(resolved_ingredients)
    d_uri = FKG[d_slug]
    g.add((d_uri, RDF.type, FKG.DietType))
    g.add((d_uri, RDFS.label, Literal(d_slug)))
    g.add((recipe_uri, FKG.hasDietType, d_uri))

    # Course
    course = norm_course(recipe.get("course"))
    if course:
        co_uri = FKG[course]
        g.add((co_uri, RDF.type, FKG.Course))
        g.add((co_uri, RDFS.label, Literal(course)))
        g.add((recipe_uri, FKG.hasCourse, co_uri))

    # Preparation time
    t = parse_time(recipe.get("total_time")) or parse_time(recipe.get("prep_time"))
    if t is not None:
        g.add((recipe_uri, FKG.preparationTime, Literal(t, datatype=XSD.integer)))

    # String/URI properties
    for prop, key, dtype, limit in [
        ("hasInstruction", "instructions", XSD.string, 3000),
        ("hasDescription", "description", XSD.string, 1000),
        ("hasURL", "url", XSD.anyURI, None),
        ("hasImageURL", "image_url", XSD.anyURI, None),
    ]:
        val = recipe.get(key)
        if val and not pd.isna(val):
            s = str(val)[:limit] if limit else str(val)
            g.add((recipe_uri, FKG[prop], Literal(s, datatype=dtype)))

    # Ingredients
    for ing_name in resolved_ingredients:
        if not ing_name:
            continue
        ing_uri = HEALS_ING[slugify(ing_name)]
        g.add((ing_uri, RDF.type, HEALS_ING.Ingredient))
        g.add((ing_uri, RDFS.label, Literal(ing_name)))
        g.add((recipe_uri, FKG.hasIngredient, ing_uri))


def save_graph(g: Graph, output_path: str | Path):
    """Serialize the graph to a Turtle file."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    g.serialize(str(output_path), format="turtle")
    print(f"\n  💾 Saved ontology → {output_path}")


def print_stats(g: Graph):
    """Print summary statistics of the graph."""
    recipes = sum(1 for _ in g.subjects(RDF.type, HEALS.Recipe))
    ingredients = sum(1 for _ in g.subjects(RDF.type, HEALS_ING.Ingredient))
    cuisines = sum(1 for _ in g.subjects(RDF.type, FKG.Cuisine))
    diets = sum(1 for _ in g.subjects(RDF.type, FKG.DietType))
    print(f"  Total triples : {len(g)}")
    print(f"  Recipes       : {recipes}")
    print(f"  Ingredients   : {ingredients}")
    print(f"  Cuisines      : {cuisines}")
    print(f"  Diet types    : {diets}")
