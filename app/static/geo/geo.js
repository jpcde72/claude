/* GEO Studio client: brand toggle, Ask drawer, streaming answers, save-to-project. */
(function () {
  "use strict";
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => Array.from(el.querySelectorAll(s));

  // ------------------------------------------------------------ brand toggle
  function setBrand(b) {
    document.documentElement.dataset.brand = b;
    try { localStorage.setItem("geo_brand", b); } catch (e) {}
    document.cookie = "geo_brand=" + b + "; path=/; max-age=31536000; SameSite=Lax";
    $$("[data-brand-btn]").forEach((btn) => btn.setAttribute("aria-pressed", String(btn.dataset.brandBtn === b)));
  }
  $$("[data-brand-btn]").forEach((btn) => btn.addEventListener("click", () => setBrand(btn.dataset.brandBtn)));
  setBrand(document.documentElement.dataset.brand || "jp");

  // ------------------------------------------------------------ markdown
  function md(text) {
    if (window.marked && window.DOMPurify) return DOMPurify.sanitize(marked.parse(text || ""));
    const div = document.createElement("div");
    div.textContent = text || "";
    return "<p style='white-space:pre-wrap'>" + div.innerHTML + "</p>";
  }

  // ------------------------------------------------------------ drawer state
  const state = { historyIds: [], target: null, busy: false, suggestedTitle: "", kind: "llm_answer" };
  const drawer = $(".drawer");
  const thread = $("#ask-thread");
  const input = $("#ask-input");
  const projectSel = $("#ask-project");
  const assetsBox = $("#ask-assets");
  const targetNote = $("#ask-target");

  function open() {
    document.body.classList.add("ask-open");
    drawer.setAttribute("aria-hidden", "false");
    setTimeout(() => input.focus(), 150);
  }
  function close() {
    document.body.classList.remove("ask-open");
    drawer.setAttribute("aria-hidden", "true");
  }
  function newThread() {
    state.historyIds = [];
    $$(".msg-q, .msg-a", thread).forEach((n) => n.remove());
    const empty = $("#ask-empty");
    if (empty) empty.classList.remove("hidden");
  }
  function setTarget(t) {
    state.target = t;
    targetNote.classList.toggle("hidden", !t);
    targetNote.textContent = t ? "Updating asset: " + t.title + ". Save the answer as its next version." : "";
  }

  async function loadAssets(checked = []) {
    assetsBox.innerHTML = "";
    const pid = projectSel.value;
    if (!pid) return;
    try {
      const res = await fetch("/geo/projects/" + pid + "/assets.json");
      if (!res.ok) return;
      const assets = await res.json();
      assets.forEach((a) => {
        const label = document.createElement("label");
        const cb = document.createElement("input");
        cb.type = "checkbox";
        cb.value = a.id;
        cb.checked = checked.includes(a.id);
        label.appendChild(cb);
        label.appendChild(document.createTextNode(a.title + " · v" + a.version));
        assetsBox.appendChild(label);
      });
    } catch (e) {}
  }
  projectSel.addEventListener("change", () => { setTarget(null); loadAssets(); });

  /** Public entry point used by buttons across the app. */
  window.GEO = {
    openAsk(opts = {}) {
      if (opts.projectId !== undefined && opts.projectId !== null) projectSel.value = String(opts.projectId);
      setTarget(opts.targetAssetId ? { id: opts.targetAssetId, title: opts.targetTitle || "asset" } : null);
      state.suggestedTitle = opts.title || "";
      state.kind = opts.kind || "llm_answer";
      loadAssets(opts.assetIds || []);
      if (opts.question) input.value = opts.question;
      open();
      if (opts.autoSend && opts.question) send();
    },
  };

  $$("[data-ask]").forEach((btn) =>
    btn.addEventListener("click", () => {
      const d = btn.dataset;
      GEO.openAsk({
        question: d.askQ || "",
        projectId: d.askProject !== undefined ? d.askProject : undefined,
        assetIds: (d.askAssets || "").split(",").filter(Boolean).map(Number),
        targetAssetId: d.askTarget ? Number(d.askTarget) : null,
        targetTitle: d.askTargetTitle,
        title: d.askTitle,
        kind: d.askKind,
        autoSend: d.askAuto === "1",
      });
    })
  );
  $$("[data-ask-close]").forEach((b) => b.addEventListener("click", close));
  $("[data-ask-new]").addEventListener("click", () => { newThread(); setTarget(null); });
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") close(); });
  $$("[data-suggest]").forEach((b) => b.addEventListener("click", () => { input.value = b.dataset.suggest; send(); }));

  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); }
  });
  $("#ask-form").addEventListener("submit", (e) => { e.preventDefault(); send(); });

  // ------------------------------------------------------------ send + stream
  async function send() {
    const question = input.value.trim();
    if (!question || state.busy) return;
    state.busy = true;
    $("#ask-send").disabled = true;
    const empty = $("#ask-empty");
    if (empty) empty.classList.add("hidden");

    const q = document.createElement("div");
    q.className = "msg-q";
    q.textContent = question;
    const a = document.createElement("div");
    a.className = "msg-a";
    a.innerHTML = '<div class="status">Thinking…</div><div class="prose"></div>';
    thread.append(q, a);
    thread.scrollTop = thread.scrollHeight;
    input.value = "";

    const body = {
      question,
      project_id: projectSel.value ? Number(projectSel.value) : null,
      asset_ids: $$("input:checked", assetsBox).map((c) => Number(c.value)),
      history_ids: state.historyIds,
      web_search: $("#ask-web").checked,
    };
    if (state.target && !body.asset_ids.includes(state.target.id)) body.asset_ids.push(state.target.id);

    let text = "";
    const prose = $(".prose", a);
    const status = $(".status", a);
    try {
      const res = await fetch("/geo/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (!res.ok || !res.body) throw new Error("Request failed (" + res.status + ")");
      const reader = res.body.getReader();
      const dec = new TextDecoder();
      let buf = "";
      let frame = 0;
      for (;;) {
        const { value, done } = await reader.read();
        if (done) break;
        buf += dec.decode(value, { stream: true });
        let idx;
        while ((idx = buf.indexOf("\n\n")) >= 0) {
          const chunk = buf.slice(0, idx);
          buf = buf.slice(idx + 2);
          if (!chunk.startsWith("data: ")) continue;
          const ev = JSON.parse(chunk.slice(6));
          if (ev.type === "text") {
            text += ev.text;
            status.classList.add("hidden");
            if (!frame) frame = requestAnimationFrame(() => { prose.innerHTML = md(text); frame = 0; });
          } else if (ev.type === "status") {
            status.textContent = ev.message;
            status.classList.remove("hidden");
          } else if (ev.type === "error") {
            status.remove();
            const err = document.createElement("div");
            err.className = "err";
            err.textContent = ev.message;
            a.appendChild(err);
          } else if (ev.type === "done") {
            prose.innerHTML = md(text);
            status.remove();
            state.historyIds.push(ev.exchange_id);
            a.appendChild(saveActions(ev.exchange_id, question));
          }
        }
      }
    } catch (err) {
      status.remove();
      const e = document.createElement("div");
      e.className = "err";
      e.textContent = err.message || String(err);
      a.appendChild(e);
    } finally {
      state.busy = false;
      $("#ask-send").disabled = false;
      thread.scrollTop = thread.scrollHeight;
    }
  }

  function saveActions(exchangeId, question) {
    const box = document.createElement("div");
    box.className = "msg-actions";
    const pid = projectSel.value;
    if (!pid) {
      box.innerHTML = '<span class="faint" style="font-size:.82rem">Choose a project above to save this answer as an asset.</span>';
      projectSel.addEventListener("change", () => box.replaceWith(saveActions(exchangeId, question)), { once: true });
      return box;
    }
    const target = state.target;
    const title = document.createElement("input");
    title.type = "text";
    title.value = state.suggestedTitle || question.slice(0, 90);
    title.setAttribute("aria-label", "Asset title");
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "btn small primary";
    btn.textContent = target ? "Save as new version" : "Save to project";
    if (!target) box.appendChild(title);
    box.appendChild(btn);
    btn.addEventListener("click", async () => {
      btn.disabled = true;
      const fd = new FormData();
      fd.append("project_id", pid);
      fd.append("title", title.value);
      fd.append("kind", state.kind || "llm_answer");
      if (target) fd.append("asset_id", target.id);
      const res = await fetch("/geo/exchanges/" + exchangeId + "/save", { method: "POST", body: fd });
      if (res.ok) {
        const data = await res.json();
        box.innerHTML = 'Saved. <a href="' + data.url + '">Open asset →</a>';
      } else {
        btn.disabled = false;
        btn.textContent = "Save failed, retry";
      }
    });
    return box;
  }

  // ------------------------------------------------------------ knowledge filter
  const search = $("#k-search");
  if (search) {
    const filter = () => {
      const term = search.value.trim().toLowerCase();
      const layer = ($("[data-layer].on") || {}).dataset?.layer || "";
      $$(".k-item").forEach((el) => {
        const okText = !term || el.textContent.toLowerCase().includes(term);
        const okLayer = !layer || !el.dataset.layer || el.dataset.layer === layer;
        el.classList.toggle("hidden", !(okText && okLayer));
      });
      $$(".k-section").forEach((sec) => {
        const any = $$(".k-item", sec).some((el) => !el.classList.contains("hidden"));
        sec.classList.toggle("hidden", !!term && !any);
      });
    };
    search.addEventListener("input", filter);
    $$("[data-layer]").forEach((chip) =>
      chip.addEventListener("click", () => {
        const on = chip.classList.contains("on");
        $$("[data-layer]").forEach((c) => { c.classList.remove("on", "accent"); c.setAttribute("aria-pressed", "false"); });
        if (!on) { chip.classList.add("on", "accent"); chip.setAttribute("aria-pressed", "true"); }
        filter();
      })
    );
  }

  // ------------------------------------------------------------ ARI scorer (live total)
  const ari = $("#ari-form");
  if (ari) {
    const bands = JSON.parse(ari.dataset.bands);
    const update = () => {
      let total = 0, weights = 0, complete = true;
      $$("input[type=range]", ari).forEach((r) => {
        const w = Number(r.dataset.weight);
        const v = Number(r.value);
        $("#val-" + r.name).textContent = r.dataset.touched === "1" ? v : "–";
        if (r.dataset.touched !== "1") complete = false;
        total += w * v; weights += w;
      });
      const score = Math.round(total / weights);
      $("#ari-big").textContent = complete ? score : "–";
      const band = bands.find((b) => score >= b.min && score <= b.max);
      $("#ari-band").textContent = complete && band ? band.label : "Score every component";
      $$(".bandbar div", ari).forEach((d, i) => d.classList.toggle("on", complete && bands[i] === band));
    };
    $$("input[type=range]", ari).forEach((r) =>
      r.addEventListener("input", () => { r.dataset.touched = "1"; update(); })
    );
    update();
  }
})();
