document.addEventListener("DOMContentLoaded", () => {
  const fileInput = document.getElementById("resume-file");
  if (!fileInput) return;

  const MAX_FILE_SIZE = 5 * 1024 * 1024;
  const DOCX_TYPE = "application/vnd.openxmlformats-officedocument.wordprocessingml.document";
  const fileDisplay = document.getElementById("selected-file");
  const dropzone = document.getElementById("resume-dropzone");
  const analyzeButton = document.getElementById("analyze-button");
  const message = document.getElementById("upload-message");
  const historyList = document.getElementById("history-list");
  const analysisPanel = document.getElementById("analysis-panel");
  const analysisContent = document.getElementById("analysis-content");
  let selectedFile = null;
  let history = [];

  if (!localStorage.getItem("access_token")) {
    window.location.replace("./login.html");
    return;
  }

  const escapeHtml = (value) => String(value ?? "").replace(/[&<>"']/g, (char) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  })[char]);

  function handleAuthError(error) {
    if (error.status !== 401 && error.status !== 403) return false;
    localStorage.removeItem("access_token");
    window.location.replace("./login.html");
    return true;
  }

  function showMessage(text, type = "error") {
    message.textContent = text;
    message.className = `mt-4 rounded-xl px-4 py-3 text-sm ${type === "success" ? "bg-emerald-50 text-emerald-700" : "bg-rose-50 text-rose-700"}`;
  }

  function clearMessage() {
    message.textContent = "";
    message.className = "mt-4 hidden rounded-xl px-4 py-3 text-sm";
  }

  function formatSize(bytes) {
    return bytes < 1024 * 1024
      ? `${Math.max(1, Math.round(bytes / 1024))} KB`
      : `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  }

  function selectFile(file) {
    clearMessage();
    if (!file) return;
    const name = file.name.toLowerCase();
    const isPdf = name.endsWith(".pdf") && (!file.type || file.type === "application/pdf");
    const isDocx = name.endsWith(".docx") && (!file.type || file.type === DOCX_TYPE);
    if (!isPdf && !isDocx) {
      selectedFile = null;
      fileInput.value = "";
      fileDisplay.classList.add("hidden");
      fileDisplay.classList.remove("flex");
      analyzeButton.disabled = true;
      showMessage("Choose a PDF or DOCX resume file.");
      return;
    }
    if (file.size === 0) {
      selectedFile = null;
      fileInput.value = "";
      fileDisplay.classList.add("hidden");
      fileDisplay.classList.remove("flex");
      analyzeButton.disabled = true;
      showMessage("This file is empty. Choose a resume with readable content.");
      return;
    }
    if (file.size > MAX_FILE_SIZE) {
      selectedFile = null;
      fileInput.value = "";
      fileDisplay.classList.add("hidden");
      fileDisplay.classList.remove("flex");
      analyzeButton.disabled = true;
      showMessage("This file is larger than 5 MB. Choose a smaller resume.");
      return;
    }

    selectedFile = file;
    document.getElementById("selected-file-name").textContent = file.name;
    document.getElementById("selected-file-size").textContent = formatSize(file.size);
    fileDisplay.classList.remove("hidden");
    fileDisplay.classList.add("flex");
    analyzeButton.disabled = false;
  }

  function asArray(value) {
    return Array.isArray(value) ? value : [];
  }

  function emptyState(text = "No details were found in this section.") {
    return `<p class="text-sm text-slate-400">${escapeHtml(text)}</p>`;
  }

  function card(title, body, accent = "violet") {
    const accentClasses = accent === "emerald"
      ? "border-emerald-100 bg-emerald-50/30"
      : accent === "amber"
        ? "border-amber-100 bg-amber-50/30"
        : "border-violet-100 bg-white";
    return `<article class="rounded-[20px] border ${accentClasses} p-5 sm:p-6"><h3 class="mb-4 text-base font-extrabold text-[#25264f]">${escapeHtml(title)}</h3>${body}</article>`;
  }

  function pillList(items, tone = "violet") {
    const values = asArray(items).filter((item) => typeof item === "string" && item.trim());
    if (!values.length) return emptyState();
    const toneClasses = tone === "amber"
      ? "bg-amber-100 text-amber-800"
      : tone === "emerald"
        ? "bg-emerald-100 text-emerald-800"
        : "bg-violet-100 text-violet-800";
    return `<ul class="flex flex-wrap gap-2">${values.map((item) => `<li class="rounded-full ${toneClasses} px-3 py-1.5 text-xs font-semibold">${escapeHtml(item)}</li>`).join("")}</ul>`;
  }

  function textList(items) {
    const values = asArray(items).filter((item) => typeof item === "string" && item.trim());
    if (!values.length) return emptyState();
    return `<ul class="space-y-3">${values.map((item) => `<li class="flex gap-3 text-sm leading-6 text-slate-600"><span class="mt-2 size-1.5 shrink-0 rounded-full bg-violet-500"></span><span>${escapeHtml(item)}</span></li>`).join("")}</ul>`;
  }

  function renderAnalysis(analysis, filename, createdAt) {
    const details = analysis || {};
    const skills = details.skills || {};
    const education = asArray(details.education);
    const projects = asArray(details.projects);
    document.getElementById("analysis-title").textContent = details.candidate_name || "Resume analysis";
    document.getElementById("analysis-filename").textContent = filename || "Resume analysis";
    document.getElementById("analysis-date").textContent = createdAt
      ? ` · ${new Date(createdAt).toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" })}`
      : "";

    const contact = [details.email, details.phone]
      .filter((item) => item && item !== "Not provided")
      .map(escapeHtml);
    const contactBody = contact.length
      ? `<p class="mt-2 text-sm text-slate-500">${contact.join(" <span class=\"px-2 text-violet-300\">·</span> ")}</p>`
      : `<p class="mt-2 text-sm text-slate-400">Contact details were not provided.</p>`;

    const educationBody = education.length
      ? `<div class="space-y-3">${education.map((item) => `<div class="rounded-xl bg-violet-50/70 p-4"><p class="font-bold text-slate-800">${escapeHtml(item.degree || "Education")}</p><p class="mt-1 text-sm text-slate-600">${escapeHtml(item.institution || "Institution not provided")}</p><p class="mt-1 text-xs text-slate-500">${escapeHtml(item.expected_graduation || "Graduation date not provided")}</p></div>`).join("")}</div>`
      : emptyState();

    const projectBody = projects.length
      ? `<div class="space-y-4">${projects.map((item) => `<article class="border-l-2 border-violet-200 pl-4"><h4 class="font-bold text-slate-800">${escapeHtml(item.name || "Project")}</h4><p class="mt-1 text-sm leading-6 text-slate-600">${escapeHtml(item.description || "Description not provided")}</p><div class="mt-3">${pillList(item.technologies)}</div></article>`).join("")}</div>`
      : emptyState();

    analysisContent.innerHTML = [
      card("Candidate profile", `<div class="flex items-center gap-4"><span class="grid size-12 shrink-0 place-items-center rounded-2xl bg-violet-100 text-xl font-extrabold text-violet-700">${escapeHtml((details.candidate_name || "?").trim().charAt(0).toUpperCase())}</span><div><p class="font-bold text-slate-800">${escapeHtml(details.candidate_name || "Name not provided")}</p>${contactBody}</div></div>`),
      card("Skills", `<div><p class="mb-2 text-xs font-bold uppercase tracking-wider text-slate-400">Technical</p>${pillList(skills.technical)}<p class="mb-2 mt-5 text-xs font-bold uppercase tracking-wider text-slate-400">People skills</p>${pillList(skills.soft, "emerald")}</div>`, "emerald"),
      card("Education", educationBody),
      card("Work experience", textList(details.work_experience), "emerald"),
      card("Projects", projectBody),
      card("Recommended internship roles", pillList(details.recommended_internship_roles), "amber"),
      card("Recommended job roles", pillList(details.recommended_job_roles)),
      card("Skills to build", pillList(details.missing_skills, "amber"), "amber"),
      card("Career suggestions", textList(details.career_suggestions), "emerald"),
    ].join("");
    analysisPanel.classList.remove("hidden");
  }

  function renderHistory() {
    document.getElementById("history-count").textContent = String(history.length);
    if (!history.length) {
      historyList.innerHTML = `<div class="px-4 py-10 text-center"><span class="mx-auto mb-3 grid size-12 place-items-center rounded-2xl bg-violet-50 text-xl text-violet-400">✦</span><p class="text-sm font-semibold text-slate-600">No saved analyses yet</p><p class="mt-1 text-xs text-slate-400">Your reports will appear here after analysis.</p></div>`;
      return;
    }
    historyList.innerHTML = history.map((item) => {
      const candidate = item.analysis?.candidate_name || "Resume analysis";
      const date = item.created_at
        ? new Date(item.created_at).toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" })
        : "Saved analysis";
      return `<button type="button" data-analysis-id="${Number(item.id)}" class="group w-full rounded-2xl border border-transparent p-3 text-left transition hover:border-violet-100 hover:bg-violet-50/70 focus:border-violet-200 focus:outline-none focus:ring-2 focus:ring-violet-100"><span class="flex items-start gap-3"><span class="grid size-10 shrink-0 place-items-center rounded-xl bg-violet-100 text-violet-700"><svg class="size-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M7 3h7l5 5v13H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2Z"/><path d="M14 3v6h6M9 13h7M9 17h5"/></svg></span><span class="min-w-0 flex-1"><span class="block truncate text-sm font-bold text-slate-800 group-hover:text-violet-700">${escapeHtml(candidate)}</span><span class="mt-1 block truncate text-xs text-slate-500">${escapeHtml(item.filename || "Resume")}</span><span class="mt-1 block text-[11px] text-slate-400">${escapeHtml(date)}</span></span><span class="pt-1 text-slate-300 transition group-hover:translate-x-0.5 group-hover:text-violet-500" aria-hidden="true">›</span></span></button>`;
    }).join("");
  }

  async function loadHistory() {
    try {
      history = await apiRequest("/ai/resume-analyses");
      renderHistory();
    } catch (error) {
      if (handleAuthError(error)) return;
      historyList.innerHTML = `<p class="px-4 py-8 text-center text-sm text-rose-600">${escapeHtml(error.message || "Could not load analysis history.")}</p>`;
    }
  }

  async function openSavedAnalysis(id, button) {
    if (button) button.disabled = true;
    try {
      const result = await apiRequest(`/ai/resume-analyses/${encodeURIComponent(id)}`);
      renderAnalysis(result.analysis, result.filename, result.created_at);
      analysisPanel.scrollIntoView({ behavior: "smooth", block: "start" });
    } catch (error) {
      if (!handleAuthError(error)) showMessage(error.message || "Could not open this analysis.");
    } finally {
      if (button) button.disabled = false;
    }
  }

  async function loadProfile() {
    try {
      const profile = await apiRequest("/auth/me");
      const name = profile.full_name || "ApplyWise user";
      document.getElementById("profile-name").textContent = name;
      document.getElementById("profile-email").textContent = profile.email || "";
      document.getElementById("profile-initials").textContent = name.trim().split(/\s+/).slice(0, 2).map((part) => part[0]).join("").toUpperCase();
    } catch (error) {
      handleAuthError(error);
    }
  }

  dropzone.addEventListener("click", () => fileInput.click());
  fileInput.addEventListener("change", () => selectFile(fileInput.files?.[0]));
  document.getElementById("clear-file").addEventListener("click", () => {
    selectedFile = null;
    fileInput.value = "";
    fileDisplay.classList.add("hidden");
    fileDisplay.classList.remove("flex");
    analyzeButton.disabled = true;
    clearMessage();
  });

  ["dragenter", "dragover"].forEach((eventName) => dropzone.addEventListener(eventName, (event) => {
    event.preventDefault();
    dropzone.classList.add("border-violet-500", "bg-violet-100", "ring-4", "ring-violet-100");
  }));
  ["dragleave", "drop"].forEach((eventName) => dropzone.addEventListener(eventName, (event) => {
    event.preventDefault();
    dropzone.classList.remove("border-violet-500", "bg-violet-100", "ring-4", "ring-violet-100");
  }));
  dropzone.addEventListener("drop", (event) => selectFile(event.dataTransfer?.files?.[0]));

  analyzeButton.addEventListener("click", async () => {
    if (!selectedFile) return;
    clearMessage();
    analyzeButton.disabled = true;
    analyzeButton.querySelector("span").textContent = "Analyzing resume...";
    const formData = new FormData();
    formData.append("file", selectedFile);
    try {
      const result = await apiRequest("/ai/analyze-resume", {
        method: "POST",
        body: formData,
      });
      renderAnalysis(result.analysis, result.filename, new Date().toISOString());
      analysisPanel.scrollIntoView({ behavior: "smooth", block: "start" });
      showMessage("Analysis complete and saved to your history.", "success");
      selectedFile = null;
      fileInput.value = "";
      fileDisplay.classList.add("hidden");
      fileDisplay.classList.remove("flex");
      await loadHistory();
    } catch (error) {
      if (!handleAuthError(error)) showMessage(error.message || "Resume analysis failed. Please try again.");
    } finally {
      analyzeButton.disabled = !selectedFile;
      analyzeButton.querySelector("span").textContent = "Analyze resume";
    }
  });

  historyList.addEventListener("click", (event) => {
    const button = event.target.closest("button[data-analysis-id]");
    if (button) openSavedAnalysis(button.dataset.analysisId, button);
  });
  document.getElementById("back-to-upload").addEventListener("click", () => {
    document.getElementById("upload-heading").scrollIntoView({ behavior: "smooth", block: "center" });
  });
  document.querySelectorAll("[data-logout]").forEach((button) => button.addEventListener("click", () => {
    localStorage.removeItem("access_token");
    window.location.replace("./login.html");
  }));

  loadProfile();
  loadHistory();
});
