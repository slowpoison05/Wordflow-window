const MENU = {
  parent: "wordflow-parent",
  current: "wordflow-current",
  character: "wordflow-character",
  word: "wordflow-word",
  stop: "wordflow-stop"
};

// Rebuild menus on installation/update and browser startup so they cannot be
// left missing after an interrupted extension reload.
async function registerWordFlowMenus() {
  try {
    await chrome.contextMenus.removeAll();
    chrome.contextMenus.create({
      id: MENU.parent,
      title: "WordFlow",
      contexts: ["editable"]
    });
    chrome.contextMenus.create({
      id: MENU.current,
      parentId: MENU.parent,
      title: "Write All (current mode)",
      contexts: ["editable"]
    });
    chrome.contextMenus.create({
      id: MENU.character,
      parentId: MENU.parent,
      title: "Write All in Character Mode",
      contexts: ["editable"]
    });
    chrome.contextMenus.create({
      id: MENU.word,
      parentId: MENU.parent,
      title: "Write All in Word Mode",
      contexts: ["editable"]
    });
    chrome.contextMenus.create({
      id: MENU.stop,
      parentId: MENU.parent,
      title: "Stop Writing",
      contexts: ["editable"]
    });
    console.log("WordFlow context menus registered.");
  } catch (error) {
    console.error("WordFlow could not register context menus:", error);
  }
}

chrome.runtime.onInstalled.addListener(() => {
  void registerWordFlowMenus();
});
chrome.runtime.onStartup.addListener(() => {
  void registerWordFlowMenus();
});

async function ensureClipboardPage() {
  const url = chrome.runtime.getURL("offscreen.html");
  const contexts = await chrome.runtime.getContexts({
    contextTypes: ["OFFSCREEN_DOCUMENT"],
    documentUrls: [url]
  });
  if (!contexts.length) {
    await chrome.offscreen.createDocument({
      url: "offscreen.html",
      reasons: ["CLIPBOARD"],
      justification: "Read clipboard text only after the user explicitly invokes WordFlow."
    });
  }
}

async function readClipboard() {
  await ensureClipboardPage();
  const response = await chrome.runtime.sendMessage({ type: "WORDFLOW_READ_CLIPBOARD" });
  return typeof response?.text === "string" ? response.text : "";
}

async function sendStatus(tabId, message) {
  try {
    await chrome.tabs.sendMessage(tabId, { type: "WORDFLOW_STATUS", message });
  } catch (error) {
    console.warn("WordFlow could not display page status:", error);
  }
}

// A tab that was already open when the extension was reloaded may not have
// the content script. Inject it on demand, then retry messaging.
async function ensureContentScript(tabId) {
  try {
    await chrome.tabs.sendMessage(tabId, { type: "WORDFLOW_PING" });
    return true;
  } catch {
    // No listener in this tab yet; try injecting the packaged content script.
  }
  try {
    await chrome.scripting.executeScript({
      target: { tabId },
      files: ["content.js"]
    });
    await chrome.tabs.sendMessage(tabId, { type: "WORDFLOW_PING" });
    console.log("WordFlow content script injected successfully.");
    return true;
  } catch (error) {
    console.error("WordFlow cannot inject into this tab. Open a normal http/https webpage, refresh it, and try again:", error);
    return false;
  }
}

async function writeToTab(tabId, modeOverride = null) {
  const ready = await ensureContentScript(tabId);
  if (!ready) return;
  const settings = await chrome.storage.local.get({ sourceText: "", mode: "character", speed: "normal" });
  const mode = modeOverride || settings.mode;
  await sendStatus(tabId, "WordFlow command received…");
  let text = "";
  try {
    text = await readClipboard();
  } catch (error) {
    console.warn("WordFlow clipboard read failed:", error);
  }
  if (!text) text = settings.sourceText;
  if (!text) {
    await sendStatus(tabId, "WordFlow started, but clipboard text was unavailable. Save fallback text in the WordFlow toolbar popup.");
    return;
  }
  try {
    await chrome.tabs.sendMessage(tabId, {
      type: "WORDFLOW_WRITE",
      text,
      mode,
      speed: settings.speed
    });
  } catch (error) {
    console.warn("WordFlow could not start on this tab:", error);
    await sendStatus(tabId, "WordFlow cannot access this page. Refresh the webpage and try a normal text field.");
  }
}

chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  console.log("WordFlow context menu clicked:", info.menuItemId);
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
  console.log("WordFlow command received:", command);
  if (command !== "wordflow-write") return;
  try {
    const [tab] = await chrome.tabs.query({ active: true, lastFocusedWindow: true });
    if (!tab?.id) {
      console.warn("WordFlow shortcut: no active tab found.");
      return;
    }
    await writeToTab(tab.id);
  } catch (error) {
    console.error("WordFlow shortcut failed:", error);
  }
});

// Popup fallback: allows testing WordFlow even if Chrome has not assigned the shortcut.
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message?.type !== "WORDFLOW_POPUP_WRITE") return;
  (async () => {
    try {
      const [tab] = await chrome.tabs.query({ active: true, lastFocusedWindow: true });
      if (!tab?.id) throw new Error("No active tab found");
      await writeToTab(tab.id);
      sendResponse({ ok: true });
    } catch (error) {
      console.error("WordFlow popup write failed:", error);
      sendResponse({ ok: false, error: String(error?.message || error) });
    }
  })();
  return true;
});
