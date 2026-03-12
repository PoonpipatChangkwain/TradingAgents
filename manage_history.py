"""
Utility script to manage trading history - review, analyze, and update completed trades.
Run this script to interact with the trading history CSV file.
"""

import sys
from tradingagents.agents.utils.history_tracker import HistoryTracker
import csv
from typing import Optional
import os


def display_menu():
    """Display the main menu."""
    print("\n" + "=" * 80)
    print("[TRADING HISTORY MANAGER]")
    print("=" * 80)
    print("1. View recent trades (last 5)")
    print("2. View all trades")
    print("3. Mark trade as completed (TP or SL)")
    print("4. Update balance for a trade")
    print("5. Get trading statistics")
    print("6. Update reason for a trade")
    print("7. Reset history file")
    print("8. Exit")
    print("=" * 80)
    return input("Select an option (1-8): ").strip()


def view_recent_trades(tracker: HistoryTracker):
    """Display recent trades."""
    records = tracker.read_recent_history(n_records=5)
    if not records:
        print("No trading history available.")
        return

    print("\n" + tracker.format_history_for_ai(records))


def view_all_trades(tracker: HistoryTracker):
    """Display all trades."""
    records = tracker.read_recent_history(n_records=10000)
    if not records:
        print("No trading history available.")
        return

    print("\n[ALL TRADING HISTORY]:")
    print("=" * 120)
    for i, record in enumerate(records, 1):
        print(
            f"{i}. [{record['Date']}] {record['TypeEntry']:15} | "
            f"Entry: {record['Entry']:10} | SL: {record['SL']:10} | TP: {record['TP']:10} | "
            f"Complete: {record['Complete'] or 'PENDING':10} | Balance: {record['Balance']:12}"
        )
    print("=" * 120)


def mark_trade_completed(tracker: HistoryTracker):
    """Mark a trade as completed (TP or SL)."""
    records = tracker.read_recent_history(n_records=10000)
    if not records:
        print("No trading history available.")
        return

    # Show recent trades with index
    print("\nRecent trades (showing last 20):")
    recent = records[-20:] if len(records) > 20 else records
    for i, record in enumerate(recent, 1):
        status = record.get("Complete", "PENDING") or "PENDING"
        print(
            f"{i}. [{record['Date']}] {record['TypeEntry']:15} | "
            f"Entry: {record['Entry']:10} | Status: {status}"
        )

    index = input("\nEnter trade number to mark as completed: ").strip()
    try:
        idx = int(index) - 1
        if 0 <= idx < len(recent):
            trade_index = len(records) - len(recent) + idx
            completion = input("Enter TP or SL: ").strip().upper()
            if completion in ["TP", "SL"]:
                # Read the CSV and update
                with open(tracker.history_path, "r", newline="", encoding="utf-8") as f:
                    rows = list(csv.DictReader(f))

                if 0 <= trade_index < len(rows):
                    rows[trade_index]["Complete"] = completion
                    # Write back
                    with open(
                        tracker.history_path, "w", newline="", encoding="utf-8"
                    ) as f:
                        writer = csv.DictWriter(
                            f,
                            fieldnames=[
                                "Date",
                                "TypeEntry",
                                "Entry",
                                "SL",
                                "TP",
                                "Reason",
                                "Val",
                                "Complete",
                                "Balance",
                            ],
                        )
                        writer.writeheader()
                        writer.writerows(rows)
                    print("[OK] Trade marked as {}".format(completion))
            else:
                print("Invalid input. Please enter TP or SL.")
        else:
            print("Invalid trade number.")
    except ValueError:
        print("Invalid input.")


