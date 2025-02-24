import os
import discord
from discord.ext import commands, tasks
from web3 import Web3
from eth_account import Account
from datetime import datetime, timedelta
import sqlite3
import asyncio
from dotenv import load_dotenv
from discord.ext.commands import CommandOnCooldown

# Carregar variáveis de ambiente
load_dotenv()

# Configurações
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
RPC_URL = "https://testnet-rpc.monad.xyz/"
FAUCET_PRIVATE_KEY = os.getenv("FAUCET_PRIVATE_KEY")
MONAD_AMOUNT = 0.1  # quantidade por request
COOLDOWN_HOURS = 24  # voltar para 24 horas

# Configurações de segurança
MAX_REQUESTS_PER_DAY = 1  # voltar para 1 request por dia
MAX_WALLET_BALANCE = 10  # máximo de MON permitido na carteira
REQUIRED_ROLE_ID = 1334899788541595679
MAX_GAS_LIMIT = 100000  # Limite máximo de gas
SAFE_GAS_MULTIPLIER = 1.2  # Multiplicador de segurança para gas price
MIN_ACCOUNT_AGE_DAYS = 30  # Conta precisa ter pelo menos 30 dias

# IDs dos moderadores (adicione os IDs dos mods aqui)
MOD_ROLE_NAME = "Moderator"  # Nome do cargo de moderador
MOD_ROLE_IDS = [
    1334882610488541288,  # ID do cargo Moderator
    1334903945608564766,   # ID de outro cargo com permissão
    1282273258460151892,
    1334883291475476540
]

# No início do arquivo, após carregar as variáveis de ambiente
if not FAUCET_PRIVATE_KEY.startswith('0x'):
    FAUCET_PRIVATE_KEY = '0x' + FAUCET_PRIVATE_KEY

# Inicialização
w3 = Web3(Web3.HTTPProvider(RPC_URL))
faucet_account = Account.from_key(FAUCET_PRIVATE_KEY)
FAUCET_ADDRESS = faucet_account.address

# Configurações que dependem do Web3
MAX_GAS_COST_WEI = w3.to_wei(0.01, 'ether')  # Aumentado o limite de custo de gas

# Identificador único para esta versão do bot
BOT_VERSION = "v1.0.0"

