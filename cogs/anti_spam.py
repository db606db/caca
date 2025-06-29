import discord
from discord.ext import commands
from utils.embeds import EmbedBuilder
from datetime import datetime
import re
from typing import List

class AntiSpam(commands.Cog):
    """Module de protection anti-spam et anti-liens"""
    
    def __init__(self, bot):
        self.bot = bot
        
        # Patterns pour détecter les liens
        self.url_patterns = [
            re.compile(r'https?://(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?)?'),
            re.compile(r'www\.(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?)?'),
            re.compile(r'(?:discord\.gg|discordapp\.com/invite)/[a-zA-Z0-9]+'),
            re.compile(r'[a-zA-Z0-9-]+\.(?:com|net|org|fr|be|ca|uk|de|es|it|pl|ru|jp|br|mx|au|nl|se|no|dk|fi|ch|at|pt|gr|cz|hu|bg|ro|hr|sk|si|ee|lv|lt|ie|lu|mt|cy)(?:/[^\s]*)?')
        ]
        
        # Domaines autorisés par défaut
        self.allowed_domains = [
            'youtube.com', 'youtu.be', 'twitter.com', 'twitch.tv', 
            'github.com', 'stackoverflow.com', 'reddit.com'
        ]
    
    def _get_logs_channel(self, guild):
        """Récupère le canal de logs configuré"""
        logs_channel_id = self.bot.config.get_guild_setting(guild.id, 'logs_channel')
        if logs_channel_id:
            return guild.get_channel(logs_channel_id)
        return None
    
    def _is_moderator(self, member: discord.Member) -> bool:
        """Vérifie si un membre est modérateur"""
        if member.guild_permissions.manage_messages:
            return True
        
        mod_role_id = self.bot.config.get_guild_setting(member.guild.id, 'mod_role')
        if mod_role_id:
            mod_role = member.guild.get_role(mod_role_id)
            if mod_role and mod_role in member.roles:
                return True
        
        return False
    
    def _contains_links(self, content: str) -> List[str]:
        """Détecte les liens dans un message"""
        found_links = []
        
        for pattern in self.url_patterns:
            matches = pattern.findall(content.lower())
            found_links.extend(matches)
        
        return found_links
    
    def _is_allowed_domain(self, url: str) -> bool:
        """Vérifie si un domaine est autorisé"""
        url_lower = url.lower()
        for domain in self.allowed_domains:
            if domain in url_lower:
                return True
        return False
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Vérification anti-spam et anti-liens sur chaque message"""
        # Ignorer les bots et les MPs
        if message.author.bot or not message.guild:
            return
        
        # Ignorer les modérateurs
        if self._is_moderator(message.author):
            return
        
        guild_config = self.bot.config.get_guild_config(message.guild.id)
        auto_mod = guild_config.get('auto_mod', {})
        
        # Vérification anti-spam
        if auto_mod.get('anti_spam', True):
            await self._check_spam(message, auto_mod)
        
        # Vérification anti-liens
        if auto_mod.get('anti_links', True):
            await self._check_links(message)
        
        # Vérification du nombre de mentions
        await self._check_mentions(message, auto_mod)
    
    async def _check_spam(self, message, auto_mod_config):
        """Vérifie le spam de messages"""
        message_limit = auto_mod_config.get('message_limit', 5)
        
        # Ajouter le message à l'historique
        self.bot.config.add_user_message(message.guild.id, message.author.id, datetime.utcnow())
        
        # Vérifier le nombre de messages récents
        message_count = self.bot.config.get_user_message_count(message.guild.id, message.author.id)
        
        if message_count >= message_limit:
            await self._handle_spam_violation(message, "Trop de messages envoyés rapidement")
    
    async def _check_links(self, message):
        """Vérifie les liens dans les messages"""
        links = self._contains_links(message.content)
        
        if links:
            # Vérifier si au moins un lien n'est pas autorisé
            forbidden_links = []
            for link in links:
                if not self._is_allowed_domain(link):
                    forbidden_links.append(link)
            
            if forbidden_links:
                await self._handle_link_violation(message, forbidden_links)
    
    async def _check_mentions(self, message, auto_mod_config):
        """Vérifie le nombre de mentions"""
        max_mentions = auto_mod_config.get('max_mentions', 5)
        
        # Compter les mentions uniques (utilisateurs + rôles)
        unique_mentions = set()
        unique_mentions.update([user.id for user in message.mentions])
        unique_mentions.update([role.id for role in message.role_mentions])
        
        if len(unique_mentions) > max_mentions:
            await self._handle_mention_violation(message, len(unique_mentions), max_mentions)
    
    async def _handle_spam_violation(self, message, reason):
        """Gère les violations de spam"""
        try:
            # Supprimer le message
            await message.delete()
            
            # Ajouter un avertissement
            warning_count = self.bot.config.add_warning(message.guild.id, message.author.id)
            
            # Sanctions progressives basées sur le nombre d'avertissements
            action_taken = await self._apply_progressive_punishment(message.author, warning_count, reason)
            
            # Log de l'action
            logs_channel = self._get_logs_channel(message.guild)
            if logs_channel:
                embed = EmbedBuilder.auto_moderation(
                    action_taken,
                    message.author,
                    reason,
                    f"Message supprimé dans {message.channel.mention}\nContenu: {message.content[:200]}..."
                )
                await logs_channel.send(embed=embed)
            
            # Envoyer un message de notification temporaire
            warning_embed = EmbedBuilder.warning(
                "Message supprimé",
                f"{message.author.mention}, votre message a été supprimé pour: **{reason}**\n"
                f"Avertissements: **{warning_count}**/5"
            )
            warning_msg = await message.channel.send(embed=warning_embed)
            
            # Supprimer le message d'avertissement après 5 secondes
            await warning_msg.delete(delay=5)
            
        except discord.NotFound:
            pass  # Message déjà supprimé
        except discord.Forbidden:
            pass  # Pas de permissions
    
    async def _handle_link_violation(self, message, forbidden_links):
        """Gère les violations de liens"""
        try:
            await message.delete()
            
            warning_count = self.bot.config.add_warning(message.guild.id, message.author.id)
            action_taken = await self._apply_progressive_punishment(
                message.author, 
                warning_count, 
                "Lien non autorisé"
            )
            
            # Log de l'action
            logs_channel = self._get_logs_channel(message.guild)
            if logs_channel:
                embed = EmbedBuilder.auto_moderation(
                    action_taken,
                    message.author,
                    "Lien non autorisé détecté",
                    f"Liens trouvés: {', '.join(forbidden_links[:3])}"
                )
                await logs_channel.send(embed=embed)
            
            # Message de notification
            warning_embed = EmbedBuilder.warning(
                "Lien supprimé",
                f"{message.author.mention}, votre message contenant un lien non autorisé a été supprimé.\n"
                f"Avertissements: **{warning_count}**/5"
            )
            warning_msg = await message.channel.send(embed=warning_embed)
            await warning_msg.delete(delay=5)
            
        except discord.NotFound:
            pass
        except discord.Forbidden:
            pass
    
    async def _handle_mention_violation(self, message, mention_count, max_mentions):
        """Gère les violations de mentions excessives"""
        try:
            await message.delete()
            
            warning_count = self.bot.config.add_warning(message.guild.id, message.author.id)
            action_taken = await self._apply_progressive_punishment(
                message.author, 
                warning_count, 
                f"Trop de mentions ({mention_count}/{max_mentions})"
            )
            
            # Log de l'action
            logs_channel = self._get_logs_channel(message.guild)
            if logs_channel:
                embed = EmbedBuilder.auto_moderation(
                    action_taken,
                    message.author,
                    f"Mentions excessives ({mention_count}/{max_mentions})",
                    f"Message dans {message.channel.mention}"
                )
                await logs_channel.send(embed=embed)
            
            # Message de notification
            warning_embed = EmbedBuilder.warning(
                "Trop de mentions",
                f"{message.author.mention}, votre message avec trop de mentions a été supprimé.\n"
                f"Limite: **{max_mentions}** mentions par message\n"
                f"Avertissements: **{warning_count}**/5"
            )
            warning_msg = await message.channel.send(embed=warning_embed)
            await warning_msg.delete(delay=5)
            
        except discord.NotFound:
            pass
        except discord.Forbidden:
            pass
    
    async def _apply_progressive_punishment(self, member: discord.Member, warning_count: int, reason: str) -> str:
        """Applique des sanctions progressives basées sur le nombre d'avertissements"""
        try:
            if warning_count >= 5:
                # 5+ avertissements = bannissement
                await member.ban(reason=f"Auto-modération: {reason} (5+ avertissements)")
                return "Bannissement automatique"
            
            elif warning_count >= 4:
                # 4 avertissements = kick
                await member.kick(reason=f"Auto-modération: {reason} (4 avertissements)")
                return "Expulsion automatique"
            
            elif warning_count >= 3:
                # 3 avertissements = timeout 1 heure
                from datetime import timedelta
                until = datetime.utcnow() + timedelta(hours=1)
                await member.timeout(until, reason=f"Auto-modération: {reason} (3 avertissements)")
                return "Timeout 1h automatique"
            
            elif warning_count >= 2:
                # 2 avertissements = mute 10 minutes
                from utils.checks import get_mute_role
                mute_role = await get_mute_role(member.guild, self.bot.config)
                if mute_role:
                    await member.add_roles(mute_role, reason=f"Auto-modération: {reason} (2 avertissements)")
                    
                    # Programmer le démute automatique
                    import asyncio
                    async def auto_unmute():
                        await asyncio.sleep(600)  # 10 minutes
                        if mute_role in member.roles:
                            await member.remove_roles(mute_role, reason="Fin du mute automatique")
                    
                    asyncio.create_task(auto_unmute())
                    return "Mute 10min automatique"
                else:
                    return "Avertissement (mute non disponible)"
            
            else:
                # 1 avertissement = simple avertissement
                return "Avertissement automatique"
        
        except discord.Forbidden:
            return "Avertissement (permissions insuffisantes)"
        except Exception:
            return "Avertissement (erreur technique)"

async def setup(bot):
    await bot.add_cog(AntiSpam(bot))
