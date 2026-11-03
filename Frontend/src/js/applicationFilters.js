function filterApplications(applications, searchValue = "", statusValue = "") {
  const term = String(searchValue).trim().toLowerCase();
  return applications.filter((application) => {
    const matchesStatus = !statusValue || application.status === statusValue;
    const searchable = `${application.company_name} ${application.job_title} ${application.notes || ""}`.toLowerCase();
    return matchesStatus && searchable.includes(term);
  });
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = { filterApplications };
} else {
  window.filterApplications = filterApplications;
}
