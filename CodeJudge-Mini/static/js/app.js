/* ============================================================
   CodeJudge-Mini — app.js
   All dummy/mock data lives here for now.

   WHEN CONNECTING FLASK LATER:
   Replace each "MOCK_" constant / function below with a real
   fetch() call to your Flask API. The shape of the mock data
   already matches what your Flask routes should return as JSON,
   so the rest of the page code won't need to change much —
   only how the data is fetched.
   ============================================================ */


/* ----------------------------------------------------------
   MOCK DATA
   Later this comes from: GET /api/problems, GET /api/submissions, etc.
   ---------------------------------------------------------- */

const MOCK_PROBLEMS = [
  { id: 1, title: "Sum of Two Numbers", difficulty: "Easy", time_limit: 1 },
  { id: 2, title: "Factorial of a Number", difficulty: "Easy", time_limit: 1 },
  { id: 3, title: "Check Prime Number", difficulty: "Easy", time_limit: 1 },
  { id: 4, title: "Reverse a String", difficulty: "Easy", time_limit: 1 },
  { id: 5, title: "Fibonacci Series", difficulty: "Medium", time_limit: 2 },
  { id: 6, title: "Palindrome Check", difficulty: "Medium", time_limit: 2 },
  { id: 7, title: "Array Maximum Element", difficulty: "Easy", time_limit: 1 },
  { id: 8, title: "Linear Search", difficulty: "Medium", time_limit: 2 },
];

const MOCK_PROBLEM_DETAIL = {
  id: 1,
  title: "Sum of Two Numbers",
  difficulty: "Easy",
  time_limit: 1,
  description:
    "You are given two integers A and B. Write a C program that reads both integers and prints their sum.",
  input_format: "A single line containing two space-separated integers A and B.",
  output_format: "A single integer — the sum of A and B.",
  sample_input: "3 5",
  sample_output: "8",
};

const MOCK_SUBMISSION_HISTORY = [
  { id: 1042, problem: "Sum of Two Numbers", status: "accepted", time: "0.04s", submitted_at: "23 Aug, 6:12 PM" },
  { id: 1039, problem: "Check Prime Number", status: "wrong-answer", time: "0.06s", submitted_at: "23 Aug, 5:58 PM" },
  { id: 1035, problem: "Factorial of a Number", status: "compilation-error", time: "—", submitted_at: "22 Aug, 9:40 PM" },
  { id: 1031, problem: "Fibonacci Series", status: "time-limit-exceeded", time: "1.00s", submitted_at: "22 Aug, 9:12 PM" },
  { id: 1028, problem: "Reverse a String", status: "runtime-error", time: "0.02s", submitted_at: "21 Aug, 8:03 PM" },
  { id: 1024, problem: "Array Maximum Element", status: "accepted", time: "0.03s", submitted_at: "20 Aug, 7:45 PM" },
];

const MOCK_RESULT = {
  submission_id: 1042,
  problem: "Sum of Two Numbers",
  verdict: "accepted",
  execution_time: "0.04s",
  passed: 4,
  total: 4,
  test_cases: [
    { id: 1, status: "passed" },
    { id: 2, status: "passed" },
    { id: 3, status: "passed" },
    { id: 4, status: "passed" },
  ],
  expected_output: "8",
  actual_output: "8",
};

function formatStatus(status) {
  const labels = {
    "accepted": "Accepted",
    "wrong-answer": "Wrong Answer",
    "compilation-error": "Compilation Error",
    "runtime-error": "Runtime Error",
    "time-limit-exceeded": "Time Limit Exceeded",
    "pending": "Pending",
  };
  return labels[status] || status;
}

function renderResult() {
  const verdictEl = document.getElementById("verdict-badge");
  if (!verdictEl) return;

  const r = MOCK_RESULT;

  document.getElementById("submission-id").textContent = `#${r.submission_id}`;
  document.getElementById("result-problem-name").textContent = r.problem;
  document.getElementById("execution-time").textContent = r.execution_time;
  document.getElementById("testcase-summary").textContent = `${r.passed} / ${r.total} passed`;
  document.getElementById("expected-output").textContent = r.expected_output;
  document.getElementById("actual-output").textContent = r.actual_output;

  verdictEl.innerHTML = `
    <span class="badge badge-${r.verdict}">
      <span class="badge-dot"></span>${formatStatus(r.verdict)}
    </span>
  `;

  const list = document.getElementById("testcase-list");
  list.innerHTML = r.test_cases.map((tc) => `
    <div class="testcase-row">
      <span>Test Case ${tc.id}</span>
      <span class="badge badge-${tc.status === "passed" ? "accepted" : "wrong-answer"}">
        <span class="badge-dot"></span>${tc.status === "passed" ? "Passed" : "Failed"}
      </span>
    </div>
  `).join("");
}

