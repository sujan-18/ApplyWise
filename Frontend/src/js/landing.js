document.addEventListener("DOMContentLoaded", () => {
  if (!localStorage.getItem("access_token")) return;

  const actions = [
    ["nav-login", "Dashboard", "./dashboard.html"],
    ["nav-register", "Resume Analyzer", "./resume.html"],
    ["primary-action", "Continue to your dashboard", "./dashboard.html"],
    ["secondary-action", "Analyze your resume", "./resume.html"],
  ];

  actions.forEach(([id, label, href]) => {
    const link = document.getElementById(id);
    if (!link) return;
    link.textContent = label;
    link.href = href;
  });
});
