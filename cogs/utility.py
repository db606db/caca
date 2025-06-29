import discord
from discord.ext import commands
from discord import app_commands
from utils.embeds import EmbedBuilder
from datetime import datetime
import platform
import psutil
import os

class Utility(commands.Cog):
    """Module d'utilitaires et commandes diverses"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="ping", description="Afficher la latence du bot")
    async def ping(self, interaction: discord.Interaction):
        """Affiche la latence du bot"""
        latency = round(self.bot.latency * 1000)
        
        if latency < 100:
            color = 0x00ff00  # Vert
            status = "Excellent"
        elif latency < 200:
            color = 0xffa500  # Orange
            status = "Bon"
        else:
            color = 0xff0000  # Rouge
            status = "Élevé"
        
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"Latence: **{latency}ms** ({status})",
            color=color,
            timestamp=datetime.utcnow()
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="serverinfo", description="Informations sur le serveur")
    async def serverinfo(self, interaction: discord.Interaction):
        """Affiche les informations du serveur"""
        guild = interaction.guild
        
        embed = discord.Embed(
            title=f"📊 Informations - {guild.name}",
            color=0x00ff00,
            timestamp=datetime.utcnow()
        )
        
        # Informations générales
        embed.add_field(name="🆔 ID", value=str(guild.id), inline=True)
        embed.add_field(name="👑 Propriétaire", value=guild.owner.mention if guild.owner else "Inconnu", inline=True)
        embed.add_field(name="📅 Créé le", value=f"<t:{int(guild.created_at.timestamp())}:F>", inline=True)
        
        # Statistiques des membres
        total_members = guild.member_count
        bots = sum(1 for member in guild.members if member.bot)
        humans = total_members - bots
        
        embed.add_field(name="👥 Membres", value=f"Total: {total_members}\nHumains: {humans}\nBots: {bots}", inline=True)
        
        # Statistiques des canaux
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        categories = len(guild.categories)
        
        embed.add_field(name="📝 Canaux", value=f"Texte: {text_channels}\nVocal: {voice_channels}\nCatégories: {categories}", inline=True)
        
        # Autres statistiques
        embed.add_field(name="🎭 Rôles", value=str(len(guild.roles)), inline=True)
        embed.add_field(name="😀 Émojis", value=str(len(guild.emojis)), inline=True)
        embed.add_field(name="📈 Niveau de boost", value=f"Niveau {guild.premium_tier} ({guild.premium_subscription_count} boosts)", inline=True)
        
        # Niveau de vérification
        verification_levels = {
            discord.VerificationLevel.none: "Aucune",
            discord.VerificationLevel.low: "Faible",
            discord.VerificationLevel.medium: "Moyenne",
            discord.VerificationLevel.high: "Élevée",
            discord.VerificationLevel.highest: "Très élevée"
        }
        embed.add_field(name="🔒 Vérification", value=verification_levels.get(guild.verification_level, "Inconnu"), inline=True)
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        embed.set_footer(text=f"Serveur créé il y a {(datetime.utcnow() - guild.created_at).days} jours")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="userinfo", description="Informations sur un utilisateur")
    @app_commands.describe(user="L'utilisateur dont voir les informations (optionnel)")
    async def userinfo(self, interaction: discord.Interaction, user: discord.Member = None):
        """Affiche les informations d'un utilisateur"""
        if user is None:
            user = interaction.user
        
        embed = discord.Embed(
            title=f"👤 Informations - {user.display_name}",
            color=user.color if user.color != discord.Color.default() else 0x00ff00,
            timestamp=datetime.utcnow()
        )
        
        # Informations générales
        embed.add_field(name="🏷️ Nom d'utilisateur", value=str(user), inline=True)
        embed.add_field(name="🆔 ID", value=str(user.id), inline=True)
        embed.add_field(name="🤖 Bot", value="Oui" if user.bot else "Non", inline=True)
        
        # Dates importantes
        embed.add_field(name="📅 Compte créé", value=f"<t:{int(user.created_at.timestamp())}:F>", inline=False)
        if user.joined_at:
            embed.add_field(name="📥 A rejoint", value=f"<t:{int(user.joined_at.timestamp())}:F>", inline=False)
        
        # Statut et activité
        status_emojis = {
            discord.Status.online: "🟢 En ligne",
            discord.Status.idle: "🟡 Absent",
            discord.Status.dnd: "🔴 Ne pas déranger",
            discord.Status.offline: "⚫ Hors ligne"
        }
        embed.add_field(name="📶 Statut", value=status_emojis.get(user.status, "❓ Inconnu"), inline=True)
        
        if user.activity:
            activity_type = {
                discord.ActivityType.playing: "🎮 Joue à",
                discord.ActivityType.streaming: "📺 Stream",
                discord.ActivityType.listening: "🎵 Écoute",
                discord.ActivityType.watching: "👀 Regarde"
            }
            activity_text = activity_type.get(user.activity.type, "💭 Activité")
            embed.add_field(name="🎯 Activité", value=f"{activity_text} {user.activity.name}", inline=True)
        
        # Rôles (top 10)
        if len(user.roles) > 1:  # Exclut @everyone
            roles = [role.mention for role in user.roles[1:]][:10]  # Top 10 rôles
            roles_text = ", ".join(roles)
            if len(user.roles) > 11:
                roles_text += f" ... (+{len(user.roles) - 11} rôles)"
            embed.add_field(name="🎭 Rôles", value=roles_text, inline=False)
        
        # Permissions clés
        key_permissions = []
        if user.guild_permissions.administrator:
            key_permissions.append("👑 Administrateur")
        elif user.guild_permissions.manage_guild:
            key_permissions.append("⚙️ Gérer le serveur")
        elif user.guild_permissions.manage_messages:
            key_permissions.append("🛡️ Modérateur")
        
        if key_permissions:
            embed.add_field(name="🔑 Permissions clés", value=", ".join(key_permissions), inline=False)
        
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_footer(text=f"Demandé par {interaction.user.display_name}")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="avatar", description="Afficher l'avatar d'un utilisateur")
    @app_commands.describe(user="L'utilisateur dont voir l'avatar (optionnel)")
    async def avatar(self, interaction: discord.Interaction, user: discord.Member = None):
        """Affiche l'avatar d'un utilisateur"""
        if user is None:
            user = interaction.user
        
        embed = discord.Embed(
            title=f"🖼️ Avatar de {user.display_name}",
            color=user.color if user.color != discord.Color.default() else 0x00ff00,
            timestamp=datetime.utcnow()
        )
        
        embed.set_image(url=user.display_avatar.url)
        embed.add_field(name="🔗 Lien direct", value=f"[Cliquez ici]({user.display_avatar.url})", inline=False)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="botinfo", description="Informations sur le bot")
    async def botinfo(self, interaction: discord.Interaction):
        """Affiche les informations du bot"""
        embed = discord.Embed(
            title=f"🤖 Informations - {self.bot.user.name}",
            color=0x00ff00,
            timestamp=datetime.utcnow()
        )
        
        # Informations générales
        embed.add_field(name="🆔 ID", value=str(self.bot.user.id), inline=True)
        embed.add_field(name="📅 Créé le", value=f"<t:{int(self.bot.user.created_at.timestamp())}:F>", inline=True)
        embed.add_field(name="🏓 Latence", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        
        # Statistiques
        total_members = sum(guild.member_count for guild in self.bot.guilds)
        embed.add_field(name="🏠 Serveurs", value=str(len(self.bot.guilds)), inline=True)
        embed.add_field(name="👥 Utilisateurs", value=str(total_members), inline=True)
        embed.add_field(name="📝 Commandes", value=str(len(self.bot.tree.get_commands())), inline=True)
        
        # Informations système
        try:
            process = psutil.Process()
            memory_usage = process.memory_info().rss / 1024 / 1024  # MB
            cpu_usage = process.cpu_percent()
            
            embed.add_field(name="💾 RAM", value=f"{memory_usage:.1f} MB", inline=True)
            embed.add_field(name="🖥️ CPU", value=f"{cpu_usage:.1f}%", inline=True)
        except:
            pass
        
        embed.add_field(name="🐍 Python", value=platform.python_version(), inline=True)
        embed.add_field(name="📚 discord.py", value=discord.__version__, inline=True)
        embed.add_field(name="💻 OS", value=platform.system(), inline=True)
        
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_footer(text="Bot de modération français avec système de logs complet")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="help", description="Afficher l'aide du bot")
    async def help(self, interaction: discord.Interaction):
        """Affiche l'aide du bot"""
        embed = discord.Embed(
            title="📚 Aide - Commandes du Bot",
            description="Voici toutes les commandes disponibles organisées par catégories.",
            color=0x00ff00,
            timestamp=datetime.utcnow()
        )
        
        # Catégorie Modération
        moderation_commands = [
            "`/kick` - Expulser un membre",
            "`/ban` - Bannir un membre", 
            "`/unban` - Débannir un utilisateur",
            "`/mute` - Rendre muet un membre",
            "`/unmute` - Enlever le mute",
            "`/timeout` - Mettre en timeout",
            "`/clear` - Supprimer des messages",
            "`/warn` - Avertir un membre",
            "`/warnings` - Voir les avertissements",
            "`/clearwarn` - Effacer les avertissements",
            "`/slowmode` - Mode lent d'un canal",
            "`/lock` - Verrouiller un canal",
            "`/unlock` - Déverrouiller un canal",
            "`/nuke` - Supprimer et recréer un canal"
        ]
        embed.add_field(
            name="🔨 Modération",
            value="\n".join(moderation_commands),
            inline=False
        )
        
        # Catégorie Configuration
        config_commands = [
            "`/panel` - Panneau de configuration interactif",
            "`/config` - Voir la configuration",
            "`/setlogs` - Définir le canal de logs",
            "`/setmodrole` - Définir le rôle modérateur",
            "`/setmuterole` - Définir le rôle mute",
            "`/antispam` - Configurer l'anti-spam",
            "`/antilinks` - Configurer l'anti-liens",
            "`/maxmentions` - Limite de mentions",
            "`/setstatus` - Changer le statut du bot",
            "`/resetconfig` - Réinitialiser la config"
        ]
        embed.add_field(
            name="⚙️ Configuration",
            value="\n".join(config_commands),
            inline=False
        )
        
        # Catégorie Utilitaires
        utility_commands = [
            "`/ping` - Latence du bot",
            "`/serverinfo` - Infos du serveur",
            "`/userinfo` - Infos d'un utilisateur",
            "`/avatar` - Avatar d'un utilisateur",
            "`/botinfo` - Informations du bot",
            "`/help` - Cette aide"
        ]
        embed.add_field(
            name="🛠️ Utilitaires", 
            value="\n".join(utility_commands),
            inline=False
        )
        
        # Fonctionnalités automatiques
        auto_features = [
            "🛡️ **Anti-spam** - Détection automatique",
            "🔗 **Anti-liens** - Filtrage des liens",
            "📢 **Limite mentions** - Protection contre le spam de mentions",
            "📋 **Logs complets** - Tous les événements enregistrés",
            "⚡ **Sanctions progressives** - Avertissements → Mute → Kick → Ban"
        ]
        embed.add_field(
            name="🤖 Fonctionnalités Automatiques",
            value="\n".join(auto_features),
            inline=False
        )
        
        embed.set_footer(text="💡 Conseil: Configurez d'abord le canal de logs avec /setlogs")
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Utility(bot))
