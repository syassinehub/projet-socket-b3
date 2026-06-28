<template>
  <div class="soc-layout">
    <!-- Menu latéral (Sidebar) -->
    <aside class="sidebar">
      <div class="logo">
        <h2>🛡️ SOCket</h2>
      </div>
      <nav>
        <ul>
          <li class="active">📊 Tableau de bord</li>
          <li>🚨 Incidents (Tickets)</li>
          <li>🔍 Investigation (Logs)</li>
          <li>⚙️ Paramètres</li>
        </ul>
      </nav>
      <div class="user-info">
        <p>👤 Analyste_N1</p>
      </div>
    </aside>

    <!-- Contenu Principal -->
    <main class="main-content">
      <header class="topbar">
        <h1>Vue d'ensemble de la sécurité</h1>
        <div class="actions">
          <button class="btn-export">📥 Exporter le rapport</button>
        </div>
      </header>

      <!-- Indicateurs de performance (KPIs) -->
      <section class="kpi-cards">
        <div class="card danger">
          <h3>Alertes Critiques</h3>
          <p class="kpi-value">3</p>
        </div>
        <div class="card warning">
          <h3>En Attente</h3>
          <p class="kpi-value">12</p>
        </div>
        <div class="card success">
          <h3>Résolus (24h)</h3>
          <p class="kpi-value">45</p>
        </div>
        <div class="card info">
          <h3>Temps de réponse moy.</h3>
          <p class="kpi-value">14 min</p>
        </div>
      </section>

      <!-- Tableau des incidents -->
      <section class="incidents-section">
        <h2>Derniers Incidents Détectés</h2>
        <div class="table-container">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Date & Heure</th>
                <th>Description de l'événement</th>
                <th>Sévérité</th>
                <th>Statut</th>
                <th>Assigné à</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="incident in incidents" :key="incident.id">
                <td>#{{ incident.id }}</td>
                <td>{{ incident.date }}</td>
                <td><strong>{{ incident.title }}</strong><br/><small>{{ incident.ip }}</small></td>
                <td><span :class="['badge', incident.severity.toLowerCase()]">{{ incident.severity }}</span></td>
                <td><span :class="['status', incident.status.toLowerCase()]">{{ incident.status }}</span></td>
                <td>{{ incident.assigned }}</td>
                <td><button class="btn-action">Analyser</button></td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue';

// Fausses données avancées en attendant notre API Python
const incidents = ref([
  { id: 1042, date: '2026-06-28 18:45', title: 'Exfiltration de données suspectée', ip: 'IP Source: 192.168.1.15', severity: 'Critical', status: 'Nouveau', assigned: 'Non assigné' },
  { id: 1041, date: '2026-06-28 17:30', title: 'Tentative de Bruteforce SSH', ip: 'IP Source: 45.33.22.11', severity: 'High', status: 'En cours', assigned: 'Analyste_N1' },
  { id: 1040, date: '2026-06-28 16:15', title: 'Connexion inhabituelle (VPN)', ip: 'IP Source: 89.123.45.67', severity: 'Medium', status: 'En cours', assigned: 'Analyste_N2' },
  { id: 1039, date: '2026-06-28 14:00', title: 'Scan de ports détecté (Nmap)', ip: 'IP Source: 10.0.0.5', severity: 'Low', status: 'Résolu', assigned: 'Automatisé' }
]);
</script>

<style>
/* Base et Reset */
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0f172a; color: #f8fafc; }

/* Layout Global */
.soc-layout { display: flex; min-height: 100vh; }

/* Menu Latéral (Sidebar) */
.sidebar { width: 250px; background-color: #1e293b; padding: 20px; display: flex; flex-direction: column; border-right: 1px solid #334155; }
.logo h2 { color: #38bdf8; margin-bottom: 30px; font-size: 1.5rem; }
.sidebar nav ul { list-style: none; flex-grow: 1; }
.sidebar nav ul li { padding: 12px 15px; margin-bottom: 10px; border-radius: 6px; cursor: pointer; color: #cbd5e1; transition: 0.3s; }
.sidebar nav ul li:hover, .sidebar nav ul li.active { background-color: #38bdf8; color: #0f172a; font-weight: bold; }
.user-info { margin-top: auto; padding-top: 20px; border-top: 1px solid #334155; color: #94a3b8; font-size: 0.9rem; }

/* Contenu Principal */
.main-content { flex-grow: 1; padding: 30px; display: flex; flex-direction: column; gap: 30px; }
.topbar { display: flex; justify-content: space-between; align-items: center; }
.topbar h1 { font-size: 1.8rem; font-weight: 600; color: #f1f5f9; }
.btn-export { background-color: #334155; color: white; border: 1px solid #475569; padding: 8px 16px; border-radius: 6px; cursor: pointer; }
.btn-export:hover { background-color: #475569; }

/* Cartes KPI */
.kpi-cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }
.card { background-color: #1e293b; padding: 20px; border-radius: 10px; border: 1px solid #334155; }
.card h3 { font-size: 0.9rem; color: #94a3b8; text-transform: uppercase; margin-bottom: 10px; }
.kpi-value { font-size: 2rem; font-weight: bold; }
.danger .kpi-value { color: #ef4444; }
.warning .kpi-value { color: #f59e0b; }
.success .kpi-value { color: #10b981; }
.info .kpi-value { color: #38bdf8; }

/* Tableau */
.incidents-section h2 { margin-bottom: 15px; font-size: 1.2rem; color: #cbd5e1; }
.table-container { background-color: #1e293b; border-radius: 10px; overflow: hidden; border: 1px solid #334155; }
table { width: 100%; border-collapse: collapse; text-align: left; }
th, td { padding: 15px; border-bottom: 1px solid #334155; }
th { background-color: #0f172a; color: #94a3b8; font-weight: 600; font-size: 0.85rem; text-transform: uppercase; }
tr:hover { background-color: #334155; }
small { color: #94a3b8; }

/* Badges & Statuts */
.badge { padding: 4px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: bold; }
.badge.critical { background-color: rgba(239, 68, 68, 0.2); color: #ef4444; border: 1px solid #ef4444; }
.badge.high { background-color: rgba(245, 158, 11, 0.2); color: #f59e0b; border: 1px solid #f59e0b; }
.badge.medium { background-color: rgba(56, 189, 248, 0.2); color: #38bdf8; border: 1px solid #38bdf8; }
.badge.low { background-color: rgba(16, 185, 129, 0.2); color: #10b981; border: 1px solid #10b981; }

.status.nouveau { color: #ef4444; font-weight: bold; }
.status.en { color: #f59e0b; }
.status.résolu { color: #10b981; }

.btn-action { background-color: #38bdf8; color: #0f172a; border: none; padding: 6px 12px; border-radius: 4px; font-weight: bold; cursor: pointer; transition: 0.2s; }
.btn-action:hover { background-color: #0284c7; color: white; }
</style>