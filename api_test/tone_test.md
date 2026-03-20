# exemple de : STRUCTURE JSON du POST de la front end vers l'API a l'appel de la route sessions/init/

```json
{
  "uuid": "7a73ae45-de57-4fc6-a3c0-66aad352ff9e",
  "question_1": "Comment vous sentez-vous aujourd'hui ?",
  "reponse_q1": "Bof, un peu fatigué mais ça va merci",
  "question_2": "Décrivez votre météo du jour en quelques mots.",
  "reponse_q2": "Aujourd'hui c'est plutôt nuageux avec des éclaircies"
}
```

# exemple de : STRUCTURE JSON de la réponse de l'appel à la route sessions/init/

```json
{
  "question_id": "q1",
  "question_reformulee": "Alors, t'as mal où exactement ?",
  "options": [
    { "id": "q1_a", "label": "Dans le dos" },
    { "id": "q1_b", "label": "Dans le cou" },
    { "id": "q1_c", "label": "Dans les jambes" }
  ]
}
```

