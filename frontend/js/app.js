import { apiFetch, getToken, setToken, clearToken } from './api.js';
import { initUIEnhancements, hidePreloader, animateCounter } from './ui.js';
import { initBoard } from './board.js';

export const state = {
    user: null,
    workspaces: [],
    currentWorkspaceId: null,
    members: [],
    projects: [],
    currentProject: null,
};

const authView = document.getElementById('auth-view');
const appView = document.getElementById('app-view');
const authError = document.getElementById('auth-error');

async function init() {
    initUIEnhancements();
    initBoard();
    bindAuthEvents();
    bindModalEvents();
    bindWorkspaceAndProjectEvents();
    bindProfileEvents();

    window.addEventListener('auth:logout', showAuthView);

    if (getToken()) {
        try {
            state.user = await apiFetch('/auth/me');
            await showAppView();
        } catch {
            showAuthView();
        }
    } else {
        showAuthView();
    }

    hidePreloader();
}

function showAuthView() {
    authView.classList.remove('hidden');
    appView.classList.add('hidden');
}

async function showAppView() {
    authView.classList.add('hidden');
    appView.classList.remove('hidden');

    document.getElementById('user-name').textContent = state.user.full_name;
    document.getElementById('user-avatar').textContent = state.user.full_name.charAt(0).toUpperCase();

    await loadWorkspaces();
}

function bindAuthEvents() {
    const tabLogin = document.getElementById('tab-login');
    const tabRegister = document.getElementById('tab-register');
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');

    tabLogin.addEventListener('click', () => {
        tabLogin.classList.add('active');
        tabRegister.classList.remove('active');
        loginForm.classList.remove('hidden');
        registerForm.classList.add('hidden');
        authError.classList.add('hidden');
    });

    tabRegister.addEventListener('click', () => {
        tabRegister.classList.add('active');
        tabLogin.classList.remove('active');
        registerForm.classList.remove('hidden');
        loginForm.classList.add('hidden');
        authError.classList.add('hidden');
    });

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        authError.classList.add('hidden');
        try {
            const formBody = new URLSearchParams({
                username: document.getElementById('login-email').value,
                password: document.getElementById('login-password').value,
            });
            const data = await apiFetch('/auth/login', { method: 'POST', body: formBody });
            setToken(data.access_token);
            state.user = await apiFetch('/auth/me');
            await showAppView();
        } catch (err) {
            authError.textContent = err.message;
            authError.classList.remove('hidden');
        }
    });

    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        authError.classList.add('hidden');
        try {
            const email = document.getElementById('reg-email').value;
            const password = document.getElementById('reg-password').value;
            const full_name = document.getElementById('reg-name').value;

            await apiFetch('/auth/register', {
                method: 'POST',
                body: JSON.stringify({ email, password, full_name }),
            });

            const formBody = new URLSearchParams({ username: email, password });
            const data = await apiFetch('/auth/login', { method: 'POST', body: formBody });
            setToken(data.access_token);
            state.user = await apiFetch('/auth/me');
            await showAppView();
        } catch (err) {
            authError.textContent = err.message;
            authError.classList.remove('hidden');
        }
    });

    document.getElementById('btn-logout').addEventListener('click', () => {
        clearToken();
        showAuthView();
    });
}

// --- USER PROFILE & INTERACTIVE WORKSPACE / PROJECT SWITCHER ---
function bindProfileEvents() {
    document.getElementById('btn-open-profile-nav')?.addEventListener('click', openProfileView);
    document.getElementById('btn-open-profile-sidebar')?.addEventListener('click', openProfileView);

    document.getElementById('btn-back-to-board')?.addEventListener('click', () => {
        document.getElementById('profile-view').classList.add('hidden');
        if (state.currentProject) {
            document.getElementById('project-view').classList.remove('hidden');
            document.getElementById('breadcrumb-title').textContent = state.currentProject.name;
        } else {
            document.getElementById('empty-state').classList.remove('hidden');
            document.getElementById('breadcrumb-title').textContent = 'Dashboard';
        }
    });

    // Toggle Workspace Explorer panel when clicking the 01 / WORKSPACES card
    document.getElementById('profile-ws-tile-trigger')?.addEventListener('click', () => {
        const trigger = document.getElementById('profile-ws-tile-trigger');
        const explorer = document.getElementById('profile-workspace-explorer');
        trigger.classList.toggle('expanded');
        explorer.classList.toggle('hidden');
        if (!explorer.classList.contains('hidden')) {
            renderProfileWorkspaceExplorer();
        }
    });
}

