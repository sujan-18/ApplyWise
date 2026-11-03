const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

function element() {
  const classes = new Set();
  const listeners = {};
  return {
    value: "",
    textContent: "",
    disabled: false,
    listeners,
    classList: {
      add: (...names) => names.forEach((name) => classes.add(name)),
      remove: (...names) => names.forEach((name) => classes.delete(name)),
      contains: (name) => classes.has(name),
    },
    addEventListener: (name, callback) => { listeners[name] = callback; },
    querySelector: () => element(),
    reset() { this.wasReset = true; },
  };
}

function authHarness({ apiResponse, apiError, page }) {
  const loginForm = page === "login" ? element() : null;
  const registerForm = page === "register" ? element() : null;
  const nodes = {
    "login-form": loginForm,
    "register-form": registerForm,
    "login-message": element(),
    "register-message": element(),
    email: element(),
    password: element(),
    "full-name": element(),
    "register-email": element(),
    "register-password": element(),
  };
  const stored = new Map();
  const redirects = [];
  const requests = [];
  const context = {
    document: { getElementById: (id) => nodes[id] || null },
    localStorage: {
      setItem: (key, value) => stored.set(key, value),
      getItem: (key) => stored.get(key) || null,
    },
    window: { location: { replace: (url) => redirects.push(url) } },
    apiRequest: async (...args) => {
      requests.push(args);
      if (apiError) throw apiError;
      return apiResponse;
    },
  };
  vm.runInNewContext(fs.readFileSync("src/js/auth.js", "utf8"), context);
  return { nodes, stored, redirects, requests, loginForm, registerForm };
}

test("login stores the bearer token and opens the dashboard", async () => {
  const harness = authHarness({ page: "login", apiResponse: { access_token: "signed-token" } });
  harness.nodes.email.value = "  person@example.com  ";
  harness.nodes.password.value = "password123";
  await harness.loginForm.listeners.submit({ preventDefault() {} });

  assert.equal(harness.requests[0][0], "/auth/login");
  assert.equal(harness.requests[0][1].method, "POST");
  assert.equal(harness.requests[0][1].body, JSON.stringify({ email: "person@example.com", password: "password123" }));
  assert.equal(harness.stored.get("access_token"), "signed-token");
  assert.deepEqual(harness.redirects, ["./index.html"]);
});

test("login shows API errors and remains on the login page", async () => {
  const harness = authHarness({ page: "login", apiError: new Error("Invalid email or password") });
  harness.nodes.email.value = "person@example.com";
  harness.nodes.password.value = "wrongpass";
  await harness.loginForm.listeners.submit({ preventDefault() {} });

  assert.equal(harness.nodes["login-message"].textContent, "Invalid email or password");
  assert.equal(harness.nodes["login-message"].classList.contains("hidden"), false);
  assert.deepEqual(harness.redirects, []);
});

test("registration sends the account fields and confirms success", async () => {
  const harness = authHarness({ page: "register", apiResponse: { id: 1 } });
  harness.nodes["full-name"].value = "Test Person";
  harness.nodes["register-email"].value = "person@example.com";
  harness.nodes["register-password"].value = "password123";
  await harness.registerForm.listeners.submit({ preventDefault() {} });

  assert.equal(harness.requests[0][0], "/auth/register");
  assert.equal(harness.requests[0][1].method, "POST");
  assert.equal(harness.requests[0][1].body, JSON.stringify({ full_name: "Test Person", email: "person@example.com", password: "password123" }));
  assert.equal(harness.nodes["register-message"].textContent, "Account created. You can now log in.");
  assert.equal(harness.registerForm.wasReset, true);
});
