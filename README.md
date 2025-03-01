# 🤖 Monadians Faucet Bot

Discord bot for distributing MON tokens on Monad testnet.

## 📋 Features

- Automatic distribution of 0.2 MON per request
- 24-hour cooldown system between requests
- Wallet balance verification
- Discord account age verification
- Role-based permission system
- Moderation commands

## 🛠️ Commands

- `!faucet <address>` - Request 0.2 MON tokens
- `!helpme` - Show help message
- `!info` - Show network information
- `!balance` - (Moderators only) Check faucet balance

## ⚙️ Requirements

- Python 3.12+
- discord.py
- web3
- python-dotenv
- SQLite3

## 🚀 Setup

1. Clone the repository
```bash
git clone https://github.com/Karatekid05/MonadiansFaucet.git
cd MonadiansFaucet
```

2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Configure .env file
```env
DISCORD_TOKEN=your_token_here
FAUCET_PRIVATE_KEY=your_private_key_here
```

5. Run the bot
```bash
python bot.py
```

## 🔒 Usage Requirements

- Discord account older than 30 days
- Specific server role
- Maximum wallet balance of 10 MON
- 24-hour wait between requests

## 🌐 Useful Links

- [Monad Explorer](https://testnet.monadexplorer.com)
- [RPC URL](https://testnet-rpc.monad.xyz/)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests.

## 📄 License

This project is under the MIT license. See the [LICENSE](LICENSE) file for details.

