"""
Agricultural advisory generation for plant disease predictions.

The advisory is generated from the PlantVillage class name so every class
receives a complete, beginner-readable care plan without hardcoding UI logic.
"""

import re


def _clean_text(value):
    value = value.replace("___", " - ")
    value = value.replace("_", " ")
    value = value.replace(",", ", ")
    value = re.sub(r"\s+", " ", value)
    return value.strip(" -").title()


def parse_class_name(class_name):
    """Split a dataset folder name into crop and condition display names."""
    if "___" in class_name:
        crop, condition = class_name.split("___", 1)
    else:
        crop, condition = "Plant", class_name

    return _clean_text(crop), _clean_text(condition)


def _canonical(value):
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def _base_advisory(crop, condition):
    return {
        "disease_name": condition,
        "crop": crop,
        "description": (
            f"{condition} affects {crop} health and can reduce growth, yield, "
            "and produce quality if it is not managed early."
        ),
        "symptoms": [
            "Discolored spots, patches, curling, wilting, or drying may appear on leaves.",
            "Affected leaves can lose vigor and may drop early in severe cases.",
            "Disease symptoms usually begin on older or stressed leaves first.",
        ],
        "causes": [
            "Disease pressure increases when plants are stressed or weak.",
            "Poor airflow, excess leaf wetness, and infected plant debris can spread infection.",
            "Contaminated tools, soil splash, insects, or nearby infected crops may carry pathogens.",
        ],
        "prevention": [
            "Use healthy seeds or seedlings and avoid planting infected material.",
            "Keep enough spacing between plants so leaves dry quickly after watering or rain.",
            "Remove infected leaves and plant debris from the field or garden.",
            "Rotate crops when possible and avoid repeated planting of the same crop family.",
        ],
        "treatment": [
            "Isolate heavily infected plants and remove badly affected leaves.",
            "Apply crop-appropriate treatment early; advanced infections are harder to control.",
            "Follow local agricultural extension guidance and product labels before chemical use.",
        ],
        "pesticide_suggestions": [
            "Use a locally approved fungicide or bactericide only after confirming the disease type.",
            "Follow label dose, waiting period, safety equipment, and local regulations.",
        ],
        "fertilizer_suggestions": [
            "Avoid excess nitrogen because soft new growth is often more disease-prone.",
            "Maintain balanced nutrition with potassium, calcium, magnesium, and micronutrients.",
            "Use soil testing where possible before changing fertilizer schedules.",
        ],
        "organic_treatments": [
            "Remove infected leaves with clean tools and dispose of them away from crops.",
            "Neem oil, compost tea, or biofungicides may help in early, mild cases.",
            "Improve airflow and keep leaves dry to slow disease spread.",
        ],
        "irrigation_advice": [
            "Water at the base of the plant instead of wetting leaves.",
            "Irrigate early in the day so accidental leaf moisture dries quickly.",
            "Avoid waterlogging because weak roots increase disease susceptibility.",
        ],
        "environmental_triggers": [
            "High humidity and long leaf-wetness periods increase many leaf diseases.",
            "Crowded planting and poor airflow create a favorable disease microclimate.",
            "Plant stress from drought, nutrient imbalance, or pests can worsen symptoms.",
        ],
        "crop_care_guidance": [
            "Scout plants twice a week and compare new symptoms with older leaves.",
            "Prune dense foliage where appropriate and sanitize tools between plants.",
            "Record the date, weather, crop stage, and treatment used for future decisions.",
        ],
        "urgency": "medium",
        "disclaimer": (
            "This is decision-support guidance, not a pesticide prescription. "
            "Confirm severe cases with a local agricultural expert."
        ),
    }


