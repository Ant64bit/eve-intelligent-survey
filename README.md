# Intelligent Survey API

API REST Python/FastAPI qui personnalise un questionnaire de santé physique (arbre de décision) via un LLM — sans modifier l'interface utilisateur.

---

## Lancement

```bash
# Démarrer la base de données
docker compose up -d

# Lancer l'API
cd PROJET_TUT_01
uvicorn main:app --reload
```

**Commandes Docker utiles**

```bash
docker compose up -d     # démarre en arrière-plan
docker compose stop      # met en pause
docker compose down      # supprime les conteneurs
docker compose down -v   # supprime les conteneurs + les volumes (données perdues)
```

---

## Concept

L'arbre de décision du client reste intact. Les boutons de réponse ne changent pas. Ce qui change : les questions sont reformulées selon le profil détecté de l'utilisateur, et le conseil final est contextualisé.

```
Profil formel / anxieux
→ "Il est recommandé de consulter un professionnel de santé afin d'évaluer
   vos douleurs articulaires et d'adapter votre pratique sportive."

Profil casual / détendu
→ "Honnêtement ? Vaut mieux voir un médecin du sport histoire de pas aggraver
   le truc. Il pourra te dire exactement ce que tu peux continuer à faire."
```

Deux utilisateurs qui cliquent les mêmes boutons reçoivent une expérience différente.

---

## Flux global

```
┌─────────────────────────────────────────────────────────────┐
│  ÉTAPE 1 — Détection du profil utilisateur                  │
│                                                             │
│  GET  /humor/question  →  question neutre (fixe)            │
│  POST /humor/answer    →  réponse libre R1                  │
│                                                             │
│  GET  /humor/question  →  question reformulée (ton R1)      │
│  POST /humor/answer    →  réponse libre R2                  │
│                                                             │
│  GET  /humor/question  →  question reformulée (ton R1+R2)   │
│  POST /humor/answer    →  réponse libre R3                  │
│                            │                                │
│                            ▼                                │
│               tone FINAL : casual / formal /                │
│                            empathetic / humorous            │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  ÉTAPE 2 — Questionnaire santé personnalisé                 │
│                                                             │
│  GET  /survey/question                                      │
│    → Python navigue dans l'arbre JSON                       │
│    → LLM reformule la question (tone + historique)          │
│    → Front affiche question + boutons                       │
│                                                             │
│  POST /survey/answer                                        │
│    → Python reçoit la valeur du bouton cliqué               │
│    → avance dans l'arbre JSON                               │
│    → répété jusqu'au nœud feuille                           │
│                            │                                │
│                            ▼                                │
│                  conseil brut (arbre client)                │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  ÉTAPE 3 — Personnalisation du conseil final                │
│                                                             │
│  Entrées LLM :                                              │
│    - conseil brut de l'arbre                                │
│    - tone détecté                                           │
│    - historique complet de la session                       │
│                                                             │
│  Sortie :                                                   │
│    conseil enrichi, contextualisé, dans le ton détecté      │
└─────────────────────────────────────────────────────────────┘
```

---

## Rôle du LLM

| Étape | Ce que fait le LLM | Ce que le LLM ne fait PAS |
|---|---|---|
| `get_user_humor` | Reformule Q2 et Q3 — détecte le tone final | Poser Q1 (question fixe) |
| `intelligent_survey` | Reformule chaque question (tone + historique) | Choisir le nœud suivant (Python + JSON) |
| Conseil final | Enrichit et contextualise le conseil brut | Inventer un conseil |

Le LLM n'a jamais accès à l'arbre entier. Il travaille toujours sur un contexte court et constant.

---

## Contexte LLM par appel

```
Reformulation d'une question :
  - tone détecté                     ~  50 tokens
  - question brute du nœud courant   ~  30 tokens
  - 3 dernières Q/R de la session    ~ 200 tokens
  - instruction système              ~ 150 tokens
  ─────────────────────────────────────────────────
  Total                              ~ 430 tokens  ✅

Personnalisation du conseil final :
  - tone détecté                     ~  50 tokens
  - conseil brut du client           ~ 100 tokens
  - historique complet session       ~ 800 tokens
  - instruction système              ~ 150 tokens
  ─────────────────────────────────────────────────
  Total                              ~ 1 100 tokens ✅
```

