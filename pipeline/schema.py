"""
Ontology schema definition and controlled vocabularies.
Defines OWL classes, properties, and normalization helpers.
"""

import re
import pandas as pd
from rdflib import Graph, Literal
from rdflib.namespace import RDF, OWL, RDFS, XSD, SKOS

from pipeline.config import FKG, HEALS, HEALS_ING


# ══════════════════════════════════════════════════════════════════════════
#  CONTROLLED VOCABULARIES
# ══════════════════════════════════════════════════════════════════════════

CUISINE_MAP = {
    "indian": "Indian",
    "north indian": "NorthIndian",
    "northindian": "NorthIndian",
    "north indian recipes": "NorthIndian",
    "south indian": "SouthIndian",
    "southindian": "SouthIndian",
    "south indian recipes": "SouthIndian",
    "punjabi": "Punjabi",
    "rajasthani": "Rajasthani",
    "bengali": "Bengali",
    "gujarati": "Gujarati",
    "maharashtrian": "Maharashtrian",
    "kerala": "Kerala",
    "keralarecipes": "Kerala",
    "kerala recipes": "Kerala",
    "hyderabadi": "Hyderabadi",
    "chettinad": "Chettinad",
    "mughlai": "Mughlai",
    "goan": "Goan",
    "goan recipes": "Goan",
    "andhra": "Andhra",
    "tamil": "Tamil",
    "tamil nadu": "TamilNadu",
    "karnataka": "Karnataka",
    "bihari": "Bihari",
    "odia": "Odia",
    "kashmiri": "Kashmiri",
    "assamese": "Assamese",
    "manipuri": "Manipuri",
    "north east indian": "NorthEastIndian",
    "north east indian recipes": "NorthEastIndian",
    "parsi": "Parsi",
    "parsi recipes": "Parsi",
    "udupi": "Udupi",
    "lucknowi": "Lucknowi",
    "awadhi": "Awadhi",
    "mangalorean": "Mangalorean",
    "konkan": "Konkan",
    "sindhi": "Sindhi",
    "malvani": "Malvani",
    "coorg": "Coorg",
    "nagaland": "Nagaland",
    "uttarpradesh": "UttarPradesh",
    "uttar pradesh": "UttarPradesh",
    "jharkhand": "Jharkhand",
    "haryana": "Haryana",
    "oriya": "Oriya",
    "malabar": "Malabar",
}

DIET_MAP = {
    "vegetarian": "Vegetarian",
    "vegan": "Vegan",
    "non vegetarian": "NonVegetarian",
    "non-vegetarian": "NonVegetarian",
    "nonvegetarian": "NonVegetarian",
    "non vegeterian": "NonVegetarian",
    "jain": "Jain",
    "diabetic friendly": "DiabeticFriendly",
    "high protein non vegetarian": "HighProteinNonVeg",
    "high protein vegetarian": "HighProteinVeg",
    "eggetarian": "Eggetarian",
    "gluten free": "GlutenFree",
    "sugar free diet": "SugarFree",
    "no onion no garlic (sattvic)": "Satvik",
    "satvik": "Satvik",
}

COURSE_MAP = {
    "main course": "MainCourse",
    "side dish": "SideDish",
    "snack": "Snack",
    "dessert": "Dessert",
    "breakfast": "Breakfast",
    "lunch": "Lunch",
    "dinner": "Dinner",
    "appetizer": "Appetizer",
    "starter": "Starter",
    "beverage": "Beverage",
    "drink": "Drink",
    "one pot dish": "OnePotDish",
    "brunch": "Brunch",
    "soup": "Soup",
    "salad": "Salad",
    "chutney": "Chutney",
    "pickle": "Pickle",
    "bread": "Bread",
    "rice": "Rice",
    "dal": "Dal",
    "curry": "Curry",
}

# ── Ingredient-based diet inference ────────────────────────────────────────
# Keywords (lowercased) that indicate non-vegetarian ingredients.
# Matched as substrings against the resolved ingredient slug/name.
_NON_VEG_KEYWORDS = [
    "chicken", "mutton", "lamb", "pork", "beef", "fish", "prawn",
    "shrimp", "crab", "lobster", "squid", "clam", "sardine", "mackerel",
    "pomfret", "hilsa", "rohu", "surmai", "salmon", "tuna", "bacon",
    "ham", "sausage", "keema", "gosht", "murg", "meat", "duck",
    "venison", "quail", "anchov",
]

_EGG_KEYWORDS = ["egg"]

# Ingredient names (lowercased) or substrings that should NOT trigger
# a non-veg or egg match, to avoid false positives.
_FALSE_POSITIVE_EXCLUSIONS = {
    "eggplant", "eggless", "egg replacer", "eggnog flavoring",
    "turkey berries", "turkeyberries",
    "goat cheese", "goatcheese",
    "tender coconut meat", "tendercoconutmeat",
    "coconut meat", "coconutmeat",
    "champagne",
    "oyster sauce", "oystersauce",
    "fish sauce", "fishsauce",
    "nutmeg",
    "drumstick",
    "jackfruit",
    "mock meat", "mockmeat",
    "soy meat", "soymeat",
    "pazham",        # Nendra Pazham Banana — "ham" is a false substring match
    "nendrapazham",
    "garam masala",  # "ham" is a false substring match
    "garammasala",
    "graham",        # Graham crackers — "ham" false match
    "chamomile",     # "ham" false match
}


