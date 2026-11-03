const test = require("node:test");
const assert = require("node:assert/strict");
const { filterApplications } = require("../src/js/applicationFilters.js");

const applications = [
  {
    company_name: "Northstar Labs",
    job_title: "Software Intern",
    status: "Applied",
    notes: "Follow up next week",
  },
  {
    company_name: "Juniper Works",
    job_title: "Product Designer",
    status: "Interview",
    notes: "Portfolio review",
  },
  {
    company_name: "Copper & Co",
    job_title: "Frontend Engineer",
    status: "Rejected",
    notes: null,
  },
];

test("search matches company, role, and notes without case sensitivity", () => {
  assert.deepEqual(filterApplications(applications, "NORTHSTAR"), [applications[0]]);
  assert.deepEqual(filterApplications(applications, "designer"), [applications[1]]);
  assert.deepEqual(filterApplications(applications, "portfolio"), [applications[1]]);
});

test("status filter can select Interview and can be combined with search", () => {
  assert.deepEqual(filterApplications(applications, "", "Interview"), [applications[1]]);
  assert.deepEqual(filterApplications(applications, "juniper", "Interview"), [applications[1]]);
  assert.deepEqual(filterApplications(applications, "northstar", "Interview"), []);
});

test("empty search and status return every application", () => {
  assert.deepEqual(filterApplications(applications), applications);
  assert.deepEqual(filterApplications(applications, "  ", ""), applications);
});
