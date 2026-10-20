const MENU = {
  parent: "wordflow-parent",
  current: "wordflow-current",
  character: "wordflow-character",
  word: "wordflow-word",
  stop: "wordflow-stop"
};

chrome.runtime.onInstalled.addListener(async () => {
  await chrome.contextMenus.removeAll();
  chrome.contextMenus.create({ id: MENU.parent, title: "WordFlow", contexts: ["editable"] });
  chrome.contextMenus.create({ id: MENU.current, parentId: MENU.parent, title: "Write All (current mode)", contexts: ["editable"] });
  chrome.contextMenus.create({ id: MENU.character, parentId: MENU.parent, title: "Write All in Character Mode", contexts: ["editable"] });
  chrome.contextMenus.create({ id: MENU.word, parentId: MENU.parent, title: "Write All in Word Mode", contexts: ["editable"] });
  chrome.contextMenus.create({ id: MENU.stop, parentId: MENU.parent, title: "Stop Writing", contexts: ["editable"] });
});

async function ensureClipboardPage() {
  const url = chrome.runtime.getURL("offscreen.html");
  const contexts = await chrome.runtime.getContexts({ contextTypes: ["OFFSCREEN_DOCUMENT"], documentUrls: [url] });
  if (!contexts.length) {
    await chrome.offscreen.createDocument({
      url: "offscreen.html",
      reasons: ["CLIPBOARD"],
      justification: "Read clipboard text only when the user selects a WordFlow right-click command."
    });
  }
}

chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  if (!tab?.id) return;
  if (info.menuItemId === MENU.stop) {
    chrome.tabs.sendMessage(tab.id, { type: "WORDFLOW_STOP" });
    return;
  }
  const settings = await chrome.storage.local.get({ sourceText: "", mode: "character", speed: "normal" });
  const mode = info.menuItemId === MENU.character ? "character"
    : info.menuItemId === MENU.word ? "word" : settings.mode;
  try {
    await ensureClipboardPage();
    const response = await chrome.runtime.sendMessage({ type: "WORDFLOW_READ_CLIPBOARD" });
    const text = typeof response?.text === "string" && response.text.length ? response.text : settings.sourceText;
    if (!text) {
      chrome.tabs.sendMessage(tab.id, { type: "WORDFLOW_STATUS", message: "Clipboard is empty. Copy text first." });
      return;
    }
    chrome.tabs.sendMessage(tab.id, {
      type: "WORDFLOW_WRITE",
      text,
      mode,
      speed: settings.speed
    });
  } catch (error) {
    console.error("WordFlow clipboard read failed:", error);
    if (settings.sourceText) {
      chrome.tabs.sendMessage(tab.id, { type: "WORDFLOW_WRITE", text: settings.sourceText, mode, speed: settings.speed });
    } else {
      chrome.tabs.sendMessage(tab.id, { type: "WORDFLOW_STATUS", message: "Could not read clipboard. Open WordFlow settings and save your text there." });
    }
  }
});