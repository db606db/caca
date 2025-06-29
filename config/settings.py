import discord
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

class BotConfig:
    def __init__(self):
        # Configuration des serveurs (en mémoire pour le MVP)
        self.guilds_config: Dict[int, Dict[str, Any]] = {}
        
        # Configuration par défaut
        self.default_config = {
            'logs_channel': None,
            'mod_role': None,
            'mute_role': None,
            'auto_mod': {
                'anti_spam': True,
                'anti_links': True,
                'max_mentions': 5,
                'message_limit': 5,
                'time_window': 10  # secondes
            },
            'status': {
                'type': 'watching',
                'text': '🛡️ Protéger le serveur'
            }
        }
        
        # Cache des infractions (anti-spam)
        self.user_messages: Dict[int, Dict[int, list]] = {}  # guild_id -> user_id -> messages
        self.user_warnings: Dict[int, Dict[int, int]] = {}  # guild_id -> user_id -> count
    
    def get_guild_config(self, guild_id: int) -> Dict[str, Any]:
        """Récupère la configuration d'un serveur"""
        if guild_id not in self.guilds_config:
            self.guilds_config[guild_id] = self.default_config.copy()
        return self.guilds_config[guild_id]
    
    def set_guild_setting(self, guild_id: int, key: str, value: Any) -> None:
        """Définit un paramètre pour un serveur"""
        config = self.get_guild_config(guild_id)
        keys = key.split('.')
        
        current = config
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        current[keys[-1]] = value
    
    def get_guild_setting(self, guild_id: int, key: str, default=None):
        """Récupère un paramètre d'un serveur"""
        config = self.get_guild_config(guild_id)
        keys = key.split('.')
        
        current = config
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return default
        
        return current
    
    def add_user_message(self, guild_id: int, user_id: int, timestamp: datetime) -> None:
        """Ajoute un message à l'historique d'un utilisateur"""
        if guild_id not in self.user_messages:
            self.user_messages[guild_id] = {}
        if user_id not in self.user_messages[guild_id]:
            self.user_messages[guild_id][user_id] = []
        
        # Ajouter le timestamp et nettoyer les anciens messages
        messages = self.user_messages[guild_id][user_id]
        messages.append(timestamp)
        
        # Supprimer les messages de plus de 10 secondes
        cutoff = timestamp - timedelta(seconds=10)
        self.user_messages[guild_id][user_id] = [
            msg for msg in messages if msg > cutoff
        ]
    
    def get_user_message_count(self, guild_id: int, user_id: int) -> int:
        """Récupère le nombre de messages récents d'un utilisateur"""
        if guild_id not in self.user_messages:
            return 0
        if user_id not in self.user_messages[guild_id]:
            return 0
        return len(self.user_messages[guild_id][user_id])
    
    def add_warning(self, guild_id: int, user_id: int) -> int:
        """Ajoute un avertissement à un utilisateur"""
        if guild_id not in self.user_warnings:
            self.user_warnings[guild_id] = {}
        if user_id not in self.user_warnings[guild_id]:
            self.user_warnings[guild_id][user_id] = 0
        
        self.user_warnings[guild_id][user_id] += 1
        return self.user_warnings[guild_id][user_id]
    
    def get_warning_count(self, guild_id: int, user_id: int) -> int:
        """Récupère le nombre d'avertissements d'un utilisateur"""
        if guild_id not in self.user_warnings:
            return 0
        return self.user_warnings[guild_id].get(user_id, 0)
    
    def clear_warnings(self, guild_id: int, user_id: int) -> None:
        """Efface les avertissements d'un utilisateur"""
        if guild_id in self.user_warnings and user_id in self.user_warnings[guild_id]:
            del self.user_warnings[guild_id][user_id]

# Couleurs pour les embeds
class Colors:
    SUCCESS = 0x00ff00    # Vert
    ERROR = 0xff0000      # Rouge
    WARNING = 0xffa500    # Orange
    INFO = 0x0099ff       # Bleu
    MODERATION = 0xff6b35 # Orange-rouge
    LOGS = 0x36393f       # Gris Discord
    DELETE = 0xe74c3c     # Rouge foncé
    EDIT = 0xf39c12       # Orange
    JOIN = 0x2ecc71       # Vert
    LEAVE = 0xe67e22      # Orange foncé
    BAN = 0x992d22        # Rouge très foncé
    KICK = 0xc0392b       # Rouge
    MUTE = 0x95a5a6       # Gris
