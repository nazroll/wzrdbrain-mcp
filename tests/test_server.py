import re
from unittest.mock import patch

from wzrdbrain_mcp.server import (
    _sanitize_for_log,
    generate_skating_combo,
    get_tricks_by_category,
    list_trick_categories,
    skating_practice_routine,
)


# --- _sanitize_for_log ---

class TestSanitizeForLog:
    def test_normal_string(self):
        assert _sanitize_for_log("hello world") == "hello world"

    def test_truncates_long_string(self):
        long = "a" * 100
        assert _sanitize_for_log(long) == "a" * 50

    def test_strips_non_printable(self):
        assert _sanitize_for_log("hello\x00world") == "helloworld"
        assert _sanitize_for_log("line\nbreak") == "linebreak"
        assert _sanitize_for_log("\x1b[31mred\x1b[0m") == "[31mred[0m"

    def test_empty_string(self):
        assert _sanitize_for_log("") == ""

    def test_custom_max_len(self):
        assert _sanitize_for_log("abcdef", max_len=3) == "abc"


# --- generate_skating_combo: happy path ---

class TestGenerateSkatingComboHappy:
    LINE_RE = re.compile(r"^\d+\. .+: .+/.+/.+/.+ → .+/.+/.+/.+$")

    def test_default_three_tricks(self):
        result = generate_skating_combo()
        lines = result.strip().split("\n")
        assert len(lines) == 3
        for line in lines:
            assert self.LINE_RE.match(line), f"Line did not match format: {line}"

    def test_one_trick(self):
        result = generate_skating_combo(num_tricks=1)
        lines = result.strip().split("\n")
        assert len(lines) == 1
        assert self.LINE_RE.match(lines[0])

    def test_twenty_tricks(self):
        result = generate_skating_combo(num_tricks=20)
        lines = result.strip().split("\n")
        assert len(lines) == 20
        for line in lines:
            assert self.LINE_RE.match(line), f"Line did not match format: {line}"


# --- generate_skating_combo: validation errors ---

class TestGenerateSkatingComboValidation:
    def test_zero(self):
        assert generate_skating_combo(num_tricks=0) == "Error: num_tricks must be between 1 and 20."

    def test_over_twenty(self):
        assert generate_skating_combo(num_tricks=21) == "Error: num_tricks must be between 1 and 20."

    def test_negative(self):
        assert generate_skating_combo(num_tricks=-1) == "Error: num_tricks must be between 1 and 20."

    def test_string_input(self):
        assert generate_skating_combo(num_tricks="3") == "Error: num_tricks must be an integer."

    def test_float_input(self):
        assert generate_skating_combo(num_tricks=3.5) == "Error: num_tricks must be an integer."


# --- generate_skating_combo: mocked error paths ---

class TestGenerateSkatingComboMocked:
    @patch("wzrdbrain_mcp.server.wzrdbrain.generate_combo")
    def test_exception(self, mock_gen):
        mock_gen.side_effect = Exception("boom")
        result = generate_skating_combo(num_tricks=3)
        assert "An internal error occurred" in result

    @patch("wzrdbrain_mcp.server.wzrdbrain.generate_combo")
    def test_returns_none(self, mock_gen):
        mock_gen.return_value = None
        result = generate_skating_combo(num_tricks=3)
        assert "Unexpected internal response format" in result

    @patch("wzrdbrain_mcp.server.wzrdbrain.generate_combo")
    def test_bad_dict_keys(self, mock_gen):
        mock_gen.return_value = [{"bad": "dict"}]
        result = generate_skating_combo(num_tricks=1)
        assert "Unexpected internal trick format" in result

    @patch("wzrdbrain_mcp.server.wzrdbrain.generate_combo")
    def test_missing_sub_keys_uses_fallback(self, mock_gen):
        mock_gen.return_value = [
            {"name": "TestTrick", "entry": {}, "exit": {}}
        ]
        result = generate_skating_combo(num_tricks=1)
        assert "TestTrick" in result
        assert "?/?/?/?" in result


# --- list_trick_categories ---

class TestListTrickCategories:
    def test_returns_sorted_list(self):
        cats = list_trick_categories()
        assert cats == sorted(cats)

    def test_expected_categories(self):
        cats = list_trick_categories()
        expected = {"base", "manual", "pivot", "slide", "swivel", "transition", "turn"}
        assert set(cats) == expected

    def test_no_duplicates(self):
        cats = list_trick_categories()
        assert len(cats) == len(set(cats))


# --- get_tricks_by_category ---

class TestGetTricksByCategory:
    def test_valid_category(self):
        result = get_tricks_by_category("base")
        assert result.startswith("Tricks in category:\n-")

    def test_case_insensitive_title(self):
        assert get_tricks_by_category("Base") == get_tricks_by_category("base")

    def test_case_insensitive_upper(self):
        assert get_tricks_by_category("BASE") == get_tricks_by_category("base")

    def test_invalid_category(self):
        result = get_tricks_by_category("nonexistent")
        assert result.startswith("Error: Invalid category.")
        assert "Valid categories are:" in result

    def test_empty_string(self):
        result = get_tricks_by_category("")
        assert "Error: Invalid category." in result
        assert "Valid categories are:" in result


# --- skating_practice_routine ---

class TestSkatingPracticeRoutine:
    def test_returns_nonempty(self):
        result = skating_practice_routine()
        assert len(result) > 0

    def test_contains_key_terms(self):
        result = skating_practice_routine()
        assert "generate_skating_combo" in result
        assert "Warm-up" in result
        assert "Cool-down" in result
        assert "30-minute" in result

# --- Error paths for Priority 2 tools ---

class TestToolErrorPaths:
    @patch("wzrdbrain_mcp.server.MOVES")
    def test_list_trick_categories_error(self, mock_moves):
        mock_moves.values.side_effect = Exception("Mocked exception")
        assert list_trick_categories() == []

    @patch("wzrdbrain_mcp.server.MOVES")
    def test_get_tricks_by_category_error(self, mock_moves):
        mock_moves.values.side_effect = Exception("Mocked exception")
        result = get_tricks_by_category("base")
        assert result == "Error: Could not retrieve tricks for the specified category."

# --- Main entry point ---

class TestMainEntry:
    @patch("wzrdbrain_mcp.server.mcp.run")
    def test_main(self, mock_run):
        from wzrdbrain_mcp.server import main
        main()
        mock_run.assert_called_once()
