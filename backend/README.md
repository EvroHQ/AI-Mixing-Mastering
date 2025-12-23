# 🎵 MixMaster - Guide de Démarrage Backend Complet

## 📋 Prérequis

Avant de démarrer, assurez-vous que :

- ✅ Python 3.10+ est installé
- ✅ Les dépendances sont installées (`pip install -r requirements.txt`)
- ✅ Le fichier `.env` est configuré avec vos credentials B2
- ✅ Les buckets B2 sont créés (`mixmaster-input`, `mixmaster-output`)

---

## 🚀 Démarrage du Backend Complet

Le backend MixMaster nécessite **3 services** qui fonctionnent ensemble :

### 1️⃣ Redis Server (Base de données & Queue)

**Démarrer Redis :**

```bash
cd c:\Users\EvroHQ\Desktop\mixmaster\backend
.\start-redis.bat
```

**Vérifier que Redis fonctionne :**

```bash
.\test-redis.bat
```

Vous devriez voir : `PONG`

**Arrêter Redis :**

```bash
.\stop-redis.bat
```

---

### 2️⃣ Backend API (FastAPI)

**Terminal 1 - Démarrer l'API :**

```powershell
# Naviguer vers le dossier backend
cd c:\Users\EvroHQ\Desktop\mixmaster\backend

# Activer l'environnement virtuel
.\venv\Scripts\Activate.ps1

# Démarrer l'API
uvicorn main:app --reload
```

**L'API sera disponible sur :**

- 🌐 API : http://localhost:8000
- 📚 Documentation : http://localhost:8000/docs
- ❤️ Health Check : http://localhost:8000/health

**Arrêter l'API :**

- Appuyez sur `Ctrl+C` dans le terminal

---

### 3️⃣ Celery Worker (Traitement Audio)

**Terminal 2 - Démarrer Celery :**

```powershell
# Naviguer vers le dossier backend
cd c:\Users\EvroHQ\Desktop\mixmaster\backend

# Activer l'environnement virtuel
.\venv\Scripts\Activate.ps1

# Démarrer Celery Worker
celery -A celery_app worker --loglevel=info --pool=solo
```

**Note :** `--pool=solo` est nécessaire sur Windows

**Arrêter Celery :**

- Appuyez sur `Ctrl+C` dans le terminal

---

## 🎯 Démarrage Rapide (Tout en Une Fois)

### Option A : Script Automatique

**Double-cliquez sur :**

```
start-backend.bat
```

Ce script démarre automatiquement :

- ✅ Redis Server
- ✅ Backend API
- ✅ Celery Worker

### Option B : Commandes Manuelles

**Terminal 1 - Redis :**

```bash
cd c:\Users\EvroHQ\Desktop\mixmaster\backend
.\start-redis.bat
```

**Terminal 2 - API :**

```powershell
cd c:\Users\EvroHQ\Desktop\mixmaster\backend
.\venv\Scripts\Activate.ps1
uvicorn main:app --reload
```

**Terminal 3 - Celery :**

```powershell
cd c:\Users\EvroHQ\Desktop\mixmaster\backend
.\venv\Scripts\Activate.ps1
celery -A celery_app worker --loglevel=info --pool=solo
```

---

## ✅ Vérification du Démarrage

### 1. Vérifier Redis

```bash
.\test-redis.bat
# Devrait afficher : PONG
```

### 2. Vérifier l'API

Ouvrez dans votre navigateur :

```
http://localhost:8000/health
```

Devrait retourner :

```json
{
  "status": "healthy",
  "timestamp": "2025-12-09T20:00:00.000000"
}
```

### 3. Vérifier Celery

Dans le terminal Celery, vous devriez voir :

```
[tasks]
  . tasks.audio_processor.process_audio_job

celery@HOSTNAME ready.
```

### 4. Vérifier la Documentation API

```
http://localhost:8000/docs
```

Vous devriez voir l'interface Swagger avec tous les endpoints.

---

## 🛑 Arrêter Tous les Services

### Option A : Script Automatique

```bash
.\stop-backend.bat
```

