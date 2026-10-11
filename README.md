# Todo App v3 - Gestion de tâches avec statuts

## Description

Application multi-services avec gestion des statuts des tâches (À faire / En cours / Terminée).

## Structure

todo-app3/
├── docker-compose.yml          # Orchestration (4 services, réseau app-network-2)
├── .env.example                # Variables d'environnement par défaut
├── .gitignore                  # Exclusions Git
├── README.md                   # Documentation
│
├── api/                        # Service API (Flask + PostgreSQL)
│   ├── Dockerfile              # Image Python 3.11 + Flask
│   ├── requirements.txt        # Dépendances (flask, psycopg2, requests, flask-cors)
│   ├── app.py                  # Routes: GET/POST/PUT /tasks
│   └── .dockerignore
│
├── logger/                     # Service Logger (Flask)
│   ├── Dockerfile              # Image Python 3.11
│   ├── requirements.txt        # Dépendance: flask
│   ├── app.py                  # Route: POST /log
│   └── .dockerignore
│
└── frontend/                   # Interface web (Nginx)
├── Dockerfile              # Image nginx:alpine
├── index.html              # HTML/JS/CSS (gestion des statuts)
└── .dockerignore

## Flux de données

Utilisateur (Navigateur)
↓ HTTP (8081)
Frontend (Nginx)
↓ HTTP (5002) → POST/GET/PUT /tasks
API (Flask)
↓ PostgreSQL (5432) → CRUD tâches
↓ HTTP (5003) → POST /log
Logger (Flask)
↓ Affiche les logs dans le terminal

## Prérequis

- Docker avec `docker compose` v2

## Démarrage

docker compose up -d --build

## Services

| Service     | Port | Rôle                           |
|-------------|------|--------------------------------|
| api         | 5002 | API REST (POST/GET/PUT /tasks) |
| logger      | 5003 | Service de logging             |
| frontend    | 8081 | Interface web                  |
| postgres-db | —    | Base de données (non exposée)  |

## Statuts des tâches

-  **À faire** (gris)
-  **En cours** (jaune)
-  **Terminée** (vert barré)

## Vérifier que tout fonctionne

1. Ouvrir http://localhost:8081
2. Ajouter une tâche
3. Cliquer sur une tâche pour changer son statut
4. Vérifier les logs: docker compose logs logger

## Arrêt

docker compose down   
docker compose down -v

## Persistance

Les données sont stockées dans un volume Docker nommé (postgres_data). Elles survivent à un docker compose down mais sont supprimées avec down -v.

## Sécurité

- PostgreSQL **non exposé** sur l'hôte (accès interne uniquement via `app-network-2`)
- Communication par **noms de service** (`api`, `logger`, `postgres-db`)
- Healthcheck sur PostgreSQL (l'API attend que la DB soit prête)

## Vérifier que tous les services sont up-healthy, et les logs

docker compose ps 
docker compose logs XXXXX
