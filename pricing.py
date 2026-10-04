def get_offer_price(
    vehicle_model: str,
    customer_type: str,
    city: str
) -> str:
    """
    Return indicative selling price and offer for a vehicle.
    """

    pricing_data = {
        ("Tata Nexon", "retail", "Ranchi"): {
            "base_price_lakh": 14.5,
            "discount_lakh": 0.30
        },

        ("Hyundai Venue", "retail", "Ranchi"): {
            "base_price_lakh": 15.8,
            "discount_lakh": 0.25
        },

        ("Hyundai Creta", "retail", "Ranchi"): {
            "base_price_lakh": 18.5,
            "discount_lakh": 0.20
        },

        ("Kia Seltos", "retail", "Ranchi"): {
            "base_price_lakh": 19.2,
            "discount_lakh": 0.35
        },
    }

    key = (vehicle_model, customer_type.lower(), city)

    if key not in pricing_data:
        return (
            f"Pricing information not available for "
            f"{vehicle_model} in {city}."
        )

    data = pricing_data[key]

    final_price = (
        data["base_price_lakh"]
        - data["discount_lakh"]
    )

    return (
        f"{vehicle_model}: "
        f"Base price ₹{data['base_price_lakh']} lakh, "
        f"discount ₹{data['discount_lakh']} lakh, "
        f"indicative offer price ₹{final_price:.2f} lakh."
    )