# Monad Testnet Discord Faucet Bot

A Discord bot for distributing Monad testnet tokens with security features and role-based access control.

## Features
- Automated token distribution (0.1 MON per request)
- Role-based access control
- Security checks:
  - Discord account age verification (30+ days)
  - Wallet balance limit (< 10 MON)
  - Daily request limits (1 per day)
  - Role requirement
- Transaction tracking and monitoring
- Moderator commands

## Requirements
- Python 3.8+
- discord.py
- web3.py
- python-dotenv

## Setup
1. Clone the repository
```bash
git clone https://github.com/Karatekid05/FacuetBotMonad.git
cd FacuetBotMonad
```

2. Create and activate virtual environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Configure environment variables
```bash
cp .env.example .env
# Edit .env with your Discord token and wallet private key
```

5. Run the bot
```bash
chmod +x run_bot.sh
./run_bot.sh
```

## Commands
- `!faucet <address>` - Request 0.1 MON tokens
- `!helpme` - Show help message
- `!info` - Show network information
- `!balance` - Check faucet balance (moderators only)

## Security Features
- Role-based access control
- Account age verification (30 days minimum)
- Wallet balance checks (max 10 MON)
- Daily request limits (1 per 24h)
- Transaction monitoring
- Gas limits and safety checks

## Running 24/7
The bot includes a run_bot.sh script that automatically restarts the bot if it crashes. Use screen or tmux to keep it running in the background:

```bash
screen -S monadbot
./run_bot.sh
# Press Ctrl+A, D to detach
```

## License
MIT