def infer_diet_from_ingredients(ingredient_names: list[str]) -> str:
    """
    Infer diet type from a list of resolved ingredient names.

    Returns one of: "NonVegetarian", "Eggetarian", "Vegetarian".
    """
    has_egg = False

    for ing in ingredient_names:
        if not ing:
            continue
        ing_lower = ing.lower().replace(" ", "").replace("-", "").replace("_", "")
        ing_lower_spaced = ing.lower()

        # Check if this ingredient matches any false-positive exclusion
        is_excluded = any(
            exc.replace(" ", "") in ing_lower for exc in _FALSE_POSITIVE_EXCLUSIONS
        )
        if is_excluded:
            continue

        # Check non-veg keywords
        for kw in _NON_VEG_KEYWORDS:
            if kw in ing_lower_spaced or kw in ing_lower:
                return "NonVegetarian"

        # Check egg keywords
        for kw in _EGG_KEYWORDS:
            if kw in ing_lower_spaced or kw in ing_lower:
                has_egg = True

    return "Eggetarian" if has_egg else "Vegetarian"


# ══════════════════════════════════════════════════════════════════════════
#  HELPER FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════

def slugify(text: str) -> str:
    """Convert text to a URI-safe slug: PascalCase, no special chars."""
    if not text or (isinstance(text, float) and pd.isna(text)):
        return "Unknown"
    text = str(text).strip()
    # Remove special characters except spaces and hyphens
    text = re.sub(r"[^\w\s-]", "", text)
    # Split on whitespace/hyphens, title-case each word, join
    words = re.split(r"[\s\-_]+", text)
    return "".join(w.capitalize() for w in words if w)


def norm_cuisine(raw) -> str:
    """Normalize a raw cuisine string to a controlled vocabulary slug."""
    if pd.isna(raw):
        return "Indian"
    key = str(raw).strip().lower().replace("-", " ")
    return CUISINE_MAP.get(key, slugify(str(raw)))


def norm_diet(raw) -> str:
    """Normalize a raw diet string to a controlled vocabulary slug."""
    if pd.isna(raw):
        return "Vegetarian"
    key = str(raw).strip().lower().replace("-", " ")
    return DIET_MAP.get(key, slugify(str(raw)))


def norm_course(raw) -> str | None:
    """Normalize a raw course string to a controlled vocabulary slug."""
    if pd.isna(raw) or not str(raw).strip():
        return None
    key = str(raw).strip().lower().replace("-", " ")
    return COURSE_MAP.get(key, slugify(str(raw)))


def parse_time(raw) -> int | None:
    """Extract integer minutes from a raw time value."""
    if pd.isna(raw):
        return None
    m = re.search(r"(\d+)", str(raw))
    return int(m.group(1)) if m else None


# ══════════════════════════════════════════════════════════════════════════
#  ONTOLOGY SCHEMA BUILDER
# ══════════════════════════════════════════════════════════════════════════

def build_schema(g: Graph):
    """Add OWL class and property definitions to the graph."""

    # ── Namespace bindings ─────────────────────────────────────────────
    g.bind("skos", SKOS)

    # ── Classes ────────────────────────────────────────────────────────
    classes = {
        HEALS.Recipe:       "Recipe",
        HEALS_ING.Ingredient: "Ingredient",
        FKG.Cuisine:        "Cuisine",
        FKG.DietType:       "DietType",
        FKG.Course:         "Course",
        FKG.Nutrient:       "Nutrient",
    }
    for uri, label in classes.items():
        g.add((uri, RDF.type, OWL.Class))
        g.add((uri, RDFS.label, Literal(label)))

    # ── Object Properties ──────────────────────────────────────────────
    obj_props = {
        "hasIngredient": (HEALS.Recipe, HEALS_ING.Ingredient),
        "hasCuisine":    (HEALS.Recipe, FKG.Cuisine),
        "hasDietType":   (HEALS.Recipe, FKG.DietType),
        "hasCourse":     (HEALS.Recipe, FKG.Course),
    }
    for prop, (domain, rng) in obj_props.items():
        uri = FKG[prop]
        g.add((uri, RDF.type, OWL.ObjectProperty))
        g.add((uri, RDFS.domain, domain))
        g.add((uri, RDFS.range, rng))

    # ── Datatype Properties ────────────────────────────────────────────
    data_props = {
        "preparationTime": XSD.integer,
        "hasName":         XSD.string,
        "hasInstruction":  XSD.string,
        "hasDescription":  XSD.string,
        "hasURL":          XSD.anyURI,
        "hasImageURL":     XSD.anyURI,
        "hasServings":     XSD.integer,
    }
    for prop, dtype in data_props.items():
        uri = FKG[prop]
        g.add((uri, RDF.type, OWL.DatatypeProperty))
        g.add((uri, RDFS.domain, HEALS.Recipe))
        g.add((uri, RDFS.range, dtype))

    # ── Annotation Properties (SKOS) ──────────────────────────────────
    # skos:altLabel is used for transliteration variants of ingredient names
    g.add((SKOS.altLabel, RDF.type, OWL.AnnotationProperty))
