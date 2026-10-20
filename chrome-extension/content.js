let wordFlowRun = 0;
let wordFlowTarget = null;
let wordFlowNotice = null;

function wordFlowEditable(el) {
  if (!(el instanceof HTMLElement)) return false;
  if (el instanceof HTMLTextAreaElement) return !el.disabled && !el.readOnly;
  if (el instanceof HTMLInputElement) return !el.disabled && !el.readOnly && ["text", "search", "email", "url", "tel", "number"].includes(el.type);
  return el.isContentEditable;
}
document.addEventListener("focusin", e => { if (wordFlowEditable(e.target)) wordFlowTarget = e.target; }, true);
document.addEventListener("contextmenu", e => { if (wordFlowEditable(e.target)) wordFlowTarget = e.target; }, true);

function wordFlowStatus(message) {
  if (!wordFlowNotice || !wordFlowNotice.isConnected) {
    wordFlowNotice = document.createElement("div");
    wordFlowNotice.style.cssText = "position:fixed;z-index:2147483647;right:16px;bottom:16px;background:#171a21;color:#f2f5fa;padding:10px 14px;border:1px solid #6ea8fe;border-radius:9px;font:13px system-ui,sans-serif;box-shadow:0 4px 20px #0005";
    document.documentElement.appendChild(wordFlowNotice);
  }
  wordFlowNotice.textContent = message;
  clearTimeout(wordFlowNotice._timer);
  wordFlowNotice._timer = setTimeout(() => wordFlowNotice && wordFlowNotice.remove(), 3000);
}

chrome.runtime.onMessage.addListener(message => {
  if (message?.type === "WORDFLOW_STATUS") { wordFlowStatus(message.message); return; }
  if (message?.type === "WORDFLOW_STOP") { wordFlowRun++; wordFlowStatus("WordFlow stopped."); return; }
  if (message?.type !== "WORDFLOW_WRITE") return;
  const target = wordFlowTarget && wordFlowTarget.isConnected ? wordFlowTarget : document.activeElement;
  if (!wordFlowEditable(target)) { wordFlowStatus("Right-click inside an editable webpage field first."); return; }
  const id = ++wordFlowRun;
  const text = String(message.text || "");
  const chunks = message.mode === "word" ? (text.match(/\\S+\\s*/g) || []) : Array.from(text);
  const delay = message.speed === "fast" ? 35 : message.speed === "slow" ? 300 : 120;
  let i = 0;
  wordFlowStatus("WordFlow writing…");
  function step() {
    if (id !== wordFlowRun) return;
    if (i >= chunks.length) { wordFlowStatus("WordFlow finished."); return; }
    const value = chunks[i++];
    try {
      target.focus({ preventScroll: true });
      if (target instanceof HTMLInputElement || target instanceof HTMLTextAreaElement) {
        const start = target.selectionStart ?? target.value.length;
        target.setRangeText(value, start, target.selectionEnd ?? start, "end");
      } else {
        document.execCommand("insertText", false, value);
      }
      target.dispatchEvent(new InputEvent("input", { bubbles: true, data: value, inputType: "insertText" }));
    } catch {
      wordFlowRun++;
      wordFlowStatus("WordFlow could not edit this field.");
      return;
    }
    if (i < chunks.length) setTimeout(step, delay);
    else wordFlowStatus("WordFlow finished.");
  }
  step();
});