Taille constante quelle que soit la complexité de l'arbre.

---

## Détail — détection du tone (étape 1)

```
FRONT                          API                         LLM
  │                             │                           │
  │  GET /humor/question        │                           │
  │ ─────────────────────────► │                           │
  │ ◄───────────────────────── │  Q1 fixe (neutre)         │
  │                             │                           │
  │  POST /humor/answer (R1)    │                           │
  │ ─────────────────────────► │                           │
  │                             │  analyse R1 ─────────────►│
  │                             │ ◄──────────────────────── │
  │                             │  tone partiel détecté     │
  │  GET /humor/question        │                           │
  │ ─────────────────────────► │                           │
  │                             │  Q2 reformulée ──────────►│
  │ ◄───────────────────────── │  selon tone partiel       │
  │                             │                           │
  │  POST /humor/answer (R2)    │                           │
  │ ─────────────────────────► │                           │
  │                             │  analyse R1+R2 ──────────►│
  │                             │ ◄──────────────────────── │
  │                             │  tone affiné              │
  │  GET /humor/question        │                           │
  │ ─────────────────────────► │                           │
  │                             │  Q3 reformulée ──────────►│
  │ ◄───────────────────────── │  selon tone affiné        │
  │                             │                           │
  │  POST /humor/answer (R3)    │                           │
  │ ─────────────────────────► │                           │
  │                             │  analyse R1+R2+R3 ───────►│
  │                             │ ◄──────────────────────── │
  │                             │  tone FINAL stocké        │
  │ ◄───────────────────────── │  { done: true, tone: X }  │
```

**Payload LLM à chaque étape :**

```
Q1 → rien                      (question fixe, pas d'appel LLM)

Q2 → { reponse: R1,
        question_base: "...",
        instruction: "reformule en adoptant le style de l'utilisateur" }

Q3 → { reponses: [R1, R2],
        question_base: "...",
        instruction: "même instruction + tone plus précis" }

Après R3 → { reponses: [R1, R2, R3],
              instruction: "détermine le tone final parmi :
                            casual / formal / empathetic / humorous" }
```

---

## Stack technique

| Composant | Technologie |
|---|---|
| API | Python / FastAPI |
| Base de données | PostgreSQL 16 (Docker) |
| LLM | OpenAI GPT |
| Navigation arbre | Python pur (JSON statique) |

---

## Modèle de données

```sql
sessions
  id            UUID
  tone          VARCHAR   -- casual / formal / empathetic / humorous
  current_node  VARCHAR   -- position courante dans l'arbre JSON
  status        VARCHAR   -- pending_humor / in_survey / done
  created_at    TIMESTAMP

humor_answers
  id            UUID
  session_id    UUID  → sessions
  question_id   INT        -- 1, 2 ou 3
  answer        TEXT
  answered_at   TIMESTAMP

survey_answers
  id            UUID
  session_id    UUID  → sessions
  node_id       VARCHAR    -- référence au nœud JSON
  question_llm  TEXT       -- question reformulée par le LLM
  answer        VARCHAR    -- valeur du bouton cliqué
  answered_at   TIMESTAMP
```

---

## Routes API

| Méthode | Route | Description |
|---|---|---|
| `POST` | `/session` | Crée une session, retourne un UUID |
| `GET` | `/humor/question` | Retourne la prochaine question d'humeur |
| `POST` | `/humor/answer` | Enregistre une réponse — calcule le tone après R3 |
| `GET` | `/survey/question` | Retourne la question courante reformulée |
| `POST` | `/survey/answer` | Enregistre la réponse, avance dans l'arbre |

---

## Structure du projet

```
intelligent-survey/
├── data/
│   └── decision_tree.json      # arbre de décision du client
├── app/
│   ├── main.py
│   ├── models/
│   │   └── session.py          # modèles SQLAlchemy
│   ├── routes/
│   │   ├── session.py
│   │   ├── humor.py
│   │   └── survey.py
│   ├── services/
│   │   ├── humor_service.py    # scoring + détection tone
│   │   ├── llm_service.py      # appels OpenAI + prompt builder
│   │   └── survey_service.py   # navigation dans l'arbre JSON
│   └── schemas/
│       └── pydantic.py         # schémas de validation
├── alembic/                    # migrations DB
├── docker-compose.yml
└── README.md
```