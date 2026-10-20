let wordFlowRun = 0;
chrome.runtime.onMessage.addListener((message) => {
  if (message?.type === "WORDFLOW_STOP") { wordFlowRun++; return; }
  if (message?.type !== "WORDFLOW_WRITE") return;
  const target = document.activeElement;
  if (!(target instanceof HTMLElement) || !(target.isContentEditable || target instanceof HTMLInputElement || target instanceof HTMLTextAreaElement)) return;
  const id = ++wordFlowRun;
  const text = String(message.text || "");
  const chunks = message.mode === "word" ? (text.match(/\S+\s*/g) || []) : Array.from(text);
  const delay = message.speed === "fast" ? 35 : message.speed === "slow" ? 300 : 120;
  let i = 0;
  function step() {
    if (id !== wordFlowRun || i >= chunks.length) return;
    const value = chunks[i++];
    target.focus();
    if (target instanceof HTMLInputElement || target instanceof HTMLTextAreaElement) {
      const start = target.selectionStart ?? target.value.length;
      target.setRangeText(value, start, target.selectionEnd ?? start, "end");
    } else document.execCommand("insertText", false, value);
    target.dispatchEvent(new InputEvent("input", { bubbles: true, data: value, inputType: "insertText" }));
    if (i < chunks.length) setTimeout(step, delay);
  }
  step();
});