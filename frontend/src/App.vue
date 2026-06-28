<template>
  <div class="dashboard">
    <header>
      <h1>🛡️ SOCket - Dashboard Analyste</h1>
      <p>Connecté en tant que : <strong>Analyste_N1</strong></p>
    </header>

    <main>
      <h2>Alertes Récentes</h2>
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Titre de l'incident</th>
            <th>Sévérité</th>
            <th>Statut</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="incident in incidents" :key="incident.id">
            <td>#{{ incident.id }}</td>
            <td>{{ incident.title }}</td>
            <td :class="incident.severity.toLowerCase()">{{ incident.severity }}</td>
            <td>{{ incident.status }}</td>
            <td><button>Qualifier</button></td>
          </tr>
        </tbody>
      </table>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue';

// Données simulées en attendant de les relier à notre API Python
const incidents = ref([
  { id: 1, title: 'Tentative de Bruteforce SSH', severity: 'High', status: 'Open' },
  { id: 2, title: 'Connexion suspecte IP étrangère', severity: 'Medium', status: 'Open' }
]);
</script>

<style scoped>
.dashboard { font-family: Arial, sans-serif; padding: 20px; }
header { background-color: #2c3e50; color: white; padding: 15px; border-radius: 8px; }
table { width: 100%; margin-top: 20px; border-collapse: collapse; }
th, td { padding: 12px; border: 1px solid #ddd; text-align: left; }
.high { color: red; font-weight: bold; }
.medium { color: orange; font-weight: bold; }
button { background-color: #3498db; color: white; border: none; padding: 8px; cursor: pointer; }
</style>