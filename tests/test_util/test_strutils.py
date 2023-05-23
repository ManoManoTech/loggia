from mm_utils.utils.strutils import clean_string, to_camel_case
from mm_utils.utils.strutils import to_snake_case_bis as to_snake_case


def test_snake_case():
    assert to_snake_case("Test") == "test"
    assert to_snake_case("Test@") == "test"
    assert to_snake_case("Test Case Space") == "test_case_space"
    assert to_snake_case("Test-Case-Space", separator="-") == "test_case_space"
    assert to_snake_case("Test Case 1_2") == "test_case_1_2"
    assert to_snake_case("Test Case1_2") == "test_case1_2"
    assert to_snake_case("") == ""
    assert to_snake_case(" ") == ""
    assert to_snake_case("Mano - Mano ", separator="-") == "mano_mano"


def test_clean_string():
    assert clean_string("Test") == "Test"
    assert clean_string("") == ""
    assert clean_string(" ") == " "
    assert clean_string("  ") == "  "
    assert clean_string("m@nomano") == "m nomano"
    assert clean_string("Business & Fun") == "Business and Fun"


def test_camel_case():
    assert to_camel_case("Test") == "Test"
    assert to_camel_case("Test@") == "Test"
    assert to_camel_case("SPA_cAse_space") == "SPACaseSpace"
    assert to_camel_case("Test Case Space", separator=" ") == "TestCaseSpace"
    assert to_camel_case("Test-Case-Space", separator="-") == "TestCaseSpace"
    assert to_camel_case("Test Case 1_2", separator=" ") == "TestCase1_2"
    assert to_camel_case("Test case1_2", separator="_") == "Testcase12"
    assert to_camel_case("") == ""
    assert to_camel_case(" ") == ""
