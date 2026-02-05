import sys
import os

# Add the project root to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.common.utils import parse_podcast_script

def test_parsing():
    # Test Case 1: Standard Format
    script1 = """
Jamie: Welcome to the show.
Alex: Thanks for having me.
Jamie: Let's dive in.
    """
    parsed1 = parse_podcast_script(script1)
    print(f"Test 1 (Standard): {parsed1}")
    assert len(parsed1) == 3
    assert parsed1[0] == ("Jamie", "Welcome to the show.")
    assert parsed1[1] == ("Alex", "Thanks for having me.")

    # Test Case 2: Markdown Bolding
    script2 = """
**Jamie**: Welcome to the show.
**Alex**: Thanks for having me.
    """
    parsed2 = parse_podcast_script(script2)
    print(f"Test 2 (Bold): {parsed2}")
    assert len(parsed2) == 2
    assert parsed2[0] == ("Jamie", "Welcome to the show.")

    # Test Case 3: Messy Format (spaces, quotes)
    script3 = """
  Jamie : "Welcome to the show."
*Alex*: 'Thanks for having me.'
  """
    parsed3 = parse_podcast_script(script3)
    print(f"Test 3 (Messy): {parsed3}")
    assert len(parsed3) == 2
    assert parsed3[0][1] == "Welcome to the show."

    # Test Case 4: Wrong Casing
    script4 = """
JAMIE: Hello.
alex: Hi for having me.
    """
    parsed4 = parse_podcast_script(script4)
    print(f"Test 4 (Case): {parsed4}")
    assert parsed4[0][0] == "Jamie"
    assert parsed4[1][0] == "Alex"

    # Test Case 5: Garbage / Code Blocks (from User Log)
    script5 = """
Jamie: Real dialogue.
# Outputs: 5 4 3 2 1
print("Valid:", score)
1️⃣ Trying to loop over an integer (`for i in 5: `)
Alex: Another real dialogue.
    """
    parsed5 = parse_podcast_script(script5)
    print(f"Test 5 (Garbage Filtering): {parsed5}")
    assert len(parsed5) == 2
    assert parsed5[0] == ("Jamie", "Real dialogue.")
    assert parsed5[1] == ("Alex", "Another real dialogue.")

    print("\nAll Tests Passed!")

if __name__ == "__main__":
    test_parsing()
