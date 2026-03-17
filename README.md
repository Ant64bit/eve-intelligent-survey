# FONCTIONNEMENT GLOBAL

```text
Une API REST en Python/FastAPI qui utilise un LLM pour reformuler et distribuer des questions de santé physique sous forme d'arbre de décision, avec stockage des sessions en PostgreSQL.
```


```bash
cd PROJET_TUT_01
uvicorn main:app --reload
```
lancer docker puis :

```bash
docker compose up -d -> demarre le compose en arriere plan

docker compose down -v -> supprime le compose et les données associés dans le volume

docker compose stop -> pause le compose

docker compose down -> supprime juste les conteneur
```



## idée sur route get_user_humor :

```text
FRONT                          API                         LLM
  │                             │                           │
  │  GET /humor/question        │                           │
  │ ─────────────────────────► │                           │
  │                             │  question fixe Q1         │
  │ ◄───────────────────────── │  (neutre, ton standard)   │
  │                             │                           │
  │  POST /humor/answer (R1)    │                           │
  │ ─────────────────────────► │                           │
  │                             │  analyse R1 ─────────────►│
  │                             │ ◄─────────────────────── │
  │                             │  tone partiel détecté     │
  │  GET /humor/question        │                           │
  │ ─────────────────────────► │                           │
  │                             │  Q2 reformulée ──────────►│
  │ ◄───────────────────────── │  selon tone partiel       │
  │                             │                           │
  │  POST /humor/answer (R2)    │                           │
  │ ─────────────────────────► │                           │
  │                             │  analyse R1+R2 ──────────►│
  │                             │ ◄─────────────────────── │
  │                             │  tone plus précis         │
  │  GET /humor/question        │                           │
  │ ─────────────────────────► │                           │
  │                             │  Q3 reformulée ──────────►│
  │ ◄───────────────────────── │  selon tone affiné        │
  │                             │                           │
  │  POST /humor/answer (R3)    │                           │
  │ ─────────────────────────► │                           │
  │                             │  analyse R1+R2+R3 ───────►│
  │                             │ ◄─────────────────────── │
  │                             │  tone FINAL stocké        │
  │ ◄───────────────────────── │  { done: true, tone: X }  │
  │                             │                           │
  │  → appelle intelligent_survey avec ce tone
```

### Ce que le LLM reçoit à chaque étape : 
```text
Q1 → rien                    (question fixe)

Q2 → { reponse: R1,
        question_base: "...",
        instruction: "reformule cette question en adoptant
                      le style de langage de l'utilisateur,
                      reste naturel et bienveillant" }

Q3 → { reponses: [R1, R2],
        question_base: "...",
        instruction: "même instruction + tone maintenant plus précis" }

Après R3 → { reponses: [R1, R2, R3],
              instruction: "détermine le tone final parmi :
                            casual / formal / empathetic / humorous" }
```

## Valeur ajoutée du projet
 
**Ce que le client a aujourd'hui**
- Un arbre de décision statique
- Tout le monde reçoit les mêmes questions, formulées de la même façon
- Un conseil générique à la fin
 
**Ce que ce projet apporte**
- La même interface à boutons que le client souhaite conserver
- Des questions reformulées selon le profil détecté de l'utilisateur
- Un conseil final personnalisé et contextualisé
 
La valeur n'est pas visible dans l'interface — elle est dans **l'expérience ressentie**.  
Deux personnes qui cliquent exactement les mêmes boutons reçoivent :
 
> **Profil formel / anxieux**  
> *"Il est recommandé de consulter un professionnel de santé afin d'évaluer vos douleurs articulaires et d'adapter votre pratique sportive en conséquence."*
 
> **Profil casual / détendu**  
> *"Honnêtement ? Vaut mieux voir un médecin du sport histoire de pas aggraver le truc. Il pourra te dire exactement ce que tu peux continuer à faire ou pas."*
 

# Intelligent Survey API

## Concept

Un questionnaire de santé physique classique (arbre de décision, réponses à boutons) rendu intelligent via un LLM — non pas en changeant l'interface, mais en personnalisant **l'expérience ressentie** selon le profil de l'utilisateur.

> Même arbre. Mêmes boutons. Même parcours.  
> Mais une expérience et un conseil radicalement différents selon qui répond.

---

## Flux global

