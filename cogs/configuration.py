import discord
from discord.ext import commands
from discord import app_commands
from utils.embeds import EmbedBuilder
from utils.checks import is_admin, is_moderator
from typing import Literal

class Configuration(commands.Cog):
    """Module de configuration du bot"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="panel", description="Panneau de configuration interactif du serveur")
    @app_commands.default_permissions(administrator=True)
    async def panel(self, interaction: discord.Interaction):
        """Panneau de configuration interactif"""
        embed = discord.Embed(
            title="⚙️ Panneau de Configuration",
            description="Utilisez les boutons ci-dessous pour configurer le bot sur votre serveur.",
            color=0x00ff00,
            timestamp=discord.utils.utcnow()
        )
        
        embed.add_field(
            name="🛠️ Configuration Rapide",
            value="Configurez les paramètres essentiels du bot",
            inline=False
        )
        
        view = ConfigPanelView(self.bot, interaction.user)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @app_commands.command(name="config", description="Afficher la configuration actuelle du serveur")
    @is_moderator()
    async def config(self, interaction: discord.Interaction):
        """Affiche la configuration actuelle du serveur"""
        config = self.bot.config.get_guild_config(interaction.guild.id)
        
        embed = discord.Embed(
            title="⚙️ Configuration du Serveur",
            color=0x00ff00,
            timestamp=discord.utils.utcnow()
        )
        
        # Canal de logs
        logs_channel_id = config.get('logs_channel')
        logs_channel = interaction.guild.get_channel(logs_channel_id) if logs_channel_id else None
        embed.add_field(
            name="📋 Canal de Logs",
            value=logs_channel.mention if logs_channel else "*Non configuré*",
            inline=True
        )
        
        # Rôle de modérateur
        mod_role_id = config.get('mod_role')
        mod_role = interaction.guild.get_role(mod_role_id) if mod_role_id else None
        embed.add_field(
            name="👮 Rôle Modérateur",
            value=mod_role.mention if mod_role else "*Non configuré*",
            inline=True
        )
        
        # Rôle de mute
        mute_role_id = config.get('mute_role')
        mute_role = interaction.guild.get_role(mute_role_id) if mute_role_id else None
        embed.add_field(
            name="🔇 Rôle Mute",
            value=mute_role.mention if mute_role else "*Non configuré*",
            inline=True
        )
        
        # Configuration anti-spam
        auto_mod = config.get('auto_mod', {})
        anti_spam_status = "✅ Activé" if auto_mod.get('anti_spam', True) else "❌ Désactivé"
        anti_links_status = "✅ Activé" if auto_mod.get('anti_links', True) else "❌ Désactivé"
        
        embed.add_field(
            name="🛡️ Anti-Spam",
            value=f"{anti_spam_status}\nLimite: {auto_mod.get('message_limit', 5)} msg/{auto_mod.get('time_window', 10)}s",
            inline=True
        )
        
        embed.add_field(
            name="🔗 Anti-Liens",
            value=anti_links_status,
            inline=True
        )
        
        embed.add_field(
            name="📢 Max Mentions",
            value=str(auto_mod.get('max_mentions', 5)),
            inline=True
        )
        
        # Statut du bot
        status_config = config.get('status', {})
        embed.add_field(
            name="🤖 Statut du Bot",
            value=f"Type: {status_config.get('type', 'watching')}\nTexte: {status_config.get('text', '🛡️ Protéger le serveur')}",
            inline=False
        )
        
        embed.set_footer(text=f"Serveur: {interaction.guild.name}")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="setlogs", description="Configurer le canal de logs")
    @app_commands.describe(channel="Le canal pour les logs")
    @is_admin()
    async def setlogs(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """Configure le canal de logs"""
        self.bot.config.set_guild_setting(interaction.guild.id, 'logs_channel', channel.id)
        
        embed = EmbedBuilder.success(
            "Canal de logs configuré",
            f"Le canal {channel.mention} a été défini comme canal de logs.",
            interaction.user
        )
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="setmodrole", description="Configurer le rôle de modérateur")
    @app_commands.describe(role="Le rôle de modérateur")
    @is_admin()
    async def setmodrole(self, interaction: discord.Interaction, role: discord.Role):
        """Configure le rôle de modérateur"""
        self.bot.config.set_guild_setting(interaction.guild.id, 'mod_role', role.id)
        
        embed = EmbedBuilder.success(
            "Rôle de modérateur configuré",
            f"Le rôle {role.mention} a été défini comme rôle de modérateur.",
            interaction.user
        )
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="setmuterole", description="Configurer le rôle de mute")
    @app_commands.describe(role="Le rôle de mute")
    @is_admin()
    async def setmuterole(self, interaction: discord.Interaction, role: discord.Role):
        """Configure le rôle de mute"""
        self.bot.config.set_guild_setting(interaction.guild.id, 'mute_role', role.id)
        
        embed = EmbedBuilder.success(
            "Rôle de mute configuré",
            f"Le rôle {role.mention} a été défini comme rôle de mute.",
            interaction.user
        )
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="antispam", description="Configurer l'anti-spam")
    @app_commands.describe(
        enabled="Activer ou désactiver l'anti-spam",
        message_limit="Nombre maximum de messages",
        time_window="Fenêtre de temps en secondes"
    )
    @is_admin()
    async def antispam(self, interaction: discord.Interaction, enabled: bool, 
                      message_limit: int = 5, time_window: int = 10):
        """Configure l'anti-spam"""
        if message_limit < 1 or message_limit > 20:
            embed = EmbedBuilder.error("Paramètre invalide", "La limite de messages doit être entre 1 et 20.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if time_window < 5 or time_window > 60:
            embed = EmbedBuilder.error("Paramètre invalide", "La fenêtre de temps doit être entre 5 et 60 secondes.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        self.bot.config.set_guild_setting(interaction.guild.id, 'auto_mod.anti_spam', enabled)
        self.bot.config.set_guild_setting(interaction.guild.id, 'auto_mod.message_limit', message_limit)
        self.bot.config.set_guild_setting(interaction.guild.id, 'auto_mod.time_window', time_window)
        
        status = "activé" if enabled else "désactivé"
        embed = EmbedBuilder.success(
            "Anti-spam configuré",
            f"L'anti-spam a été **{status}**.\nLimite: {message_limit} messages par {time_window} secondes.",
            interaction.user
        )
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="antilinks", description="Configurer l'anti-liens")
    @app_commands.describe(enabled="Activer ou désactiver l'anti-liens")
    @is_admin()
    async def antilinks(self, interaction: discord.Interaction, enabled: bool):
        """Configure l'anti-liens"""
        self.bot.config.set_guild_setting(interaction.guild.id, 'auto_mod.anti_links', enabled)
        
        status = "activé" if enabled else "désactivé"
        embed = EmbedBuilder.success(
            "Anti-liens configuré",
            f"L'anti-liens a été **{status}**.",
            interaction.user
        )
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="maxmentions", description="Configurer le nombre maximum de mentions")
    @app_commands.describe(limit="Nombre maximum de mentions par message")
    @is_admin()
    async def maxmentions(self, interaction: discord.Interaction, limit: int):
        """Configure le nombre maximum de mentions"""
        if limit < 1 or limit > 20:
            embed = EmbedBuilder.error("Paramètre invalide", "La limite de mentions doit être entre 1 et 20.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        self.bot.config.set_guild_setting(interaction.guild.id, 'auto_mod.max_mentions', limit)
        
        embed = EmbedBuilder.success(
            "Limite de mentions configurée",
            f"Le nombre maximum de mentions par message a été défini à **{limit}**.",
            interaction.user
        )
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="setstatus", description="Configurer le statut du bot")
    @app_commands.describe(
        activity_type="Type d'activité",
        text="Texte du statut"
    )
    @is_admin()
    async def setstatus(self, interaction: discord.Interaction, 
                       activity_type: Literal['playing', 'watching', 'listening', 'streaming'], 
                       text: str):
        """Configure le statut du bot"""
        if len(text) > 128:
            embed = EmbedBuilder.error("Texte trop long", "Le texte du statut ne peut pas dépasser 128 caractères.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Mapper les types d'activité
        activity_map = {
            'playing': discord.ActivityType.playing,
            'watching': discord.ActivityType.watching,
            'listening': discord.ActivityType.listening,
            'streaming': discord.ActivityType.streaming
        }
        
        activity = discord.Activity(type=activity_map[activity_type], name=text)
        
        try:
            await self.bot.change_presence(activity=activity, status=discord.Status.online)
            
            # Sauvegarder la configuration
            self.bot.config.set_guild_setting(interaction.guild.id, 'status.type', activity_type)
            self.bot.config.set_guild_setting(interaction.guild.id, 'status.text', text)
            
            embed = EmbedBuilder.success(
                "Statut configuré",
                f"Le statut du bot a été défini sur:\n**{activity_type.capitalize()}** {text}",
                interaction.user
            )
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            embed = EmbedBuilder.error("Erreur", f"Impossible de changer le statut: {str(e)}")
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="resetconfig", description="Réinitialiser la configuration du serveur")
    @is_admin()
    async def resetconfig(self, interaction: discord.Interaction):
        """Réinitialise la configuration du serveur"""
        # Demander confirmation
        embed = EmbedBuilder.warning(
            "Confirmation requise",
            "Êtes-vous sûr de vouloir réinitialiser toute la configuration du serveur?\n\n**Cette action est irréversible!**"
        )
        
        view = ConfirmView(interaction.user)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        
        # Attendre la réponse
        await view.wait()
        
        if view.value is None:
            embed = EmbedBuilder.error("Timeout", "Temps d'attente dépassé. Action annulée.")
            await interaction.edit_original_response(embed=embed, view=None)
        elif view.value:
            # Réinitialiser la configuration
            if interaction.guild.id in self.bot.config.guilds_config:
                del self.bot.config.guilds_config[interaction.guild.id]
            
            embed = EmbedBuilder.success(
                "Configuration réinitialisée",
                "La configuration du serveur a été réinitialisée aux valeurs par défaut.",
                interaction.user
            )
            await interaction.edit_original_response(embed=embed, view=None)
        else:
            embed = EmbedBuilder.info("Action annulée", "La réinitialisation a été annulée.")
            await interaction.edit_original_response(embed=embed, view=None)

