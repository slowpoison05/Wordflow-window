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

chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  if (!tab?.id) return;
  if (info.menuItemId === MENU.stop) {
    chrome.tabs.sendMessage(tab.id, { type: "WORDFLOW_STOP" });
    return;
  }
  const settings = await chrome.storage.local.get({ sourceText: "", mode: "character", speed: "normal" });
  if (!settings.sourceText) {
    chrome.tabs.sendMessage(tab.id, { type: "WORDFLOW_STATUS", message: "Open WordFlow from the toolbar and paste or enter your text first." });
    return;
  }
  const mode = info.menuItemId === MENU.character ? "character"
    : info.menuItemId === MENU.word ? "word" : settings.mode;
  chrome.tabs.sendMessage(tab.id, {
    type: "WORDFLOW_WRITE",
    text: settings.sourceText,
    mode,
    speed: settings.speed
  });
});