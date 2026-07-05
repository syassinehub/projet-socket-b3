<template>
  <main class="app-shell">
    <section v-if="!token" class="login-view">
      <div class="brand-panel">
        <span class="brand-mark">S</span>
        <div>
          <p class="eyebrow">SOCket</p>
          <h1>Console SOC</h1>
        </div>
      </div>
      <form class="login-form" @submit.prevent="login">
        <label>
          <span>Utilisateur</span>
          <input v-model="loginForm.username" autocomplete="username" required />
        </label>
        <label>
          <span>Mot de passe</span>
          <input v-model="loginForm.password" type="password" autocomplete="current-password" required />
        </label>
        <p v-if="error" class="error-message">{{ error }}</p>
        <button type="submit" :disabled="loading">Connexion</button>
      </form>
    </section>

    <section v-else class="dashboard">
      <aside class="sidebar">
        <div class="brand-row">
          <span class="brand-mark">S</span>
          <div>
            <strong>SOCket</strong>
            <small>{{ user?.username }} · {{ user?.role }}</small>
          </div>
        </div>
        <nav class="status-nav">
          <button :class="{ active: activeView === 'incidents' }" @click="activeView = 'incidents'">Incidents</button>
          <button v-if="canViewData" :class="{ active: activeView === 'data' }" @click="openDataView">Donnees</button>
        </nav>
        <nav v-if="activeView === 'incidents'" class="status-nav compact">
          <button :class="{ active: filters.status === '' }" @click="filters.status = ''">Tous</button>
          <button :class="{ active: filters.status === 'Nouveau' }" @click="filters.status = 'Nouveau'">Nouveaux</button>
          <button :class="{ active: filters.status === 'En cours' }" @click="filters.status = 'En cours'">En cours</button>
          <button :class="{ active: filters.status === 'Résolu' }" @click="filters.status = 'Résolu'">Resolus</button>
        </nav>
        <button class="ghost-button" @click="logout">Deconnexion</button>
      </aside>

      <section class="workspace">
        <header class="topbar">
          <div>
            <p class="eyebrow">{{ activeView === 'incidents' ? 'Supervision temps reel' : 'Exploration des donnees' }}</p>
            <h1>{{ activeView === 'incidents' ? 'Incidents et detections IDS' : 'PostgreSQL et Elasticsearch' }}</h1>
          </div>
          <div class="topbar-actions">
            <span v-if="activeView === 'incidents'" class="live-indicator">
              <span></span>
              Temps reel actif{{ lastRefreshAt ? ` · ${lastRefreshAt}` : '' }}
            </span>
            <button class="primary-button" @click="loadAll">Actualiser</button>
          </div>
        </header>

        <section v-if="activeView === 'incidents'" class="metrics-grid">
          <article><span>{{ stats.total }}</span><p>Incidents</p></article>
          <article><span>{{ stats.critical }}</span><p>Critiques</p></article>
          <article><span>{{ stats.open }}</span><p>Ouverts</p></article>
          <article><span>{{ stats.avgScore }}</span><p>Score moyen</p></article>
        </section>

        <section v-if="activeView === 'incidents'" class="toolbar">
          <input v-model="filters.q" placeholder="Rechercher IP, titre, type" />
          <select v-model="filters.severity">
            <option value="">Toutes severites</option>
            <option>Critical</option>
            <option>High</option>
            <option>Medium</option>
            <option>Low</option>
          </select>
        </section>

        <section v-if="activeView === 'incidents'" class="content-grid">
          <div class="incident-list">
            <div class="table-scroll">
              <table>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Incident</th>
                    <th>IP</th>
                    <th>Score</th>
                    <th>Severite</th>
                    <th>Statut</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="incident in filteredIncidents"
                    :key="incident.id"
                    :class="{ selected: selectedIncident?.id === incident.id, 'new-alert': newIncidentIds.has(incident.id) }"
                    @click="selectIncident(incident)"
                  >
                    <td>#{{ incident.id }}</td>
                    <td>
                      <strong>{{ incident.title }}</strong>
                      <small>{{ incident.attack_type }} · {{ incident.created_at }}</small>
                    </td>
                    <td>{{ incident.source_ip }}</td>
                    <td>{{ incident.score }}</td>
                    <td><span :class="['badge', incident.severity.toLowerCase()]">{{ incident.severity }}</span></td>
                    <td><span :class="['status-pill', statusClass(incident.status)]">{{ incident.status }}</span></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <aside class="detail-panel" v-if="selectedIncident">
            <div class="detail-head">
              <div>
                <p class="eyebrow">Incident #{{ selectedIncident.id }}</p>
                <h2>{{ selectedIncident.title }}</h2>
              </div>
              <span :class="['badge', selectedIncident.severity.toLowerCase()]">{{ selectedIncident.severity }}</span>
            </div>

            <dl class="detail-grid">
              <div><dt>Type</dt><dd>{{ selectedIncident.attack_type }}</dd></div>
              <div><dt>Source</dt><dd>{{ selectedIncident.source_ip }}</dd></div>
              <div><dt>Confiance</dt><dd>{{ selectedIncident.confidence }}%</dd></div>
              <div><dt>Assigne</dt><dd>{{ selectedIncident.assigned_username || 'Non assigne' }}</dd></div>
            </dl>

            <p class="description">{{ selectedIncident.description }}</p>
            <div class="recommendation">{{ selectedIncident.recommendation || 'Analyse en cours.' }}</div>

            <div class="evidence-list" v-if="selectedIncident.evidence?.length">
              <strong>Preuves</strong>
              <code v-for="item in selectedIncident.evidence" :key="item">{{ item }}</code>
            </div>

            <form class="action-grid" @submit.prevent="updateSelectedIncident">
              <select v-model="editForm.status">
                <option>Nouveau</option>
                <option>En cours</option>
                <option>Résolu</option>
                <option>Clos</option>
              </select>
              <select v-model="editForm.assigned_to">
                <option :value="null">Non assigne</option>
                <option v-for="person in users" :key="person.id" :value="person.id">{{ person.username }}</option>
              </select>
              <button type="submit">Enregistrer</button>
            </form>

            <form class="comment-form" @submit.prevent="addComment">
              <input v-model="comment" placeholder="Commentaire d'investigation" />
              <button type="submit">Ajouter</button>
            </form>

            <div class="timeline">
              <h3>Chronologie</h3>
              <article v-for="event in selectedIncident.events || []" :key="event.id">
                <strong>{{ event.event_type }}</strong>
                <span>{{ event.actor }} · {{ event.created_at }}</span>
                <p>{{ event.message }}</p>
              </article>
            </div>
          </aside>
        </section>

        <section v-else-if="canViewData" class="data-view">
          <div class="data-tabs">
            <button :class="{ active: dataTab === 'sql' }" @click="dataTab = 'sql'">PostgreSQL</button>
            <button :class="{ active: dataTab === 'nosql' }" @click="dataTab = 'nosql'">Elasticsearch</button>
          </div>

          <p v-if="dataError" class="error-message">{{ dataError }}</p>

          <div v-if="dataTab === 'sql'" class="data-stack">
            <article class="data-panel">
              <header>
                <div>
                  <p class="eyebrow">Table SQL</p>
                  <h2>users</h2>
                </div>
                <span>{{ databasePreview.postgresql.users.length }} lignes</span>
              </header>
              <div class="table-scroll">
                <table class="data-table">
                  <thead><tr><th>ID</th><th>Utilisateur</th><th>Role</th><th>Creation</th></tr></thead>
                  <tbody>
                    <tr v-for="row in databasePreview.postgresql.users" :key="row.id">
                      <td>{{ row.id }}</td>
                      <td>{{ row.username }}</td>
                      <td>{{ row.role }}</td>
                      <td>{{ row.created_at }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </article>

            <article class="data-panel">
              <header>
                <div>
                  <p class="eyebrow">Table SQL</p>
                  <h2>incidents</h2>
                </div>
                <span>{{ databasePreview.postgresql.incidents.length }} lignes</span>
              </header>
              <div class="table-scroll">
                <table class="data-table wide">
                  <thead>
                    <tr><th>ID</th><th>Titre</th><th>IP</th><th>Type</th><th>Score</th><th>Severite</th><th>Statut</th><th>Creation</th></tr>
                  </thead>
                  <tbody>
                    <tr v-for="row in databasePreview.postgresql.incidents" :key="row.id">
                      <td>#{{ row.id }}</td>
                      <td>{{ row.title }}</td>
                      <td>{{ row.source_ip }}</td>
                      <td>{{ row.attack_type }}</td>
                      <td>{{ row.score }}</td>
                      <td><span :class="['badge', row.severity.toLowerCase()]">{{ row.severity }}</span></td>
                      <td><span :class="['status-pill', statusClass(row.status)]">{{ row.status }}</span></td>
                      <td>{{ row.created_at }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </article>

            <article class="data-panel">
              <header>
                <div>
                  <p class="eyebrow">Table SQL</p>
                  <h2>incident_events</h2>
                </div>
                <span>{{ databasePreview.postgresql.incident_events.length }} lignes</span>
              </header>
              <div class="table-scroll">
                <table class="data-table wide">
                  <thead><tr><th>ID</th><th>Incident</th><th>Acteur</th><th>Type</th><th>Message</th><th>Creation</th></tr></thead>
                  <tbody>
                    <tr v-for="row in databasePreview.postgresql.incident_events" :key="row.id">
                      <td>{{ row.id }}</td>
                      <td>#{{ row.incident_id }}</td>
                      <td>{{ row.actor }}</td>
                      <td>{{ row.event_type }}</td>
                      <td>{{ row.message }}</td>
                      <td>{{ row.created_at }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </article>
          </div>

          <div v-else class="data-stack">
            <article class="data-panel">
              <header>
                <div>
                  <p class="eyebrow">Index NoSQL</p>
                  <h2>{{ databasePreview.elasticsearch.index }}</h2>
                </div>
                <span>{{ securityLogs.length }} documents</span>
              </header>
              <div class="log-grid">
                <article v-for="(log, index) in securityLogs" :key="`${log.timestamp}-${index}`" class="log-card">
                  <div>
                    <strong>{{ log.event_type || 'event' }}</strong>
                    <span>{{ log.timestamp }}</span>
                  </div>
                  <p>{{ log.message }}</p>
                  <code>{{ formatLog(log) }}</code>
                </article>
              </div>
            </article>
          </div>
        </section>

        <section v-else class="data-view">
          <p class="error-message">Acces reserve aux administrateurs</p>
        </section>
      </section>
    </section>
  </main>
</template>

<script setup>
import { computed, onMounted, onUnmounted, reactive, ref } from 'vue';

const token = ref(localStorage.getItem('socket_token') || '');
const user = ref(JSON.parse(localStorage.getItem('socket_user') || 'null'));
const incidents = ref([]);
const users = ref([]);
const selectedIncident = ref(null);
const loading = ref(false);
const error = ref('');
const dataError = ref('');
const comment = ref('');
const timer = ref(null);
const polling = ref(false);
const firstIncidentLoad = ref(true);
const lastRefreshAt = ref('');
const activeView = ref('incidents');
const dataTab = ref('sql');
const securityLogs = ref([]);
const newIncidentIds = ref(new Set());
const databasePreview = reactive({
  postgresql: {
    users: [],
    incidents: [],
    incident_events: [],
  },
  elasticsearch: {
    index: 'socket-events',
  },
});

const loginForm = reactive({ username: '', password: '' });
const filters = reactive({ q: '', severity: '', status: '' });
const editForm = reactive({ status: 'Nouveau', assigned_to: null });

const apiFetch = async (path, options = {}) => {
  const response = await fetch(`/api/v1${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token.value ? { Authorization: `Bearer ${token.value}` } : {}),
      ...(options.headers || {}),
    },
  });
  if (response.status === 401 && token.value) logout();
  if (!response.ok) throw new Error((await response.json()).detail || 'Erreur API');
  return response.json();
};

const login = async () => {
  loading.value = true;
  error.value = '';
  try {
    const data = await apiFetch('/auth/login', { method: 'POST', body: JSON.stringify(loginForm) });
    token.value = data.access_token;
    user.value = data.user;
    localStorage.setItem('socket_token', token.value);
    localStorage.setItem('socket_user', JSON.stringify(user.value));
    await loadAll();
  } catch (err) {
    error.value = err.message;
  } finally {
    loading.value = false;
  }
};

const logout = () => {
  token.value = '';
  user.value = null;
  selectedIncident.value = null;
  activeView.value = 'incidents';
  incidents.value = [];
  users.value = [];
  newIncidentIds.value = new Set();
  firstIncidentLoad.value = true;
  resetDataViews();
  localStorage.removeItem('socket_token');
  localStorage.removeItem('socket_user');
};

const loadIncidents = async () => {
  if (!token.value) return;
  const previousIds = new Set(incidents.value.map((incident) => incident.id));
  const rows = await apiFetch('/incidents');
  if (!firstIncidentLoad.value) {
    const detectedNewIds = rows
      .filter((incident) => !previousIds.has(incident.id))
      .map((incident) => incident.id);
    if (detectedNewIds.length) {
      newIncidentIds.value = new Set([...newIncidentIds.value, ...detectedNewIds]);
      window.setTimeout(() => {
        newIncidentIds.value = new Set([...newIncidentIds.value].filter((id) => !detectedNewIds.includes(id)));
      }, 9000);
    }
  }
  firstIncidentLoad.value = false;
  incidents.value = rows;
  lastRefreshAt.value = new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  if (!selectedIncident.value && incidents.value.length) await selectIncident(incidents.value[0]);
};

const loadUsers = async () => {
  users.value = await apiFetch('/users');
};

const loadDataViews = async () => {
  if (!token.value || !canViewData.value) {
    resetDataViews();
    return;
  }
  dataError.value = '';
  try {
    const [preview, logs] = await Promise.all([
      apiFetch('/database/preview'),
      apiFetch('/logs/recent'),
    ]);
    Object.assign(databasePreview.postgresql, preview.postgresql);
    Object.assign(databasePreview.elasticsearch, preview.elasticsearch);
    securityLogs.value = logs;
  } catch (err) {
    resetDataViews();
    dataError.value = err.message;
  }
};

const loadAll = async () => {
  await Promise.all([loadIncidents(), loadUsers(), loadDataViews()]);
  if (selectedIncident.value) await selectIncident(selectedIncident.value);
};

const refreshLiveData = async () => {
  if (!token.value || polling.value) return;
  polling.value = true;
  try {
    await loadIncidents();
    if (activeView.value === 'data' && canViewData.value) await loadDataViews();
  } catch (err) {
    error.value = err.message;
  } finally {
    polling.value = false;
  }
};

const openDataView = async () => {
  if (!canViewData.value) {
    activeView.value = 'incidents';
    resetDataViews();
    return;
  }
  activeView.value = 'data';
  await loadDataViews();
};

const selectIncident = async (incident) => {
  selectedIncident.value = await apiFetch(`/incidents/${incident.id}`);
  editForm.status = selectedIncident.value.status;
  editForm.assigned_to = selectedIncident.value.assigned_to;
};

const updateSelectedIncident = async () => {
  const updated = await apiFetch(`/incidents/${selectedIncident.value.id}`, {
    method: 'PATCH',
    body: JSON.stringify(editForm),
  });
  selectedIncident.value = { ...selectedIncident.value, ...updated };
  await loadIncidents();
  await selectIncident(updated);
};

const addComment = async () => {
  if (!comment.value.trim()) return;
  await apiFetch(`/incidents/${selectedIncident.value.id}/comments`, {
    method: 'POST',
    body: JSON.stringify({ message: comment.value }),
  });
  comment.value = '';
  await selectIncident(selectedIncident.value);
};

const filteredIncidents = computed(() => incidents.value.filter((incident) => {
  const q = filters.q.trim().toLowerCase();
  const matchQ = !q || [incident.title, incident.source_ip, incident.attack_type]
    .some((value) => String(value || '').toLowerCase().includes(q));
  const matchSeverity = !filters.severity || incident.severity === filters.severity;
  const matchStatus = !filters.status || incident.status === filters.status;
  return matchQ && matchSeverity && matchStatus;
}));

const stats = computed(() => {
  const total = incidents.value.length;
  const critical = incidents.value.filter((item) => item.severity === 'Critical').length;
  const open = incidents.value.filter((item) => !['Résolu', 'Clos'].includes(item.status)).length;
  const avgScore = total ? Math.round(incidents.value.reduce((sum, item) => sum + Number(item.score || 0), 0) / total) : 0;
  return { total, critical, open, avgScore };
});

const statusClass = (value) => String(value || '')
  .toLowerCase()
  .replaceAll(' ', '-')
  .normalize('NFD')
  .replace(/[\u0300-\u036f]/g, '');

const formatLog = (log) => JSON.stringify(log, null, 2);

const canViewData = computed(() => user.value?.role === 'admin');

const resetDataViews = () => {
  databasePreview.postgresql.users = [];
  databasePreview.postgresql.incidents = [];
  databasePreview.postgresql.incident_events = [];
  databasePreview.elasticsearch.index = 'socket-events';
  securityLogs.value = [];
  dataError.value = '';
};

onMounted(async () => {
  if (token.value) await loadAll();
  timer.value = setInterval(refreshLiveData, 2500);
});

onUnmounted(() => clearInterval(timer.value));
</script>
