/**
 * OFRENDA: The Offline Memory Altar
 * Client-side reactivity, streaming RAG interaction, and ambient canvas simulation.
 */

document.addEventListener('DOMContentLoaded', () => {
  // DOM Elements
  const body = document.getElementById('app-body');
  const btnToggleCandle = document.getElementById('btn-toggle-candle');
  const candleBtnLabel = document.getElementById('candle-btn-label');
  const candleStand = document.getElementById('candle-stand');
  const petalsCanvas = document.getElementById('petals-canvas');
  
  const statusPill = document.getElementById('status-pill');
  const statusText = document.getElementById('status-text');
  
  const chatViewport = document.getElementById('chat-viewport');
  const chatForm = document.getElementById('chat-form');
  const queryInput = document.getElementById('query-input');
  const btnSubmitQuery = document.getElementById('btn-submit-query');
  const btnExportVigil = document.getElementById('btn-export-vigil');
  
  // Archives Drawer Elements
  const btnOpenArchives = document.getElementById('btn-open-archives');
  const btnCloseArchives = document.getElementById('btn-close-archives');
  const archivesDrawer = document.getElementById('archives-drawer');
  const drawerBackdrop = document.getElementById('drawer-backdrop');
  const archivesCount = document.getElementById('archives-count');
  const memoryCardList = document.getElementById('memory-card-list');
  const btnReindex = document.getElementById('btn-reindex');
  const tabBrowse = document.getElementById('tab-browse-memories');
  const tabAdd = document.getElementById('tab-add-memory');
  const tabContentBrowse = document.getElementById('tab-content-browse');
  const tabContentAdd = document.getElementById('tab-content-add');
  const addMemoryForm = document.getElementById('add-memory-form');
  
  // Modals
  const docModal = document.getElementById('doc-modal');
  const docModalTitle = document.getElementById('doc-modal-title');
  const docModalContent = document.getElementById('doc-modal-content');
  const btnCloseDocModal = document.getElementById('btn-close-doc-modal');
  
  const essayModal = document.getElementById('essay-modal');
  const essayModalContent = document.getElementById('essay-modal-content');
  const btnOpenEssay = document.getElementById('btn-open-essay');
  const btnCloseEssayModal = document.getElementById('btn-close-essay-modal');
  const btnCloseEssayFooter = document.getElementById('btn-close-essay-footer');
  const btnCopyEssay = document.getElementById('btn-copy-essay');
  
  const settingsModal = document.getElementById('settings-modal');
  const btnOpenSettings = document.getElementById('btn-open-settings');
  const btnCloseSettingsModal = document.getElementById('btn-close-settings-modal');
  const btnSaveSettings = document.getElementById('btn-save-settings');
  const ollamaProbeBadge = document.getElementById('ollama-probe-badge');
  const settingOllamaModel = document.getElementById('setting-ollama-model');

  // Application State
  const state = {
    isCandleLit: true,
    activeProvider: 'local_echo',
    ollamaOnline: false,
    activeModel: 'ofrenda-echo-v1',
    conversationLog: []
  };

  /* ==========================================================================
     1. Ambient Floating Marigold Petals Canvas Simulation
     ========================================================================== */
  function initPetalsSimulation() {
    if (!petalsCanvas) return;
    const ctx = petalsCanvas.getContext('2d');
    let width = petalsCanvas.width = window.innerWidth;
    let height = petalsCanvas.height = window.innerHeight;

    window.addEventListener('resize', () => {
      width = petalsCanvas.width = window.innerWidth;
      height = petalsCanvas.height = window.innerHeight;
    });

    const petals = [];
    const petalColors = ['#f59e0b', '#fbbf24', '#d97706', '#ea580c', '#fb923c'];

    for (let i = 0; i < 35; i++) {
      petals.push({
        x: Math.random() * width,
        y: Math.random() * height,
        size: Math.random() * 8 + 6,
        speedY: Math.random() * 0.8 + 0.35,
        speedX: Math.random() * 0.6 - 0.3,
        rotation: Math.random() * 360,
        rotSpeed: (Math.random() - 0.5) * 1.5,
        oscillation: Math.random() * 2 * Math.PI,
        color: petalColors[Math.floor(Math.random() * petalColors.length)],
        opacity: Math.random() * 0.45 + 0.3
      });
    }

    function animate() {
      ctx.clearRect(0, 0, width, height);

      const alphaMultiplier = state.isCandleLit ? 1.0 : 0.2;

      petals.forEach(p => {
        p.y += p.speedY;
        p.oscillation += 0.02;
        p.x += Math.sin(p.oscillation) * 0.7 + p.speedX;
        p.rotation += p.rotSpeed;

        if (p.y > height + 20) {
          p.y = -20;
          p.x = Math.random() * width;
        }
        if (p.x > width + 20) p.x = -20;
        if (p.x < -20) p.x = width + 20;

        ctx.save();
        ctx.translate(p.x, p.y);
        ctx.rotate((p.rotation * Math.PI) / 180);
        ctx.globalAlpha = p.opacity * alphaMultiplier;
        ctx.fillStyle = p.color;

        // Draw curved marigold petal shape
        ctx.beginPath();
        ctx.moveTo(0, -p.size);
        ctx.bezierCurveTo(p.size * 0.6, -p.size * 0.7, p.size * 0.8, p.size * 0.4, 0, p.size);
        ctx.bezierCurveTo(-p.size * 0.8, p.size * 0.4, -p.size * 0.6, -p.size * 0.7, 0, -p.size);
        ctx.fill();
        ctx.restore();
      });

      requestAnimationFrame(animate);
    }

    animate();
  }

  /* ==========================================================================
     2. Candle Lighting & Ambient Controls
     ========================================================================== */
  function toggleCandleState() {
    state.isCandleLit = !state.isCandleLit;
    if (state.isCandleLit) {
      body.classList.add('candle-lit');
      candleBtnLabel.textContent = 'Vigil Lit';
      btnToggleCandle.style.borderColor = 'var(--border-gold-bright)';
      showToast('🕯️ The vigil candle is lit. The golden marigold path awakens.');
    } else {
      body.classList.remove('candle-lit');
      candleBtnLabel.textContent = 'Relight Candle';
      btnToggleCandle.style.borderColor = 'var(--border-subtle)';
      showToast('💨 The candle softly dims. The altar rests in quiet twilight.');
    }
  }

  btnToggleCandle.addEventListener('click', toggleCandleState);
  candleStand.addEventListener('click', toggleCandleState);

  /* ==========================================================================
     3. Toast Notifications
     ========================================================================== */
  function showToast(message) {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = message;
    container.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(10px)';
      toast.style.transition = 'all 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, 3500);
  }

  /* ==========================================================================
     4. System Status & Model Detection
     ========================================================================== */
  async function fetchSystemStatus() {
    try {
      const res = await fetch('/api/status');
      if (!res.ok) throw new Error('Status endpoint unavailable');
      const data = await res.json();

      state.ollamaOnline = data.ollama_online;
      state.activeProvider = data.active_provider;
      state.activeModel = data.active_model;

      if (archivesCount) {
        archivesCount.textContent = data.total_memories;
      }

      if (data.ollama_online) {
        statusPill.style.background = 'rgba(16, 185, 129, 0.15)';
        statusPill.style.borderColor = 'rgba(16, 185, 129, 0.4)';
        statusText.textContent = `Ollama: ${data.active_model}`;
        if (ollamaProbeBadge) {
          ollamaProbeBadge.textContent = 'Online & Ready';
          ollamaProbeBadge.className = 'probe-badge badge-active';
        }
      } else {
        statusPill.style.background = 'rgba(245, 158, 11, 0.15)';
        statusPill.style.borderColor = 'rgba(245, 158, 11, 0.4)';
        statusText.textContent = '100% Air-Gapped (Local Echo)';
        if (ollamaProbeBadge) {
          ollamaProbeBadge.textContent = 'Offline (Start Ollama locally)';
          ollamaProbeBadge.className = 'probe-badge';
        }
      }
    } catch (err) {
      statusText.textContent = 'Local Offline Mode';
    }
  }

  /* ==========================================================================
     5. Memory Archives Drawer Management
     ========================================================================== */
  function openArchives() {
    archivesDrawer.classList.add('open');
    drawerBackdrop.classList.add('open');
    loadMemories();
  }

  function closeArchives() {
    archivesDrawer.classList.remove('open');
    drawerBackdrop.classList.remove('open');
  }

  btnOpenArchives.addEventListener('click', openArchives);
  btnCloseArchives.addEventListener('click', closeArchives);
  drawerBackdrop.addEventListener('click', closeArchives);

  // Tab switching inside drawer
  tabBrowse.addEventListener('click', () => {
    tabBrowse.classList.add('active');
    tabAdd.classList.remove('active');
    tabContentBrowse.classList.remove('hidden');
    tabContentAdd.classList.add('hidden');
  });

  tabAdd.addEventListener('click', () => {
    tabAdd.classList.add('active');
    tabBrowse.classList.remove('active');
    tabContentAdd.classList.remove('hidden');
    tabContentBrowse.classList.add('hidden');
  });

  async function loadMemories() {
    try {
      const res = await fetch('/api/memories');
      const items = await res.json();
      archivesCount.textContent = items.length;
      memoryCardList.innerHTML = '';

      items.forEach(item => {
        const card = document.createElement('div');
        card.className = 'memory-card';
        card.innerHTML = `
          <div class="memory-card-header">
            <h3 class="memory-card-title">${item.title}</h3>
          </div>
          <p class="memory-card-preview">${item.preview}</p>
          <div class="memory-card-meta">
            <span>📄 ${item.filename}</span>
            <span>${item.chunk_count} Sections • ${(item.char_count / 1000).toFixed(1)}k chars</span>
          </div>
          <div class="memory-card-actions">
            <button class="btn-card-action btn-view-file" data-filename="${item.filename}">View Text</button>
          </div>
        `;
        memoryCardList.appendChild(card);
      });

      // Bind view text buttons
      document.querySelectorAll('.btn-view-file').forEach(btn => {
        btn.addEventListener('click', () => viewMemoryFile(btn.dataset.filename));
      });
    } catch (err) {
      memoryCardList.innerHTML = '<p class="drawer-intro">Failed to load local memories.</p>';
    }
  }

  async function viewMemoryFile(filename) {
    try {
      const res = await fetch(`/api/memories/${filename}`);
      const data = await res.json();
      docModalTitle.textContent = `Viewing: ${filename}`;
      docModalContent.textContent = data.content;
      docModal.classList.add('open');
    } catch (err) {
      showToast('Error loading document content.');
    }
  }

  // Handle adding new memory
  addMemoryForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const filename = document.getElementById('new-memory-filename').value.trim();
    const content = document.getElementById('new-memory-content').value.trim();

    if (!filename || !content) return;

    try {
      const res = await fetch('/api/memories/upload', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ filename, content })
      });
      const data = await res.json();
      showToast(`✅ Archived & Indexed: ${data.filename}`);
      addMemoryForm.reset();
      tabBrowse.click();
      loadMemories();
      fetchSystemStatus();
    } catch (err) {
      showToast('Failed to save memory file.');
    }
  });

  // Reindex button
  btnReindex.addEventListener('click', async () => {
    btnReindex.textContent = '⏳ Re-indexing ChromaDB...';
    try {
      const res = await fetch('/api/reindex', { method: 'POST' });
      const data = await res.json();
      showToast(`✅ ${data.message}`);
      loadMemories();
      fetchSystemStatus();
    } catch (err) {
      showToast('Reindexing failed.');
    } finally {
      btnReindex.textContent = '🔄 Re-index All Local Memories';
    }
  });

  /* ==========================================================================
     6. Streaming Chat & RAG Interaction
     ========================================================================== */
  chatForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const query = queryInput.value.trim();
    if (!query) return;
    executeAltarQuery(query);
  });

  // Wire prompt discovery chips
  document.querySelectorAll('.chip-btn').forEach(chip => {
    chip.addEventListener('click', () => {
      const query = chip.dataset.query;
      queryInput.value = query;
      executeAltarQuery(query);
    });
  });

  async function executeAltarQuery(query) {
    queryInput.value = '';
    btnSubmitQuery.disabled = true;

    // Log user query to session
    state.conversationLog.push({ role: 'User', text: query, time: new Date().toLocaleTimeString() });

    // 1. Render User Message Card
    const userMsg = document.createElement('article');
    userMsg.className = 'chat-message user-message';
    userMsg.innerHTML = `
      <div class="message-avatar">🕯️</div>
      <div class="message-body">
        <div class="message-meta">
          <span class="speaker-name">Your Reflection</span>
          <span class="timestamp">${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
        </div>
        <div class="message-text"><p>${escapeHtml(query)}</p></div>
      </div>
    `;
    chatViewport.appendChild(userMsg);

    // 2. Render Altar Placeholder Message Card
    const altarMsg = document.createElement('article');
    altarMsg.className = 'chat-message altar-message';
    altarMsg.innerHTML = `
      <div class="message-avatar">💀</div>
      <div class="message-body">
        <div class="message-meta">
          <span class="speaker-name">Altar of Remembrance</span>
          <span class="timestamp">Reflecting...</span>
        </div>
        <div class="message-text" id="stream-target">
          <span class="pulse-dot" style="display:inline-block; vertical-align:middle;"></span>
        </div>
        <div class="citations-wrapper hidden" id="stream-citations">
          <div class="citations-title">Recalled From Family Archives:</div>
          <div class="citations-pills" id="stream-pills"></div>
        </div>
        <div class="message-badges" id="stream-badges" style="display:none;"></div>
      </div>
    `;
    chatViewport.appendChild(altarMsg);
    chatViewport.scrollTop = chatViewport.scrollHeight;

    const streamTarget = altarMsg.querySelector('#stream-target');
    const streamCitations = altarMsg.querySelector('#stream-citations');
    const streamPills = altarMsg.querySelector('#stream-pills');
    const streamBadges = altarMsg.querySelector('#stream-badges');

    let fullAltarText = '';
    let retrievedCitations = [];

    try {
      const response = await fetch('/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: query,
          stream: true,
          provider: state.activeProvider,
          model: state.activeModel,
          candle_lit: state.isCandleLit
        })
      });

      if (!response.ok) throw new Error('Query error');

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      streamTarget.innerHTML = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n\n');
        buffer = lines.pop(); // keep remainder

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue;
          const jsonStr = line.replace('data: ', '').trim();
          if (!jsonStr) continue;

          try {
            const data = JSON.parse(jsonStr);

            if (data.type === 'citations') {
              retrievedCitations = data.citations;
              if (retrievedCitations.length > 0) {
                streamCitations.classList.remove('hidden');
                streamPills.innerHTML = '';
                retrievedCitations.forEach(c => {
                  const pill = document.createElement('button');
                  pill.className = 'citation-pill';
                  pill.innerHTML = `📜 ${c.document} &bull; ${escapeHtml(c.section.slice(0, 28))} <span class="citation-score">${(c.score * 100).toFixed(0)}%</span>`;
                  pill.addEventListener('click', () => {
                    docModalTitle.textContent = `${c.document} — ${c.section}`;
                    docModalContent.textContent = `[Section Lines ${c.line_start || 1} - ${c.line_end || 'end'}]\n\n${c.snippet}`;
                    docModal.classList.add('open');
                  });
                  streamPills.appendChild(pill);
                });
              }
            } else if (data.type === 'token') {
              fullAltarText += data.text;
              streamTarget.innerHTML = `<p>${formatParagraphs(fullAltarText)}</p>`;
              chatViewport.scrollTop = chatViewport.scrollHeight;
            } else if (data.type === 'done') {
              streamBadges.style.display = 'flex';
              if (data.is_grounded) {
                streamBadges.innerHTML = `
                  <span class="badge badge-grounded">🛡️ Verified Grounded in Archive (${(data.grounding_score * 100).toFixed(0)}% confidence)</span>
                  <span class="badge badge-private">🔒 100% On-Device</span>
                `;
              } else {
                streamBadges.innerHTML = `
                  <span class="badge badge-warning">⚠️ Unrecorded Detail &bull; Respectfully Acknowledged</span>
                `;
              }
              // Record in session
              state.conversationLog.push({ role: 'Ofrenda', text: fullAltarText, citations: retrievedCitations });
            }
          } catch (e) {
            console.error('Parse chunk error', e);
          }
        }
      }
    } catch (err) {
      streamTarget.innerHTML = `<p style="color: #f87171;">The ofrenda whispers softly into the silence: connection error. Please ensure the backend is running.</p>`;
    } finally {
      btnSubmitQuery.disabled = false;
      queryInput.focus();
    }
  }

  /* ==========================================================================
     7. Session Keepsake Export (Markdown)
     ========================================================================== */
  btnExportVigil.addEventListener('click', () => {
    if (state.conversationLog.length === 0) {
      showToast('No reflections have been spoken yet to export.');
      return;
    }

    let md = `# Ofrenda: Memorial Vigil Keepsake\n`;
    md += `*Recorded locally on ${new Date().toLocaleDateString()} at ${new Date().toLocaleTimeString()}*\n`;
    md += `*Theme: Día de los Muertos • Built on Open-Source AI*\n\n---\n\n`;

    state.conversationLog.forEach(entry => {
      md += `### ${entry.role} (${entry.time || ''})\n\n${entry.text}\n\n`;
      if (entry.citations && entry.citations.length > 0) {
        md += `*Archival Citations:*\n`;
        entry.citations.forEach(c => {
          md += `- **${c.document}** (${c.section}) [Confidence: ${(c.score * 100).toFixed(0)}%]\n`;
        });
        md += `\n`;
      }
      md += `---\n\n`;
    });

    const blob = new Blob([md], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ofrenda_memorial_vigil_${Date.now()}.md`;
    a.click();
    URL.revokeObjectURL(url);
    showToast('💾 Memorial vigil downloaded as Markdown keepsake.');
  });

  /* ==========================================================================
     8. Modals (Document View, Challenge Essay, Settings)
     ========================================================================== */
  // Document modal close
  btnCloseDocModal.addEventListener('click', () => docModal.classList.remove('open'));
  docModal.addEventListener('click', (e) => {
    if (e.target === docModal) docModal.classList.remove('open');
  });

  // Essay modal open & fetch
  btnOpenEssay.addEventListener('click', async () => {
    essayModal.classList.add('open');
    try {
      const res = await fetch('/api/challenge-post');
      const data = await res.json();
      essayModalContent.innerHTML = renderMarkdownSimple(data.content);
    } catch (e) {
      essayModalContent.innerHTML = '<p>Failed to load challenge essay.</p>';
    }
  });

  function closeEssay() {
    essayModal.classList.remove('open');
  }
  btnCloseEssayModal.addEventListener('click', closeEssay);
  btnCloseEssayFooter.addEventListener('click', closeEssay);
  essayModal.addEventListener('click', (e) => {
    if (e.target === essayModal) closeEssay();
  });

  btnCopyEssay.addEventListener('click', async () => {
    try {
      const res = await fetch('/api/challenge-post');
      const data = await res.json();
      await navigator.clipboard.writeText(data.content);
      showToast('📋 Challenge post copied to clipboard!');
    } catch (e) {
      showToast('Failed to copy to clipboard.');
    }
  });

  // Settings modal
  btnOpenSettings.addEventListener('click', () => settingsModal.classList.add('open'));
  btnCloseSettingsModal.addEventListener('click', () => settingsModal.classList.remove('open'));
  settingsModal.addEventListener('click', (e) => {
    if (e.target === settingsModal) settingsModal.classList.remove('open');
  });

  btnSaveSettings.addEventListener('click', async () => {
    const selectedProvider = document.querySelector('input[name="provider-choice"]:checked').value;
    const modelName = settingOllamaModel.value.trim();

    try {
      await fetch('/api/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          provider: selectedProvider,
          ollama_model: modelName
        })
      });
      state.activeProvider = selectedProvider;
      state.activeModel = modelName;
      showToast(`⚙️ Provider updated to ${selectedProvider}`);
      settingsModal.classList.remove('open');
      fetchSystemStatus();
    } catch (e) {
      showToast('Failed to save settings.');
    }
  });

  /* ==========================================================================
     9. Helpers
     ========================================================================== */
  function escapeHtml(str) {
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  function formatParagraphs(text) {
    return escapeHtml(text).replace(/\n\n/g, '</p><p>').replace(/\n/g, '<br>');
  }

  function renderMarkdownSimple(md) {
    let html = escapeHtml(md);
    // Headers
    html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
    html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
    html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>');
    // Bold & Italics
    html = html.replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>');
    html = html.replace(/\*(.*?)\*/gim, '<em>$1</em>');
    // Lists
    html = html.replace(/^\- (.*$)/gim, '<li>$1</li>');
    // Paragraphs
    html = html.replace(/\n\n/gim, '</p><p>');
    return `<p>${html}</p>`;
  }

  // Initialize
  initPetalsSimulation();
  fetchSystemStatus();
  loadMemories();
});