class ConfirmView(discord.ui.View):
    """Vue de confirmation pour les actions importantes"""
    
    def __init__(self, user: discord.Member):
        super().__init__(timeout=30)
        self.user = user
        self.value = None
    
    @discord.ui.button(label="✅ Confirmer", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.user:
            await interaction.response.send_message("❌ Vous ne pouvez pas utiliser ce bouton.", ephemeral=True)
            return
        
        self.value = True
        self.stop()
    
    @discord.ui.button(label="❌ Annuler", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.user:
            await interaction.response.send_message("❌ Vous ne pouvez pas utiliser ce bouton.", ephemeral=True)
            return
        
        self.value = False
        self.stop()

class ConfigPanelView(discord.ui.View):
    """Vue pour le panneau de configuration interactif"""
    
    def __init__(self, bot, user):
        super().__init__(timeout=300)
        self.bot = bot
        self.user = user
    
    @discord.ui.button(label="📋 Voir Config", style=discord.ButtonStyle.secondary, emoji="📋")
    async def view_config(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.user:
            await interaction.response.send_message("❌ Vous ne pouvez pas utiliser ce bouton.", ephemeral=True)
            return
        
        config = self.bot.config.get_guild_config(interaction.guild.id)
        
        embed = discord.Embed(
            title="⚙️ Configuration Actuelle",
            color=0x00ff00,
            timestamp=discord.utils.utcnow()
        )
        
        # Canal de logs
        logs_channel_id = config.get('logs_channel')
        logs_channel = interaction.guild.get_channel(logs_channel_id) if logs_channel_id else None
        embed.add_field(
            name="📋 Canal de Logs",
            value=logs_channel.mention if logs_channel else "*Non configuré*",
            inline=True
        )
        
        # Rôle de modérateur
        mod_role_id = config.get('mod_role')
        mod_role = interaction.guild.get_role(mod_role_id) if mod_role_id else None
        embed.add_field(
            name="👮 Rôle Modérateur",
            value=mod_role.mention if mod_role else "*Non configuré*",
            inline=True
        )
        
        # Anti-spam
        auto_mod = config.get('auto_mod', {})
        anti_spam_status = "✅ Activé" if auto_mod.get('anti_spam', True) else "❌ Désactivé"
        embed.add_field(
            name="🛡️ Anti-Spam",
            value=f"{anti_spam_status}\n{auto_mod.get('message_limit', 5)} msg/{auto_mod.get('time_window', 10)}s",
            inline=True
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="🛡️ Anti-Spam", style=discord.ButtonStyle.primary, emoji="🛡️")
    async def toggle_antispam(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.user:
            await interaction.response.send_message("❌ Vous ne pouvez pas utiliser ce bouton.", ephemeral=True)
            return
        
        current = self.bot.config.get_guild_setting(interaction.guild.id, 'auto_mod.anti_spam', True)
        new_value = not current
        self.bot.config.set_guild_setting(interaction.guild.id, 'auto_mod.anti_spam', new_value)
        
        status = "activé" if new_value else "désactivé"
        embed = EmbedBuilder.success(
            "Anti-spam modifié",
            f"L'anti-spam est maintenant **{status}**."
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="🔗 Anti-Liens", style=discord.ButtonStyle.primary, emoji="🔗")
    async def toggle_antilinks(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.user:
            await interaction.response.send_message("❌ Vous ne pouvez pas utiliser ce bouton.", ephemeral=True)
            return
        
        current = self.bot.config.get_guild_setting(interaction.guild.id, 'auto_mod.anti_links', True)
        new_value = not current
        self.bot.config.set_guild_setting(interaction.guild.id, 'auto_mod.anti_links', new_value)
        
        status = "activé" if new_value else "désactivé"
        embed = EmbedBuilder.success(
            "Anti-liens modifié",
            f"L'anti-liens est maintenant **{status}**."
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="🤖 Statut Bot", style=discord.ButtonStyle.success, emoji="🤖")
    async def change_status(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.user:
            await interaction.response.send_message("❌ Vous ne pouvez pas utiliser ce bouton.", ephemeral=True)
            return
        
        modal = StatusModal(self.bot)
        await interaction.response.send_modal(modal)

class StatusModal(discord.ui.Modal, title="🤖 Changer le Statut du Bot"):
    """Modal pour changer le statut du bot"""
    
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
    
    activity_type = discord.ui.TextInput(
        label="Type d'activité",
        placeholder="playing, watching, listening, streaming",
        default="watching",
        max_length=20
    )
    
    activity_text = discord.ui.TextInput(
        label="Texte du statut",
        placeholder="🛡️ Protéger le serveur",
        default="🛡️ Protéger le serveur",
        max_length=128
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        activity_types = {
            'playing': discord.ActivityType.playing,
            'watching': discord.ActivityType.watching,
            'listening': discord.ActivityType.listening,
            'streaming': discord.ActivityType.streaming
        }
        
        activity_type_str = self.activity_type.value.lower()
        if activity_type_str not in activity_types:
            embed = EmbedBuilder.error(
                "Type invalide",
                "Types valides: playing, watching, listening, streaming"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            activity = discord.Activity(
                type=activity_types[activity_type_str],
                name=self.activity_text.value
            )
            await self.bot.change_presence(activity=activity, status=discord.Status.online)
            
            embed = EmbedBuilder.success(
                "Statut modifié",
                f"Nouveau statut: **{activity_type_str.capitalize()}** {self.activity_text.value}"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            embed = EmbedBuilder.error("Erreur", f"Impossible de changer le statut: {str(e)}")
            await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Configuration(bot))
