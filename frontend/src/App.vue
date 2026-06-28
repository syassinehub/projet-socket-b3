<template>
  <div class="soc-layout">
    <main class="main-content">
      <header class="topbar">
        <h1>🚨 SOCket - Moniteur d'événements en Temps Réel</h1>
      </header>

      <section class="incidents-section">
        <div class="table-container">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Date & Heure</th>
                <th>Description de l'événement</th>
                <th>IP Source</th>
                <th>Sévérité</th>
                <th>Statut</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="incident in incidents" :key="incident.id">
                <td>#{{ incident.id }}</td>
                <td>{{ incident.date }}</td>
                <td><strong>{{ incident.title }}</strong></td>
                <td><small>{{ incident.ip }}</small></td>
                <td><span :class="['badge', incident.severity.toLowerCase()]">{{ incident.severity }}</span></td>
                <td><span :class="['status', incident.status.toLowerCase()]">{{ incident.status }}</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';

const incidents = ref([]);
let pollingInterval = null;

// Fonction qui va chercher les alertes
const fetchIncidents = async () => {
  try {
    const response = await fetch('/api/v1/incidents');
    const data = await response.json();
    incidents.value = data; // Met à jour le tableau
  } catch (error) {
    console.error("Erreur réseau :", error);
  }
};

// Au chargement de la page : on cherche les données, puis on boucle toutes les 2 secondes !
onMounted(() => {
  fetchIncidents();
  pollingInterval = setInterval(fetchIncidents, 2000); // Demande au backend toutes les 2 secondes
});

// Nettoyage si on quitte la page
onUnmounted(() => {
  clearInterval(pollingInterval);
});
</script>

<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0f172a; color: #f8fafc; }
.soc-layout { display: flex; min-height: 100vh; justify-content: center; padding: 40px; }
.main-content { width: 100%; max-width: 1200px; display: flex; flex-direction: column; gap: 30px; }
.topbar h1 { font-size: 1.8rem; font-weight: 600; color: #38bdf8; text-align: center; }
.table-container { background-color: #1e293b; border-radius: 10px; overflow: hidden; border: 1px solid #334155; }
table { width: 100%; border-collapse: collapse; text-align: left; }
th, td { padding: 15px; border-bottom: 1px solid #334155; }
th { background-color: #0f172a; color: #94a3b8; font-size: 0.85rem; text-transform: uppercase; }
tr:hover { background-color: #334155; }
small { color: #94a3b8; }
.badge { padding: 4px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: bold; }
.badge.critical { background-color: rgba(239, 68, 68, 0.2); color: #ef4444; border: 1px solid #ef4444; }
.badge.high { background-color: rgba(245, 158, 11, 0.2); color: #f59e0b; border: 1px solid #f59e0b; }
.badge.medium { background-color: rgba(56, 189, 248, 0.2); color: #38bdf8; border: 1px solid #38bdf8; }
.badge.low { background-color: rgba(16, 185, 129, 0.2); color: #10b981; border: 1px solid #10b981; }
.status.nouveau { color: #ef4444; font-weight: bold; }
.status.en { color: #f59e0b; }
.status.résolu { color: #10b981; }
</style>