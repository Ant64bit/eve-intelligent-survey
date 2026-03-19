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

# Compte rendu — Base de données

## Structure

La base de données repose sur deux tables PostgreSQL.

### Table `sessions`

Créée au premier appel API. Contient une ligne par utilisateur.

| Colonne | Type | Description |
|---|---|---|
| `uuid` | uuid (PK) | Token généré par l'API au premier appel, identifiant unique de la session |
| `ton` | varchar | Profil de ton détecté lors du questionnaire préliminaire (ex: tutoiement, vouvoiement, registre) |
| `current_question_id` | varchar | Identifiant de la question en cours dans l'arbre de décision |
| `created_at` | timestamp | Date de création de la session |

---

### Table `session_history`

Alimentée à chaque réponse de l'utilisateur. Contient une ligne par étape du questionnaire.

| Colonne | Type | Description |
|---|---|---|
| `id` | int (PK) | Identifiant auto-incrémenté |
| `uuid` | uuid (FK) | Référence vers la session dans la table `sessions` |
| `question_id` | varchar | Identifiant de la question dans l'arbre JSON (ex: `q4`) |
| `question_reformulee` | text | Texte de la question tel qu'il a été reformulé par le LLM et affiché à l'utilisateur |
| `options_proposees` | jsonb | Liste des boutons affichés à l'utilisateur, générée par le LLM depuis l'arbre |
| `reponse_utilisateur` | varchar | Identifiant de l'option choisie par l'utilisateur (ex: `q4_b`) |
| `step_order` | int | Numéro de l'étape dans le parcours (1, 2, 3...) |
| `answered_at` | timestamp | Date et heure de la réponse |

---

## Flux de fonctionnement

### 1. Premier appel API — initialisation

Le frontend appelle une route dédiée (ex: `POST /session/init`). L'API génère un `uuid` et crée une ligne vide dans `sessions`. Ce `uuid` est retourné au frontend qui le conserve pour tous les appels suivants.

### 2. Chaque réponse utilisateur — mise à jour

Quand l'utilisateur clique sur un bouton, le frontend envoie à l'API :
- le `uuid` de la session
- le `question_id` de la question courante
- la réponse choisie (`reponse_utilisateur`)

L'API effectue alors deux opérations :
- **INSERT** d'une nouvelle ligne dans `session_history` avec toutes les données de l'étape
- **UPDATE** de `current_question_id` dans `sessions` pour refléter l'avancement

### 3. Chaque appel au LLM — construction du contexte

Avant d'appeler le LLM, l'API reconstruit l'historique complet de la session avec :

```sql
SELECT * FROM session_history
WHERE uuid = '...'
ORDER BY step_order ASC;
```

Cet historique est ensuite injecté dans le prompt avec l'arbre de décision JSON complet. Le LLM détermine lui-même la question suivante et les options à proposer en fonction des réponses précédentes, sans qu'aucune logique de navigation ne soit codée côté Python.

### 4. Réponse du LLM — format structuré

Le LLM retourne toujours un JSON structuré du type :

```json
{
  "question_id": "q4",
  "question_reformulee": "Est-ce que tu ressens cette douleur plutôt le matin ou le soir ?",
  "options": [
    { "id": "q4_a", "label": "Plutôt le matin" },
    { "id": "q4_b", "label": "Plutôt le soir" },
    { "id": "q4_c", "label": "Les deux" }
  ]
}
```

L'API valide que les `id` des options existent bien dans l'arbre JSON avant de renvoyer la réponse au frontend. Le frontend affiche les boutons dynamiquement sans connaître l'arbre — si l'ostéopathe modifie son arbre, aucun changement n'est nécessaire côté frontend.