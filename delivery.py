def get_delivery_eta(vehicle_model: str, city: str) -> str:
    """
    Get delivery ETA for ONE specific vehicle model in a city.

    vehicle_model MUST be the exact vehicle model name,
    such as 'Hyundai Creta' or 'Tata Nexon'.

    Do not pass customer requirements, descriptions,
    categories, prices, or natural-language queries.
    """

    eta_data = {
        ("Hyundai Creta", "Ranchi"): 4,
        ("Kia Seltos", "Ranchi"): 6,
        ("Toyota Urban Cruiser Hyryder", "Ranchi"): 9,
        ("Tata Nexon", "Ranchi"): 3,
        ("Hyundai Venue", "Ranchi"): 5,

        ("Hyundai Creta", "Delhi"): 3,
        ("Kia Seltos", "Delhi"): 4,
        ("Tata Nexon", "Delhi"): 2,
    }

    key = (vehicle_model, city)

    if key not in eta_data:
        return (
            f"Invalid vehicle_model '{vehicle_model}'. "
            "vehicle_model must be an exact model name returned "
            "by check_inventory()."
        )

    days = eta_data[key]

    return (
        f"{vehicle_model} in {city} has an estimated "
        f"delivery time of {days} days."
    )