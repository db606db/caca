
import discord
from discord.ext import commands
import asyncio
import os
import logging
from config.settings import BotConfig
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
import signal
import sys

# Configuration du logging pour Render
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

# Serveur HTTP keep-alive pour Render
class KeepAliveHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "status": "healthy",
                "bot_status": "online" if hasattr(self.server, 'bot') and self.server.bot.is_ready() else "starting",
                "timestamp": time.time()
            }
            self.wfile.write(str(response).encode())
        elif self.path == '/ping':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'pong')
        elif self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html = '''
            <!DOCTYPE html>
            <html>
            <head><title>Discord Bot Français</title></head>
            <body>
                <h1>🤖 Bot Discord Français</h1>
                <p>✅ Service actif sur Render</p>
                <p>🛡️ Bot de modération complet</p>
                <p>📊 Status: En ligne</p>
            </body>
            </html>
            '''
            self.wfile.write(html.encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        # Gérer les webhooks Render si nécessaire
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'OK')
    
    def log_message(self, format, *args):
        # Logs silencieux pour éviter le spam
        pass

class KeepAliveServer:
    def __init__(self, port=10000):
        self.port = port
        self.server = None
        self.thread = None
        self.running = False
    
    def start(self, bot=None):
        """Démarre le serveur keep-alive"""
        try:
            self.server = HTTPServer(('0.0.0.0', self.port), KeepAliveHandler)
            if bot:
                self.server.bot = bot
            
            self.thread = threading.Thread(target=self._run_server, daemon=True)
            self.thread.start()
            self.running = True
            logging.info(f"🌐 Serveur keep-alive démarré sur le port {self.port}")
        except Exception as e:
            logging.error(f"❌ Erreur serveur keep-alive: {e}")
    
    def _run_server(self):
        """Execute le serveur HTTP"""
        try:
            self.server.serve_forever()
        except Exception as e:
            logging.error(f"❌ Serveur keep-alive arrêté: {e}")
    
    def stop(self):
        """Arrête le serveur proprement"""
        if self.server and self.running:
            self.server.shutdown()
            self.running = False
            logging.info("🛑 Serveur keep-alive arrêté")

class FrenchBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(
            command_prefix='!',
            intents=intents,
            help_command=None,
            case_insensitive=True
        )
        self.config = BotConfig()
        self.keep_alive_server = None
        
    async def setup_hook(self):
        """Chargement des cogs au démarrage"""
        cogs_to_load = [
            'cogs.logs',
            'cogs.moderation',
            'cogs.configuration', 
            'cogs.anti_spam',
            'cogs.utility'
        ]
        
        for cog in cogs_to_load:
            try:
                await self.load_extension(cog)
                logging.info(f"✅ Cog {cog} chargé avec succès")
            except Exception as e:
                logging.error(f"❌ Erreur lors du chargement de {cog}: {e}")
        
        # Synchronisation des commandes slash
        try:
            synced = await self.tree.sync()
            logging.info(f"✅ {len(synced)} commandes slash synchronisées")
            
            # Synchronisation globale
            global_synced = await self.tree.sync(guild=None)
            logging.info(f"✅ Synchronisation globale: {len(global_synced)} commandes")
        except Exception as e:
            logging.error(f"❌ Erreur lors de la synchronisation: {e}")
    
    async def on_ready(self):
        """Événement déclenché quand le bot est prêt"""
        print(f"🤖 {self.user} est connecté et prêt!")
        print(f"📊 Connecté à {len(self.guilds)} serveur(s)")
        
        # Statut du bot
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="🛡️ Protéger le serveur | Render Online"
            ),
            status=discord.Status.online
        )
        
        # Tâche de maintenance keep-alive
        if not hasattr(self, '_keep_alive_task'):
            self._keep_alive_task = asyncio.create_task(self._keep_alive_loop())
    
    async def _keep_alive_loop(self):
        """Boucle de maintenance pour keep-alive"""
        while True:
            try:
                await asyncio.sleep(300)  # 5 minutes
                logging.info(f"💓 Keep-alive: Bot actif - {len(self.guilds)} serveurs")
            except Exception as e:
                logging.error(f"❌ Erreur keep-alive: {e}")
                await asyncio.sleep(60)
    
    async def on_command_error(self, ctx, error):
        """Gestion globale des erreurs"""
        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ Vous n'avez pas les permissions nécessaires pour cette commande.")
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("❌ Je n'ai pas les permissions nécessaires pour exécuter cette commande.")
        else:
            logging.error(f"Erreur dans {ctx.command}: {error}")
            await ctx.send("❌ Une erreur inattendue s'est produite.")

# Gestionnaire de signaux pour arrêt propre
def signal_handler(signum, frame):
    logging.info("🛑 Signal d'arrêt reçu, fermeture propre...")
    sys.exit(0)

async def main():
    """Fonction principale optimisée pour Render"""
    # Configuration des signaux
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Port Render
    port = int(os.environ.get('PORT', 10000))
    
    # Serveur keep-alive
    keep_alive = KeepAliveServer(port)
    
    # Création du bot
    bot = FrenchBot()
    bot.keep_alive_server = keep_alive
    
    # Token Discord
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        logging.error("❌ Token Discord non trouvé dans les variables d'environnement!")
        return
    
    try:
        # Démarrage du serveur keep-alive
        keep_alive.start(bot)
        
        # Attendre que le serveur démarre
        await asyncio.sleep(2)
        
        logging.info("🚀 Démarrage du bot Discord sur Render...")
        logging.info(f"🌐 Serveur keep-alive: http://0.0.0.0:{port}")
        logging.info("💡 Endpoints: /health, /ping, /")
        
        # Démarrage du bot Discord
        await bot.start(token)
        
    except discord.LoginFailure:
        logging.error("❌ Token Discord invalide!")
    except KeyboardInterrupt:
        logging.info("🛑 Arrêt demandé par l'utilisateur")
    except Exception as e:
        logging.error(f"❌ Erreur lors du démarrage: {e}")
    finally:
        # Nettoyage
        if keep_alive:
            keep_alive.stop()
        logging.info("🏁 Bot arrêté proprement")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("🛑 Arrêt du programme")