# Configuração do bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Conexão com banco de dados
def init_db():
    conn = sqlite3.connect('faucet.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS requests
                 (user_id TEXT, address TEXT, timestamp DATETIME)''')
    conn.commit()
    conn.close()

async def check_cooldown(user_id):
    conn = sqlite3.connect('faucet.db')
    c = conn.cursor()
    c.execute('SELECT timestamp FROM requests WHERE user_id = ? ORDER BY timestamp DESC LIMIT 1', (str(user_id),))
    result = c.fetchone()
    conn.close()
    
    if result:
        last_request = datetime.strptime(result[0], '%Y-%m-%d %H:%M:%S')
        if datetime.now() - last_request < timedelta(hours=COOLDOWN_HOURS):
            return False
    return True

# Melhorar o sistema de cache
class ResponseCache:
    def __init__(self):
        self.message_cache = set()
    
    def has_responded(self, message_id):
        return message_id in self.message_cache
    
    def add_response(self, message_id):
        self.message_cache.add(message_id)
    
    def clear(self):
        self.message_cache.clear()

# Instanciar o cache
cache = ResponseCache()

@tasks.loop(minutes=1)
async def clear_old_responses():
    """Limpa o cache de respostas a cada minuto"""
    cache.clear()

@bot.event
async def on_ready():
    print(f'{bot.user} está online!')
    init_db()
    clear_old_responses.start()

def is_mod(ctx):
    """Verifica se o usuário tem algum cargo de moderador"""
    return any(role.id in MOD_ROLE_IDS for role in ctx.author.roles)

@bot.command(name='balance')
@commands.cooldown(1, 3, commands.BucketType.user)
async def check_balance(ctx):
    # Verificar cache primeiro
    if cache.has_responded(ctx.message.id):
        return
        
    # Adicionar ao cache antes de processar
    cache.add_response(ctx.message.id)
    
    if not is_mod(ctx):
        await ctx.reply("❌ This command is only available to moderators.")
        return
    
    try:
        balance = w3.eth.get_balance(FAUCET_ADDRESS)
        balance_eth = w3.from_wei(balance, 'ether')
        await ctx.reply(f'[{BOT_VERSION}] 💰 Current faucet balance: {balance_eth:.4f} MON')
    except Exception as e:
        await ctx.reply(f'[{BOT_VERSION}] ❌ Error checking faucet balance.')

@bot.command(name='helpme')
async def help_command(ctx):
    help_text = """
**Available Commands:**
`!faucet <address>` - Request 0.1 MON tokens
`!helpme` - Show this help message
`!info` - Show network information

**Requirements:**
• Must have the required role
• Discord account must be at least 30 days old
• Wallet balance must be less than 10 MON
• Can request once per day

**Moderator Commands:**
`!balance` - Check current faucet balance
"""
    await ctx.reply(help_text)

@bot.command(name='info')
async def info_command(ctx):
    info_text = f"""
**Monad Testnet Faucet**
• Network: Monad Testnet
• Amount per request: {MONAD_AMOUNT} MON
• Explorer: https://testnet.monadexplorer.com
• RPC: {RPC_URL}
• Chain ID: {w3.eth.chain_id}

For support or issues, contact the moderators.
"""
    await ctx.reply(info_text)

# Adicionar um conjunto para rastrear transações processadas
processed_transactions = set()

async def can_request_tokens(ctx, address):
    """Verifica se o usuário pode solicitar tokens"""
    try:
        # Verificar se tem a role necessária
        if not any(role.id == REQUIRED_ROLE_ID for role in ctx.author.roles):
            await ctx.reply('❌ You need the required role to use this faucet.')
            return False

        # Verificar idade da conta
        account_age = (datetime.now(ctx.author.created_at.tzinfo) - ctx.author.created_at).days
        if account_age < MIN_ACCOUNT_AGE_DAYS:
            await ctx.reply(f'❌ Your Discord account must be at least {MIN_ACCOUNT_AGE_DAYS} days old to use this faucet.')
            return False

        # Verificar saldo da carteira
        balance = w3.eth.get_balance(address)
        balance_mon = w3.from_wei(balance, 'ether')
        if balance_mon >= MAX_WALLET_BALANCE:
            await ctx.reply('❌ You have enough MON in your wallet. Save some for others!')
            return False

        # Verificar limite diário
        conn = sqlite3.connect('faucet.db')
        c = conn.cursor()
        today = datetime.now().strftime('%Y-%m-%d')
        c.execute('''SELECT COUNT(*) FROM requests 
                    WHERE user_id = ? AND date(timestamp) = ?''', 
                    (str(ctx.author.id), today))
        daily_requests = c.fetchone()[0]
        conn.close()

        if daily_requests >= MAX_REQUESTS_PER_DAY:
            await ctx.reply('❌ You can only request tokens once per day. Try again tomorrow.')
            return False

        return True

    except Exception as e:
        await ctx.reply(f'❌ Error checking eligibility: {str(e)}')
        return False

@bot.command(name='faucet')
@commands.cooldown(1, 3, commands.BucketType.user)
async def send_tokens(ctx, address: str):
    if cache.has_responded(ctx.message.id):
        return
    
    cache.add_response(ctx.message.id)
    
    try:
        # Validações básicas
        if not w3.is_address(address):
            await ctx.reply('❌ Invalid Ethereum address!')
            return

        # Verificar elegibilidade
        if not await can_request_tokens(ctx, address):
            return

        if not await check_cooldown(ctx.author.id):
            remaining_time = 30  # segundos
            await ctx.reply(f'⏳ Please wait {remaining_time} seconds before requesting again!')
            return

        faucet_balance = w3.eth.get_balance(FAUCET_ADDRESS)
        amount_wei = w3.to_wei(MONAD_AMOUNT, 'ether')
        
        if faucet_balance < amount_wei:
            await ctx.reply('❌ Insufficient funds in faucet!')
            return

        # Preparar transação
        nonce = w3.eth.get_transaction_count(FAUCET_ADDRESS, 'pending')
        gas_price = w3.eth.gas_price

        transaction = {
            'nonce': nonce,
            'to': w3.to_checksum_address(address),  # Converter para checksum address
            'value': amount_wei,
            'gas': 21000,
            'gasPrice': gas_price,
            'chainId': w3.eth.chain_id,
            'from': FAUCET_ADDRESS  # Adicionar endereço de origem
        }

        # Assinar e enviar transação
        try:
            # Estimar gas com limite
            gas_estimate = min(w3.eth.estimate_gas(transaction), MAX_GAS_LIMIT)
            transaction['gas'] = int(gas_estimate * SAFE_GAS_MULTIPLIER)

            # Verificar se o gas total não é muito alto
            total_gas_cost = transaction['gas'] * transaction['gasPrice']
            if total_gas_cost > MAX_GAS_COST_WEI:  # Usando a nova constante
                await ctx.reply('❌ Transaction gas cost too high.')
                return

            # Assinar transação
            signed_txn = w3.eth.account.sign_transaction(transaction, FAUCET_PRIVATE_KEY)
            
            # Enviar transação assinada
            tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)  # Usar raw_transaction em vez de rawTransaction
            
            # Aguardar confirmação
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)
            
            if receipt.status == 1:
                # Registrar no banco de dados
                conn = sqlite3.connect('faucet.db')
                c = conn.cursor()
                c.execute('INSERT INTO requests VALUES (?, ?, ?)',
                         (str(ctx.author.id), address, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                conn.commit()
                conn.close()

                # Enviar confirmação
                explorer_url = f'https://testnet.monadexplorer.com/tx/{tx_hash.hex()}'
                await ctx.reply(f'✅ {MONAD_AMOUNT} MON sent to {address}\n'
                             f'🔍 View transaction: {explorer_url}')
            else:
                await ctx.reply('❌ Transaction failed!')

        except Exception as e:
            if "insufficient funds" in str(e).lower():
                await ctx.reply('❌ Insufficient funds for gas fees.')
            else:
                await ctx.reply(f'❌ Transaction error: {str(e)}')

    except Exception as e:
        await ctx.reply(f'❌ Request processing error: {str(e)}')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.reply(f'⏳ Please wait {error.retry_after:.1f} seconds before using this command again.')
    elif isinstance(error, commands.MissingRequiredArgument):
        if ctx.command.name == 'faucet':
            await ctx.reply('❌ Please provide an address: `!faucet <address>`')

def main():
    bot.run(DISCORD_TOKEN)

if __name__ == "__main__":
    main() 