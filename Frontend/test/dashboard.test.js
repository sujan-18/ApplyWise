const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

function makeElement() {
  const listeners = {};
  const classes = new Set();
  return {
    value: "",
    textContent: "",
    innerHTML: "",
    dataset: {},
    classList: {
      add: (...names) => names.forEach((name) => classes.add(name)),
      remove: (...names) => names.forEach((name) => classes.delete(name)),
      contains: (name) => classes.has(name),
    },
    addEventListener: (type, handler) => { listeners[type] = handler; },
    listeners,
    reset() {},
    showModal() {},
    close() {},
  };
}

async function bootDashboard({ profileError } = {}) {
  const ids = [
    "applications-table", "application-search", "status-filter", "application-modal",
    "application-form", "form-message", "profile-name", "profile-email",
    "profile-initials", "total-count", "table-count", "progress-count",
    "interview-count", "offer-count", "add-application", "modal-close",
    "modal-cancel", "application-id", "modal-title", "company-name", "job-title",
    "application-status", "applied-date", "application-notes", "save-application",
  ];
  const elements = Object.fromEntries(ids.map((id) => [id, makeElement()]));
  const redirects = [];
  const removed = [];
  const calls = [];
  const documentListeners = {};
  const context = {
    document: {
      addEventListener: (type, handler) => { documentListeners[type] = handler; },
      getElementById: (id) => elements[id] || null,
      querySelectorAll: () => [],
    },
    localStorage: {
      getItem: () => "test-token",
      removeItem: (key) => removed.push(key),
    },
    window: {
      location: { replace: (url) => redirects.push(url) },
      filterApplications: (rows) => rows,
      confirm: () => true,
      alert() {},
    },
    apiRequest: async (path) => {
      calls.push(path);
      if (path === "/auth/me") {
        if (profileError) throw profileError;
        return { id: 42, full_name: "Jamie Park", email: "jamie@example.com" };
      }
      if (path.startsWith("/applications/")) return [];
      throw new Error(`Unexpected request: ${path}`);
    },
  };
  vm.runInNewContext(fs.readFileSync("src/js/app.js", "utf8"), context);
  documentListeners.DOMContentLoaded();
  await new Promise((resolve) => setTimeout(resolve, 0));
  return { elements, redirects, removed, calls };
}

test("dashboard shows the signed-in user's name, email, and initials", async () => {
  const dashboard = await bootDashboard();
  assert.equal(dashboard.elements["profile-name"].textContent, "Jamie Park");
  assert.equal(dashboard.elements["profile-email"].textContent, "jamie@example.com");
  assert.equal(dashboard.elements["profile-initials"].textContent, "JP");
  assert.ok(dashboard.calls.includes("/auth/me"));
});

test("expired profile credentials are cleared and return to login", async () => {
  const error = Object.assign(new Error("Could not validate credentials"), { status: 401 });
  const dashboard = await bootDashboard({ profileError: error });
  assert.deepEqual(dashboard.removed, ["access_token"]);
  assert.deepEqual(dashboard.redirects, ["./login.html"]);
});
