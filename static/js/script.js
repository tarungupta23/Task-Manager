(() => {
  const tableBody = document.getElementById("task-table-body");
  const emptyState = document.getElementById("empty-state");
  const form = document.getElementById("task-form");
  const formMsg = document.getElementById("form-msg");
  const submitBtn = document.getElementById("form-submit-btn");
  const cancelBtn = document.getElementById("form-cancel-btn");
  const searchInput = document.getElementById("search-input");

  const idInput = document.getElementById("task-id");
  const empIdInput = document.getElementById("emp_id");
  const empNameInput = document.getElementById("emp_name");
  const taskSelect = document.getElementById("task_name");
  const completedSelect = document.getElementById("completed");

  const statTotal = document.getElementById("stat-total");
  const statDone = document.getElementById("stat-done");
  const statPending = document.getElementById("stat-pending");

  let allTasks = [];

  function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
  }

  function showMessage(text, type) {
    formMsg.textContent = text;
    formMsg.className = "form-msg" + (type ? ` is-${type}` : "");
  }

  function updateStats(tasks) {
    const total = tasks.length;
    const done = tasks.filter((t) => t.completed === "Yes").length;
    statTotal.textContent = total;
    statDone.textContent = done;
    statPending.textContent = total - done;
  }

  function renderRows(tasks) {
    tableBody.innerHTML = "";

    if (tasks.length === 0) {
      emptyState.hidden = false;
      return;
    }
    emptyState.hidden = true;

    tasks.forEach((task) => {
      const tr = document.createElement("tr");
      tr.dataset.id = task.id;

      const statusClass = task.completed === "Yes" ? "status-yes" : "status-no";

      tr.innerHTML = `
        <td><span class="id-badge">${escapeHtml(task.emp_id)}</span></td>
        <td>${escapeHtml(task.emp_name)}</td>
        <td>${escapeHtml(task.task_name)}</td>
        <td><span class="status-pill ${statusClass}">${task.completed}</span></td>
        <td class="col-actions">
          <span class="row-actions">
            <button type="button" class="btn btn-ghost btn-icon" data-action="edit">Edit</button>
            <button type="button" class="btn btn-ghost btn-icon" data-action="delete">Delete</button>
          </span>
        </td>
      `;
      tableBody.appendChild(tr);
    });
  }

  async function fetchTasks() {
    try {
      const res = await fetch("/api/tasks");
      if (res.status === 401) {
        window.location.href = "/login";
        return;
      }
      const data = await res.json();
      allTasks = data;
      applyFilter();
      updateStats(allTasks);
    } catch (err) {
      showMessage("Could not load tasks. Check your connection.", "error");
    }
  }

  function applyFilter() {
    const q = searchInput.value.trim().toLowerCase();
    if (!q) {
      renderRows(allTasks);
      return;
    }
    const filtered = allTasks.filter((t) =>
      t.emp_id.toLowerCase().includes(q) ||
      t.emp_name.toLowerCase().includes(q) ||
      t.task_name.toLowerCase().includes(q)
    );
    renderRows(filtered);
  }

  function resetForm() {
    idInput.value = "";
    empIdInput.value = "";
    empNameInput.value = "";
    taskSelect.selectedIndex = 0;
    completedSelect.selectedIndex = 0;
    submitBtn.textContent = "Add task";
    cancelBtn.hidden = true;
    empIdInput.focus();
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    showMessage("", "");

    const payload = {
      emp_id: empIdInput.value.trim(),
      emp_name: empNameInput.value.trim(),
      task_name: taskSelect.value,
      completed: completedSelect.value,
    };

    if (!payload.emp_id || !payload.emp_name || !payload.task_name || !payload.completed) {
      showMessage("Please fill in every field.", "error");
      return;
    }

    const editingId = idInput.value;
    const url = editingId ? `/api/tasks/${editingId}` : "/api/tasks";
    const method = editingId ? "PUT" : "POST";

    try {
      const res = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json();

      if (!res.ok) {
        showMessage(data.error || "Something went wrong.", "error");
        return;
      }

      showMessage(editingId ? "Task updated." : "Task added.", "success");
      resetForm();
      fetchTasks();
    } catch (err) {
      showMessage("Network error. Please try again.", "error");
    }
  });

  cancelBtn.addEventListener("click", resetForm);

  tableBody.addEventListener("click", async (e) => {
    const btn = e.target.closest("button[data-action]");
    if (!btn) return;

    const tr = btn.closest("tr");
    const id = tr.dataset.id;
    const task = allTasks.find((t) => String(t.id) === String(id));
    if (!task) return;

    if (btn.dataset.action === "edit") {
      idInput.value = task.id;
      empIdInput.value = task.emp_id;
      empNameInput.value = task.emp_name;
      taskSelect.value = task.task_name;
      completedSelect.value = task.completed;
      submitBtn.textContent = "Save changes";
      cancelBtn.hidden = false;
      showMessage("", "");
      window.scrollTo({ top: 0, behavior: "smooth" });
      return;
    }

    if (btn.dataset.action === "delete") {
      if (!confirm(`Delete the task for ${task.emp_name} (${task.emp_id})?`)) return;
      try {
        const res = await fetch(`/api/tasks/${id}`, { method: "DELETE" });
        const data = await res.json();
        if (!res.ok) {
          showMessage(data.error || "Could not delete task.", "error");
          return;
        }
        fetchTasks();
      } catch (err) {
        showMessage("Network error. Please try again.", "error");
      }
    }
  });

  searchInput.addEventListener("input", applyFilter);

  fetchTasks();
})();