def _healthy_advisory(crop, condition):
    return {
        **_base_advisory(crop, condition),
        "description": (
            f"The {crop} leaf appears healthy based on the model prediction. "
            "Continue preventive care and regular monitoring."
        ),
        "symptoms": [
            "No clear disease pattern was detected in the uploaded image.",
            "Leaf color and structure appear consistent with healthy growth.",
        ],
        "causes": [
            "Healthy status usually reflects good nutrition, suitable watering, and low disease pressure.",
        ],
        "prevention": [
            "Continue routine scouting, especially after rain or humid weather.",
            "Maintain spacing, sanitation, balanced fertilization, and pest monitoring.",
        ],
        "treatment": [
            "No chemical treatment is recommended for a healthy prediction.",
            "Avoid unnecessary pesticide use because it can increase cost and resistance risk.",
        ],
        "pesticide_suggestions": [
            "No pesticide is needed unless pests or disease symptoms are confirmed separately.",
        ],
        "organic_treatments": [
            "Maintain mulch, compost, clean tools, and good airflow.",
        ],
        "irrigation_advice": [
            "Keep watering consistent and avoid both drought stress and waterlogging.",
        ],
        "environmental_triggers": [
            "Monitor closely during humid, rainy, or unusually hot conditions.",
        ],
        "crop_care_guidance": [
            "Photograph the same plant weekly to track changes over time.",
            "Remove weeds and crop debris that can host pests or pathogens.",
        ],
        "urgency": "low",
    }


def _apply_profile(advisory, profile):
    for key, value in profile.items():
        advisory[key] = value
    return advisory


