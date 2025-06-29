import discord
from discord.ext import commands
from typing import Union

def is_moderator():
    """Vérifie si l'utilisateur a les permissions de modération"""
    async def predicate(interaction: discord.Interaction) -> bool:
        if not isinstance(interaction.user, discord.Member):
            return False
        
        # Vérifier les permissions Discord
        if interaction.user.guild_permissions.manage_messages:
            return True
        
        # Vérifier le rôle de modérateur configuré
        bot_config = interaction.client.config
        mod_role_id = bot_config.get_guild_setting(interaction.guild.id, 'mod_role')
        
        if mod_role_id:
            mod_role = interaction.guild.get_role(mod_role_id)
            if mod_role and mod_role in interaction.user.roles:
                return True
        
        return False
    
    return discord.app_commands.check(predicate)

def is_admin():
    """Vérifie si l'utilisateur a les permissions d'administration"""
    async def predicate(interaction: discord.Interaction) -> bool:
        if not isinstance(interaction.user, discord.Member):
            return False
        
        return interaction.user.guild_permissions.administrator
    
    return discord.app_commands.check(predicate)

def bot_has_permissions(**perms):
    """Vérifie si le bot a les permissions nécessaires"""
    async def predicate(interaction: discord.Interaction) -> bool:
        if not interaction.guild:
            return False
        
        bot_member = interaction.guild.get_member(interaction.client.user.id)
        if not bot_member:
            return False
        
        bot_perms = bot_member.guild_permissions
        
        for perm, value in perms.items():
            if getattr(bot_perms, perm) != value:
                return False
        
        return True
    
    return discord.app_commands.check(predicate)

async def can_moderate_member(moderator: discord.Member, target: discord.Member) -> bool:
    """Vérifie si un modérateur peut modérer un membre"""
    # Ne peut pas se modérer soi-même
    if moderator.id == target.id:
        return False
    
    # Ne peut pas modérer le propriétaire du serveur
    if target.id == target.guild.owner_id:
        return False
    
    # Vérifier la hiérarchie des rôles
    if moderator.top_role <= target.top_role and moderator.id != target.guild.owner_id:
        return False
    
    return True

async def get_mute_role(guild: discord.Guild, bot_config) -> Union[discord.Role, None]:
    """Récupère ou crée le rôle de mute"""
    # Vérifier si un rôle de mute est configuré
    mute_role_id = bot_config.get_guild_setting(guild.id, 'mute_role')
    
    if mute_role_id:
        mute_role = guild.get_role(mute_role_id)
        if mute_role:
            return mute_role
    
    # Chercher un rôle "Muted" existant
    for role in guild.roles:
        if role.name.lower() in ['muted', 'muet', 'silence']:
            bot_config.set_guild_setting(guild.id, 'mute_role', role.id)
            return role
    
    # Créer un nouveau rôle de mute
    try:
        mute_role = await guild.create_role(
            name="Muted",
            color=discord.Color.dark_grey(),
            reason="Création automatique du rôle de mute"
        )
        
        # Configurer les permissions pour tous les canaux
        for channel in guild.channels:
            try:
                if isinstance(channel, discord.TextChannel):
                    await channel.set_permissions(
                        mute_role,
                        send_messages=False,
                        add_reactions=False,
                        reason="Configuration du rôle de mute"
                    )
                elif isinstance(channel, discord.VoiceChannel):
                    await channel.set_permissions(
                        mute_role,
                        speak=False,
                        reason="Configuration du rôle de mute"
                    )
            except discord.Forbidden:
                continue
        
        bot_config.set_guild_setting(guild.id, 'mute_role', mute_role.id)
        return mute_role
    
    except discord.Forbidden:
        return None
