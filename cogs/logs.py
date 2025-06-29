import discord
from discord.ext import commands
from utils.embeds import EmbedBuilder
from config.settings import Colors

class Logs(commands.Cog):
    """Module de logs complet pour toutes les activités du serveur"""
    
    def __init__(self, bot):
        self.bot = bot
    
    def _get_logs_channel(self, guild):
        """Récupère le canal de logs configuré"""
        logs_channel_id = self.bot.config.get_guild_setting(guild.id, 'logs_channel')
        if logs_channel_id:
            return guild.get_channel(logs_channel_id)
        return None
    
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        """Log des messages supprimés"""
        if message.author.bot:
            return
        
        logs_channel = self._get_logs_channel(message.guild)
        if not logs_channel:
            return
        
        embed = EmbedBuilder.message_delete(message)
        try:
            await logs_channel.send(embed=embed)
        except discord.Forbidden:
            pass
    
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        """Log des messages édités"""
        if before.author.bot or before.content == after.content:
            return
        
        logs_channel = self._get_logs_channel(before.guild)
        if not logs_channel:
            return
        
        embed = EmbedBuilder.message_edit(before, after)
        try:
            await logs_channel.send(embed=embed)
        except discord.Forbidden:
            pass
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Log des arrivées de membres"""
        logs_channel = self._get_logs_channel(member.guild)
        if not logs_channel:
            return
        
        embed = EmbedBuilder.member_join(member)
        try:
            await logs_channel.send(embed=embed)
        except discord.Forbidden:
            pass
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """Log des départs de membres"""
        logs_channel = self._get_logs_channel(member.guild)
        if not logs_channel:
            return
        
        embed = EmbedBuilder.member_leave(member)
        try:
            await logs_channel.send(embed=embed)
        except discord.Forbidden:
            pass
    
    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        """Log des bannissements (si pas fait par le bot)"""
        logs_channel = self._get_logs_channel(guild)
        if not logs_channel:
            return
        
        embed = discord.Embed(
            title="🔨 Membre Banni",
            color=Colors.BAN,
            timestamp=discord.utils.utcnow()
        )
        
        embed.add_field(name="👤 Utilisateur", value=f"{user.mention}\n`{user}`", inline=True)
        embed.add_field(name="📅 Banni le", value=f"<t:{int(discord.utils.utcnow().timestamp())}:F>", inline=True)
        
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_footer(text=f"ID: {user.id}")
        
        try:
            await logs_channel.send(embed=embed)
        except discord.Forbidden:
            pass
    
    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        """Log des débannissements"""
        logs_channel = self._get_logs_channel(guild)
        if not logs_channel:
            return
        
        embed = discord.Embed(
            title="✅ Membre Débanni",
            color=Colors.SUCCESS,
            timestamp=discord.utils.utcnow()
        )
        
        embed.add_field(name="👤 Utilisateur", value=f"{user.mention}\n`{user}`", inline=True)
        embed.add_field(name="📅 Débanni le", value=f"<t:{int(discord.utils.utcnow().timestamp())}:F>", inline=True)
        
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_footer(text=f"ID: {user.id}")
        
        try:
            await logs_channel.send(embed=embed)
        except discord.Forbidden:
            pass
    
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        """Log de création de canaux"""
        logs_channel = self._get_logs_channel(channel.guild)
        if not logs_channel or logs_channel == channel:
            return
        
        embed = discord.Embed(
            title="📝 Canal Créé",
            color=Colors.SUCCESS,
            timestamp=discord.utils.utcnow()
        )
        
        channel_type = "Vocal" if isinstance(channel, discord.VoiceChannel) else "Textuel"
        embed.add_field(name="📍 Canal", value=f"{channel.mention}\n`{channel.name}`", inline=True)
        embed.add_field(name="🏷️ Type", value=channel_type, inline=True)
        embed.add_field(name="🆔 ID", value=str(channel.id), inline=True)
        
        try:
            await logs_channel.send(embed=embed)
        except discord.Forbidden:
            pass
    
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        """Log de suppression de canaux"""
        logs_channel = self._get_logs_channel(channel.guild)
        if not logs_channel:
            return
        
        embed = discord.Embed(
            title="🗑️ Canal Supprimé",
            color=Colors.DELETE,
            timestamp=discord.utils.utcnow()
        )
        
        channel_type = "Vocal" if isinstance(channel, discord.VoiceChannel) else "Textuel"
        embed.add_field(name="📍 Canal", value=f"`{channel.name}`", inline=True)
        embed.add_field(name="🏷️ Type", value=channel_type, inline=True)
        embed.add_field(name="🆔 ID", value=str(channel.id), inline=True)
        
        try:
            await logs_channel.send(embed=embed)
        except discord.Forbidden:
            pass
    
    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after):
        """Log de modification de canaux"""
        logs_channel = self._get_logs_channel(after.guild)
        if not logs_channel:
            return
        
        changes = []
        
        if before.name != after.name:
            changes.append(f"**Nom:** `{before.name}` → `{after.name}`")
        
        if hasattr(before, 'topic') and before.topic != after.topic:
            before_topic = before.topic or "*Aucun*"
            after_topic = after.topic or "*Aucun*"
            changes.append(f"**Sujet:** `{before_topic}` → `{after_topic}`")
        
        if not changes:
            return
        
        embed = discord.Embed(
            title="✏️ Canal Modifié",
            color=Colors.EDIT,
            timestamp=discord.utils.utcnow()
        )
        
        embed.add_field(name="📍 Canal", value=after.mention, inline=True)
        embed.add_field(name="🔄 Modifications", value="\n".join(changes), inline=False)
        
        try:
            await logs_channel.send(embed=embed)
        except discord.Forbidden:
            pass
    
    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        """Log de création de rôles"""
        logs_channel = self._get_logs_channel(role.guild)
        if not logs_channel:
            return
        
        embed = discord.Embed(
            title="🎭 Rôle Créé",
            color=Colors.SUCCESS,
            timestamp=discord.utils.utcnow()
        )
        
        embed.add_field(name="🏷️ Rôle", value=f"{role.mention}\n`{role.name}`", inline=True)
        embed.add_field(name="🎨 Couleur", value=str(role.color), inline=True)
        embed.add_field(name="🆔 ID", value=str(role.id), inline=True)
        
        try:
            await logs_channel.send(embed=embed)
        except discord.Forbidden:
            pass
    
    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        """Log de suppression de rôles"""
        logs_channel = self._get_logs_channel(role.guild)
        if not logs_channel:
            return
        
        embed = discord.Embed(
            title="🗑️ Rôle Supprimé",
            color=Colors.DELETE,
            timestamp=discord.utils.utcnow()
        )
        
        embed.add_field(name="🏷️ Rôle", value=f"`{role.name}`", inline=True)
        embed.add_field(name="🎨 Couleur", value=str(role.color), inline=True)
        embed.add_field(name="🆔 ID", value=str(role.id), inline=True)
        
        try:
            await logs_channel.send(embed=embed)
        except discord.Forbidden:
            pass
    
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        """Log des modifications de membres (rôles, pseudo, etc.)"""
        logs_channel = self._get_logs_channel(after.guild)
        if not logs_channel:
            return
        
        changes = []
        
        # Changement de pseudo
        if before.display_name != after.display_name:
            changes.append(f"**Pseudo:** `{before.display_name}` → `{after.display_name}`")
        
        # Changement de rôles
        if before.roles != after.roles:
            added_roles = set(after.roles) - set(before.roles)
            removed_roles = set(before.roles) - set(after.roles)
            
            if added_roles:
                roles_list = ", ".join([role.mention for role in added_roles])
                changes.append(f"**Rôles ajoutés:** {roles_list}")
            
            if removed_roles:
                roles_list = ", ".join([role.name for role in removed_roles])
                changes.append(f"**Rôles supprimés:** {roles_list}")
        
        if not changes:
            return
        
        embed = discord.Embed(
            title="👤 Membre Modifié",
            color=Colors.EDIT,
            timestamp=discord.utils.utcnow()
        )
        
        embed.add_field(name="👤 Membre", value=f"{after.mention}\n`{after}`", inline=True)
        embed.add_field(name="🔄 Modifications", value="\n".join(changes), inline=False)
        
        embed.set_thumbnail(url=after.display_avatar.url)
        embed.set_footer(text=f"ID: {after.id}")
        
        try:
            await logs_channel.send(embed=embed)
        except discord.Forbidden:
            pass
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """Log des activités vocales"""
        logs_channel = self._get_logs_channel(member.guild)
        if not logs_channel:
            return
        
        # Rejoindre un canal vocal
        if before.channel is None and after.channel is not None:
            embed = discord.Embed(
                title="🔊 Connexion Vocale",
                color=Colors.JOIN,
                timestamp=discord.utils.utcnow()
            )
            embed.add_field(name="👤 Membre", value=f"{member.mention}\n`{member}`", inline=True)
            embed.add_field(name="📍 Canal", value=after.channel.mention, inline=True)
            embed.set_thumbnail(url=member.display_avatar.url)
            
        # Quitter un canal vocal
        elif before.channel is not None and after.channel is None:
            embed = discord.Embed(
                title="🔇 Déconnexion Vocale",
                color=Colors.LEAVE,
                timestamp=discord.utils.utcnow()
            )
            embed.add_field(name="👤 Membre", value=f"{member.mention}\n`{member}`", inline=True)
            embed.add_field(name="📍 Canal", value=before.channel.mention, inline=True)
            embed.set_thumbnail(url=member.display_avatar.url)
            
        # Changer de canal vocal
        elif before.channel != after.channel and before.channel is not None and after.channel is not None:
            embed = discord.Embed(
                title="🔄 Changement de Canal Vocal",
                color=Colors.EDIT,
                timestamp=discord.utils.utcnow()
            )
            embed.add_field(name="👤 Membre", value=f"{member.mention}\n`{member}`", inline=True)
            embed.add_field(name="📍 De", value=before.channel.mention, inline=True)
            embed.add_field(name="📍 Vers", value=after.channel.mention, inline=True)
            embed.set_thumbnail(url=member.display_avatar.url)
        else:
            return
        
        try:
            await logs_channel.send(embed=embed)
        except discord.Forbidden:
            pass

async def setup(bot):
    await bot.add_cog(Logs(bot))
