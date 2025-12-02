"""Example usage of the Q&A Agent."""
import json
from utils.logger import setup_logger
from graph.workflow import QAAgent


def main():
    """Run example queries."""
    # Setup logging
    setup_logger("INFO")

    # Initialize agent
    print("Initializing Q&A Agent...")
    agent = QAAgent()
    print("Agent ready!\n")

    # Example queries
    queries = [
        "What are people saying about the latest iPhone?",
        "How do I fix a memory leak in Python?",
        "What's the best way to learn machine learning in 2024?",
        "What are developers saying about the new React features?",
    ]

    for query in queries:
        print(f"\n{'='*80}")
        print(f"QUERY: {query}")
        print(f"{'='*80}\n")

        # Execute query
        result = agent.query(query)

        # Print results
        print("ANSWER:")
        print(result["answer"])
        print(f"\nConfidence: {result['confidence']:.2%}")
        print(f"Consensus Level: {result['consensus_level']}")
        print(f"Processing Time: {result['processing_time']}s")

        if result.get("perspectives"):
            print("\nPERSPECTIVES:")
            for key, value in result["perspectives"].items():
                print(f"  {key.title()}: {value}")

        print(f"\nSOURCES ({len(result['sources'])}):")
        for idx, source in enumerate(result["sources"][:5], 1):
            print(f"  {idx}. [{source['platform'].upper()}] {source['author']}")
            print(f"     {source['url']}")

        print(f"\n{'-'*80}\n")

        # Save to file
        with open(f"result_{queries.index(query) + 1}.json", "w") as f:
            json.dump(result, f, indent=2)


if __name__ == "__main__":
    main()
