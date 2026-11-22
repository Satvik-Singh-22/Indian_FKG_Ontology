"""
Transliteration map: Hindi + regional-language ingredient aliases.

Each entry is (transliterated_name, canonical_english_name, lang_tag).
The lang_tag follows ISO 639-1 codes:
    hi  – Hindi       ta  – Tamil        te  – Telugu
    bn  – Bengali     kn  – Kannada      ml  – Malayalam
    mr  – Marathi     gu  – Gujarati     pa  – Punjabi
    or  – Odia        ur  – Urdu
"""

# ──────────────────────────────────────────────────────────────────────
#  (alt_label, canonical_label_in_KG, lang_tag)
#  canonical_label must match an existing rdfs:label on an Ingredient
#  node in food_kg.ttl exactly (case-sensitive).
# ──────────────────────────────────────────────────────────────────────

TRANSLITERATION_MAP: list[tuple[str, str, str]] = [
    # ── Spices & Seasonings ──────────────────────────────────────────
    # Cumin Seeds
    ("jeera",           "Cumin Seeds",              "hi"),
    ("zeera",           "Cumin Seeds",              "hi"),
    ("jeerakam",        "Cumin Seeds",              "ta"),
    ("jilakarra",       "Cumin Seeds",              "te"),
    ("jire",            "Cumin Seeds",              "mr"),
    ("jiiru",           "Cumin Seeds",              "kn"),
    ("jeerakam",        "Cumin Seeds",              "ml"),

    # Coriander Powder
    ("dhania powder",   "Coriander Powder",         "hi"),
    ("dhania",          "Coriander Powder",         "hi"),
    ("kothamalli podi", "Coriander Powder",         "ta"),
    ("dhaniya pudi",    "Coriander Powder",         "kn"),

    # Coriander Leaves
    ("hara dhania",     "Coriander Leaves",         "hi"),
    ("dhania patta",    "Coriander Leaves",         "hi"),
    ("kothamalli",      "Coriander Leaves",         "ta"),
    ("kothimeera",      "Coriander Leaves",         "te"),
    ("kottambari soppu","Coriander Leaves",         "kn"),
    ("mallipathri",     "Coriander Leaves",         "ml"),

    # Coriander Seeds
    ("dhania seeds",    "Coriander Seeds",          "hi"),
    ("dhania sabut",    "Coriander Seeds",          "hi"),

    # Turmeric Powder
    ("haldi",           "Turmeric Powder",          "hi"),
    ("haldi powder",    "Turmeric Powder",          "hi"),
    ("manjal podi",     "Turmeric Powder",          "ta"),
    ("pasupu",          "Turmeric Powder",          "te"),
    ("arishina",        "Turmeric Powder",          "kn"),
    ("manjal podi",     "Turmeric Powder",          "ml"),
    ("halad",           "Turmeric Powder",          "mr"),

    # Red Chilli Powder
    ("lal mirch powder","Red Chilli Powder",        "hi"),
    ("lal mirch",       "Red Chilli Powder",        "hi"),
    ("milagai podi",    "Red Chilli Powder",        "ta"),
    ("mirapakaya podi", "Red Chilli Powder",        "te"),
    ("menasina pudi",   "Red Chilli Powder",        "kn"),

    # Red Chilli
    ("lal mirch sabut", "Red Chilli",               "hi"),
    ("sukhi lal mirch", "Red Chilli",               "hi"),

    # Green Chilli
    ("hari mirch",      "Green Chilli",             "hi"),
    ("pachai milagai",  "Green Chilli",             "ta"),
    ("pachimirapa",     "Green Chilli",             "te"),
    ("hasiru menasinakayi", "Green Chilli",         "kn"),
    ("pacha mulaku",    "Green Chilli",             "ml"),
    ("hirvi mirchi",    "Green Chilli",             "mr"),

    # Mustard Seeds
    ("rai",             "Mustard Seeds",            "hi"),
    ("sarson",          "Mustard Seeds",            "hi"),
    ("kadugu",          "Mustard Seeds",            "ta"),
    ("avalu",           "Mustard Seeds",            "te"),
    ("sasive",          "Mustard Seeds",            "kn"),
    ("kaduku",          "Mustard Seeds",            "ml"),
    ("mohori",          "Mustard Seeds",            "mr"),

    # Fenugreek Seeds
    ("methi dana",      "Fenugreek Seeds",          "hi"),
    ("vendhayam",       "Fenugreek Seeds",          "ta"),
    ("menthulu",        "Fenugreek Seeds",          "te"),
    ("menthya",         "Fenugreek Seeds",          "kn"),
    ("uluva",           "Fenugreek Seeds",          "ml"),

    # Methi Seeds (alias in KG)
    ("methi ke beej",   "Methi Seeds",              "hi"),

    # Methi Leaves
    ("methi ka saag",   "Methi Leaves",             "hi"),
    ("methi patta",     "Methi Leaves",             "hi"),

    # Fennel Seeds
    ("saunf",           "Fennel Seeds",             "hi"),
    ("moti saunf",      "Fennel Seeds",             "hi"),
    ("sombu",           "Fennel Seeds",             "ta"),
    ("sopu",            "Fennel Seeds",             "kn"),
    ("perumjeerakam",   "Fennel Seeds",             "ml"),

    # Asafoetida
    ("hing",            "Asafoetida",               "hi"),
    ("heeng",           "Asafoetida",               "hi"),
    ("perungayam",      "Asafoetida",               "ta"),
    ("inguva",          "Asafoetida",               "te"),
    ("hingu",           "Asafoetida",               "kn"),
    ("kayam",           "Asafoetida",               "ml"),

    # Bay Leaves
    ("tej patta",       "Bay Leaves",               "hi"),
    ("biryani aaku",    "Bay Leaves",               "te"),
    ("pirinji ila",     "Bay Leaves",               "ta"),

    # Cardamom
    ("elaichi",         "Cardamom",                 "hi"),
    ("chhoti elaichi",  "Cardamom",                 "hi"),
    ("elakkai",         "Cardamom",                 "ta"),
    ("yelakki",         "Cardamom",                 "kn"),
    ("yalakulu",        "Cardamom",                 "te"),
    ("elathari",        "Cardamom",                 "ml"),
    ("elchi",           "Cardamom",                 "mr"),
    ("elaichi",         "Cardamom",                 "gu"),

    # Cinnamon
    ("dalchini",        "Cinnamon",                 "hi"),
    ("pattai",          "Cinnamon",                 "ta"),
    ("dalchina chekka", "Cinnamon",                 "te"),
    ("chakke",          "Cinnamon",                 "kn"),
    ("karuvapatta",     "Cinnamon",                 "ml"),

    # Cloves
    ("laung",           "Cloves",                   "hi"),
    ("lavangam",        "Cloves",                   "ta"),
    ("lavangalu",       "Cloves",                   "te"),
    ("lavanga",         "Cloves",                   "kn"),
    ("grambu",          "Cloves",                   "ml"),
    ("laving",          "Cloves",                   "mr"),

    # Black Pepper / Whole Black Peppercorns
    ("kali mirch",      "Whole Black Peppercorns",  "hi"),
    ("milagu",          "Whole Black Peppercorns",  "ta"),
    ("miriyalu",        "Whole Black Peppercorns",  "te"),
    ("menasu",          "Whole Black Peppercorns",  "kn"),
    ("kurumulaku",      "Whole Black Peppercorns",  "ml"),

    # Garam Masala Powder
    ("garam masala",    "Garam Masala Powder",      "hi"),

    # Star Anise
    ("chakri phool",    "Star Anise",               "hi"),

    # Ajwain
    ("ajwain",          "Ajwain",                   "hi"),
    ("omam",            "Ajwain",                   "ta"),
    ("vamu",            "Ajwain",                   "te"),
    ("oma",             "Ajwain",                   "kn"),

    # Kalonji
    ("kalonji",         "Kalonji",                  "hi"),
    ("mangrail",        "Kalonji",                  "hi"),
    ("karunjeeragam",   "Kalonji",                  "ta"),
    ("nalla jeelakarra","Kalonji",                  "te"),

    # Sesame Seeds
    ("til",             "Sesame Seeds",             "hi"),
    ("ellu",            "Sesame Seeds",             "ta"),
    ("nuvvulu",         "Sesame Seeds",             "te"),
    ("ellu",            "Sesame Seeds",             "kn"),
    ("ellu",            "Sesame Seeds",             "ml"),

    # Poppy Seeds
    ("khus khus",       "Poppy Seeds",              "hi"),
    ("kasa kasa",       "Poppy Seeds",              "ta"),
    ("gasagasalu",      "Poppy Seeds",              "te"),

    # ── Herbs & Aromatics ────────────────────────────────────────────

    # Ginger
    ("adrak",           "Ginger",                   "hi"),
    ("inji",            "Ginger",                   "ta"),
    ("allam",           "Ginger",                   "te"),
    ("shunti",          "Ginger",                   "kn"),
    ("inchi",           "Ginger",                   "ml"),
    ("ale",             "Ginger",                   "mr"),
    ("aadu",            "Ginger",                   "gu"),

    # Garlic
    ("lehsun",          "Garlic",                   "hi"),
    ("lahsun",          "Garlic",                   "hi"),
    ("poondu",          "Garlic",                   "ta"),
    ("vellulli",        "Garlic",                   "te"),
    ("bellulli",        "Garlic",                   "kn"),
    ("veluthulli",      "Garlic",                   "ml"),
    ("lasun",           "Garlic",                   "mr"),

    # Ginger Garlic Paste
    ("adrak lehsun paste", "Ginger Garlic Paste",   "hi"),

    # Curry Leaves
    ("kadi patta",      "Curry Leaves",             "hi"),
    ("kadhi patta",     "Curry Leaves",             "hi"),
    ("karivepilai",     "Curry Leaves",             "ta"),
    ("karivepaku",      "Curry Leaves",             "te"),
    ("karibevu",        "Curry Leaves",             "kn"),
    ("kariveppila",     "Curry Leaves",             "ml"),
    ("limbdo",          "Curry Leaves",             "gu"),

    # Mint Leaves
    ("pudina",          "Mint Leaves",              "hi"),
    ("pudina",          "Mint Leaves",              "ta"),
    ("pudina",          "Mint Leaves",              "te"),

    # Onion
    ("pyaaz",           "Onion",                    "hi"),
    ("vengayam",        "Onion",                    "ta"),
    ("ullipaya",        "Onion",                    "te"),
    ("eerulli",         "Onion",                    "kn"),
    ("savala",          "Onion",                    "ml"),
    ("kanda",           "Onion",                    "mr"),
    ("dungri",          "Onion",                    "gu"),

    # Tomatoes
    ("tamatar",         "Tomatoes",                 "hi"),
    ("thakkali",        "Tomatoes",                 "ta"),
    ("tomato",          "Tomatoes",                 "te"),
    ("tomato",          "Tomatoes",                 "kn"),

    # ── Lentils & Pulses ─────────────────────────────────────────────

    # Arhar Dal / Toor Dal
    ("arhar dal",       "Arhar Dal",                "hi"),
    ("toor dal",        "Arhar Dal",                "hi"),
    ("tuvar dal",       "Arhar Dal",                "hi"),
    ("tuvar dal",       "Arhar Dal",                "gu"),
    ("thuvaram paruppu","Arhar Dal",                "ta"),
    ("kandi pappu",     "Arhar Dal",                "te"),

    # Masoor Dal
    ("masoor dal",      "Masoor Dal",               "hi"),
    ("masur dal",       "Masoor Dal",               "hi"),
    ("mysore paruppu",  "Masoor Dal",               "ta"),

    # Green Moong Dal
    ("moong dal",       "Green Moong Dal",          "hi"),
    ("hare moong dal",  "Green Moong Dal",          "hi"),
    ("pachai payatham", "Green Moong Dal",           "ta"),
    ("pesara pappu",    "Green Moong Dal",          "te"),

    # Yellow Moong Dal
    ("peeli moong dal", "Yellow Moong Dal",         "hi"),

    # Urad Dal
    ("urad dal",        "Urad Dal",                 "hi"),
    ("ulutham paruppu", "Urad Dal",                 "ta"),
    ("minappappu",      "Urad Dal",                 "te"),
    ("uddina bele",     "Urad Dal",                 "kn"),

    # Chana Dal
    ("chana dal",       "Chana Dal",                "hi"),
    ("kadalai paruppu", "Chana Dal",                "ta"),
    ("senaga pappu",    "Chana Dal",                "te"),
    ("kadale bele",     "Chana Dal",                "kn"),

    # Kidney Beans
    ("rajma",           "Kidney Beans",             "hi"),

    # Kabuli Chana / Chickpeas
    ("chole",           "Kabuli Chana",             "hi"),
    ("chhole",          "Kabuli Chana",             "hi"),
    ("kabuli chana",    "Kabuli Chana",             "hi"),
    ("kondai kadalai",  "Kabuli Chana",             "ta"),
    ("senagalu",        "Kabuli Chana",             "te"),

    # ── Flours & Grains ──────────────────────────────────────────────

    # Gram Flour (Besan)
    ("besan",           "Gram Flour",               "hi"),
    ("kadalai maavu",   "Gram Flour",               "ta"),
    ("senaga pindi",    "Gram Flour",               "te"),
    ("kadale hittu",    "Gram Flour",               "kn"),

    # Whole Wheat Flour
    ("atta",            "Whole Wheat Flour",         "hi"),
    ("gehu ka atta",    "Whole Wheat Flour",         "hi"),
    ("godhi hittu",     "Whole Wheat Flour",         "kn"),

    # All Purpose Flour
    ("maida",           "All Purpose Flour",        "hi"),

    # Rice Flour
    ("chawal ka atta",  "Rice Flour",               "hi"),
    ("arisi maavu",     "Rice Flour",               "ta"),

    # Rice
    ("chawal",          "Rice",                     "hi"),
    ("arisi",           "Rice",                     "ta"),
    ("biyyam",          "Rice",                     "te"),
    ("akki",            "Rice",                     "kn"),
    ("ari",             "Rice",                     "ml"),

    # Sooji / Semolina
    ("suji",            "Sooji",                    "hi"),
    ("rawa",            "Sooji",                    "hi"),
    ("rava",            "Sooji",                    "hi"),
    ("rava",            "Sooji",                    "ta"),
    ("rava",            "Sooji",                    "kn"),

    # Poha
    ("chivda",          "Poha",                     "mr"),
    ("aval",            "Poha",                     "ta"),
    ("atukulu",         "Poha",                     "te"),
    ("avalakki",        "Poha",                     "kn"),

    # ── Dairy & Fats ─────────────────────────────────────────────────

    # Ghee
    ("ghee",            "Ghee",                     "hi"),
    ("nei",             "Ghee",                     "ta"),
    ("neyyi",           "Ghee",                     "te"),
    ("tuppa",           "Ghee",                     "kn"),
    ("nei",             "Ghee",                     "ml"),
    ("tup",             "Ghee",                     "mr"),
    ("ghee",            "Ghee",                     "gu"),

    # Curd / Yogurt
    ("dahi",            "Curd",                     "hi"),
    ("thayir",          "Curd",                     "ta"),
    ("perugu",          "Curd",                     "te"),
    ("mosaru",          "Curd",                     "kn"),
    ("thayir",          "Curd",                     "ml"),

    # Paneer
    ("paneer",          "Paneer",                   "hi"),
    ("chena",           "Paneer",                   "bn"),

    # Milk
    ("doodh",           "Milk",                     "hi"),
    ("paal",            "Milk",                     "ta"),
    ("paalu",           "Milk",                     "te"),
    ("haalu",           "Milk",                     "kn"),

    # Cream
    ("malai",           "Cream",                    "hi"),

    # Butter
    ("makhan",          "Salted Butter",            "hi"),

    # ── Sweeteners ───────────────────────────────────────────────────

    # Jaggery
    ("gur",             "Jaggery",                  "hi"),
    ("gud",             "Jaggery",                  "hi"),
    ("vellam",          "Jaggery",                  "ta"),
    ("bellam",          "Jaggery",                  "te"),
    ("bella",           "Jaggery",                  "kn"),
    ("sharkara",        "Jaggery",                  "ml"),

    # Sugar
    ("cheeni",          "Sugar",                    "hi"),
    ("shakkar",         "Sugar",                    "hi"),
    ("sakkarai",        "Sugar",                    "ta"),

    # ── Souring Agents ───────────────────────────────────────────────

    # Tamarind
    ("imli",            "Tamarind",                 "hi"),
    ("puli",            "Tamarind",                 "ta"),
    ("chintapandu",     "Tamarind",                 "te"),
    ("hunase",          "Tamarind",                 "kn"),
    ("valan puli",      "Tamarind",                 "ml"),
    ("chinch",          "Tamarind",                 "mr"),
    ("ambli",           "Tamarind",                 "gu"),

    # Amchoor Powder
    ("amchur powder",   "Amchoor Powder",           "hi"),
    ("amchur",          "Amchoor Powder",           "hi"),
    ("aam ka powder",   "Amchoor Powder",           "hi"),

    # Lemon
    ("nimbu",           "Lemon",                    "hi"),
    ("elumichai",       "Lemon",                    "ta"),
    ("nimma",           "Lemon",                    "te"),
    ("nimbe",           "Lemon",                    "kn"),
    ("cherunaranga",    "Lemon",                    "ml"),
    ("limbu",           "Lemon",                    "mr"),

    # ── Vegetables ───────────────────────────────────────────────────

    # Potatoes
    ("aloo",            "Potatoes",                 "hi"),
    ("urulaikizhangu",  "Potatoes",                 "ta"),
    ("bangaladumpa",    "Potatoes",                 "te"),
    ("aalugadde",       "Potatoes",                 "kn"),
    ("urulakkizhangu",  "Potatoes",                 "ml"),
    ("batata",          "Potatoes",                 "mr"),

    # Cauliflower
    ("gobi",            "Cauliflower",              "hi"),
    ("phool gobi",      "Cauliflower",              "hi"),
    ("cauliflower",     "Cauliflower",              "ta"),
    ("hookosu",         "Cauliflower",              "kn"),

    # Eggplant / Brinjal
    ("baingan",         "Eggplant",                 "hi"),
    ("kathirikai",      "Eggplant",                 "ta"),
    ("vankaya",         "Eggplant",                 "te"),
    ("badanekayi",      "Eggplant",                 "kn"),
    ("vazhuthananga",   "Eggplant",                 "ml"),
    ("vangi",           "Eggplant",                 "mr"),

    # Okra / Bhindi
    ("bhindi",          "Okra",                     "hi"),
    ("vendakkai",       "Okra",                     "ta"),
    ("bendakaya",       "Okra",                     "te"),
    ("bendekayi",       "Okra",                     "kn"),
    ("vendakka",        "Okra",                     "ml"),

    # Green Peas
    ("matar",           "Green Peas",               "hi"),
    ("pattani",         "Green Peas",               "ta"),
    ("batani",          "Green Peas",               "te"),

    # Spinach
    ("palak",           "Spinach",                  "hi"),
    ("keerai",          "Spinach",                  "ta"),
    ("palakura",        "Spinach",                  "te"),
    ("palak soppu",     "Spinach",                  "kn"),
    ("cheera",          "Spinach",                  "ml"),

    # Pumpkin
    ("kaddu",           "Pumpkin",                  "hi"),
    ("poosanikai",      "Pumpkin",                  "ta"),
    ("gummadikaya",     "Pumpkin",                  "te"),
    ("kumbalakai",      "Pumpkin",                  "kn"),

    # Bottle Gourd / Lauki
    ("lauki",           "Gourd",                    "hi"),
    ("dudhi",           "Gourd",                    "mr"),
    ("sorakaya",        "Gourd",                    "te"),

    # Ridge Gourd
    ("tori",            "Ridge Gourd",              "hi"),
    ("peerkangai",      "Ridge Gourd",              "ta"),
    ("beerakaya",       "Ridge Gourd",              "te"),
    ("heerekaayi",      "Ridge Gourd",              "kn"),

    # Drumstick
    ("sahjan",          "Drumstick",                "hi"),
    ("murungai",        "Drumstick",                "ta"),
    ("mulakkada",       "Drumstick",                "te"),
    ("nugge",           "Drumstick",                "kn"),
    ("muringakka",      "Drumstick",                "ml"),

    # Radish
    ("mooli",           "Radish",                   "hi"),
    ("mullangi",        "Radish",                   "ta"),
    ("mullangi",        "Radish",                   "te"),
    ("moolangi",        "Radish",                   "kn"),

    # Carrots
    ("gajar",           "Carrots",                  "hi"),

    # Cabbage
    ("patta gobi",      "Cabbage",                  "hi"),

    # Coconut
    ("nariyal",         "Fresh Coconut",            "hi"),
    ("thengai",         "Fresh Coconut",            "ta"),
    ("kobbari",         "Fresh Coconut",            "te"),
    ("thenginakayi",    "Fresh Coconut",            "kn"),
    ("thenga",          "Fresh Coconut",            "ml"),

    # ── Fruits ───────────────────────────────────────────────────────

    # Mango
    ("aam",             "Mango",                    "hi"),
    ("maanga",          "Mango",                    "ta"),
    ("mamidi",          "Mango",                    "te"),

    # Banana
    ("kela",            "Banana",                   "hi"),
    ("vaazhai",         "Banana",                   "ta"),
    ("arati",           "Banana",                   "te"),

    # ── Nuts & Dry Fruits ────────────────────────────────────────────

    # Cashew
    ("kaju",            "Cashew",                   "hi"),
    ("mundhiri",        "Cashew",                   "ta"),
    ("jeedi pappu",     "Cashew",                   "te"),
    ("godambi",         "Cashew",                   "kn"),

    # Almond
    ("badam",           "Almond",                   "hi"),

    # Peanuts
    ("moongphali",      "Peanuts",                  "hi"),
    ("verkadalai",      "Peanuts",                  "ta"),
    ("pallilu",         "Peanuts",                  "te"),
    ("kadalekayi",      "Peanuts",                  "kn"),
    ("shengdana",       "Peanuts",                  "mr"),

    # Pistachios
    ("pista",           "Pistachios",               "hi"),

    # Walnuts
    ("akhrot",          "Walnuts",                  "hi"),

    # Raisins
    ("kishmish",        "Raisins",                  "hi"),

    # Dates
    ("khajur",          "Dates",                    "hi"),

    # ── Oils ─────────────────────────────────────────────────────────

    # Mustard Oil
    ("sarson ka tel",   "Mustard Oil",              "hi"),

    # Sesame Oil
    ("til ka tel",      "Sesame Oil",               "hi"),
    ("nallennai",       "Sesame Oil",               "ta"),

    # Coconut Oil
    ("nariyal ka tel",  "Coconut Oil",              "hi"),
    ("velichenna",      "Coconut Oil",              "ml"),

    # ── Miscellaneous ────────────────────────────────────────────────

    # Salt
    ("namak",           "Salt",                     "hi"),
    ("uppu",            "Salt",                     "ta"),
    ("uppu",            "Salt",                     "te"),

    # Water
    ("pani",            "Water",                    "hi"),
    ("jal",             "Water",                    "hi"),

    # Saffron
    ("kesar",           "Saffron",                  "hi"),
    ("kungumapoo",      "Saffron",                  "ta"),

    # Jaggery variants (Palm Jaggery)
    ("karupatti",       "Palm Jaggery",             "ta"),

    # Kokum
    ("kokam",           "Kokum",                    "mr"),
    ("aamsul",          "Kokum",                    "mr"),

    # Khoya
    ("mawa",            "Khoya",                    "hi"),

    # Rose Water
    ("gulab jal",       "Rose Water",               "hi"),

    # Cottage Cheese (same as Paneer in many contexts)
    ("chhena",          "Chenna",                   "bn"),
]
