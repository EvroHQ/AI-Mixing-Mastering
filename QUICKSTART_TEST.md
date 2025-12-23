# 🚀 Guide de Démarrage Rapide - Test du Nouveau Mastering

## Option 1: Test Direct (Sans Docker) ⚡

### 1. Installer les dépendances

```bash
cd backend
pip install -r requirements.txt
```

### 2. Démarrer le serveur API

```bash
cd backend
python main.py
```

Le serveur démarrera sur `http://localhost:8000`

### 3. Démarrer le frontend

```bash
cd frontend
npm install
npm run dev
```

Le frontend sera accessible sur `http://localhost:3000`

### 4. Tester sur le site

1. Ouvrez `http://localhost:3000`
2. Uploadez vos stems
3. Sélectionnez un preset (Balanced, Dynamic, ou Loud)
4. Lancez le processing
5. Téléchargez le résultat masterisé

---

## Option 2: Test avec Script Python 🧪

### Test rapide du moteur de mastering

```bash
cd backend
python test_pro_mastering.py
```

Cela va:

- Générer un signal de test
- Appliquer les 3 presets (Balanced, Dynamic, Loud)
- Sauvegarder les fichiers dans `backend/test_outputs/`
- Afficher toutes les métriques

### Fichiers générés

```
backend/test_outputs/
├── input.wav                    # Signal original
├── mastered_balanced.wav        # Preset Balanced
├── mastered_dynamic.wav         # Preset Dynamic
└── mastered_loud.wav           # Preset Loud
```

---

## Option 3: Test avec vos propres stems 🎵

### Script de test personnalisé

```python
from audio_engine.pipeline import AudioPipeline

# Vos stems
stem_files = [
    "path/to/kick.wav",
    "path/to/bass.wav",
    "path/to/vocals.wav",
    # ... autres stems
]

# Créer le pipeline
pipeline = AudioPipeline(sample_rate=48000)

# Traiter
report = pipeline.process(
    stem_files=stem_files,
    output_mix_path="output/mix.wav",
    output_master_path="output/master.wav",
    target_lufs=-14.0,
    ceiling_dbTP=-0.3,
    preset='balanced'  # ou 'dynamic' ou 'loud'
)

print(f"LUFS final: {report['final_quality']['lufs']:.1f}")
print(f"True Peak: {report['final_quality']['true_peak_dbTP']:.1f} dBTP")
```

---

## 🎛️ Presets Disponibles

### **Balanced** (Recommandé pour la plupart des cas)

- EQ équilibré avec boost bass/highs
- Compression modérée
- Saturation analogique équilibrée
- **Idéal pour**: Pop, Rock, Indie

### **Dynamic** (Préserve la dynamique)

- EQ subtil
- Compression douce
- Saturation chaude (tape)
- **Idéal pour**: Jazz, Classical, Acoustic

### **Loud** (Maximum impact)

- EQ agressif
- Compression forte
- Saturation agressive
- **Idéal pour**: EDM, Hip-Hop, Electro House

---

## 📊 Métriques à Vérifier

### Avant (Input)

```
LUFS: ~-18.0 dB (niveau mix typique)
True Peak: ~-3.0 dBTP
```

### Après (Output)

```
LUFS: -14.0 dB (±0.5) ✅
True Peak: -0.3 dBTP ✅
LRA: 4-8 LU (dynamique préservée) ✅
Crest Factor: >3.5 (pas sur-compressé) ✅
```

---

## 🔧 Dépendances Requises

```txt
numpy>=1.21.0
scipy>=1.7.0
soundfile>=0.11.0
librosa>=0.10.0
pedalboard>=0.7.0
pyloudnorm>=0.1.0
fastapi>=0.104.0
uvicorn>=0.24.0
```

Installation rapide:

```bash
pip install numpy scipy soundfile librosa pedalboard pyloudnorm fastapi uvicorn
```

---

## 🐛 Troubleshooting

### Erreur: "No module named 'pro_limiter'"

```bash
# Vérifier que vous êtes dans le bon répertoire
cd backend
python -c "from audio_engine.masterer.pro_limiter import ProLimiter; print('OK')"
```

### Erreur: "Cannot import pedalboard"

```bash
pip install pedalboard
```

### Erreur: Sample rate mismatch

Les stems doivent tous avoir le même sample rate. Le système détecte automatiquement et resample si nécessaire.

---

## 📈 Comparaison Avant/Après

### Ancien Système ❌

```
Reverb: 30% wet (trop!)
EQ: +0.5 à +1.5 dB (imperceptible)
Compression: Basique
Limiter: Basique (peut clipper)
Saturation: Minimale
```

### Nouveau Système ✅

```
Reverb: 15% wet (professionnel)
EQ: +1.5 à +3.0 dB (impactful)
Compression: Multi-bande pro avec phase linéaire
Limiter: True-peak avec oversampling 4x
Saturation: Tape + Tube + Harmonic Exciter
```

---

## 🎯 Prochaines Étapes

1. **Tester avec vos stems** - Uploadez vos pistes
2. **Comparer les presets** - Écoutez Balanced vs Dynamic vs Loud
3. **Vérifier les métriques** - LUFS, True Peak, LRA
4. **A/B avec référence** - Comparez avec un master commercial

---

## 💡 Tips Pro

### Pour EDM/Electronic

- Utilisez le preset **Loud**
- Target LUFS: -8 à -10 (plus fort)
- Vérifiez que le kick punch bien

### Pour Acoustic/Jazz

- Utilisez le preset **Dynamic**
- Target LUFS: -16 à -14 (plus doux)
- Préservez la dynamique naturelle

### Pour Pop/Rock

- Utilisez le preset **Balanced**
- Target LUFS: -14 à -12
- Équilibre entre punch et clarté

---

## 📞 Support

Si vous rencontrez des problèmes:

1. Vérifiez les logs dans la console
2. Vérifiez que tous les modules sont bien installés
3. Testez d'abord avec le script de test

---

**Créé par**: Antigravity AI  
**Version**: 2.0.0 Professional  
**Date**: 2025-12-12
