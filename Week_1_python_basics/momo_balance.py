"""A focused simulation of the MTN MoMo balance-check USSD process."""

SECRET_PIN = "2345"  # Demo PIN 
ACCOUNT_BALANCE = 1247.50  # Demo balance in Ghana cedis.
MAX_ATTEMPTS = 3
PIN_LENGTH = 4
USSD_CODE = "*170#"


def display_main_menu() -> None:
    """Display the first menu shown after dialing *170#."""
    print("\nUnlock more deals, try our new MoMo App")
    print("1) Transfer Money")
    print("2) MoMoPay& Pay Bill")
    print("3) Airtime& Bundles")
    print("4) Allow Cash Out")
    print("5) Financial")
    print("# for next")


def display_services_menu() -> None:
    """Display the Services menu after selecting # for next."""
    print("\nServices")
    print("6) My Wallet")
    print("7) Just4U Offers for you")
    print("8) MoMo App (300MB free data)")


def display_wallet_menu() -> None:
    """Display the wallet menu used for the balance request."""
    print("\nMy Wallet")
    print("1) Check Balance")
    print("2) Allow Cash Out")
    print("3) My Approvals")
    print("4) Report Fraud")
    print("5) Statements")
    print("6) Change PIN")
    print("7) Upgrade Profile Type")
    print("8) Reversals")
    print("9) Check Wallet Limits")
    print("0) Back")


def get_pin() -> bool:
    """Verify the demo PIN and return whether the request is authorised."""
    for attempt in range(MAX_ATTEMPTS):
        pin = input("Fee is GHS 0.00. Enter MM PIN: ").strip()

        if len(pin) == PIN_LENGTH and pin.isdigit() and pin == SECRET_PIN:
            return True

        attempts_left = MAX_ATTEMPTS - attempt - 1
        if attempts_left:
            print(f"Incorrect PIN. {attempts_left} attempt(s) remaining.")
        else:
            print("Too many incorrect attempts. Your account has been locked.")

    return False


def check_balance() -> None:
    """Complete the balance-check request after the wallet menu selection."""
    if get_pin():
        print(f"\nYour MoMo balance is GHS {ACCOUNT_BALANCE:,.2f}.")


def run_ussd_session() -> None:
    """Run the menu steps represented in the supplied MTN screenshots."""
    print(f"\nDialling {USSD_CODE}...")
    display_main_menu()

    while input("\nReply: ").strip() != "#":
        print("\nThis simulation only supports # for next.")

    while True:
        display_services_menu()
        service_choice = input("\nReply: ").strip()

        if service_choice != "6":
            print("\nThis simulation only supports My Wallet (option 6).")
            continue

        while True:
            display_wallet_menu()
            wallet_choice = input("\nReply: ").strip()

            if wallet_choice == "1":
                check_balance()
                return
            if wallet_choice == "0":
                print("\nReturning to Services.")
                break

            print("\nThis simulation only supports Check Balance (option 1).")


def main() -> None:
    """Provide a small launcher for the balance-check USSD simulation."""
    while True:
        print("\nMTN MoMo Balance Checker")
        print(f"1) Dial {USSD_CODE}")
        print("2) Exit")
        choice = input("\nSelect an option: ").strip()

        if choice == "1":
            run_ussd_session()
        elif choice == "2":
            print("\nThank you for using MTN Mobile Money. Goodbye!")
            return
        else:
            print("\nInvalid option. Please select 1 or 2.")


if __name__ == "__main__":
    main()
