import { apiFetch } from './api.js';
import { state, selectProject } from './app.js';

let tasks = [];
let activeTaskId = null;
let socket = null;

export function initBoard() {
    bindTaskCreationModal();
    bindTaskDetailModal();
    initDragAndDrop();

    window.addEventListener('project:selected', async (e) => {
        const project = e.detail;
        if (!project) return;
        await loadTasks(project.id);
        connectProjectWebSocket(project.id);
    });
}

async function loadTasks(projectId) {
    tasks = await apiFetch(`/projects/${projectId}/tasks`);
    renderBoard();
}

function renderBoard() {
    const statuses = ['TODO', 'IN_PROGRESS', 'IN_REVIEW', 'DONE'];

    statuses.forEach((status) => {
        const columnBody = document.querySelector(`.kanban-column-body[data-status="${status}"]`);
        const countBadge = document.getElementById(`count-${status}`);
        const filtered = tasks.filter((t) => t.status === status);

        if (countBadge) countBadge.textContent = filtered.length;
        if (!columnBody) return;

        columnBody.innerHTML = '';
        filtered.forEach((task) => {
            columnBody.appendChild(createTaskCard(task));
        });
    });
}

function createTaskCard(task) {
    const card = document.createElement('div');
    card.className = 'task-card';
    card.draggable = true;
    card.dataset.taskId = task.id;

    const isOverdue = task.due_date && new Date(task.due_date) < new Date() && task.status !== 'DONE';
    const dueLabel = task.due_date
        ? new Date(task.due_date).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
        : 'No due date';

    card.innerHTML = `
        <div class="task-card-top">
            <span class="priority-badge prio-${task.priority}">${task.priority}</span>
            <span class="${isOverdue ? 'overdue-tag' : ''}" style="font-size:0.75rem;">
                ${isOverdue ? '⚠ ' : ''}${dueLabel}
            </span>
        </div>
        <div class="task-title">${escapeHtml(task.title)}</div>
        <div class="task-card-footer">
            <span>👤 ${escapeHtml(task.assignee_name || 'Unassigned')}</span>
            <span>💬 ${task.comment_count || 0}</span>
        </div>
    `;

    card.addEventListener('click', () => openTaskDetail(task.id));
    return card;
}

// --- DRAG AND DROP ---
function initDragAndDrop() {
    const board = document.getElementById('kanban-board');
    let draggedTaskId = null;

    board.addEventListener('dragstart', (e) => {
        const card = e.target.closest('.task-card');
        if (!card) return;
        draggedTaskId = card.dataset.taskId;
        card.classList.add('dragging');
        e.dataTransfer.effectAllowed = 'move';
    });

    board.addEventListener('dragend', (e) => {
        const card = e.target.closest('.task-card');
        if (card) card.classList.remove('dragging');
        draggedTaskId = null;
    });

    document.querySelectorAll('.kanban-column-body').forEach((col) => {
        col.addEventListener('dragover', (e) => {
            e.preventDefault();
            col.classList.add('drag-over');
        });

        col.addEventListener('dragleave', () => {
            col.classList.remove('drag-over');
        });

        col.addEventListener('drop', async (e) => {
            e.preventDefault();
            col.classList.remove('drag-over');
            if (!draggedTaskId) return;

            const newStatus = col.dataset.status;
            const task = tasks.find((t) => t.id === draggedTaskId);
            if (!task || task.status === newStatus) return;

            // Optimistic UI move
            task.status = newStatus;
            renderBoard();

            try {
                await apiFetch(`/tasks/${draggedTaskId}`, {
                    method: 'PATCH',
                    body: JSON.stringify({ status: newStatus }),
                });
                if (state.currentProject) {
                    await selectProject(state.currentProject.id);
                }
            } catch (err) {
                alert(err.message);
                if (state.currentProject) await loadTasks(state.currentProject.id);
            }
        });
    });
}

// --- NEW TASK MODAL ---
function bindTaskCreationModal() {
    document.getElementById('btn-open-task-modal').addEventListener('click', () => {
        if (!state.currentProject) return;
        populateMemberSelect('task-assignee-input');
        document.getElementById('modal-task').classList.remove('hidden');
    });

    document.getElementById('form-task').addEventListener('submit', async (e) => {
        e.preventDefault();
        if (!state.currentProject) return;

        const dueRaw = document.getElementById('task-due-input').value;
        const payload = {
            title: document.getElementById('task-title-input').value,
            description: document.getElementById('task-desc-input').value || null,
            priority: document.getElementById('task-priority-input').value,
            status: document.getElementById('task-status-input').value,
            assignee_id: document.getElementById('task-assignee-input').value || null,
            due_date: dueRaw ? new Date(dueRaw).toISOString() : null,
        };

        await apiFetch(`/projects/${state.currentProject.id}/tasks`, {
            method: 'POST',
            body: JSON.stringify(payload),
        });

        e.target.reset();
        document.getElementById('modal-task').classList.add('hidden');
        await selectProject(state.currentProject.id);
    });
}

