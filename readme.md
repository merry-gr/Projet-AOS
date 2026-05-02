# 🏥 MediConnect B2B

![Microservices](https://img.shields.io/badge/Architecture-Microservices-blue)
![Django](https://img.shields.io/badge/Backend-Django-green)
![Docker](https://img.shields.io/badge/DevOps-Docker-blue)
![RabbitMQ](https://img.shields.io/badge/Messaging-RabbitMQ-orange)

---

## 📖 Description

MediConnect B2B est une plateforme de vente en gros de produits médicaux et paramédicaux.  
Elle met en relation les fournisseurs (vendeurs) et les professionnels de santé (acheteurs) dans un environnement sécurisé, scalable et basé sur une architecture microservices.

---

## 🎯 Objectifs

- Simplifier les achats en gros de produits médicaux  
- Centraliser les échanges entre vendeurs et acheteurs  
- Mettre en place une architecture microservices  
- Assurer sécurité, performance et disponibilité  

---

## 👥 Acteurs

### 🔹 Administrateur
- Validation des comptes vendeurs  
- Gestion des utilisateurs  
- Supervision globale du système  

### 🔹 Vendeur
- Gestion des produits (CRUD)  
- Gestion des stocks  
- Traitement des commandes  

### 🔹 Acheteur
- Recherche de produits  
- Passage de commandes  
- Suivi des commandes  

---

## 🔑 Comptes de test

### 👤 Administrateur
- Username: amira  
- Password: 1234  

### 🛍️ Vendeur
- Username: amiraguerfi  
- Password: amiraguerfi0987654321  

### 🏥 Acheteur
- Username: nesrine_gf  
- Password: 1234567890qwerty  

---

## 🚀 Fonctionnalités

### 🔐 Authentification
- Inscription / connexion sécurisée  
- Gestion des rôles  

### 📦 Produits
- Ajouter / modifier / supprimer produits  
- Gestion des catégories et stocks  

### 🛒 Commandes
- Création de commandes  
- Validation / refus par vendeur  
- Suivi des statuts  

### 🔔 Notifications
- Communication asynchrone avec RabbitMQ  
- Worker Service pour traitement des messages  

---

## 🏗️ Architecture

     🧩 Architecture Diagram

               ┌─────────────────────┐
               │     Frontend        │
               └─────────┬───────────┘
                         │
                         ▼
               ┌─────────────────────┐
               │   Traefik Gateway   │
               └─────────┬───────────┘
                         │
    ┌────────────────────┼────────────────────┐
    ▼                    ▼                    ▼
    ┌───────────┐ ┌────────────┐ ┌────────────┐
    |  Auth Svc │ │ ProductSvc │ │ Order Svc │
    └───────────┘ └────────────┘ └────────────┘
                       \ │ /
                       \ ▼ /
            ┌────────────────────────────┐
                    │ RabbitMQ │
            └────────────────────────────┘
                         │
                         ▼
                 ┌────────────────┐
                 │ Worker Service │
                 └────────────────┘



### Microservices

- Auth Service → gestion auth & rôles  
- Product Service → gestion produits  
- Order Service → gestion commandes  
- Worker Service → tâches asynchrones  

### Infrastructure

- API Gateway : Traefik  
- Service Discovery : Consul  
- Message Broker : RabbitMQ  
- Base de données : SQLite  
- Conteneurisation : Docker  

---


---

## 🔄 Communication

### Synchrone
- REST API (HTTP)

### Asynchrone
- RabbitMQ messaging

---

## ⚙️ Technologies

- Django  
- Django REST Framework  
- Docker / Docker Compose  
- RabbitMQ  
- Traefik  
- Consul  
- Bootstrap  
- SQLite  

---

## 🐳 Installation

### 1. Cloner le projet

```bash
git clone https://github.com/your-username/mediconnect.git
cd mediconnect

