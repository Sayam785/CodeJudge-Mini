
def normalize_output(output):
    """Normalize whitespace before comparing program output."""
    return " ".join((output or "").split())


def evaluate_output(actual_output, expected_output):
    """Return ACCEPTED if actual output matches expected output."""
    actual = normalize_output(actual_output)
    expected = normalize_output(expected_output)

    if actual == expected:
        return "ACCEPTED"

    return "WRONG_ANSWER"