def update_balance(tracker: HistoryTracker):
    """Update balance for a trade."""
    records = tracker.read_recent_history(n_records=10000)
    if not records:
        print("No trading history available.")
        return

    # Show recent trades
    print("\nRecent trades:")
    recent = records[-10:] if len(records) > 10 else records
    for i, record in enumerate(recent, 1):
        print(f"{i}. [{record['Date']}] {record['Balance']}")

    index = input("\nEnter trade number to update balance: ").strip()
    try:
        idx = int(index) - 1
        if 0 <= idx < len(recent):
            trade_index = len(records) - len(recent) + idx
            balance_str = input("Enter new balance (e.g., 70.50): ").strip()
            try:
                balance = float(balance_str)
                # Read the CSV and update
                with open(tracker.history_path, "r", newline="", encoding="utf-8") as f:
                    rows = list(csv.DictReader(f))

                if 0 <= trade_index < len(rows):
                    rows[trade_index]["Balance"] = f"${balance:.2f}"
                    # Write back
                    with open(
                        tracker.history_path, "w", newline="", encoding="utf-8"
                    ) as f:
                        writer = csv.DictWriter(
                            f,
                            fieldnames=[
                                "Date",
                                "TypeEntry",
                                "Entry",
                                "SL",
                                "TP",
                                "Reason",
                                "Val",
                                "Complete",
                                "Balance",
                            ],
                        )
                        writer.writeheader()
                        writer.writerows(rows)
                    print("[OK] Balance updated to ${:.2f}".format(balance))
            except ValueError:
                print("Invalid balance value.")
        else:
            print("Invalid trade number.")
    except ValueError:
        print("Invalid input.")


def get_statistics(tracker: HistoryTracker):
    """Display trading statistics."""
    stats = tracker.get_history_summary()
    print("\n[TRADING STATISTICS]:")
    print("=" * 40)
    print(f"Total Trades: {stats['total_trades']}")
    print(f"Wins (TP): {stats['wins']}")
    print(f"Losses (SL): {stats['losses']}")
    print(f"Pending: {stats['pending']}")
    print(f"Win Rate: {stats['win_rate']}")
    print(f"Current Balance: {stats['current_balance']}")
    print("=" * 40)


def update_reason(tracker: HistoryTracker):
    """Update reason for a trade."""
    records = tracker.read_recent_history(n_records=10000)
    if not records:
        print("No trading history available.")
        return

    # Show recent trades
    print("\nRecent trades:")
    recent = records[-10:] if len(records) > 10 else records
    for i, record in enumerate(recent, 1):
        reason = record.get("Reason", "N/A")[:50] + "..."
        print(f"{i}. [{record['Date']}] {reason}")

    index = input("\nEnter trade number to update reason: ").strip()
    try:
        idx = int(index) - 1
        if 0 <= idx < len(recent):
            trade_index = len(records) - len(recent) + idx
            reason = input("Enter new reason (max 150 chars): ").strip()[:150]
            # Read the CSV and update
            with open(tracker.history_path, "r", newline="", encoding="utf-8") as f:
                rows = list(csv.DictReader(f))

            if 0 <= trade_index < len(rows):
                rows[trade_index]["Reason"] = reason
                # Write back
                with open(
                    tracker.history_path, "w", newline="", encoding="utf-8"
                ) as f:
                    writer = csv.DictWriter(
                        f,
                        fieldnames=[
                            "Date",
                            "TypeEntry",
                            "Entry",
                            "SL",
                            "TP",
                            "Reason",
                            "Val",
                            "Complete",
                            "Balance",
                        ],
                    )
                    writer.writeheader()
                    writer.writerows(rows)
                print("[OK] Reason updated")
        else:
            print("Invalid trade number.")
    except ValueError:
        print("Invalid input.")


def reset_history(tracker: HistoryTracker):
    """Reset the history file."""
    confirm = input("[WARNING] This will DELETE all trading history. Are you sure? (yes/no): ")
    if confirm.lower() == "yes":
        try:
            os.remove(tracker.history_path)
            tracker._initialize_csv()
            print("[OK] History file reset successfully")
        except Exception as e:
            print("[ERROR] Error resetting history: {}".format(e))


def main():
    """Main program loop."""
    tracker = HistoryTracker()

    while True:
        choice = display_menu()

        if choice == "1":
            view_recent_trades(tracker)
        elif choice == "2":
            view_all_trades(tracker)
        elif choice == "3":
            mark_trade_completed(tracker)
        elif choice == "4":
            update_balance(tracker)
        elif choice == "5":
            get_statistics(tracker)
        elif choice == "6":
            update_reason(tracker)
        elif choice == "7":
            reset_history(tracker)
        elif choice == "8":
            print("Goodbye!")
            break
        else:
            print("Invalid option. Please try again.")


if __name__ == "__main__":
    main()
