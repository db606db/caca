import discord
from discord.ext import commands
from discord import app_commands
from utils.embeds import EmbedBuilder
from utils.checks import is_moderator, is_admin, bot_has_permissions, can_moderate_member, get_mute_role
from datetime import datetime, timedelta
import asyncio
from typing import Optional

class Moderation(commands.Cog):
    """Module de modération complet"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="kick", description="Expulser un membre du serveur")
    @app_commands.describe(
        member="Le membre à expulser",
        reason="Raison de l'expulsion"
    )
    @is_moderator()
    @bot_has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = "Aucune raison spécifiée"):
        """Expulse un membre du serveur"""
        if not await can_moderate_member(interaction.user, member):
            embed = EmbedBuilder.error("Permission refusée", "Vous ne pouvez pas modérer ce membre.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            # Envoyer un message privé avant le kick
            try:
                dm_embed = EmbedBuilder.warning(
                    "Expulsion",
                    f"Vous avez été expulsé du serveur **{interaction.guild.name}**\n\n**Raison:** {reason}"
                )
                await member.send(embed=dm_embed)
            except discord.Forbidden:
                pass  # L'utilisateur a désactivé les MPs
            
            # Expulser le membre
            await member.kick(reason=f"Par {interaction.user} - {reason}")
            
            # Réponse de confirmation
            embed = EmbedBuilder.success(
                "Membre expulsé",
                f"{member.mention} a été expulsé du serveur.",
                interaction.user
            )
            await interaction.response.send_message(embed=embed)
            
            # Log de l'action
            await self._log_moderation("Expulsion", member, interaction.user, reason)
            
        except discord.Forbidden:
            embed = EmbedBuilder.error("Permission insuffisante", "Je n'ai pas les permissions pour expulser ce membre.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            embed = EmbedBuilder.error("Erreur", f"Une erreur s'est produite: {str(e)}")
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="ban", description="Bannir un membre du serveur")
    @app_commands.describe(
        member="Le membre à bannir",
        reason="Raison du bannissement",
        delete_days="Nombre de jours de messages à supprimer (0-7)"
    )
    @is_moderator()
    @bot_has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, member: discord.Member, 
                  reason: str = "Aucune raison spécifiée", delete_days: int = 0):
        """Bannit un membre du serveur"""
        if not await can_moderate_member(interaction.user, member):
            embed = EmbedBuilder.error("Permission refusée", "Vous ne pouvez pas modérer ce membre.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if delete_days < 0 or delete_days > 7:
            embed = EmbedBuilder.error("Paramètre invalide", "Le nombre de jours doit être entre 0 et 7.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            # Envoyer un message privé avant le ban
            try:
                dm_embed = EmbedBuilder.error(
                    "Bannissement",
                    f"Vous avez été banni du serveur **{interaction.guild.name}**\n\n**Raison:** {reason}"
                )
                await member.send(embed=dm_embed)
            except discord.Forbidden:
                pass
            
            # Bannir le membre
            await member.ban(reason=f"Par {interaction.user} - {reason}", delete_message_days=delete_days)
            
            # Réponse de confirmation
            embed = EmbedBuilder.success(
                "Membre banni",
                f"{member.mention} a été banni du serveur.",
                interaction.user
            )
            await interaction.response.send_message(embed=embed)
            
            # Log de l'action
            await self._log_moderation("Bannissement", member, interaction.user, reason)
            
        except discord.Forbidden:
            embed = EmbedBuilder.error("Permission insuffisante", "Je n'ai pas les permissions pour bannir ce membre.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            embed = EmbedBuilder.error("Erreur", f"Une erreur s'est produite: {str(e)}")
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="unban", description="Débannir un utilisateur")
    @app_commands.describe(
        user_id="L'ID de l'utilisateur à débannir",
        reason="Raison du débannissement"
    )
    @is_moderator()
    @bot_has_permissions(ban_members=True)
    async def unban(self, interaction: discord.Interaction, user_id: str, reason: str = "Aucune raison spécifiée"):
        """Débannit un utilisateur"""
        try:
            user_id = int(user_id)
            user = await self.bot.fetch_user(user_id)
            
            await interaction.guild.unban(user, reason=f"Par {interaction.user} - {reason}")
            
            embed = EmbedBuilder.success(
                "Utilisateur débanni",
                f"{user.mention} a été débanni du serveur.",
                interaction.user
            )
            await interaction.response.send_message(embed=embed)
            
            # Log de l'action
            await self._log_moderation("Débannissement", user, interaction.user, reason)
            
        except ValueError:
            embed = EmbedBuilder.error("ID invalide", "L'ID utilisateur fourni n'est pas valide.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except discord.NotFound:
            embed = EmbedBuilder.error("Utilisateur non trouvé", "Cet utilisateur n'est pas banni ou n'existe pas.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            embed = EmbedBuilder.error("Erreur", f"Une erreur s'est produite: {str(e)}")
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="mute", description="Rendre muet un membre")
    @app_commands.describe(
        member="Le membre à rendre muet",
        duration="Durée en minutes (optionnel)",
        reason="Raison du mute"
    )
    @is_moderator()
    @bot_has_permissions(manage_roles=True)
    async def mute(self, interaction: discord.Interaction, member: discord.Member, 
                   duration: Optional[int] = None, reason: str = "Aucune raison spécifiée"):
        """Rend muet un membre"""
        if not await can_moderate_member(interaction.user, member):
            embed = EmbedBuilder.error("Permission refusée", "Vous ne pouvez pas modérer ce membre.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        mute_role = await get_mute_role(interaction.guild, self.bot.config)
        if not mute_role:
            embed = EmbedBuilder.error("Erreur de configuration", "Impossible de créer ou trouver le rôle de mute.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if mute_role in member.roles:
            embed = EmbedBuilder.warning("Déjà muet", "Ce membre est déjà muet.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            await member.add_roles(mute_role, reason=f"Par {interaction.user} - {reason}")
            
            duration_text = f" pendant {duration} minutes" if duration else ""
            embed = EmbedBuilder.success(
                "Membre rendu muet",
                f"{member.mention} a été rendu muet{duration_text}.",
                interaction.user
            )
            await interaction.response.send_message(embed=embed)
            
            # Log de l'action
            await self._log_moderation(f"Mute{duration_text}", member, interaction.user, reason)
            
            # Démute automatique si durée spécifiée
            if duration:
                await asyncio.sleep(duration * 60)
                if mute_role in member.roles:
                    await member.remove_roles(mute_role, reason="Fin du mute temporaire")
                    await self._log_moderation("Démute automatique", member, self.bot.user, "Fin de la durée")
            
        except discord.Forbidden:
            embed = EmbedBuilder.error("Permission insuffisante", "Je n'ai pas les permissions pour modifier les rôles de ce membre.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="unmute", description="Enlever le mute d'un membre")
    @app_commands.describe(
        member="Le membre à démuter",
        reason="Raison du démute"
    )
    @is_moderator()
    @bot_has_permissions(manage_roles=True)
    async def unmute(self, interaction: discord.Interaction, member: discord.Member, reason: str = "Aucune raison spécifiée"):
        """Enlève le mute d'un membre"""
        mute_role = await get_mute_role(interaction.guild, self.bot.config)
        if not mute_role or mute_role not in member.roles:
            embed = EmbedBuilder.warning("Pas muet", "Ce membre n'est pas muet.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            await member.remove_roles(mute_role, reason=f"Par {interaction.user} - {reason}")
            
            embed = EmbedBuilder.success(
                "Membre démuté",
                f"{member.mention} n'est plus muet.",
                interaction.user
            )
            await interaction.response.send_message(embed=embed)
            
            # Log de l'action
            await self._log_moderation("Démute", member, interaction.user, reason)
            
        except discord.Forbidden:
            embed = EmbedBuilder.error("Permission insuffisante", "Je n'ai pas les permissions pour modifier les rôles de ce membre.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="timeout", description="Mettre un membre en timeout")
    @app_commands.describe(
        member="Le membre à timeout",
        duration="Durée en minutes",
        reason="Raison du timeout"
    )
    @is_moderator()
    @bot_has_permissions(moderate_members=True)
    async def timeout(self, interaction: discord.Interaction, member: discord.Member, 
                     duration: int, reason: str = "Aucune raison spécifiée"):
        """Met un membre en timeout"""
        if not await can_moderate_member(interaction.user, member):
            embed = EmbedBuilder.error("Permission refusée", "Vous ne pouvez pas modérer ce membre.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if duration <= 0 or duration > 40320:  # Max 28 jours
            embed = EmbedBuilder.error("Durée invalide", "La durée doit être entre 1 minute et 28 jours (40320 minutes).")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            until = datetime.utcnow() + timedelta(minutes=duration)
            await member.timeout(until, reason=f"Par {interaction.user} - {reason}")
            
            embed = EmbedBuilder.success(
                "Membre en timeout",
                f"{member.mention} a été mis en timeout pendant {duration} minutes.",
                interaction.user
            )
            await interaction.response.send_message(embed=embed)
            
            # Log de l'action
            await self._log_moderation(f"Timeout ({duration}min)", member, interaction.user, reason)
            
        except discord.Forbidden:
            embed = EmbedBuilder.error("Permission insuffisante", "Je n'ai pas les permissions pour mettre ce membre en timeout.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="clear", description="Supprimer des messages")
    @app_commands.describe(
        amount="Nombre de messages à supprimer",
        member="Supprimer uniquement les messages de ce membre (optionnel)"
    )
    @is_moderator()
    @bot_has_permissions(manage_messages=True)
    async def clear(self, interaction: discord.Interaction, amount: int, member: Optional[discord.Member] = None):
        """Supprime des messages"""
        if amount <= 0 or amount > 100:
            embed = EmbedBuilder.error("Nombre invalide", "Le nombre de messages doit être entre 1 et 100.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True)
        
        try:
            if member:
                # Supprimer les messages d'un membre spécifique
                def check(message):
                    return message.author == member
                
                deleted = await interaction.channel.purge(limit=amount, check=check)
            else:
                # Supprimer tous les messages
                deleted = await interaction.channel.purge(limit=amount)
            
            embed = EmbedBuilder.success(
                "Messages supprimés",
                f"**{len(deleted)}** messages ont été supprimés" + (f" de {member.mention}" if member else "") + ".",
                interaction.user
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            
            # Log de l'action
            logs_channel = self._get_logs_channel(interaction.guild)
            if logs_channel:
                log_embed = EmbedBuilder.info(
                    "Messages supprimés en masse",
                    f"**{len(deleted)}** messages supprimés dans {interaction.channel.mention}" + 
                    (f" de {member.mention}" if member else "")
                )
                log_embed.add_field(name="👮 Modérateur", value=interaction.user.mention, inline=True)
                await logs_channel.send(embed=log_embed)
            
        except discord.Forbidden:
            embed = EmbedBuilder.error("Permission insuffisante", "Je n'ai pas les permissions pour supprimer des messages.")
            await interaction.followup.send(embed=embed, ephemeral=True)
    
    @app_commands.command(name="warn", description="Avertir un membre")
    @app_commands.describe(
        member="Le membre à avertir",
        reason="Raison de l'avertissement"
    )
    @is_moderator()
    async def warn(self, interaction: discord.Interaction, member: discord.Member, reason: str):
        """Avertit un membre"""
        if not await can_moderate_member(interaction.user, member):
            embed = EmbedBuilder.error("Permission refusée", "Vous ne pouvez pas modérer ce membre.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Ajouter l'avertissement
        warning_count = self.bot.config.add_warning(interaction.guild.id, member.id)
        
        # Envoyer un message privé
        try:
            dm_embed = EmbedBuilder.warning(
                "Avertissement",
                f"Vous avez reçu un avertissement sur **{interaction.guild.name}**\n\n**Raison:** {reason}\n**Total d'avertissements:** {warning_count}"
            )
            await member.send(embed=dm_embed)
        except discord.Forbidden:
            pass
        
        embed = EmbedBuilder.warning(
            "Membre averti",
            f"{member.mention} a reçu un avertissement.\n**Total:** {warning_count} avertissement(s)",
            interaction.user
        )
        await interaction.response.send_message(embed=embed)
        
        # Log de l'action
        await self._log_moderation(f"Avertissement ({warning_count})", member, interaction.user, reason)
    
    @app_commands.command(name="warnings", description="Voir les avertissements d'un membre")
    @app_commands.describe(member="Le membre dont voir les avertissements")
    @is_moderator()
    async def warnings(self, interaction: discord.Interaction, member: discord.Member):
        """Affiche les avertissements d'un membre"""
        warning_count = self.bot.config.get_warning_count(interaction.guild.id, member.id)
        
        embed = EmbedBuilder.info(
            "Avertissements",
            f"{member.mention} a **{warning_count}** avertissement(s)."
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="clearwarn", description="Effacer les avertissements d'un membre")
    @app_commands.describe(member="Le membre dont effacer les avertissements")
    @is_moderator()
    async def clearwarn(self, interaction: discord.Interaction, member: discord.Member):
        """Efface les avertissements d'un membre"""
        self.bot.config.clear_warnings(interaction.guild.id, member.id)
        
        embed = EmbedBuilder.success(
            "Avertissements effacés",
            f"Tous les avertissements de {member.mention} ont été effacés.",
            interaction.user
        )
        await interaction.response.send_message(embed=embed)
        
        # Log de l'action
        logs_channel = self._get_logs_channel(interaction.guild)
        if logs_channel:
            log_embed = EmbedBuilder.info(
                "Avertissements effacés",
                f"Les avertissements de {member.mention} ont été effacés par {interaction.user.mention}"
            )
            await logs_channel.send(embed=log_embed)
    
    @app_commands.command(name="slowmode", description="Activer/modifier le mode lent d'un canal")
    @app_commands.describe(
        seconds="Délai en secondes (0 pour désactiver, max 21600)",
        channel="Canal à modifier (optionnel)"
    )
    @is_moderator()
    @bot_has_permissions(manage_channels=True)
    async def slowmode(self, interaction: discord.Interaction, seconds: int, channel: Optional[discord.TextChannel] = None):
        """Active ou modifie le mode lent d'un canal"""
        if seconds < 0 or seconds > 21600:
            embed = EmbedBuilder.error("Valeur invalide", "Le délai doit être entre 0 et 21600 secondes (6 heures).")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        target_channel = channel or interaction.channel
        
        try:
            await target_channel.edit(slowmode_delay=seconds)
            
            if seconds == 0:
                embed = EmbedBuilder.success(
                    "Mode lent désactivé",
                    f"Le mode lent a été désactivé dans {target_channel.mention}.",
                    interaction.user
                )
            else:
                embed = EmbedBuilder.success(
                    "Mode lent activé",
                    f"Mode lent de **{seconds}** secondes activé dans {target_channel.mention}.",
                    interaction.user
                )
            
            await interaction.response.send_message(embed=embed)
            
            # Log de l'action
            await self._log_moderation(f"Mode lent ({seconds}s)", target_channel, interaction.user, f"Canal: {target_channel.mention}")
            
        except discord.Forbidden:
            embed = EmbedBuilder.error("Permission insuffisante", "Je n'ai pas les permissions pour modifier ce canal.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="lock", description="Verrouiller un canal")
    @app_commands.describe(
        channel="Canal à verrouiller (optionnel)",
        reason="Raison du verrouillage"
    )
    @is_moderator()
    @bot_has_permissions(manage_channels=True)
    async def lock(self, interaction: discord.Interaction, channel: Optional[discord.TextChannel] = None, reason: str = "Aucune raison spécifiée"):
        """Verrouille un canal"""
        target_channel = channel or interaction.channel
        
        try:
            # Retirer la permission d'envoyer des messages pour @everyone
            overwrite = target_channel.overwrites_for(interaction.guild.default_role)
            overwrite.send_messages = False
            await target_channel.set_permissions(interaction.guild.default_role, overwrite=overwrite, reason=f"Canal verrouillé par {interaction.user} - {reason}")
            
            embed = EmbedBuilder.warning(
                "Canal verrouillé",
                f"🔒 {target_channel.mention} a été verrouillé.\n**Raison:** {reason}",
                interaction.user
            )
            await interaction.response.send_message(embed=embed)
            
            # Message dans le canal verrouillé
            lock_embed = EmbedBuilder.warning(
                "Canal verrouillé",
                f"Ce canal a été verrouillé par {interaction.user.mention}.\n**Raison:** {reason}"
            )
            await target_channel.send(embed=lock_embed)
            
            # Log de l'action
            await self._log_moderation("Verrouillage de canal", target_channel, interaction.user, reason)
            
        except discord.Forbidden:
            embed = EmbedBuilder.error("Permission insuffisante", "Je n'ai pas les permissions pour modifier ce canal.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="unlock", description="Déverrouiller un canal")
    @app_commands.describe(
        channel="Canal à déverrouiller (optionnel)",
        reason="Raison du déverrouillage"
    )
    @is_moderator()
    @bot_has_permissions(manage_channels=True)
    async def unlock(self, interaction: discord.Interaction, channel: Optional[discord.TextChannel] = None, reason: str = "Aucune raison spécifiée"):
        """Déverrouille un canal"""
        target_channel = channel or interaction.channel
        
        try:
            # Restaurer la permission d'envoyer des messages pour @everyone
            overwrite = target_channel.overwrites_for(interaction.guild.default_role)
            overwrite.send_messages = None  # Remet à la valeur par défaut
            await target_channel.set_permissions(interaction.guild.default_role, overwrite=overwrite, reason=f"Canal déverrouillé par {interaction.user} - {reason}")
            
            embed = EmbedBuilder.success(
                "Canal déverrouillé",
                f"🔓 {target_channel.mention} a été déverrouillé.\n**Raison:** {reason}",
                interaction.user
            )
            await interaction.response.send_message(embed=embed)
            
            # Message dans le canal déverrouillé
            unlock_embed = EmbedBuilder.success(
                "Canal déverrouillé",
                f"Ce canal a été déverrouillé par {interaction.user.mention}.\n**Raison:** {reason}"
            )
            await target_channel.send(embed=unlock_embed)
            
            # Log de l'action
            await self._log_moderation("Déverrouillage de canal", target_channel, interaction.user, reason)
            
        except discord.Forbidden:
            embed = EmbedBuilder.error("Permission insuffisante", "Je n'ai pas les permissions pour modifier ce canal.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="nuke", description="Supprimer et recréer un canal")
    @app_commands.describe(
        channel="Canal à recréer (optionnel)",
        reason="Raison de la suppression"
    )
    @is_moderator()
    @bot_has_permissions(manage_channels=True)
    async def nuke(self, interaction: discord.Interaction, channel: Optional[discord.TextChannel] = None, reason: str = "Nettoyage du canal"):
        """Supprime et recrée un canal (nuke)"""
        target_channel = channel or interaction.channel
        
        # Demander confirmation
        embed = EmbedBuilder.warning(
            "Confirmation requise",
            f"Êtes-vous sûr de vouloir supprimer et recréer {target_channel.mention}?\n\n**⚠️ Tous les messages seront perdus!**"
        )
        
        view = ConfirmView(interaction.user)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        
        await view.wait()
        
        if view.value is None:
            embed = EmbedBuilder.error("Timeout", "Temps d'attente dépassé. Action annulée.")
            await interaction.edit_original_response(embed=embed, view=None)
            return
        elif not view.value:
            embed = EmbedBuilder.info("Action annulée", "La suppression du canal a été annulée.")
            await interaction.edit_original_response(embed=embed, view=None)
            return
        
        try:
            # Sauvegarder les informations du canal
            channel_name = target_channel.name
            channel_topic = target_channel.topic
            channel_category = target_channel.category
            channel_position = target_channel.position
            channel_overwrites = target_channel.overwrites
            
            # Supprimer le canal
            await target_channel.delete(reason=f"Nuke par {interaction.user} - {reason}")
            
            # Recréer le canal
            new_channel = await interaction.guild.create_text_channel(
                name=channel_name,
                topic=channel_topic,
                category=channel_category,
                position=channel_position,
                overwrites=channel_overwrites,
                reason=f"Recréé après nuke par {interaction.user}"
            )
            
            # Message de confirmation dans le nouveau canal
            nuke_embed = EmbedBuilder.success(
                "Canal recréé",
                f"💥 Ce canal a été nettoyé par {interaction.user.mention}.\n**Raison:** {reason}"
            )
            await new_channel.send(embed=nuke_embed)
            
            # Log de l'action
            logs_channel = self._get_logs_channel(interaction.guild)
            if logs_channel and logs_channel != new_channel:
                log_embed = EmbedBuilder.moderation("Nuke de canal", new_channel, interaction.user, reason)
                await logs_channel.send(embed=log_embed)
            
        except discord.Forbidden:
            embed = EmbedBuilder.error("Permission insuffisante", "Je n'ai pas les permissions pour supprimer/créer des canaux.")
            try:
                await interaction.edit_original_response(embed=embed, view=None)
            except:
                await interaction.followup.send(embed=embed, ephemeral=True)
    
    async def _log_moderation(self, action: str, target, moderator, reason: str):
        """Log une action de modération"""
        logs_channel = self._get_logs_channel(target.guild if hasattr(target, 'guild') else moderator.guild)
        if logs_channel:
            embed = EmbedBuilder.moderation(action, target, moderator, reason)
            await logs_channel.send(embed=embed)
    
    def _get_logs_channel(self, guild):
        """Récupère le canal de logs configuré"""
        logs_channel_id = self.bot.config.get_guild_setting(guild.id, 'logs_channel')
        if logs_channel_id:
            return guild.get_channel(logs_channel_id)
        return None

class ConfirmView(discord.ui.View):
    """Vue de confirmation pour les actions importantes"""
    
    def __init__(self, user):
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

async def setup(bot):
    await bot.add_cog(Moderation(bot))
