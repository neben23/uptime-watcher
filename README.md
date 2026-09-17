# Uptime Watcher

Une API REST légère pour surveiller la disponibilité de services HTTP (sites, APIs, endpoints internes...), avec checks automatiques périodiques et historique.

## Stack

- **Python 3** + **FastAPI** — API REST
- **SQLAlchemy 2.0** (style typé `Mapped`) + **SQLite** — persistance
- **APScheduler** — checks HTTP périodiques en arrière-plan, par service
- **httpx** — client HTTP pour les checks
- **Pydantic** — validation des entrées/sorties

## Fonctionnalités

- Ajouter/lister/supprimer des services à surveiller (URL + intervalle de check configurable)
- Check manuel à la demande
- Check automatique en arrière-plan, à l'intervalle défini par service
- Dernier statut connu (up/down, code HTTP, temps de réponse)
- Historique complet des checks par service

## Installation

```bash
git clone https://github.com/neben23/uptime-watcher.git
cd uptime-watcher
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Lancer l'API

```bash
uvicorn app.main:app --reload
```

L'API est disponible sur `http://127.0.0.1:8000`, avec la documentation interactive (Swagger) sur `http://127.0.0.1:8000/docs`.

## Exemples d'utilisation

**Ajouter un service à surveiller** (check toutes les 60 secondes) :

```bash
curl -X POST http://127.0.0.1:8000/services \
  -H "Content-Type: application/json" \
  -d '{"name": "Mon site", "url": "https://example.com", "check_interval_seconds": 60}'
```

**Lister les services :**

```bash
curl http://127.0.0.1:8000/services
```

**Déclencher un check manuel :**

```bash
curl -X POST http://127.0.0.1:8000/services/1/check
```

**Voir le dernier statut connu :**

```bash
curl http://127.0.0.1:8000/services/1/status
```

**Voir l'historique complet :**

```bash
curl http://127.0.0.1:8000/services/1/history
```

## Endpoints

| Méthode | Route                        | Description                              |
|---------|-------------------------------|-------------------------------------------|
| POST    | `/services`                  | Créer un service à surveiller             |
| GET     | `/services`                  | Lister tous les services                  |
| GET     | `/services/{id}`             | Détail d'un service                       |
| DELETE  | `/services/{id}`             | Supprimer un service                      |
| POST    | `/services/{id}/check`       | Déclencher un check immédiat              |
| GET     | `/services/{id}/status`      | Statut + dernier check connu              |
| GET     | `/services/{id}/history`     | Historique complet des checks             |

## Architecture

```
app/
├── database.py   # connexion SQLite + session
├── models.py     # modèles SQLAlchemy (Service, CheckResult)
├── schemas.py     # schémas Pydantic (validation entrée/sortie)
├── checker.py     # logique de check HTTP
├── scheduler.py    # planification des checks automatiques (APScheduler)
└── main.py         # routes FastAPI
```

## Pistes d'amélioration

- Notifications (Discord/Slack) quand un service tombe
- Dashboard web simple
- Authentification sur l'API
- Support de checks TCP/ping en plus du HTTP