document.addEventListener("DOMContentLoaded", () => {
  renderResult();
});


/* ----------------------------------------------------------
   HELPERS
   ---------------------------------------------------------- */

// Turns a status like "wrong-answer" into a readable label
// and the matching badge CSS class.
function formatStatus(status) {
  const labels = {
    "accepted": "Accepted",
    "wrong-answer": "Wrong Answer",
    "compilation-error": "Compilation Error",
    "runtime-error": "Runtime Error",
    "time-limit-exceeded": "Time Limit Exceeded",
    "pending": "Pending",
  };
  return labels[status] || status;
}

function difficultyTagClass(difficulty) {
  if (difficulty === "Easy") return "tag-easy";
  if (difficulty === "Medium") return "tag-medium";
  return "tag-hard";
}

// Reads ?id=3 style query params (used by problem.html, result.html)
function getQueryParam(name) {
  const params = new URLSearchParams(window.location.search);
  return params.get(name);
}


/* ----------------------------------------------------------
   PAGE: problems.html
   ---------------------------------------------------------- */
function renderProblemsTable() {
  const tbody = document.getElementById("problems-table-body");
  if (!tbody) return;

  // FLASK CONNECT POINT:
  // Replace MOCK_PROBLEMS with data from: fetch("/api/problems")
  tbody.innerHTML = MOCK_PROBLEMS.map((p) => `
    <tr>
      <td class="cell-muted">#${p.id}</td>
      <td>${p.title}</td>
      <td><span class="tag ${difficultyTagClass(p.difficulty)}">${p.difficulty}</span></td>
      <td>
        <a class="btn btn-secondary btn-sm" href="/problem?id=${p.id}">Open Problem</a>
      </td>
    </tr>
  `).join("");
}


/* ----------------------------------------------------------
   PAGE: problem.html
   ---------------------------------------------------------- */
function renderProblemDetail() {
  const titleEl = document.getElementById("problem-title");
  if (!titleEl) return;

  // FLASK CONNECT POINT:
  // Replace MOCK_PROBLEM_DETAIL with:
  // fetch(`/api/problems/${getQueryParam("id")}`)
  const p = MOCK_PROBLEM_DETAIL;

  document.getElementById("problem-title").textContent = p.title;
  document.getElementById("problem-description").textContent = p.description;
  document.getElementById("input-format").textContent = p.input_format;
  document.getElementById("output-format").textContent = p.output_format;
  document.getElementById("sample-input").textContent = p.sample_input;
  document.getElementById("sample-output").textContent = p.sample_output;
  document.getElementById("time-limit-chip").textContent = `Time limit: ${p.time_limit}s`;
  document.getElementById("difficulty-chip").textContent = p.difficulty;
}

function handleSubmitCode() {
  const submitBtn = document.getElementById("submit-btn");
  if (!submitBtn) return;

  submitBtn.addEventListener("click", () => {
    const code = document.getElementById("code-editor").value;

    if (!code.trim()) {
      alert("Please write some code before submitting.");
      return;
    }

    // FLASK CONNECT POINT:
    // POST the code to Flask, e.g.:
    //
    // fetch("/api/submissions", {
    //   method: "POST",
    //   headers: { "Content-Type": "application/json" },
    //   body: JSON.stringify({
    //     problem_id: getQueryParam("id"),
    //     source_code: code,
    //   }),
    // })
    //   .then((res) => res.json())
    //   .then((data) => {
    //     window.location.href = `/result?id=${data.submission_id}`;
    //   });
    //
    // For now, just navigate to the mock result page:
    window.location.href = "/result?id=1042";
  });
}

