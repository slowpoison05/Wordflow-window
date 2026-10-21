const text = document.getElementById("text");
const mode = document.getElementById("mode");
const speed = document.getElementById("speed");
const status = document.getElementById("status");
chrome.storage.local.get({ sourceText: "", mode: "character", speed: "normal" }).then(value => {
  text.value = value.sourceText;
  mode.value = value.mode;
  speed.value = value.speed;
});
document.getElementById("save").addEventListener("click", async () => {
  await chrome.storage.local.set({ sourceText: text.value, mode: mode.value, speed: speed.value });
  status.textContent = text.value ? "Saved. Right-click in a webpage text field and choose WordFlow." : "Text cleared.";
});

// Show what Chrome actually assigned; suggested_key alone does not guarantee assignment.
chrome.commands.getAll(commands => {
  const command = commands.find(item => item.name === "wordflow-write");
  const shortcutBox = document.getElementById("shortcut");
  if (!command) {
    shortcutBox.textContent = "Shortcut command missing. Reload the extension at chrome://extensions.";
  } else if (!command.shortcut) {
    shortcutBox.textContent = "Shortcut NOT assigned by Chrome. Open chrome://extensions/shortcuts and assign Alt+Shift+W to WordFlow Browser.";
  } else {
    shortcutBox.textContent = "Chrome shortcut registered: " + command.shortcut;
  }
});
document.getElementById("write").addEventListener("click", async () => {
  status.textContent = "Starting WordFlow on the active tab…";
  const result = await chrome.runtime.sendMessage({ type: "WORDFLOW_POPUP_WRITE" });
  status.textContent = result?.ok ? "Command sent. Check the webpage field." : "Could not start: " + (result?.error || "unknown error");
});
