import discord
from datetime import datetime
from config.settings import Colors

class EmbedBuilder:
    """Constructeur d'embeds pour une présentation uniforme"""
    
    @staticmethod
    def success(title: str, description: str = "", user: discord.Member = None) -> discord.Embed:
        """Embed de succès"""
        embed = discord.Embed(
            title=f"✅ {title}",
            description=description,
            color=Colors.SUCCESS,
            timestamp=datetime.utcnow()
        )
        if user:
            embed.set_footer(text=f"Par {user.display_name}", icon_url=user.display_avatar.url)
        return embed
    
    @staticmethod
    def error(title: str, description: str = "", user: discord.Member = None) -> discord.Embed:
        """Embed d'erreur"""
        embed = discord.Embed(
            title=f"❌ {title}",
            description=description,
            color=Colors.ERROR,
            timestamp=datetime.utcnow()
        )
        if user:
            embed.set_footer(text=f"Par {user.display_name}", icon_url=user.display_avatar.url)
        return embed
    
    @staticmethod
    def warning(title: str, description: str = "", user: discord.Member = None) -> discord.Embed:
        """Embed d'avertissement"""
        embed = discord.Embed(
            title=f"⚠️ {title}",
            description=description,
            color=Colors.WARNING,
            timestamp=datetime.utcnow()
        )
        if user:
            embed.set_footer(text=f"Par {user.display_name}", icon_url=user.display_avatar.url)
        return embed
    
    @staticmethod
    def info(title: str, description: str = "", user: discord.Member = None) -> discord.Embed:
        """Embed d'information"""
        embed = discord.Embed(
            title=f"ℹ️ {title}",
            description=description,
            color=Colors.INFO,
            timestamp=datetime.utcnow()
        )
        if user:
            embed.set_footer(text=f"Par {user.display_name}", icon_url=user.display_avatar.url)
        return embed
    
    @staticmethod
    def moderation(action: str, target: discord.Member, moderator: discord.Member, 
                  reason: str = "Aucune raison spécifiée") -> discord.Embed:
        """Embed pour les actions de modération"""
        embed = discord.Embed(
            title=f"🔨 {action}",
            color=Colors.MODERATION,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="👤 Utilisateur", value=f"{target.mention}\n`{target}`", inline=True)
        embed.add_field(name="👮 Modérateur", value=f"{moderator.mention}\n`{moderator}`", inline=True)
        embed.add_field(name="📝 Raison", value=reason, inline=False)
        
        embed.set_thumbnail(url=target.display_avatar.url)
        embed.set_footer(text=f"ID: {target.id}")
        
        return embed
    
    @staticmethod
    def message_delete(message: discord.Message) -> discord.Embed:
        """Embed pour message supprimé"""
        embed = discord.Embed(
            title="🗑️ Message Supprimé",
            color=Colors.DELETE,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="👤 Auteur", value=f"{message.author.mention}\n`{message.author}`", inline=True)
        embed.add_field(name="📍 Canal", value=message.channel.mention, inline=True)
        embed.add_field(name="📝 Contenu", value=message.content[:1024] if message.content else "*Aucun contenu texte*", inline=False)
        
        if message.attachments:
            attachments = "\n".join([f"📎 {att.filename}" for att in message.attachments])
            embed.add_field(name="📁 Pièces jointes", value=attachments, inline=False)
        
        embed.set_thumbnail(url=message.author.display_avatar.url)
        embed.set_footer(text=f"ID Message: {message.id} | ID Auteur: {message.author.id}")
        
        return embed
    
    @staticmethod
    def message_edit(before: discord.Message, after: discord.Message) -> discord.Embed:
        """Embed pour message édité"""
        embed = discord.Embed(
            title="✏️ Message Édité",
            color=Colors.EDIT,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="👤 Auteur", value=f"{after.author.mention}\n`{after.author}`", inline=True)
        embed.add_field(name="📍 Canal", value=after.channel.mention, inline=True)
        embed.add_field(name="📝 Avant", value=before.content[:512] if before.content else "*Aucun contenu*", inline=False)
        embed.add_field(name="📝 Après", value=after.content[:512] if after.content else "*Aucun contenu*", inline=False)
        
        embed.set_thumbnail(url=after.author.display_avatar.url)
        embed.set_footer(text=f"ID Message: {after.id} | ID Auteur: {after.author.id}")
        
        return embed
    
    @staticmethod
    def member_join(member: discord.Member) -> discord.Embed:
        """Embed pour arrivée de membre"""
        embed = discord.Embed(
            title="👋 Nouveau Membre",
            description=f"{member.mention} a rejoint le serveur!",
            color=Colors.JOIN,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="👤 Utilisateur", value=f"`{member}`", inline=True)
        embed.add_field(name="📅 Compte créé", value=f"<t:{int(member.created_at.timestamp())}:R>", inline=True)
        embed.add_field(name="👥 Nombre de membres", value=str(member.guild.member_count), inline=True)
        
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"ID: {member.id}")
        
        return embed
    
    @staticmethod
    def member_leave(member: discord.Member) -> discord.Embed:
        """Embed pour départ de membre"""
        embed = discord.Embed(
            title="👋 Membre Parti",
            description=f"{member.mention} a quitté le serveur.",
            color=Colors.LEAVE,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="👤 Utilisateur", value=f"`{member}`", inline=True)
        embed.add_field(name="📅 A rejoint", value=f"<t:{int(member.joined_at.timestamp())}:R>" if member.joined_at else "Inconnu", inline=True)
        embed.add_field(name="👥 Nombre de membres", value=str(member.guild.member_count), inline=True)
        
        # Afficher les rôles qu'il avait
        if len(member.roles) > 1:  # Exclut @everyone
            roles = ", ".join([role.name for role in member.roles[1:]])
            embed.add_field(name="🎭 Rôles", value=roles[:1024], inline=False)
        
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"ID: {member.id}")
        
        return embed
    
    @staticmethod
    def auto_moderation(action: str, user: discord.Member, reason: str, details: str = "") -> discord.Embed:
        """Embed pour actions de modération automatique"""
        embed = discord.Embed(
            title=f"🤖 Modération Automatique - {action}",
            color=Colors.WARNING,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="👤 Utilisateur", value=f"{user.mention}\n`{user}`", inline=True)
        embed.add_field(name="⚡ Action", value=action, inline=True)
        embed.add_field(name="📝 Raison", value=reason, inline=False)
        
        if details:
            embed.add_field(name="🔍 Détails", value=details, inline=False)
        
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_footer(text=f"ID: {user.id}")
        
        return embed
