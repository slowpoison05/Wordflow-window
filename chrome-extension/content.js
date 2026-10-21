let wordFlowRun = 0;
let wordFlowTarget = null;

function wordFlowEditable(el) {
  if (!(el instanceof HTMLElement)) return false;
  if (el instanceof HTMLTextAreaElement) return !el.disabled && !el.readOnly;
  if (el instanceof HTMLInputElement) return !el.disabled && !el.readOnly && ["text", "search", "email", "url", "tel", "number"].includes(el.type);
  return el.isContentEditable;
}
document.addEventListener("focusin", e => { if (wordFlowEditable(e.target)) wordFlowTarget = e.target; }, true);
document.addEventListener("contextmenu", e => { if (wordFlowEditable(e.target)) wordFlowTarget = e.target; }, true);

chrome.runtime.onMessage.addListener(message => {
  if (message?.type === "WORDFLOW_STATUS") return;
  if (message?.type === "WORDFLOW_STOP") { wordFlowRun++; return; }
  if (message?.type === "WORDFLOW_PING") return;
  if (message?.type !== "WORDFLOW_WRITE") return;
  const target = wordFlowTarget && wordFlowTarget.isConnected ? wordFlowTarget : document.activeElement;
  if (!wordFlowEditable(target)) return;
  const id = ++wordFlowRun;
  const text = String(message.text || "");
  const chunks = message.mode === "word" ? (text.match(/\\S+\\s*/g) || []) : Array.from(text);
  const delay = message.speed === "fast" ? 35 : message.speed === "slow" ? 300 : 120;
  let i = 0;
  function step() {
    if (id !== wordFlowRun) return;
    if (i >= chunks.length) return;
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
      return;
    }
    if (i < chunks.length) setTimeout(step, delay);
  }
  step();
});
