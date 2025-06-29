import discord
from discord.ext import commands
import asyncio
import os
import logging
from config.settings import BotConfig

# Configuration du logging pour Render
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Logs vers stdout pour Render
    ]
)

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
    """Fonction principale pour démarrer le bot"""
    bot = FrenchBot()
    
    # Récupération du token depuis les variables d'environnement
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        logging.error("❌ Token Discord non trouvé dans les variables d'environnement!")
        return
    
    try:
        await bot.start(token)
    except discord.LoginFailure:
        logging.error("❌ Token Discord invalide!")
    except Exception as e:
        logging.error(f"❌ Erreur lors du démarrage: {e}")

if __name__ == "__main__":
    asyncio.run(main())