const STATUS_STYLES = {
  Applied: "bg-sky-50 text-sky-700 ring-sky-600/10",
  Interview: "bg-violet-50 text-violet-700 ring-violet-600/10",
  "Interview Scheduled": "bg-violet-50 text-violet-700 ring-violet-600/10",
  "Interview Taken": "bg-indigo-50 text-indigo-700 ring-indigo-600/10",
  Accepted: "bg-emerald-50 text-emerald-700 ring-emerald-600/10",
  Rejected: "bg-rose-50 text-rose-700 ring-rose-600/10",
};

document.addEventListener("DOMContentLoaded", () => {
  const table = document.getElementById("applications-table");
  if (!table) return;

  const search = document.getElementById("application-search");
  const statusFilter = document.getElementById("status-filter");
  const modal = document.getElementById("application-modal");
  const form = document.getElementById("application-form");
  const message = document.getElementById("form-message");
  let applications = [];
  let userProfile = null;
  let redirectingToLogin = false;

  if (!localStorage.getItem("access_token")) {
    window.location.replace("./login.html");
    return;
  }

  const escapeHtml = (value) => String(value ?? "").replace(/[&<>"']/g, (char) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  })[char]);

  const setText = (id, value) => {
    const node = document.getElementById(id);
    if (node) node.textContent = value;
  };

  function updateProfileView(profile) {
    userProfile = profile;
    const name = profile.full_name || "ApplyWise user";
    const initials = name.trim().split(/\s+/).slice(0, 2).map((part) => part.charAt(0)).join("").toUpperCase();
    const firstName = name.trim().split(/\s+/)[0] || "there";
    const hour = new Date().getHours();
    const greeting = hour < 12 ? "morning" : hour < 17 ? "afternoon" : "evening";
    ["profile-name", "profile-modal-name"].forEach((id) => setText(id, name));
    ["profile-email"].forEach((id) => setText(id, profile.email || ""));
    ["profile-initials", "profile-initials-top", "profile-initials-mobile", "profile-modal-initials"].forEach((id) => setText(id, initials || "?"));
    setText("greeting-name", firstName);
    setText("greeting-time", greeting);
    const nameInput = document.getElementById("profile-full-name");
    const emailInput = document.getElementById("profile-email-input");
    if (nameInput) nameInput.value = name;
    if (emailInput) emailInput.value = profile.email || "";
  }

  const displayDate = (value) => {
    if (!value) return "-";
    const [year, month, day] = value.slice(0, 10).split("-").map(Number);
    return new Date(year, month - 1, day).toLocaleDateString(undefined, {
      year: "numeric", month: "short", day: "numeric",
    });
  };

  function handleAuthError(error) {
    if (error.status !== 401 && error.status !== 403) return false;
    localStorage.removeItem("access_token");
    if (!redirectingToLogin) {
      redirectingToLogin = true;
      window.location.replace("./login.html");
    }
    return true;
  }

  async function loadProfile() {
    try {
      updateProfileView(await apiRequest("/auth/me"));
    } catch (error) {
      if (handleAuthError(error)) return;
      document.getElementById("profile-name").textContent = "Profile unavailable";
      document.getElementById("profile-email").textContent = error.message;
      document.getElementById("profile-initials").textContent = "!";
      document.getElementById("profile-initials").classList.add("bg-rose-100", "text-rose-700");
    }
  }

  function render() {
    const selectedStatus = statusFilter?.value || "";
    const filtered = window.filterApplications(applications, search?.value || "", selectedStatus);
    const count = (predicate) => applications.filter((item) => predicate(item.status)).length;
    setText("total-count", applications.length);
    setText("table-count", filtered.length);
    setText("table-tab-count", `All (${filtered.length})`);
    setText("progress-count", count((s) => s === "Applied" || s.startsWith("Interview")));
    setText("interview-count", count((s) => s.startsWith("Interview")));
    setText("offer-count", count((s) => s === "Accepted"));

    if (!filtered.length) {
      const emptyText = applications.length
        ? "No applications match these filters. Try a different search."
        : "No applications yet. Add your first one to get started.";
      table.innerHTML = `<tr><td colspan="6" class="px-6 py-12 text-center"><svg class="mx-auto h-[112px] w-[190px]" viewBox="0 0 190 112" fill="none" aria-hidden="true"><ellipse cx="93" cy="91" rx="65" ry="16" fill="#F0E9FF"/><rect x="47" y="12" width="76" height="82" rx="13" fill="#D9C8FF"/><rect x="56" y="20" width="62" height="70" rx="10" fill="url(#emptyCard)"/><path d="M73 37h28M73 48h28M73 59h18" stroke="white" stroke-width="5" stroke-linecap="round"/><circle cx="119" cy="72" r="22" fill="#F3EDFF" stroke="#7938EF" stroke-width="8"/><path d="m135 88 17 15" stroke="#7938EF" stroke-width="9" stroke-linecap="round"/><path d="m34 32 9 5-9 5m116-21 8 4-8 4" stroke="#9E68F5" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/><defs><linearGradient id="emptyCard" x1="57" y1="20" x2="116" y2="90"><stop stop-color="#B47AFF"/><stop offset="1" stop-color="#7937E9"/></linearGradient></defs></svg><p class="mt-2 text-[18px] font-extrabold text-[#15163b]">${applications.length ? "No applications match" : "No applications yet"}</p><p class="mx-auto mt-1 max-w-md text-sm text-[#62658f]">${emptyText}</p>${applications.length ? "" : '<button id="empty-add-application" type="button" class="mt-4 inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-[#772fe8] to-[#5423cf] px-5 py-3 text-sm font-bold text-white shadow-lg shadow-violet-200">Add your first application</button>'}</td></tr>`;
      document.getElementById("empty-add-application")?.addEventListener("click", () => openForm());
      return;
    }

    table.innerHTML = filtered.map((item) => `<tr class="transition hover:bg-slate-50/80">
      <td class="px-6 py-4"><div class="flex items-center gap-3"><span class="grid size-9 shrink-0 place-items-center rounded-xl bg-violet-50 text-sm font-bold text-violet-700">${escapeHtml(item.company_name.trim().charAt(0).toUpperCase())}</span><span class="font-semibold text-slate-800">${escapeHtml(item.company_name)}</span></div></td>
      <td class="px-6 py-4 text-sm text-slate-600">${escapeHtml(item.job_title)}</td>
      <td class="px-6 py-4"><span class="inline-flex items-center rounded-full px-2.5 py-1 text-xs font-semibold ring-1 ring-inset ${STATUS_STYLES[item.status] || "bg-slate-50 text-slate-600 ring-slate-500/10"}">${escapeHtml(item.status)}</span></td>
      <td class="whitespace-nowrap px-6 py-4 text-sm text-slate-500">${displayDate(item.applied_date)}</td>
      <td class="max-w-xs truncate px-6 py-4 text-sm text-slate-500" title="${escapeHtml(item.notes || "")}">${escapeHtml(item.notes || "-")}</td>
      <td class="whitespace-nowrap px-6 py-4 text-right"><button data-action="edit" data-id="${item.id}" class="mr-1 rounded-lg px-2.5 py-1.5 text-xs font-semibold text-violet-700 transition hover:bg-violet-50">Edit</button><button data-action="delete" data-id="${item.id}" class="rounded-lg px-2.5 py-1.5 text-xs font-semibold text-rose-600 transition hover:bg-rose-50">Delete</button></td>
    </tr>`).join("");
  }

  async function loadApplications() {
    try {
      applications = [];
      let skip = 0;
      let page;
      do {
        page = await apiRequest(`/applications/?skip=${skip}&limit=100`);
        applications.push(...page);
        skip += page.length;
      } while (page.length === 100);
      render();
    } catch (error) {
      if (handleAuthError(error)) return;
      table.innerHTML = `<tr><td colspan="6" class="px-6 py-10 text-center"><p class="text-sm font-semibold text-rose-700">We couldn't load your applications.</p><p class="mt-1 text-sm text-slate-500">${escapeHtml(error.message)}. Check that the API is running, then <button id="retry-load" class="font-semibold text-violet-700 underline">try again</button>.</p></td></tr>`;
      document.getElementById("retry-load")?.addEventListener("click", loadApplications);
    }
  }

  function openForm(item = null) {
    form.reset();
    message.textContent = "";
    message.classList.add("hidden");
    document.getElementById("application-id").value = item?.id || "";
    document.getElementById("modal-title").textContent = item ? "Edit application" : "Add application";
    document.getElementById("company-name").value = item?.company_name || "";
    document.getElementById("job-title").value = item?.job_title || "";
    document.getElementById("application-status").value = item?.status || "Applied";
    const today = new Date();
    const localToday = new Date(today.getTime() - today.getTimezoneOffset() * 60000).toISOString().slice(0, 10);
    document.getElementById("applied-date").value = item?.applied_date || localToday;
    document.getElementById("application-notes").value = item?.notes || "";
    modal.showModal();
  }

  function openProfile() {
    if (!userProfile) return;
    const profileMessage = document.getElementById("profile-message");
    profileMessage.textContent = "";
    profileMessage.classList.add("hidden");
    updateProfileView(userProfile);
    document.getElementById("profile-modal").showModal();
  }

  document.getElementById("quick-add-application")?.addEventListener("click", () => openForm());
  document.getElementById("sidebar-add-application")?.addEventListener("click", () => openForm());
  document.getElementById("modal-close")?.addEventListener("click", () => modal.close());
  document.getElementById("modal-cancel")?.addEventListener("click", () => modal.close());
  modal?.addEventListener("click", (event) => { if (event.target === modal) modal.close(); });
  search?.addEventListener("input", render);
  statusFilter?.addEventListener("change", render);
  search?.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      search.value = "";
      render();
      search.blur();
    }
  });

  document.addEventListener("keydown", (event) => {
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") {
      event.preventDefault();
      search?.focus();
    }
  });

  document.querySelectorAll("[data-profile-open]").forEach((button) => button.addEventListener("click", openProfile));
  document.querySelectorAll("[data-close-dialog]").forEach((button) => {
    button.addEventListener("click", () => document.getElementById(button.dataset.closeDialog)?.close());
  });
  ["notifications-button", "notifications-top-button"].forEach((id) => {
    document.getElementById(id)?.addEventListener("click", () => document.getElementById("notifications-modal").showModal());
  });
  document.getElementById("help-button")?.addEventListener("click", () => document.getElementById("help-modal").showModal());

  document.getElementById("profile-form")?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const saveButton = document.getElementById("save-profile");
    const profileMessage = document.getElementById("profile-message");
    saveButton.disabled = true;
    saveButton.textContent = "Saving...";
    profileMessage.classList.add("hidden");
    try {
      const updated = await apiRequest("/auth/me", {
        method: "PATCH",
        body: JSON.stringify({
          full_name: document.getElementById("profile-full-name").value.trim(),
          email: document.getElementById("profile-email-input").value.trim(),
        }),
      });
      updateProfileView(updated);
      document.getElementById("profile-modal").close();
    } catch (error) {
      if (handleAuthError(error)) return;
      profileMessage.textContent = error.message;
      profileMessage.classList.remove("hidden");
    } finally {
      saveButton.disabled = false;
      saveButton.textContent = "Save changes";
    }
  });

  table.addEventListener("click", async (event) => {
    const button = event.target.closest("button[data-action]");
    if (!button) return;
    const item = applications.find((row) => row.id === Number(button.dataset.id));
    if (button.dataset.action === "edit" && item) openForm(item);
    if (button.dataset.action === "delete" && item && window.confirm(`Delete the application to ${item.company_name}?`)) {
      button.disabled = true;
      try {
        await apiRequest(`/applications/${item.id}`, { method: "DELETE" });
        applications = applications.filter((row) => row.id !== item.id);
        render();
      } catch (error) {
        window.alert(`Could not delete application: ${error.message}`);
        button.disabled = false;
      }
    }
  });

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const id = document.getElementById("application-id").value;
    const payload = {
      company_name: document.getElementById("company-name").value.trim(),
      job_title: document.getElementById("job-title").value.trim(),
      status: document.getElementById("application-status").value,
      applied_date: document.getElementById("applied-date").value,
      notes: document.getElementById("application-notes").value.trim() || null,
    };
    const submit = document.getElementById("save-application");
    submit.disabled = true;
    submit.textContent = "Saving...";
    try {
      const saved = await apiRequest(id ? `/applications/${id}` : "/applications/", {
        method: id ? "PATCH" : "POST", body: JSON.stringify(payload),
      });
      applications = id
        ? applications.map((item) => item.id === saved.id ? saved : item)
        : [saved, ...applications];
      modal.close();
      render();
    } catch (error) {
      message.textContent = error.message;
      message.classList.remove("hidden");
    } finally {
      submit.disabled = false;
      submit.textContent = "Save application";
    }
  });

  document.querySelectorAll("[data-logout]").forEach((button) => {
    button.addEventListener("click", () => {
      localStorage.removeItem("access_token");
      window.location.replace("./login.html");
    });
  });

  loadProfile();
  loadApplications();
});