def _profile_for_condition(crop, condition):
    key = _canonical(condition)

    if "healthy" in key:
        return "healthy", {}

    if "spidermite" in key or "mite" in key:
        return "mite", {
            "description": (
                f"{condition} on {crop} is caused by mite feeding. Mites suck sap "
                "from leaves, creating pale speckling and weakening the plant."
            ),
            "symptoms": [
                "Fine yellow or white speckling on leaves.",
                "Bronzing, curling, drying, or webbing in heavier infestations.",
                "Symptoms often increase during hot, dry weather.",
            ],
            "causes": [
                "Hot, dry weather favors rapid mite reproduction.",
                "Dusty conditions and water-stressed plants are more vulnerable.",
                "Broad-spectrum insecticides can reduce natural mite predators.",
            ],
            "treatment": [
                "Spray leaf undersides with water to reduce mite pressure in early cases.",
                "Use miticides only when infestation is confirmed and follow local labels.",
                "Repeat monitoring after treatment because eggs may hatch later.",
            ],
            "pesticide_suggestions": [
                "Use a registered miticide such as abamectin, spiromesifen, or bifenazate where permitted.",
                "Avoid unnecessary broad-spectrum insecticides that can worsen mite outbreaks.",
            ],
            "organic_treatments": [
                "Insecticidal soap, horticultural oil, or neem oil can help when coverage is thorough.",
                "Encourage beneficial predatory mites and lady beetles.",
            ],
            "irrigation_advice": [
                "Reduce drought stress with consistent irrigation.",
                "Avoid dusty, dry plant conditions that favor mite multiplication.",
            ],
            "environmental_triggers": [
                "Hot, dry weather.",
                "Dusty fields or greenhouses.",
                "Low natural predator populations.",
            ],
            "urgency": "medium",
        }

    if "mosaicvirus" in key or "yellowleafcurlvirus" in key:
        return "viral", {
            "description": (
                f"{condition} is a viral disease. Viral diseases cannot be cured "
                "inside infected plants, so management focuses on prevention and vector control."
            ),
            "symptoms": [
                "Mosaic or mottled light and dark green patterns.",
                "Leaf curling, distortion, stunting, or yellowing.",
                "Reduced flowering, fruit set, or overall vigor.",
            ],
            "causes": [
                "Viruses are commonly spread by insects such as whiteflies, aphids, or thrips.",
                "Infected seedlings, weeds, or crop residues can act as virus sources.",
                "Handling infected and healthy plants without sanitation can spread some viruses.",
            ],
            "treatment": [
                "Remove severely infected plants to reduce virus sources.",
                "Control insect vectors early and remove nearby weed hosts.",
                "Use resistant varieties when available.",
            ],
            "pesticide_suggestions": [
                "Use registered insecticides or oils against the confirmed vector, not against the virus itself.",
                "Rotate insecticide modes of action to reduce resistance risk.",
            ],
            "organic_treatments": [
                "Use insect netting, reflective mulch, yellow sticky traps, and weed removal.",
                "Remove infected plants early and sanitize tools.",
            ],
            "irrigation_advice": [
                "Maintain steady watering to reduce plant stress, but irrigation will not cure viral infection.",
            ],
            "environmental_triggers": [
                "High whitefly, aphid, or thrip pressure.",
                "Nearby infected weeds or volunteer plants.",
                "Warm conditions that increase vector activity.",
            ],
            "urgency": "high",
        }

    if "citrusgreening" in key or "huanglongbing" in key or "haunglongbing" in key:
        return "citrus_greening", {
            "description": (
                "Citrus greening is a serious bacterial disease spread mainly by citrus psyllids. "
                "It weakens trees and can cause bitter, misshapen fruit."
            ),
            "symptoms": [
                "Blotchy yellow mottling on leaves.",
                "Small, lopsided, bitter fruit and twig dieback.",
                "Overall tree decline over time.",
            ],
            "causes": [
                "Spread by Asian citrus psyllid feeding.",
                "Movement of infected planting material.",
            ],
            "treatment": [
                "There is no reliable field cure for infected trees.",
                "Manage psyllids, remove severely infected trees where recommended, and use certified nursery stock.",
            ],
            "pesticide_suggestions": [
                "Use locally registered psyllid-control products under expert guidance.",
            ],
            "fertilizer_suggestions": [
                "Use a balanced citrus nutrition plan with micronutrients to support tree vigor.",
                "Do not rely on fertilizer as a cure for citrus greening.",
            ],
            "organic_treatments": [
                "Use certified clean plants, remove infected material, and monitor psyllids with traps.",
            ],
            "irrigation_advice": [
                "Avoid drought stress and maintain consistent deep watering for citrus roots.",
            ],
            "environmental_triggers": [
                "High psyllid populations.",
                "Movement of infected citrus plant material.",
            ],
            "urgency": "high",
        }

    if "powderymildew" in key:
        return "powdery_mildew", {
            "description": (
                f"{condition} is a fungal disease that forms powdery growth on leaf surfaces "
                "and spreads quickly when airflow is poor."
            ),
            "symptoms": [
                "White or gray powdery patches on leaves and stems.",
                "Leaf curling, yellowing, and reduced plant vigor.",
                "Premature leaf drop in severe cases.",
            ],
            "causes": [
                "Dense foliage and poor airflow.",
                "Warm days, cool nights, and moderate to high humidity.",
            ],
            "treatment": [
                "Remove heavily infected leaves and improve spacing.",
                "Apply a crop-approved powdery mildew fungicide early if symptoms spread.",
            ],
            "pesticide_suggestions": [
                "Sulfur, potassium bicarbonate, neem-based products, or registered fungicides may help when labeled for the crop.",
            ],
            "organic_treatments": [
                "Sulfur or potassium bicarbonate sprays may help in early infection.",
                "Prune dense foliage and avoid overhead irrigation.",
            ],
            "environmental_triggers": [
                "Poor airflow.",
                "Warm dry days with humid nights.",
                "Crowded crop canopy.",
            ],
            "urgency": "medium",
        }

    if "earlyblight" in key or "lateblight" in key or "northernleafblight" in key:
        disease_type = "late blight" if "lateblight" in key else "blight"
        urgency = "high" if "lateblight" in key else "medium"
        return "blight", {
            "description": (
                f"{condition} is a {disease_type} disease that can spread through leaves "
                "and reduce yield if moisture and humidity remain high."
            ),
            "symptoms": [
                "Brown or dark lesions on leaves.",
                "Yellowing around spots or rapid tissue collapse.",
                "Stem or fruit infection can occur in severe cases.",
            ],
            "causes": [
                "Fungal or oomycete pathogens favored by wet leaves.",
                "Infected crop debris, wind-driven spores, and splash dispersal.",
            ],
            "treatment": [
                "Remove infected foliage when practical and avoid working plants while wet.",
                "Use protective fungicides early; late blight needs urgent management.",
            ],
            "pesticide_suggestions": [
                "Chlorothalonil, mancozeb, copper products, or crop-specific systemic fungicides may be used where labeled.",
            ],
            "organic_treatments": [
                "Copper-based products may help protect healthy tissue in organic systems where approved.",
                "Mulch soil to reduce splash and remove infected plant debris.",
            ],
            "environmental_triggers": [
                "Cool to warm wet weather.",
                "Long leaf-wetness periods.",
                "Dense canopy and poor airflow.",
            ],
            "urgency": urgency,
        }

    if "bacterialspot" in key:
        return "bacterial_spot", {
            "description": (
                f"{condition} is a bacterial disease that creates water-soaked spots "
                "and can spread rapidly through splash, tools, and infected seed or seedlings."
            ),
            "symptoms": [
                "Small water-soaked leaf spots that turn brown or black.",
                "Yellow halos, leaf tearing, or fruit spots may appear.",
                "Symptoms worsen after rain, overhead irrigation, or warm humidity.",
            ],
            "causes": [
                "Bacteria spread by rain splash, tools, workers, and infected seed.",
                "Warm humid weather favors disease development.",
            ],
            "treatment": [
                "Remove badly infected leaves and avoid handling wet plants.",
                "Use copper-based bactericides or approved products early; they protect new growth better than curing old spots.",
            ],
            "pesticide_suggestions": [
                "Copper-based bactericides may help where locally approved.",
                "Use antibiotics only where legal, labeled, and recommended by an agricultural expert.",
            ],
            "organic_treatments": [
                "Sanitation, drip irrigation, crop rotation, and copper products approved for organic production.",
            ],
            "environmental_triggers": [
                "Warm humid weather.",
                "Overhead irrigation or heavy rain splash.",
                "Infected transplants or seed.",
            ],
            "urgency": "medium",
        }

    if "rust" in key:
        return "rust", {
            "description": (
                f"{condition} is a fungal rust disease that forms colored pustules "
                "and can reduce photosynthesis when infection is heavy."
            ),
            "symptoms": [
                "Orange, yellow, brown, or rust-colored pustules on leaves.",
                "Yellowing and drying of infected leaves.",
                "Spores may rub off like powder.",
            ],
            "causes": [
                "Rust fungi spread by windborne spores.",
                "Moderate temperatures and leaf moisture favor infection.",
            ],
            "treatment": [
                "Remove infected leaves where practical and improve airflow.",
                "Apply a labeled rust fungicide if disease is spreading.",
            ],
            "pesticide_suggestions": [
                "Use crop-labeled triazole, strobilurin, sulfur, or copper products where appropriate.",
            ],
            "organic_treatments": [
                "Sulfur or copper products may help protect healthy tissue where approved.",
            ],
            "environmental_triggers": [
                "Windborne spores.",
                "Leaf wetness and dense crop canopy.",
            ],
            "urgency": "medium",
        }

    if "leafspot" in key or "leafscorch" in key or "septoria" in key or "targetspot" in key or "leafmold" in key:
        return "leaf_spot", {
            "description": (
                f"{condition} is a leaf disease that damages photosynthetic tissue "
                "and often spreads when leaves stay wet."
            ),
            "symptoms": [
                "Circular, angular, or irregular leaf spots.",
                "Yellowing around spots and drying of affected tissue.",
                "Lower leaves are often affected first.",
            ],
            "causes": [
                "Fungal or bacterial pathogens survive on crop debris.",
                "Spores or bacteria spread through splash, wind, or tools.",
            ],
            "treatment": [
                "Remove infected lower leaves and increase airflow.",
                "Use a labeled protective fungicide or bactericide depending on disease diagnosis.",
            ],
            "pesticide_suggestions": [
                "Copper, chlorothalonil, mancozeb, or crop-specific fungicides may be used where labeled.",
            ],
            "organic_treatments": [
                "Copper products, sanitation, mulch, and drip irrigation are common organic-compatible tools.",
            ],
            "environmental_triggers": [
                "High humidity.",
                "Rain splash or overhead irrigation.",
                "Dense planting and poor airflow.",
            ],
            "urgency": "medium",
        }

    if "scab" in key:
        return "scab", {
            "description": (
                f"{condition} is a fungal disease that causes scabby lesions on leaves and fruit, "
                "especially during wet spring conditions."
            ),
            "symptoms": [
                "Olive-brown or dark scabby lesions on leaves or fruit.",
                "Leaf distortion, yellowing, and premature drop.",
                "Fruit blemishes and cracking in severe cases.",
            ],
            "causes": [
                "Spores overwinter in infected leaves and spread during wet weather.",
            ],
            "treatment": [
                "Remove fallen infected leaves and prune for airflow.",
                "Use preventive fungicide programs during high-risk wet periods.",
            ],
            "pesticide_suggestions": [
                "Captan, sulfur, or other crop-labeled apple scab fungicides may be used where permitted.",
            ],
            "organic_treatments": [
                "Sanitation, resistant varieties, sulfur products, and canopy pruning.",
            ],
            "environmental_triggers": [
                "Wet spring weather.",
                "Long leaf wetness and dense canopy.",
            ],
            "urgency": "medium",
        }

    if "blackrot" in key or "blackmeasles" in key or "esca" in key:
        return "rot_or_wood_disease", {
            "description": (
                f"{condition} can damage leaves, fruit, or woody tissue depending on crop and stage. "
                "Sanitation and early protection are important."
            ),
            "symptoms": [
                "Dark lesions, spots, or streaking on leaves or fruit.",
                "Fruit shriveling, rotting, or cane/wood decline in severe cases.",
                "Reduced plant vigor over time.",
            ],
            "causes": [
                "Pathogens survive in infected debris, mummified fruit, canes, or wood.",
                "Rain splash, wounds, and humid conditions can increase spread.",
            ],
            "treatment": [
                "Remove infected fruit, leaves, and pruning debris.",
                "Prune during dry weather and protect wounds where expert guidance recommends it.",
            ],
            "pesticide_suggestions": [
                "Use crop-labeled fungicides as preventive protection during high-risk growth stages.",
            ],
            "organic_treatments": [
                "Sanitation, pruning, canopy airflow, and removal of mummified fruit.",
            ],
            "environmental_triggers": [
                "Rainy periods.",
                "Old infected debris left in the field.",
                "Wounds or stressed woody tissue.",
            ],
            "urgency": "medium",
        }

    return "general", {}


def get_advisory(class_name, label_info=None):
    """
    Return a complete advisory dictionary for any disease class.

    label_info can contain an existing remedy from labels.json; it is preserved
    as an additional recommended treatment.
    """
    crop, condition = parse_class_name(class_name)
    profile_name, profile = _profile_for_condition(crop, condition)
    advisory = _healthy_advisory(crop, condition) if profile_name == "healthy" else _base_advisory(crop, condition)
    advisory = _apply_profile(advisory, profile)

    label_info = label_info or {}
    remedy = label_info.get("remedy")
    if remedy and remedy not in advisory["treatment"]:
        advisory["treatment"].insert(0, remedy)

    advisory["profile"] = profile_name
    return advisory