async function openProfileView() {
    if (!state.user) return;

    document.getElementById('empty-state').classList.add('hidden');
    document.getElementById('project-view').classList.add('hidden');
    document.getElementById('profile-view').classList.remove('hidden');
    document.getElementById('breadcrumb-title').textContent = 'My Profile';

    const activeWs = state.workspaces.find((w) => w.id === state.currentWorkspaceId);
    const joinedDate = state.user.created_at
        ? new Date(state.user.created_at).toLocaleDateString(undefined, {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
        })
        : '—';

    document.getElementById('profile-hero-name').textContent = state.user.full_name;
    document.getElementById('profile-hero-email').textContent = state.user.email;
    document.getElementById('profile-ws-count').textContent = state.workspaces.length;
    document.getElementById('profile-current-role').textContent = activeWs?.role || 'MEMBER';
    document.getElementById('profile-ws-name').textContent = activeWs?.name || 'No Workspace';
    document.getElementById('profile-joined-date').textContent = joinedDate;
    document.getElementById('profile-user-id').textContent = state.user.id.slice(0, 8) + '...';

    renderProfileWorkspaceExplorer();
    await renderProfileAssignedTasks();
}

function renderProfileWorkspaceExplorer() {
    const cardsContainer = document.getElementById('profile-workspace-cards');
    if (!cardsContainer) return;
    cardsContainer.innerHTML = '';

    const tileStyles = ['tile-cerise', 'tile-royal', 'tile-coral'];

    if (state.workspaces.length === 0) {
        cardsContainer.innerHTML = '<p class="muted-text">No workspaces yet. Create one from the sidebar.</p>';
        return;
    }

    state.workspaces.forEach((ws, idx) => {
        const isSelected = ws.id === state.currentWorkspaceId;
        const card = document.createElement('div');
        card.className = `vivid-tile ${tileStyles[idx % tileStyles.length]} ws-choice-card hover-lift ${isSelected ? 'selected-ws' : ''
            }`;
        card.innerHTML = `
            <span class="tile-kicker">${isSelected ? '● ACTIVE WORKSPACE' : 'CLICK TO SELECT'}</span>
            <h3 class="hover-grow">${ws.name}</h3>
            <p>Your Role: <strong>${ws.role}</strong></p>
        `;
        card.addEventListener('click', async () => {
            if (state.currentWorkspaceId !== ws.id) {
                state.currentWorkspaceId = ws.id;
                state.currentProject = null;
                document.getElementById('workspace-select').value = ws.id;
                const activeWs = state.workspaces.find((w) => w.id === ws.id);
                document.getElementById('user-role-badge').textContent = activeWs?.role || 'MEMBER';
                document.getElementById('profile-current-role').textContent = activeWs?.role || 'MEMBER';
                document.getElementById('profile-ws-name').textContent = activeWs?.name || '';

                await Promise.all([loadMembers(), loadProjects(/* keepOnProfile = */ true)]);
            }
            renderProfileWorkspaceExplorer();
            await renderProfileAssignedTasks();
        });
        cardsContainer.appendChild(card);
    });

    // Update Selected Workspace Info & Project Cards
    const activeWs = state.workspaces.find((w) => w.id === state.currentWorkspaceId);
    if (!activeWs) return;

    const wsCreated = activeWs.created_at
        ? new Date(activeWs.created_at).toLocaleDateString(undefined, {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
        })
        : '—';

    document.getElementById('ws-detail-title').textContent = activeWs.name;
    document.getElementById('ws-detail-meta').textContent = `Role: ${activeWs.role} • Created: ${wsCreated}`;
    document.getElementById('ws-detail-members-badge').textContent = `${state.members.length} Member${state.members.length === 1 ? '' : 's'
        }`;
    document.getElementById('ws-detail-projects-badge').textContent = `${state.projects.length} Project${state.projects.length === 1 ? '' : 's'
        }`;

    const projGrid = document.getElementById('profile-ws-project-cards');
    projGrid.innerHTML = '';

    if (state.projects.length === 0) {
        projGrid.innerHTML = '<p class="muted-text">No projects in this workspace yet.</p>';
        return;
    }

    state.projects.forEach((proj) => {
        const isCurrentProj = state.currentProject && state.currentProject.id === proj.id;
        const pct = proj.progress?.completion_percentage ?? 0;
        const total = proj.progress?.total_tasks ?? 0;

        const pCard = document.createElement('div');
        pCard.className = `profile-project-card hover-lift ${isCurrentProj ? 'active-proj-card' : ''}`;
        pCard.innerHTML = `
            <div>
                <div class="profile-proj-top">
                    <strong>${proj.name}</strong>
                    <span class="status-chip">${pct}%</span>
                </div>
                <p class="muted-text" style="font-size: 0.82rem;">${proj.description || 'No project description.'
            }</p>
            </div>
            <div class="task-card-footer" style="margin-top:0.2rem;">
                <span>${total} Task${total === 1 ? '' : 's'}</span>
                <span style="color: var(--cerise); font-weight: 700;">
                    ${isCurrentProj ? 'Active • Open Board →' : 'Set Active & Open →'}
                </span>
            </div>
        `;
        pCard.addEventListener('click', async () => {
            await selectProject(proj.id);
        });
        projGrid.appendChild(pCard);
    });
}

