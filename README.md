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
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your configuration:
   ```bash
   DISCORD_TOKEN=your_discord_token
   MONAD_RPC_URL=your_monad_rpc_url
   ```

