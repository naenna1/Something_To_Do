from datetime import datetime

# Eingabe definieren/Fehler ausschließen
def input_nonempty(prompt):
    while True:
        val = input(prompt).strip()
        if val != "":
            return val
        print("Input cannot be empty.")


def input_date_or_empty(prompt):
    val = input(prompt + " (YYYY-MM-DD, empty = nothing, 0 = back to menu): ").strip()
    if is_back(val):
        return "BACK"
    if val == "":
        return None
    try:
        datetime.strptime(val, "%Y-%m-%d")
        return val
    except ValueError:
        print("Please enter the date in the format YYYY-MM-DD.")
        return input_date_or_empty(prompt)

def is_back(val):
    return val.strip() == "0"