async function renderProfileAssignedTasks() {
    const listEl = document.getElementById('profile-assigned-list');
    const countEl = document.getElementById('profile-assigned-count');
    listEl.innerHTML = '';

    if (!state.currentProject) {
        countEl.textContent = '0 Tasks';
        listEl.innerHTML = '<p class="muted-text">Select a project above to inspect your assigned tasks.</p>';
        return;
    }

    const assignedTasks = await apiFetch(
        `/projects/${state.currentProject.id}/tasks?assignee_id=${state.user.id}`
    );
    countEl.textContent = `${assignedTasks.length} Task${assignedTasks.length === 1 ? '' : 's'}`;

    if (assignedTasks.length === 0) {
        listEl.innerHTML = `<p class="muted-text">No tasks assigned to you in <strong>${state.currentProject.name}</strong> yet.</p>`;
        return;
    }

    assignedTasks.forEach((task) => {
        const row = document.createElement('div');
        row.className = 'assigned-task-row';
        row.innerHTML = `
            <div>
                <strong>${task.title}</strong>
                <div class="muted-text">${task.description || 'No description'}</div>
            </div>
            <div class="assigned-task-badges">
                <span class="priority-badge prio-${task.priority}">${task.priority}</span>
                <span class="status-chip">${task.status.replace('_', ' ')}</span>
            </div>
        `;
        listEl.appendChild(row);
    });
}

export async function syncProfileIfOpen() {
    const profileView = document.getElementById('profile-view');
    if (!profileView || profileView.classList.contains('hidden')) return;

    document.getElementById('profile-ws-count').textContent = state.workspaces.length;
    renderProfileWorkspaceExplorer();
    await renderProfileAssignedTasks();
}

