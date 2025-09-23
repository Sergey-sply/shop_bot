def validate_integer(value):
    try:
        int(value)
        return True
    except ValueError:
        print("Invalid input: Not an integer")
        return None