// --- TASK DETAIL & COMMENTS ---
async function openTaskDetail(taskId) {
    activeTaskId = taskId;
    const task = tasks.find((t) => t.id === taskId);
    if (!task) return;

    populateMemberSelect('detail-assignee-select', task.assignee_id);

    document.getElementById('detail-task-title').textContent = task.title;
    document.getElementById('detail-task-desc').textContent = task.description || 'No description provided.';
    document.getElementById('detail-status-select').value = task.status;
    document.getElementById('detail-priority-select').value = task.priority;
    document.getElementById('detail-due-text').textContent = task.due_date
        ? `Due: ${new Date(task.due_date).toLocaleString()}`
        : 'No deadline set';

    document.getElementById('modal-task-detail').classList.remove('hidden');
    await loadComments(taskId);
}

function bindTaskDetailModal() {
    const updateField = async (patchPayload) => {
        if (!activeTaskId) return;
        await apiFetch(`/tasks/${activeTaskId}`, {
            method: 'PATCH',
            body: JSON.stringify(patchPayload),
        });
        if (state.currentProject) {
            await selectProject(state.currentProject.id);
        }
    };

    document.getElementById('detail-status-select').addEventListener('change', (e) => {
        updateField({ status: e.target.value });
    });

    document.getElementById('detail-priority-select').addEventListener('change', (e) => {
        updateField({ priority: e.target.value });
    });

    document.getElementById('detail-assignee-select').addEventListener('change', (e) => {
        updateField({ assignee_id: e.target.value || null });
    });

    document.getElementById('btn-delete-task').addEventListener('click', async () => {
        if (!activeTaskId || !confirm('Delete this task permanently?')) return;
        await apiFetch(`/tasks/${activeTaskId}`, { method: 'DELETE' });
        document.getElementById('modal-task-detail').classList.add('hidden');
        activeTaskId = null;
        if (state.currentProject) {
            await selectProject(state.currentProject.id);
        }
    });

    document.getElementById('form-comment').addEventListener('submit', async (e) => {
        e.preventDefault();
        if (!activeTaskId) return;
        const input = document.getElementById('comment-input');
        const content = input.value.trim();
        if (!content) return;

        await apiFetch(`/tasks/${activeTaskId}/comments`, {
            method: 'POST',
            body: JSON.stringify({ content }),
        });
        input.value = '';
        await loadComments(activeTaskId);
        if (state.currentProject) {
            await loadTasks(state.currentProject.id);
        }
    });
}

async function loadComments(taskId) {
    const comments = await apiFetch(`/tasks/${taskId}/comments`);
    const list = document.getElementById('comment-list');
    list.innerHTML = '';

    if (comments.length === 0) {
        list.innerHTML = '<p class="muted-text">No comments yet. Start the discussion below.</p>';
        return;
    }

    comments.forEach((c) => {
        const div = document.createElement('div');
        div.className = 'comment-item';
        const timeStr = new Date(c.created_at).toLocaleString(undefined, {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
        });
        div.innerHTML = `
            <div class="comment-meta">
                <strong>${escapeHtml(c.author_name)}</strong>
                <span>${timeStr}</span>
            </div>
            <div>${escapeHtml(c.content)}</div>
        `;
        list.appendChild(div);
    });
    list.scrollTop = list.scrollHeight;
}

function populateMemberSelect(selectId, selectedId = null) {
    const select = document.getElementById(selectId);
    if (!select) return;
    select.innerHTML = '<option value="">Unassigned</option>';
    (state.members || []).forEach((m) => {
        const opt = document.createElement('option');
        opt.value = m.user_id;
        opt.textContent = `${m.full_name} (${m.role})`;
        if (selectedId && m.user_id === selectedId) opt.selected = true;
        select.appendChild(opt);
    });
}

// --- REAL-TIME WEBSOCKETS ---
function connectProjectWebSocket(projectId) {
    if (socket) {
        socket.close();
        socket = null;
    }

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/api/ws/projects/${projectId}`;
    const liveBadge = document.getElementById('ws-live-indicator');

    socket = new WebSocket(wsUrl);

    socket.onopen = () => {
        if (liveBadge) liveBadge.classList.remove('hidden');
    };

    socket.onclose = () => {
        if (liveBadge) liveBadge.classList.add('hidden');
    };

    socket.onmessage = async (event) => {
        const msg = JSON.parse(event.data);
        if (!state.currentProject || state.currentProject.id !== projectId) return;

        if (['TASK_CREATED', 'TASK_UPDATED', 'TASK_DELETED'].includes(msg.event)) {
            await loadTasks(projectId);
        }
        if (msg.event === 'COMMENT_CREATED' && activeTaskId === msg.comment.task_id) {
            await loadComments(activeTaskId);
        }
    };
}

function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/[&<>"']/g, (m) => ({
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;',
    })[m]);
}