// --- WORKSPACES & TEAM ---
async function loadWorkspaces() {
    state.workspaces = await apiFetch('/workspaces');
    const select = document.getElementById('workspace-select');
    select.innerHTML = '';

    if (state.workspaces.length === 0) {
        state.currentWorkspaceId = null;
        document.getElementById('project-list').innerHTML = '';
        document.getElementById('profile-view').classList.add('hidden');
        document.getElementById('empty-state').classList.remove('hidden');
        document.getElementById('project-view').classList.add('hidden');
        return;
    }

    state.workspaces.forEach((ws) => {
        const opt = document.createElement('option');
        opt.value = ws.id;
        opt.textContent = ws.name;
        select.appendChild(opt);
    });

    if (!state.currentWorkspaceId || !state.workspaces.some((w) => w.id === state.currentWorkspaceId)) {
        state.currentWorkspaceId = state.workspaces[0].id;
    }
    select.value = state.currentWorkspaceId;

    const activeWs = state.workspaces.find((w) => w.id === state.currentWorkspaceId);
    document.getElementById('user-role-badge').textContent = activeWs?.role || 'MEMBER';

    await Promise.all([loadMembers(), loadProjects()]);
}

async function loadMembers() {
    if (!state.currentWorkspaceId) return;
    state.members = await apiFetch(`/workspaces/${state.currentWorkspaceId}/members`);
    renderTeamList();
}

function renderTeamList() {
    const list = document.getElementById('team-member-list');
    list.innerHTML = '';

    state.members.forEach((m) => {
        const li = document.createElement('li');
        li.className = 'member-item';
        li.innerHTML = `
            <div>
                <strong>${m.full_name}</strong>
                <div class="muted-text">${m.email}</div>
            </div>
            <div>
                <span class="role-pill" style="color:var(--primary);font-weight:700;">${m.role}</span>
            </div>
        `;
        list.appendChild(li);
    });
}

// --- PROJECTS & PROGRESS ---
async function loadProjects(keepOnProfile = false) {
    if (!state.currentWorkspaceId) return;
    state.projects = await apiFetch(`/workspaces/${state.currentWorkspaceId}/projects`);
    const list = document.getElementById('project-list');
    list.innerHTML = '';

    if (state.projects.length === 0) {
        state.currentProject = null;
        if (!keepOnProfile) {
            document.getElementById('profile-view').classList.add('hidden');
            document.getElementById('empty-state').classList.remove('hidden');
            document.getElementById('project-view').classList.add('hidden');
        }
        return;
    }

    state.projects.forEach((proj) => {
        const li = document.createElement('li');
        li.className = 'nav-item';
        li.dataset.projectId = proj.id;
        li.innerHTML = `<span>${proj.name}</span><small>${proj.progress?.completion_percentage ?? 0}%</small>`;
        li.addEventListener('click', () => selectProject(proj.id));
        list.appendChild(li);
    });

    const targetId =
        state.currentProject && state.projects.some((p) => p.id === state.currentProject.id)
            ? state.currentProject.id
            : state.projects[0].id;

    if (keepOnProfile) {
        state.currentProject = await apiFetch(`/projects/${targetId}`);
        document.querySelectorAll('#project-list .nav-item').forEach((el) => {
            el.classList.toggle('active', el.dataset.projectId === targetId);
        });
    } else {
        await selectProject(targetId);
    }
}

export async function selectProject(projectId) {
    state.currentProject = await apiFetch(`/projects/${projectId}`);

    document.querySelectorAll('#project-list .nav-item').forEach((el) => {
        el.classList.toggle('active', el.dataset.projectId === projectId);
    });

    document.getElementById('profile-view').classList.add('hidden');
    document.getElementById('empty-state').classList.add('hidden');
    document.getElementById('project-view').classList.remove('hidden');

    document.getElementById('breadcrumb-title').textContent = state.currentProject.name;
    document.getElementById('proj-title').textContent = state.currentProject.name;
    document.getElementById('proj-desc').textContent = state.currentProject.description || 'No description provided.';

    const deadlineBadge = document.getElementById('proj-deadline-badge');
    if (state.currentProject.target_end_date) {
        deadlineBadge.textContent = `Target: ${state.currentProject.target_end_date}`;
        deadlineBadge.classList.remove('hidden');
    } else {
        deadlineBadge.classList.add('hidden');
    }

    renderProjectProgress(state.currentProject.progress);
    window.dispatchEvent(new CustomEvent('project:selected', { detail: state.currentProject }));
}

