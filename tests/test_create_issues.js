"use strict";

// The issue-creation workflow must be repeatable without re-opening completed work.
// Execute the embedded github-script with a mocked GitHub API: no network or mutations.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const workflow = fs.readFileSync(
  path.join(__dirname, "..", ".github", "workflows", "create-issues.yml"), "utf8"
);
const marker = "          script: |\n";
assert.equal(workflow.split(marker).length, 2, "Expected one github-script block");
const script = workflow.split(marker)[1].split("\n")
  .map(line => line.startsWith("            ") ? line.slice(12) : line)
  .join("\n");

assert.match(workflow, /workflow_dispatch:/);
assert.doesNotMatch(workflow, /\n  push:/, "Issue creation should require explicit dispatch");
assert.match(workflow, /cancel-in-progress: false/);

const contact = "Dodaj sekcję kontaktową z adresem e-mail i linkami akademickimi";
const publications = "Dodaj sekcję z listą publikacji naukowych";
const profiles = "Dodaj linki do profili akademickich (ORCID, ResearchGate, Google Scholar)";
const history = [
  { title: "  DODAJ SEKCJĘ KONTAKTOWĄ Z ADRESEM E-MAIL I LINKAMI AKADEMICKIMI  ", state: "closed" },
  { title: publications, state: "open" },
  // Pull requests also occur in listForRepo results, but are not issue duplicates.
  { title: profiles, state: "open", pull_request: { url: "mock" } }
];

async function invoke() {
  const created = [];
  const github = {
    paginate: async (_fn, opts) => {
      assert.equal(opts.state, "all", "Closed issues must be included");
      assert.equal(opts.per_page, 100);
      return [...history];
    },
    rest: {
      issues: {
        listForRepo: () => {},
        create: async opts => {
          created.push(opts.title);
          history.push({ title: opts.title, state: "open" });
          return { data: { html_url: "https://github.com/example/issues/mock" } };
        }
      }
    }
  };
  await vm.runInNewContext("(async () => {\n" + script + "\n})()", {
    github,
    context: { repo: { owner: "MatPomGit", repo: "self" } },
    console: { log: () => {} }
  });
  return created;
}

(async () => {
  const first = await invoke();
  assert.equal(first.length, 6, "Only six not-yet-existing issues should be created");
  assert.ok(!first.includes(contact), "Must not recreate completed issue");
  assert.ok(!first.includes(publications), "Must not duplicate open issue");
  assert.ok(first.includes(profiles), "A PR title must not block a distinct issue");
  const second = await invoke();
  assert.deepEqual(second, [], "A second invocation must not create duplicates");
  console.log("create-issues idempotency regression: PASS");
})().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
