document.addEventListener("DOMContentLoaded", function () {
  const editor = document.getElementById("code-editor");
  const lineNumbers = document.getElementById("line-numbers");
  const reset = document.getElementById("reset-code");
  if (!editor) return;
  const initial = editor.value;
  function updateLineNumbers() {
    if (lineNumbers) lineNumbers.textContent = editor.value.split("\n").map((_, i) => i + 1).join("\n");
  }
  editor.addEventListener("input", updateLineNumbers);
  editor.addEventListener("scroll", () => { if (lineNumbers) lineNumbers.scrollTop = editor.scrollTop; });
  updateLineNumbers();
  editor.addEventListener("keydown", function (event) {
    if (event.key !== "Tab") return;
    event.preventDefault();
    const start = editor.selectionStart;
    const end = editor.selectionEnd;
    editor.value = editor.value.slice(0, start) + "    " + editor.value.slice(end);
    editor.selectionStart = editor.selectionEnd = start + 4;
  });
  if (reset) reset.addEventListener("click", () => { editor.value = initial; updateLineNumbers(); editor.focus(); });
});
