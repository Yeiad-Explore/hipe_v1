"""Simple test script for the Q&A Agent."""
import sys
from utils.logger import setup_logger
from graph.workflow import QAAgent


def test_basic_query():
    """Test basic query functionality."""
    print("Testing Q&A Agent...\n")

    # Setup
    setup_logger("INFO")

    # Initialize
    print("1. Initializing agent...")
    try:
        agent = QAAgent()
        print("   ✓ Agent initialized\n")
    except Exception as e:
        print(f"   ✗ Failed to initialize: {e}")
        return False

    # Test query
    print("2. Testing query...")
    test_query = "What is Python used for?"

    try:
        result = agent.query(test_query)
        print(f"   ✓ Query executed in {result['processing_time']}s\n")

        # Validate result
        print("3. Validating result...")
        assert "answer" in result, "Missing answer"
        assert "confidence" in result, "Missing confidence"
        assert "sources" in result, "Missing sources"
        assert len(result["answer"]) > 0, "Empty answer"

        print("   ✓ Result structure valid\n")

        # Print summary
        print("RESULT SUMMARY:")
        print(f"  Answer length: {len(result['answer'])} chars")
        print(f"  Confidence: {result['confidence']:.2%}")
        print(f"  Sources: {len(result['sources'])}")
        print(f"  Consensus: {result['consensus_level']}")
        print(f"  Processing time: {result['processing_time']}s")

        print("\nSample answer (first 200 chars):")
        print(f"  {result['answer'][:200]}...")

        print("\n✓ All tests passed!")
        return True

    except Exception as e:
        print(f"   ✗ Query failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_basic_query()
    sys.exit(0 if success else 1)