function handleClearCode() {
  const clearBtn = document.getElementById("clear-btn");
  if (!clearBtn) return;

  clearBtn.addEventListener("click", () => {
    document.getElementById("code-editor").value = "";
  });
}


/* ----------------------------------------------------------
   PAGE: result.html
   ---------------------------------------------------------- */
function renderResult() {
  const verdictEl = document.getElementById("verdict-badge");
  if (!verdictEl) return;

  // FLASK CONNECT POINT:
  // Replace MOCK_RESULT with:
  // fetch(`/api/submissions/${getQueryParam("id")}`)
  const r = MOCK_RESULT;

  document.getElementById("submission-id").textContent = `#${r.submission_id}`;
  document.getElementById("result-problem-name").textContent = r.problem;
  document.getElementById("execution-time").textContent = r.execution_time;
  document.getElementById("testcase-summary").textContent = `${r.passed} / ${r.total} passed`;
  document.getElementById("expected-output").textContent = r.expected_output;
  document.getElementById("actual-output").textContent = r.actual_output;

  verdictEl.innerHTML = `
    <span class="badge badge-${r.verdict}">
      <span class="badge-dot"></span>${formatStatus(r.verdict)}
    </span>
  `;

  const list = document.getElementById("testcase-list");
  list.innerHTML = r.test_cases.map((tc) => `
    <div class="testcase-row">
      <span>Test Case ${tc.id}</span>
      <span class="badge badge-${tc.status === "passed" ? "accepted" : "wrong-answer"}">
        <span class="badge-dot"></span>${tc.status === "passed" ? "Passed" : "Failed"}
      </span>
    </div>
  `).join("");
}


/* ----------------------------------------------------------
   PAGE: history.html
   ---------------------------------------------------------- */
function renderHistoryTable() {
  const tbody = document.getElementById("history-table-body");
  if (!tbody) return;

  // FLASK CONNECT POINT:
  // Replace MOCK_SUBMISSION_HISTORY with:
  // fetch("/api/submissions/history")
  tbody.innerHTML = MOCK_SUBMISSION_HISTORY.map((s) => `
    <tr>
      <td class="cell-muted">#${s.id}</td>
      <td>${s.problem}</td>
      <td>
        <span class="badge badge-${s.status}">
          <span class="badge-dot"></span>${formatStatus(s.status)}
        </span>
      </td>
      <td class="cell-muted">${s.time}</td>
      <td class="cell-muted">${s.submitted_at}</td>
    </tr>
  `).join("");
}


/* ----------------------------------------------------------
   AUTH FORMS (login.html / register.html)
   For now these just fake a successful login/register and
   redirect — no real check happens until Flask is connected.
   ---------------------------------------------------------- */
function handleLoginForm() {
  const form = document.getElementById("login-form");
  if (!form) return;

  form.addEventListener("submit", (e) => {
    e.preventDefault();

    // FLASK CONNECT POINT:
    // fetch("/api/login", { method: "POST", ... })
    //   .then(res => res.json())
    //   .then(data => { if (data.success) window.location.href = "/problems"; });

    window.location.href = "/problems";
  });
}

function handleRegisterForm() {
  const form = document.getElementById("register-form");
  if (!form) return;

  form.addEventListener("submit", (e) => {
    e.preventDefault();

    const password = document.getElementById("password").value;
    const confirmPassword = document.getElementById("confirm-password").value;
    const errorEl = document.getElementById("register-error");

    if (password !== confirmPassword) {
      errorEl.textContent = "Passwords do not match.";
      errorEl.style.display = "block";
      return;
    }
    errorEl.style.display = "none";

    // FLASK CONNECT POINT:
    // fetch("/api/register", { method: "POST", ... })
    //   .then(res => res.json())
    //   .then(data => { if (data.success) window.location.href = "/login"; });

    window.location.href = "/login";
  });
}


/* ----------------------------------------------------------
   INIT — runs on every page, each function exits early
   if that page's elements don't exist.
   ---------------------------------------------------------- */
document.addEventListener("DOMContentLoaded", () => {
  renderProblemsTable();
  renderProblemDetail();
  handleSubmitCode();
  handleClearCode();
  renderResult();
  renderHistoryTable();
  handleLoginForm();
  handleRegisterForm();
});
