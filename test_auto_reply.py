"""
Test script to demonstrate the autonomous auto-reply functionality
"""
from coordinator import CoordinatorAgent


def test_auto_reply():
    """Test the auto-reply agent"""
    print("\n" + "=" * 60)
    print("TESTING AUTONOMOUS AUTO-REPLY AGENT")
    print("=" * 60)
    print("\nThis test will:")
    print("1. Check for unread emails")
    print("2. Automatically detect resume/profile-related requests")
    print("3. Generate and send personalized replies")
    print("4. Mark emails as processed")
    print("\n" + "=" * 60 + "\n")
    
    # Initialize coordinator
    coordinator = CoordinatorAgent()
    
    # Run the workflow (includes auto-reply)
    coordinator.execute_workflow()
    
    print("\n" + "=" * 60)
    print("TEST COMPLETED")
    print("=" * 60)
    print("\nThe agent will now autonomously:")
    print("✓ Monitor incoming emails")
    print("✓ Detect resume/skills/profile requests")
    print("✓ Reply with personalized information")
    print("✓ No manual intervention required!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    try:
        test_auto_reply()
    except KeyboardInterrupt:
        print("\n\nTest stopped by user")
    except Exception as e:
        print(f"\nError: {e}")
