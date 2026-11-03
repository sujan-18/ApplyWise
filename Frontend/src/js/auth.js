
const loginForm = document.getElementById("login-form");
const registerForm = document.getElementById("register-form");

async function submitAuth(path, payload, message, submitButton) {
  message.classList.add("hidden");
  message.textContent = "";
  submitButton.disabled = true;
  try {
    const data = await apiRequest(path, { method: "POST", body: JSON.stringify(payload) });
    if (path === "/auth/login") {
      localStorage.setItem("access_token", data.access_token);
      window.location.replace("./index.html");
    } else {
      message.textContent = "Account created. You can now log in.";
      message.classList.remove("hidden", "text-red-600", "bg-rose-50");
      message.classList.add("text-emerald-700", "bg-emerald-50");
      registerForm.reset();
    }
  } catch (error) {
    message.textContent = error.message;
    message.classList.remove("hidden", "text-emerald-700", "bg-emerald-50");
    message.classList.add("bg-rose-50");
    message.classList.add("text-red-600");
  } finally {
    submitButton.disabled = false;
  }
}

loginForm?.addEventListener("submit", (event) => {
  event.preventDefault();
  return submitAuth("/auth/login", {
    email: document.getElementById("email").value.trim(),
    password: document.getElementById("password").value,
  }, document.getElementById("login-message"), loginForm.querySelector("button[type=submit]"));
});

registerForm?.addEventListener("submit", (event) => {
  event.preventDefault();
  return submitAuth("/auth/register", {
    full_name: document.getElementById("full-name").value.trim(),
    email: document.getElementById("register-email").value.trim(),
    password: document.getElementById("register-password").value,
  }, document.getElementById("register-message"), registerForm.querySelector("button[type=submit]"));
});