### Option B : Manuellement

1. **Redis** : `.\stop-redis.bat`
2. **API** : `Ctrl+C` dans le terminal de l'API
3. **Celery** : `Ctrl+C` dans le terminal Celery

---

## 📊 Architecture du Backend

```
┌─────────────────┐
│   Frontend      │
│  (Next.js)      │
│  Port 3000      │
└────────┬────────┘
         │ HTTP
         ▼
┌─────────────────┐
│   Backend API   │
│   (FastAPI)     │
│   Port 8000     │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐ ┌──────────────┐
│ Redis  │ │ Backblaze B2 │
│ 6379   │ │ (Storage)    │
└───┬────┘ └──────────────┘
    │
    ▼
┌─────────────────┐
│ Celery Worker   │
│ (Audio Process) │
└─────────────────┘
```

---

## 🔧 Configuration

### Fichier `.env`

Assurez-vous que votre fichier `.env` contient :

```env
# Backblaze B2
B2_APPLICATION_KEY_ID=votre_key_id
B2_APPLICATION_KEY=votre_application_key
B2_BUCKET_INPUT=mixmaster-input
B2_BUCKET_OUTPUT=mixmaster-output

# Redis
REDIS_URL=redis://localhost:6379/0

# API
ALLOWED_ORIGINS=http://localhost:3000

# Debug
DEBUG=True
```

---

## 🐛 Dépannage

### Redis ne démarre pas

```bash
# Vérifier si Redis tourne déjà
tasklist | findstr redis

# Tuer le processus si nécessaire
taskkill /F /IM redis-server.exe

# Redémarrer
.\start-redis.bat
```

### L'API ne démarre pas

```bash
# Vérifier que le port 8000 est libre
netstat -ano | findstr :8000

# Vérifier les logs pour les erreurs
# Assurez-vous que l'environnement virtuel est activé
.\venv\Scripts\Activate.ps1
```

### Celery ne démarre pas

```bash
# Vérifier que Redis tourne
.\test-redis.bat

# Vérifier les logs pour les erreurs
# Sur Windows, utilisez toujours --pool=solo
celery -A celery_app worker --loglevel=debug --pool=solo
```

### Erreur B2 Connection

```bash
# Vérifier les credentials dans .env
notepad .env

# Tester la connexion B2
python -c "from storage.b2_client import B2Client; print('B2 OK')"
```

---

## 📝 Logs et Monitoring

### Voir les logs de l'API

Les logs s'affichent directement dans le terminal où vous avez lancé `uvicorn`

### Voir les logs Celery

Les logs s'affichent dans le terminal Celery avec le niveau `--loglevel=info`

### Voir les logs Redis

Redis affiche ses logs dans sa fenêtre de terminal

---

## 🎯 Endpoints API Principaux

| Endpoint                 | Méthode | Description                      |
| ------------------------ | ------- | -------------------------------- |
| `/health`                | GET     | Vérifier l'état de l'API         |
| `/api/upload`            | POST    | Uploader des stems audio         |
| `/api/status/{job_id}`   | GET     | Vérifier le statut du traitement |
| `/api/download/{job_id}` | GET     | Obtenir l'URL de téléchargement  |
| `/api/job/{job_id}`      | DELETE  | Supprimer un job                 |
| `/docs`                  | GET     | Documentation Swagger            |

---

## 🚀 Prêt à Tester !

Une fois tous les services démarrés :

1. **Ouvrez** http://localhost:3000
2. **Allez** sur la page Studio
3. **Uploadez** vos fichiers audio
4. **Regardez** le traitement en temps réel
5. **Téléchargez** votre master !

---

## 📚 Documentation Complète

- [README.md](../README.md) - Documentation générale
- [QUICKSTART.md](../QUICKSTART.md) - Guide de démarrage rapide
- [IMPLEMENTATION.md](../IMPLEMENTATION.md) - Détails d'implémentation

---

**Besoin d'aide ?** Consultez la documentation ou ouvrez une issue sur GitHub.

🎵 **Happy Mixing!** ✨