```
┌─────────────────────────────────────────────────────────────┐
│  ÉTAPE 1 — Détection du profil utilisateur                  │
│                                                             │
│  GET  /humor/question  →  question neutre                   │
│  POST /humor/answer    →  réponse libre R1                  │
│                                                             │
│  GET  /humor/question  →  question reformulée (ton de R1)   │
│  POST /humor/answer    →  réponse libre R2                  │
│                                                             │
│  GET  /humor/question  →  question reformulée (ton R1+R2)   │
│  POST /humor/answer    →  réponse libre R3                  │
│                            │                                │
│                            ▼                                │
│                     tone FINAL détecté                      │
│               casual / formal / empathetic / humorous       │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  ÉTAPE 2 — Questionnaire santé personnalisé                 │
│                                                             │
│  GET  /survey/question                                      │
│    → Python navigue dans l'arbre JSON du client             │
│    → LLM reformule la question selon tone + historique      │
│    → Front affiche question + boutons de réponse            │
│                                                             │
│  POST /survey/answer                                        │
│    → Python reçoit la valeur du bouton cliqué               │
│    → navigue vers le nœud suivant dans l'arbre              │
│    → ... ping-pong jusqu'au nœud feuille ...                │
│                            │                                │
│                            ▼                                │
│                     conseil brut du client                  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  ÉTAPE 3 — Personnalisation du conseil final                │
│                                                             │
│  LLM reçoit :                                               │
│    - conseil brut de l'arbre du client                      │
│    - tone détecté                                           │
│    - historique complet de la session (toutes les Q/R)      │
│                                                             │
│  LLM produit :                                              │
│    un conseil enrichi, contextualisé, dans le ton           │
│    de l'utilisateur                                         │
└─────────────────────────────────────────────────────────────┘
```

---

## Exemple — même parcours, deux expériences

Deux utilisateurs cliquent exactement les mêmes boutons.

**Utilisateur A** — ton formel, profil anxieux
> *"Il est recommandé de consulter un professionnel de santé afin d'évaluer vos douleurs articulaires et d'adapter votre pratique sportive en conséquence."*

**Utilisateur B** — ton casual, profil détendu
> *"Honnêtement ? Vaut mieux voir un médecin du sport histoire de pas aggraver le truc. Il pourra te dire exactement ce que tu peux continuer à faire ou pas."*

---

## Rôle du LLM — ce qu'il fait et ne fait pas

```
                     LLM fait                 LLM ne fait PAS
                ─────────────────────────────────────────────
get_user_humor  Reformule Q2 et Q3            Poser Q1 (fixe)
                Détecte le tone final

intelligent     Reformule chaque question     Choisir le nœud suivant
survey          selon tone + historique       (c'est Python + l'arbre JSON)

conseil final   Enrichit et contextualise     Inventer un conseil
                le conseil brut du client     (source = arbre client)
```

Le LLM n'a jamais accès à l'arbre entier. Il travaille toujours sur un contexte court et constant.

---

## Contexte envoyé au LLM à chaque appel

```
Reformulation d'une question :
  - tone détecté                     ~  50 tokens
  - question brute du nœud courant   ~  30 tokens
  - 3 dernières Q/R de la session    ~ 200 tokens
  - instruction système              ~ 150 tokens
  ────────────────────────────────────────────────
  Total                              ~ 430 tokens  ✅

Personnalisation du conseil final :
  - tone détecté                     ~  50 tokens
  - conseil brut du client           ~ 100 tokens
  - historique complet session       ~ 800 tokens
  - instruction système              ~ 150 tokens
  ────────────────────────────────────────────────
  Total                              ~ 1100 tokens ✅
```

Taille constante quelle que soit la complexité de l'arbre du client.

---

## Stack technique

| Composant | Technologie |
|---|---|
| API | Python / FastAPI |
| Base de données | PostgreSQL 16 (Docker) |
| LLM | OpenAI GPT (reformulation + conseil) |
| Navigation arbre | Python pur (JSON statique) |

---

## Modèle de données

```sql
sessions
  id            UUID      -- identifiant de session
  tone          VARCHAR   -- casual / formal / empathetic / humorous
  current_node  VARCHAR   -- position courante dans l'arbre JSON
  status        VARCHAR   -- pending_humor / in_survey / done
  created_at    TIMESTAMP

humor_answers
  id            UUID
  session_id    UUID  → sessions
  question_id   INT        -- 1, 2 ou 3
  answer        TEXT       -- réponse libre de l'utilisateur
  answered_at   TIMESTAMP

survey_answers
  id            UUID
  session_id    UUID  → sessions
  node_id       VARCHAR    -- référence au nœud dans le JSON
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
| `POST` | `/humor/answer` | Enregistre une réponse, calcule le tone au bout de 3 |
| `GET` | `/survey/question` | Retourne la question courante reformulée |
| `POST` | `/survey/answer` | Enregistre la réponse, avance dans l'arbre |

---

## Structure du projet

```
intelligent-survey/
├── data/
│   └── decision_tree.json     # arbre de décision du client
├── app/
│   ├── main.py
│   ├── models/
│   │   └── session.py         # modèles SQLAlchemy
│   ├── routes/
│   │   ├── session.py
│   │   ├── humor.py
│   │   └── survey.py
│   ├── services/
│   │   ├── humor_service.py   # scoring + détection tone
│   │   ├── llm_service.py     # appels OpenAI + prompt builder
│   │   └── survey_service.py  # navigation dans l'arbre JSON
│   └── schemas/
│       └── pydantic.py        # schémas de validation
├── alembic/                   # migrations DB
├── docker-compose.yml
└── README.md
```