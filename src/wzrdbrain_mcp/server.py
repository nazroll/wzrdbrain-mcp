import logging
import re
import sys
import wzrdbrain
from wzrdbrain.wzrdbrain import MOVES
from mcp.server.fastmcp import FastMCP

# Configure logging to write security-relevant events to stderr explicitly
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s', stream=sys.stderr)
logger = logging.getLogger(__name__)

# Regex to strip non-printable/control characters for safe logging
_LOG_SANITIZE_RE = re.compile(r'[^\x20-\x7E]')


def _sanitize_for_log(value: str, max_len: int = 50) -> str:
    """Truncate and strip non-printable characters from a value before logging."""
    truncated = value[:max_len]
    return _LOG_SANITIZE_RE.sub('', truncated)


# Initialize FastMCP server
mcp = FastMCP("wzrdbrain-mcp")

@mcp.tool()
def generate_skating_combo(num_tricks: int = 3) -> str:
    """
    Generates a physics-aware sequence of wizard-style inline skating tricks.

    Args:
        num_tricks: The number of tricks to chain together in the combo. Must be between 1 and 20. Defaults to 3.
    """
    # Input Validation
    if not isinstance(num_tricks, int):
        logger.warning(f"Invalid input type for num_tricks: {type(num_tricks)}")
        return "Error: num_tricks must be an integer."

    if not (1 <= num_tricks <= 20):
        logger.warning(f"num_tricks out of bounds: {num_tricks}")
        return "Error: num_tricks must be between 1 and 20."

    try:
        combo = wzrdbrain.generate_combo(num_tricks)

        # Output Sanitization and Formatting
        if not isinstance(combo, list):
            logger.error(f"Unexpected output format from wzrdbrain: {type(combo)}")
            return "Error generating combo: Unexpected internal response format."

        formatted_combo = []
        for i, trick in enumerate(combo):
            if not isinstance(trick, dict) or 'name' not in trick or 'entry' not in trick or 'exit' not in trick:
                logger.error("Unexpected trick format in combo list.")
                return "Error generating combo: Unexpected internal trick format."

            entry = trick['entry']
            exit_ = trick['exit']
            entry_state = f"{entry.get('direction', '?')}/{entry.get('edge', '?')}/{entry.get('stance', '?')}/{entry.get('point', '?')}"
            exit_state = f"{exit_.get('direction', '?')}/{exit_.get('edge', '?')}/{exit_.get('stance', '?')}/{exit_.get('point', '?')}"
            name = trick['name']
            formatted_combo.append(f"{i+1}. {name}: {entry_state} → {exit_state}")

        return "\n".join(formatted_combo)

    except Exception as e:
        logger.error(f"Exception during combo generation: {str(e)}")
        return "Error generating combo: An internal error occurred while generating the tricks."

@mcp.tool()
def list_trick_categories() -> list[str]:
    """
    Retrieves the available categories of inline skating tricks.
    """
    try:
        categories = list(set(move.category for move in MOVES.values()))
        return sorted(categories)
    except Exception as e:
        logger.error(f"Error listing categories: {str(e)}")
        return []

@mcp.tool()
def get_tricks_by_category(category: str) -> str:
    """
    Retrieves all tricks that fall under a specific category.

    Args:
        category: The category name (e.g., 'pivot', 'slide'). Validated against known categories.
    """
    try:
        valid_categories = {move.category.lower() for move in MOVES.values()}
        target_category = category.lower()

        if target_category not in valid_categories:
            logger.warning(f"Invalid category requested: {_sanitize_for_log(category)}")
            valid_list = ', '.join(sorted(valid_categories))
            return f"Error: Invalid category. Valid categories are: {valid_list}"

        tricks = [move.name for move in MOVES.values() if move.category.lower() == target_category]
        return f"Tricks in category:\n- " + "\n- ".join(sorted(tricks))
    except Exception as e:
        logger.error(f"Error getting tricks for category: {_sanitize_for_log(category)}")
        return "Error: Could not retrieve tricks for the specified category."

@mcp.prompt()
def skating_practice_routine() -> str:
    """
    A pre-defined prompt template that instructs the LLM to use the `generate_skating_combo`
    tool to create a combo and then wrap it in a structured 30-minute practice session plan.
    """
    return (
        "Please generate a 30-minute inline skating practice routine for me. \n"
        "First, use the `generate_skating_combo` tool to create a sequence of 4 tricks.\n"
        "Then, structure the routine as follows:\n"
        "1. Warm-up (5 minutes)\n"
        "2. Trick Breakdown & Practice (15 minutes) - Explain how to approach the generated combo, focusing on the transitions between the states.\n"
        "3. Combo Execution (5 minutes) - Trying to link the whole combo together.\n"
        "4. Cool-down (5 minutes)"
    )

def main():
    """Entry point for the mcp-server-wzrdbrain script."""
    mcp.run()

if __name__ == "__main__":
    main()
