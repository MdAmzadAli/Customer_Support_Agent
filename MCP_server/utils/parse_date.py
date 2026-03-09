from datetime import datetime, date

def parse_valid_date(date_str: str) -> tuple:
    
    if isinstance(date_str,date):
        return (True,date_str)
    
    if not isinstance(date_str, str):
        return (False, f"Expected a string but got {type(date_str).__name__}")

    date_str = date_str.strip()

    if not date_str:
        return (False, "Date string is empty")

    try:
        parsed = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return (False, f"Invalid date format '{date_str}'. Expected YYYY-MM-DD")

    return (True, parsed)