# MTN MoMo Balance Checker

A Python console program that simulates checking an MTN MoMo wallet balance through a USSD-style menu.

## Requirements

- Python 3.9 or newer

No external packages are required.

## Run the program

From `Week_1_python_basics`:

```bash
python momo_balance.py
```

Select `1` to start a balance-check session or `2` to exit. The session walks through these menu steps:

1. Dial `*170#`.
2. Select `#` to open Services.
3. Select `6` for My Wallet.
4. Select `1` to check the balance.
5. Enter the demo PIN when prompted.

The demo PIN is `2345`. The displayed demo balance is GHS 1,247.50. The program allows three incorrect PIN attempts before ending the request.

## Project file

- `momo_balance.py`: menu display, PIN validation, session flow, and balance output.

## Scope

This is an offline simulation for learning Python functions, loops, conditional logic, input handling, and formatted output. It does not connect to MTN services or access a real wallet.
