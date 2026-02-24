def calculate_bmi(weight_kg: float, height_cm: float, gender: str) -> dict:
    height_m = height_cm / 100
    bmi = weight_kg / (height_m ** 2)
    bmi_rounded = round(bmi, 1)

    # Different BMI ranges for men and women
    # Women generally have healthy body fat at higher BMI
    if gender.lower() in ["female", "f", "woman", "women"]:
        if bmi < 18.5:
            category = "Underweight"
        elif bmi < 24.0:
            category = "Normal weight"
        elif bmi < 29.0:
            category = "Overweight"
        else:
            category = "Obese"
    else:  # male
        if bmi < 18.5:
            category = "Underweight"
        elif bmi < 25.0:
            category = "Normal weight"
        elif bmi < 30.0:
            category = "Overweight"
        else:
            category = "Obese"

    return {
        "bmi": bmi_rounded,
        "category": category,
        "gender": gender
    }
