# 🤖 Bot Discord Français - Guide de Déploiement Render

## 📋 Configuration Render

### 1. Fichiers de Configuration Inclus

✅ **render_requirements.txt** - Dépendances Python pour Render  
✅ **Procfile** - Configuration de démarrage  
✅ **runtime.txt** - Version Python (3.11.0)  
✅ **render.yaml** - Configuration automatique Render  
✅ **main.py** - Point d'entrée optimisé pour Render  

### 2. Variables d'Environnement Requises

Sur Render, configurer la variable d'environnement suivante:

```
DISCORD_TOKEN=votre_token_discord_ici
```

### 3. Étapes de Déploiement

1. **Créer un compte Render** sur https://render.com
2. **Connecter votre repository** GitHub/GitLab
3. **Choisir "Web Service"** 
4. **Configuration automatique** avec render.yaml
5. **Ajouter le token Discord** dans les variables d'environnement
6. **Déployer**

### 4. Configuration Manuelle (Alternative)

Si vous préférez configurer manuellement sans render.yaml:

- **Build Command**: `pip install -r render_requirements.txt`
- **Start Command**: `python main.py`
- **Environment**: `Python 3`
- **Health Check Path**: `/health`
- **Port**: Le code gère automatiquement le port (PORT) de Render

### 5. Fonctionnalités du Bot

🛡️ **Modération Complète** - 15+ commandes de modération  
🚫 **Anti-Spam/Anti-Liens** - Protection automatique avec sanctions progressives  
📝 **Logs Complets** - Tous les événements du serveur en embeds Discord  
⚙️ **Panneau de Configuration** - Interface interactive avec `/panel`  
🎯 **30 Commandes Slash** - Entièrement en français  
🎨 **Statut Dynamique** - Personnalisable via `/setstatus`  

### 6. Commandes Principales

- `/panel` - Panneau de configuration interactif (Admin)
- `/help` - Liste complète des commandes
- `/config` - Voir la configuration actuelle
- `/kick`, `/ban`, `/mute` - Modération de base
- `/clear` - Supprimer des messages
- `/warn` - Avertir un membre

### 7. Support

Le bot est entièrement autonome et ne nécessite aucune interface web. Tous les logs sont dirigés vers stdout pour Render.

**Note**: Assurez-vous que votre bot Discord a les permissions nécessaires sur votre serveur (Administrateur recommandé).
