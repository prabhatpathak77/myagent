import schedule
import time
from coordinator import CoordinatorAgent
from config import CHECK_INTERVAL_MINUTES


def main():
    print("\n" + "=" * 60)
    print("AI PERSONAL ASSISTANT - COORDINATOR SYSTEM")
    print("=" * 60)
    print(f"Check interval: {CHECK_INTERVAL_MINUTES} minutes\n")
    
    # Initialize coordinator agent
    coordinator = CoordinatorAgent()
    
    # Run immediately on start
    coordinator.execute_workflow()
    
    # Schedule periodic runs
    schedule.every(CHECK_INTERVAL_MINUTES).minutes.do(coordinator.execute_workflow)
    
    print(f"\n✓ System is now running autonomously")
    print(f"✓ Checking every {CHECK_INTERVAL_MINUTES} minutes")
    print("✓ Press Ctrl+C to stop\n")
    
    # Keep running
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n" + "=" * 60)
        print("System stopped by user")
        print("=" * 60)
    except Exception as e:
        print(f"\nError: {e}")
