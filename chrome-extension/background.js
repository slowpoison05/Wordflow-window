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
      justification: "Read clipboard text only after a user invokes WordFlow."
    });
  }
}

async function readClipboard() {
  await ensureClipboardPage();
  const response = await chrome.runtime.sendMessage({ type: "WORDFLOW_READ_CLIPBOARD" });
  return typeof response?.text === "string" ? response.text : "";
}

async function writeToTab(tabId, modeOverride = null) {
  const settings = await chrome.storage.local.get({ sourceText: "", mode: "character", speed: "normal" });
  const mode = modeOverride || settings.mode;
  let text = "";
  try { text = await readClipboard(); } catch (error) { console.warn("WordFlow clipboard unavailable", error); }
  if (!text) text = settings.sourceText;
  if (!text) {
    chrome.tabs.sendMessage(tabId, {
      type: "WORDFLOW_STATUS",
      message: "Clipboard is empty. Copy text first, or save fallback text in WordFlow settings."
    }).catch(() => {});
    return;
  }
  try {
    await chrome.tabs.sendMessage(tabId, { type: "WORDFLOW_WRITE", text, mode, speed: settings.speed });
  } catch {
    try {
      await chrome.tabs.sendMessage(tabId, {
        type: "WORDFLOW_STATUS",
        message: "WordFlow cannot access this page. Try a normal webpage text field."
      });
    } catch {}
  }
}

chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  if (!tab?.id) return;
  if (info.menuItemId === MENU.stop) {
    chrome.tabs.sendMessage(tab.id, { type: "WORDFLOW_STOP" }).catch(() => {});
    return;
  }
  const mode = info.menuItemId === MENU.character ? "character"
    : info.menuItemId === MENU.word ? "word" : null;
  await writeToTab(tab.id, mode);
});

chrome.commands.onCommand.addListener(async command => {
  if (command !== "wordflow-write") return;
  const [tab] = await chrome.tabs.query({ active: true, lastFocusedWindow: true });
  if (tab?.id) await writeToTab(tab.id);
});