export function renderProjectProgress(progress) {
    if (!progress) return;
    animateCounter(document.getElementById('progress-percent'), progress.completion_percentage, '%');
    document.getElementById('progress-fill').style.width = `${progress.completion_percentage}%`;
    animateCounter(document.getElementById('stat-total'), progress.total_tasks);
    animateCounter(document.getElementById('stat-todo'), progress.todo);
    animateCounter(document.getElementById('stat-progress'), progress.in_progress);
    animateCounter(document.getElementById('stat-review'), progress.in_review);
    animateCounter(document.getElementById('stat-done'), progress.done);
    animateCounter(document.getElementById('stat-overdue'), progress.overdue);

    syncProfileIfOpen();
}

// --- MODALS & FORM SUBMISSIONS ---
function bindModalEvents() {
    document.getElementById('btn-open-ws-modal').addEventListener('click', () => {
        document.getElementById('modal-workspace').classList.remove('hidden');
    });

    document.getElementById('btn-open-proj-modal').addEventListener('click', () => {
        if (!state.currentWorkspaceId) return alert('Create a workspace first.');
        document.getElementById('modal-project').classList.remove('hidden');
    });

    document.getElementById('btn-open-team-modal').addEventListener('click', () => {
        if (!state.currentWorkspaceId) return alert('Create a workspace first.');
        document.getElementById('team-error').classList.add('hidden');
        document.getElementById('modal-team').classList.remove('hidden');
    });

    document.querySelectorAll('.close-modal').forEach((btn) => {
        btn.addEventListener('click', () => {
            document.getElementById(btn.dataset.close).classList.add('hidden');
        });
    });
}

function bindWorkspaceAndProjectEvents() {
    document.getElementById('workspace-select').addEventListener('change', async (e) => {
        state.currentWorkspaceId = e.target.value;
        state.currentProject = null;
        await loadWorkspaces();
    });

    document.getElementById('form-workspace').addEventListener('submit', async (e) => {
        e.preventDefault();
        const name = document.getElementById('ws-name-input').value;
        const ws = await apiFetch('/workspaces', {
            method: 'POST',
            body: JSON.stringify({ name }),
        });
        document.getElementById('ws-name-input').value = '';
        document.getElementById('modal-workspace').classList.add('hidden');
        state.currentWorkspaceId = ws.id;
        await loadWorkspaces();
    });

    document.getElementById('form-project').addEventListener('submit', async (e) => {
        e.preventDefault();
        const name = document.getElementById('proj-name-input').value;
        const description = document.getElementById('proj-desc-input').value || null;
        const target_end_date = document.getElementById('proj-date-input').value || null;

        const proj = await apiFetch(`/workspaces/${state.currentWorkspaceId}/projects`, {
            method: 'POST',
            body: JSON.stringify({ name, description, target_end_date }),
        });
        e.target.reset();
        document.getElementById('modal-project').classList.add('hidden');
        state.currentProject = proj;
        await loadProjects();
    });

    document.getElementById('form-invite').addEventListener('submit', async (e) => {
        e.preventDefault();
        const teamError = document.getElementById('team-error');
        teamError.classList.add('hidden');
        try {
            const email = document.getElementById('invite-email').value;
            const role = document.getElementById('invite-role').value;
            await apiFetch(`/workspaces/${state.currentWorkspaceId}/members`, {
                method: 'POST',
                body: JSON.stringify({ email, role }),
            });
            document.getElementById('invite-email').value = '';
            await loadMembers();
        } catch (err) {
            teamError.textContent = err.message;
            teamError.classList.remove('hidden');
        }
    });
}

init();