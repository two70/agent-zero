import { createStore } from "/js/AlpineStore.js";

const fetchApi = globalThis.fetchApi;

const model = {
  loading: false,
  profiles: [],
  initialized: false,

  async ensureLoaded() {
    if (this.initialized || this.loading) return;

    this.loading = true;
    try {
      const response = await fetchApi("/agents", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "list" }),
      });
      const data = await response.json().catch(() => ({}));
      this.profiles = data.ok ? (data.data || []) : [];
      this.initialized = true;
    } catch (e) {
      console.error("Failed to load agent profiles:", e);
      this.profiles = [];
    } finally {
      this.loading = false;
    }
  },

  getCurrentProfile() {
    const selectedContext = this._getSelectedContext();
    return selectedContext?.agent_profile || "agent0";
  },

  getProfileLabel(profileKey) {
    if (!profileKey) return "";
    const profile = this.profiles.find(p => p.key === profileKey);
    return profile ? profile.label : profileKey;
  },

  async changeCurrentProfile(profileKey) {
    const chatsStore = this._getChatsStore();
    const contextId = chatsStore?.selected;
    if (!contextId || !profileKey) return;

    await chatsStore.setAgentProfile(contextId, profileKey);
  },

  _getChatsStore() {
    return window.Alpine?.store("chats") || null;
  },

  _getSelectedContext() {
    const chatsStore = this._getChatsStore();
    return chatsStore?.selectedContext || null;
  },
};

const store = createStore("agentProfileSelector", model);

export { store };
