from typing import Any


DESTINATION_ACTIVITIES = {
    "lisbon": [
        "Explore Alfama and the historic city centre",
        "Visit Belém Tower and Jerónimos Monastery",
        "Try local food at a market or traditional restaurant",
        "Take a day trip to Sintra",
    ],
    "banff": [
        "Visit Lake Louise",
        "Hike a scenic mountain trail",
        "Explore Banff town",
        "Take a gondola ride or visit a viewpoint",
    ],
    "kyoto": [
        "Visit Fushimi Inari Shrine",
        "Explore Kiyomizu-dera and Gion",
        "Walk through Arashiyama Bamboo Grove",
        "Visit temples and traditional gardens",
    ],
    "bali": [
        "Visit temples and rice terraces",
        "Relax at a beach",
        "Explore Ubud",
        "Try a yoga or wellness activity",
    ],
}


def create_trip_plan(
    destination: str,
    number_of_days: int,
    budget: str = "medium",
    interests: list[str] | None = None,
) -> dict[str, Any]:
    """Create a simple structured itinerary."""
    if number_of_days < 1:
        raise ValueError("The number of days must be at least 1.")

    interests = interests or []
    destination_key = destination.strip().lower()

    activities = DESTINATION_ACTIVITIES.get(
        destination_key,
        [
            f"Explore the main attractions in {destination}",
            f"Visit a local neighbourhood in {destination}",
            f"Try local food in {destination}",
            f"Spend time at a museum, park, or cultural site",
        ],
    )

    itinerary = []

    for day in range(1, number_of_days + 1):
        activity = activities[(day - 1) % len(activities)]

        itinerary.append(
            {
                "day": day,
                "morning": activity,
                "afternoon": (
                    f"Choose an activity related to "
                    f"{', '.join(interests) if interests else 'local culture'}"
                ),
                "evening": (
                    "Choose an affordable local restaurant"
                    if budget.lower() == "low"
                    else "Enjoy dinner and a relaxed evening activity"
                ),
            }
        )

    return {
        "destination": destination,
        "number_of_days": number_of_days,
        "budget": budget,
        "interests": interests,
        "itinerary": itinerary,
    }


def format_trip_plan(plan: dict[str, Any]) -> str:
    """Turn the structured plan into conversational text."""
    lines = [
        f"Here is a {plan['number_of_days']}-day trip plan for "
        f"{plan['destination']} on a {plan['budget']} budget."
    ]

    for day in plan["itinerary"]:
        lines.append(
            f"\nDay {day['day']}: "
            f"Morning — {day['morning']}. "
            f"Afternoon — {day['afternoon']}. "
            f"Evening — {day['evening']}."
        )

    return "".join(lines)


ITINERARY_TOOL = {
    "type": "function",
    "function": {
        "name": "create_trip_plan",
        "description": (
            "Create a day-by-day travel itinerary for a destination. "
            "Use this when the user asks to plan a trip or itinerary."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "destination": {
                    "type": "string",
                    "description": "The destination city, region, or country.",
                },
                "number_of_days": {
                    "type": "integer",
                    "description": "The length of the trip in days.",
                    "minimum": 1,
                    "maximum": 14,
                },
                "budget": {
                    "type": "string",
                    "enum": ["low", "medium", "high"],
                    "description": "The traveller's general budget level.",
                },
                "interests": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": (
                        "Traveller interests such as food, history, hiking, "
                        "museums, beaches, or shopping."
                    ),
                },
            },
            "required": [
                "destination",
                "number_of_days",
                "budget",
                "interests",
            ],
            "additionalProperties": False,
        },
    },
}


def main() -> None:
    plan = create_trip_plan(
        destination="Lisbon",
        number_of_days=3,
        budget="low",
        interests=["food", "history"],
    )

    print(format_trip_plan(plan))


if __name__ == "__main__":
    main()