chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (message?.type !== "WORDFLOW_READ_CLIPBOARD") return;
  navigator.clipboard.readText()
    .then(text => sendResponse({ text }))
    .catch(() => sendResponse({ text: "" }));
  return true;
});