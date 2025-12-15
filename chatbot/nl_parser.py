"""
Natural Language Parser for Question Requirements
Parses user input like "10 two mark questions, 5 five mark questions"
"""
import re


def parse_question_requirements(text):
    """
    Parse natural language question requirements
    
    Examples:
        "10 two mark questions" → {2: 10}
        "5 five mark, 3 ten mark" → {5: 5, 10: 3}
        "I want 10 two mark questions and 5 five mark questions" → {2: 10, 5: 5}
    
    Returns:
        dict: {marks: count} e.g., {2: 10, 5: 5, 10: 3}
    """
    if not text or not text.strip():
        return {}
    
    text = text.lower().strip()
    requirements = {}
    
    # Number words to digits
    number_words = {
        'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
        'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
        'eleven': 11, 'twelve': 12, 'fifteen': 15, 'twenty': 20
    }
    
    # Try multiple patterns
    patterns = [
        # "10 two mark" or "10 two-mark" or "10 two marks"
        r'(\d+)\s+(\w+)[\s-]?marks?',
        # "10 2 mark" or "10 2-mark"  
        r'(\d+)\s+(\d+)[\s-]?marks?',
        # "2 marks: 10" or "2 mark: 10"
        r'(\d+)\s*marks?\s*:?\s*(\d+)',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            # Determine which is count and which is marks
            first, second = match[0], match[1]
            
            # If second is a word, it's the mark value
            if second in number_words:
                count = int(first)
                marks = number_words[second]
            # If both are digits, first is count, second is marks
            elif second.isdigit():
                count = int(first)
                marks = int(second)
            # If first is digit and second is word
            elif first.isdigit() and second in number_words:
                count = int(first)
                marks = number_words[second]
            else:
                continue
            
            requirements[marks] = count
    
    # If still empty, try a very simple fallback: just extract all numbers
    if not requirements:
        numbers = re.findall(r'\d+', text)
        if len(numbers) >= 2:
            # Assume format: count mark count mark...
            for i in range(0, len(numbers)-1, 2):
                count = int(numbers[i])
                marks = int(numbers[i+1])
                requirements[marks] = count
    
    return requirements


def format_requirements_for_display(requirements):
    """
    Format requirements dict for display
    
    Args:
        requirements: {2: 10, 5: 5}
    
    Returns:
        str: "10 two-mark questions, 5 five-mark questions"
    """
    if not requirements:
        return "No requirements specified"
    
    parts = []
    for marks, count in sorted(requirements.items()):
        parts.append(f"{count} {marks}-mark question{'s' if count > 1 else ''}")
    
    return ", ".join(parts)


def validate_requirements(requirements, max_total=50):
    """
    Validate question requirements
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not requirements:
        return False, "No question requirements found. Please specify what you need."
    
    total = sum(requirements.values())
    if total > max_total:
        return False, f"Too many questions requested ({total}). Maximum is {max_total}."
    
    if total == 0:
        return False, "Please request at least one question."
    
    # Check for reasonable mark values
    for marks in requirements.keys():
        if marks < 1 or marks > 20:
            return False, f"Invalid mark value: {marks}. Please use marks between 1-20."
    
    return True, ""


# Example usage and tests
if __name__ == "__main__":
    test_cases = [
        "10 two mark questions",
        "5 five mark, 3 ten mark",
        "I want 10 two mark questions and 5 five mark questions",
        "2 marks: 10, 5 marks: 5",
        "15 one mark, 10 two mark, 5 five mark",
    ]
    
    for test in test_cases:
        result = parse_question_requirements(test)
        print(f"Input: {test}")
        print(f"Output: {result}")
        print(f"Display: {format_requirements_for_display(result)}")
        print()
