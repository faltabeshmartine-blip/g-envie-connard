import pymumble
from pymumble.callbacks import PYMUMBLE_CLBK_USERCREATED
import time
import threading
import os

# Configuration depuis les variables d'environnement
MUMBLE_HOST = os.getenv('MUMBLE_HOST', 'nocturniaffa.mumble.gg')
MUMBLE_PORT = int(os.getenv('MUMBLE_PORT', 10009))
BOT_NAME = os.getenv('BOT_NAME', 'ServerAdmin')
BOT_PASSWORD = os.getenv('BOT_PASSWORD', '')
MUTE_DURATION = int(os.getenv('MUTE_DURATION', 5))  # Durée en secondes

class AutoMuteBot:
    def __init__(self):
        print(f"🤖 Démarrage du bot {BOT_NAME}...")
        print(f"📡 Connexion à {MUMBLE_HOST}:{MUMBLE_PORT}")
        
        self.mumble = pymumble.Mumble(
            MUMBLE_HOST, 
            BOT_NAME, 
            port=MUMBLE_PORT, 
            password=BOT_PASSWORD,
            reconnect=True  # Reconnexion auto si déconnexion
        )
        
        # Configure le callback pour les nouveaux utilisateurs
        self.mumble.callbacks.set_callback(PYMUMBLE_CLBK_USERCREATED, self.on_user_connected)
        
        # Désactive la réception audio (économie de bande passante)
        self.mumble.set_receive_sound(False)
        
        # Démarre la connexion
        self.mumble.start()
        self.mumble.is_ready()
        
        print(f"✅ Bot connecté avec succès!")
        print(f"⏱️  Durée du mute automatique: {MUTE_DURATION} secondes")
    
    def on_user_connected(self, user):
        """Callback déclenché quand un utilisateur se connecte"""
        user_name = user.get('name', 'Inconnu')
        
        # Ignore le bot lui-même
        if user_name == BOT_NAME:
            return
        
        print(f"👤 Nouvel utilisateur détecté: {user_name}")
        
        # Lance le mute temporaire dans un thread séparé
        thread = threading.Thread(target=self.temp_mute, args=(user['session'], user_name))
        thread.daemon = True  # Le thread se ferme avec le programme
        thread.start()
    
    def temp_mute(self, session_id, user_name):
        """Mute un utilisateur pendant X secondes"""
        try:
            # Récupère l'utilisateur
            user = self.mumble.users.get(session_id)
            
            if not user:
                print(f"⚠️  Utilisateur {user_name} introuvable")
                return
            
            # Applique le mute
            user.mute()
            print(f"🔇 {user_name} a été mute pour {MUTE_DURATION} secondes")
            
            # Attend la durée configurée
            time.sleep(MUTE_DURATION)
            
            # Vérifie si l'utilisateur est toujours connecté
            if session_id in self.mumble.users:
                user.unmute()
                print(f"🔊 {user_name} a été unmute")
            else:
                print(f"⚠️  {user_name} s'est déconnecté avant la fin du mute")
            
        except Exception as e:
            print(f"❌ Erreur lors du mute de {user_name}: {e}")
    
    def run(self):
        """Garde le bot actif indéfiniment"""
        print("🟢 Bot en écoute... (Ctrl+C pour arrêter)")
        try:
            while self.mumble.is_alive():
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n⏹️  Arrêt du bot...")
            self.mumble.stop()
            print("👋 Bot arrêté proprement")

if __name__ == "__main__":
    try:
        bot = AutoMuteBot()
        bot.run()
    except Exception as e:
        print(f"💥 Erreur fatale: {e}")
        raise
