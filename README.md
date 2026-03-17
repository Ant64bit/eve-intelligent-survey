# FONCTIONNEMENT

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
