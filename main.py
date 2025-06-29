import discord
from discord.ext import commands
import asyncio
import os
import logging
from config.settings import BotConfig
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

# Configuration du logging pour Render (sans fichier de log)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Logs vers stdout pour Render
    ]
)

# Serveur HTTP simple pour Render (requis pour les web services)
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Bot Discord actif')
        else:
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Bot Discord Francais - Service actif')
    
    def log_message(self, format, *args):
        # Désactive les logs HTTP pour éviter le spam
        pass

def start_health_server():
    """Démarre le serveur de santé pour Render"""
    port = int(os.environ.get('PORT', 10000))  # Port par défaut Render
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    logging.info(f"🌐 Serveur de santé démarré sur le port {port}")
    server.serve_forever()

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
            
            # Forcer la synchronisation globale pour s'assurer que toutes les commandes sont visibles
            global_synced = await self.tree.sync(guild=None)
            logging.info(f"✅ Synchronisation globale: {len(global_synced)} commandes")
        except Exception as e:
            logging.error(f"❌ Erreur lors de la synchronisation: {e}")
    
    async def on_ready(self):
        """Événement déclenché quand le bot est prêt"""
        print(f"🤖 {self.user} est connecté et prêt!")
        print(f"📊 Connecté à {len(self.guilds)} serveur(s)")
        
        # Définir le statut par défaut
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="🛡️ Protéger le serveur"
            ),
            status=discord.Status.online
        )
    
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

async def main():
    """Fonction principale pour démarrer le bot avec serveur Render"""
    # Démarrer le serveur de santé pour Render en arrière-plan
    health_thread = threading.Thread(target=start_health_server, daemon=True)
    health_thread.start()
    
    # Attendre que le serveur démarre
    await asyncio.sleep(1)
    
    bot = FrenchBot()
    
    # Récupération du token depuis les variables d'environnement
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        logging.error("❌ Token Discord non trouvé dans les variables d'environnement!")
        return
    
    try:
        logging.info("🤖 Démarrage du bot Discord pour Render...")
        await bot.start(token)
    except discord.LoginFailure:
        logging.error("❌ Token Discord invalide!")
    except Exception as e:
        logging.error(f"❌ Erreur lors du démarrage: {e}")

if __name__ == "__main__":
    asyncio.run(main())
