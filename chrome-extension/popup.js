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