/* ==============================================================================
   DataSense AI - SPA Client Logic
   ============================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    // Current application state
    const appState = {
        activePage: 'chats',
        lastQueryTelemetry: null,
        config: null,
        currentRole: 'restricted_user',
        currentUsername: 'anonymous',
        providerOverride: 'Default',
        modelOverride: null,
        hasMessages: false,
        currentBenchmarkRuns: null
    };

    // DOM Elements
    const navButtons = document.querySelectorAll('.nav-menu .nav-btn');
    const pageViews = document.querySelectorAll('.page-view');
    const chatHistory = document.getElementById('chat-history');
    const chatWelcome = document.getElementById('chat-welcome');
    const chatInput = document.getElementById('chat-input');
    const chatSendBtn = document.getElementById('chat-send-btn');
    const exampleBtns = document.querySelectorAll('.example-chats .example-btn');
    const welcomeChips = document.querySelectorAll('.welcome-chip');
    
    // Header/Settings Sync Elements
    const activeEngineBadge = document.getElementById('active-engine-badge');
    const activeUserBadge = document.getElementById('active-user-badge');
    const settingsRole = document.getElementById('settings-role');
    const settingsUsername = document.getElementById('settings-username');
    const settingsProvider = document.getElementById('settings-provider');
    const settingsModelGroup = document.getElementById('settings-model-group');
    const settingsModel = document.getElementById('settings-model');
    const systemDefaultEngine = document.getElementById('system-default-engine');
    
    // Observability Page Elements
    const obsNoData = document.getElementById('obs-no-data');
    const obsDataView = document.getElementById('obs-data-view');
    const obsKpis = document.getElementById('obs-kpis');
    const obsLatencyBars = document.getElementById('obs-latency-bars');
    const obsTokensTable = document.getElementById('obs-tokens-table').querySelector('tbody');
    const obsQueryPlanDetails = document.getElementById('obs-query-plan-details');
    const obsSchemaRetrievalDetails = document.getElementById('obs-schema-retrieval-details');
    const obsSqlCode = document.getElementById('obs-sql-code').querySelector('code');
    const obsValidationResults = document.getElementById('obs-validation-results');
    const obsCorrectionPanel = document.getElementById('obs-correction-panel');
    const obsRepairHistory = document.getElementById('obs-repair-history');

    // Benchmarks Page Elements
    const benchmarkSelect = document.getElementById('benchmark-dataset-select');
    const benchmarkRunSelect = document.getElementById('benchmark-run-select');
    const benchNoData = document.getElementById('bench-no-data');
    const benchDataView = document.getElementById('bench-data-view');
    const benchKpis = document.getElementById('bench-kpis');
    const benchDifficultyBars = document.getElementById('bench-difficulty-bars');
    const benchErrorBars = document.getElementById('bench-error-bars');
    const benchLatencyDist = document.getElementById('bench-latency-dist');
    const benchTokenProjections = document.getElementById('bench-token-projections');
    const benchFailuresTable = document.getElementById('bench-failures-table').querySelector('tbody');

    // Models Map for dropdown selection
    const modelsByProvider = {
        'Default': [],
        'gemini': ['gemini-3.1-flash-lite'],
        'openai': ['gpt-4o', 'gpt-4-turbo', 'gpt-3.5-turbo'],
        'anthropic': ['claude-3-5-sonnet-20241022', 'claude-3-opus-20240229'],
        'ollama': ['qwen3:14b', 'deepseek-r1', 'llama3'],
        'vllm': ['Qwen/Qwen2.5-Coder-7B-Instruct'],
        'lmstudio': ['qwen3-14b']
    };

    // ==============================================================================
    // NAVIGATION & TAB SWITCHING
    // ==============================================================================
    function switchPage(pageId) {
        appState.activePage = pageId;

        // Toggle nav buttons
        navButtons.forEach(btn => {
            if (btn.getAttribute('data-page') === pageId) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });

        // Toggle page views
        pageViews.forEach(view => {
            if (view.id === `page-${pageId}`) {
                view.classList.add('active');
            } else {
                view.classList.remove('active');
            }
        });

        // Dynamic page-load actions
        if (pageId === 'observability') {
            renderObservability();
        } else if (pageId === 'benchmarks') {
            loadBenchmarkData(benchmarkSelect.value);
        }
    }

    navButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetPage = btn.getAttribute('data-page');
            switchPage(targetPage);
        });
    });

    // ==============================================================================
    // CONFIGURATION MANAGEMENT
    // ==============================================================================
    async function loadBackendConfig() {
        try {
            const response = await fetch('/api/v1/config');
            if (!response.ok) throw new Error('Failed to load backend config.');
            
            const config = await response.json();
            appState.config = config;

            // Update default values
            const defaultProv = config.provider || 'gemini';
            let defaultModel = config.model || 'Unknown';
            if (config[defaultProv] && config[defaultProv].model) {
                defaultModel = config[defaultProv].model;
            }

            systemDefaultEngine.textContent = `${defaultProv.toUpperCase()} (${defaultModel})`;
            syncEngineBadge(defaultProv.toUpperCase());

            // Initialize Form Settings
            settingsRole.value = appState.currentRole;
            settingsUsername.value = appState.currentUsername;
            syncUserBadges();
        } catch (error) {
            console.error('Error fetching configuration:', error);
            systemDefaultEngine.textContent = 'Failed to load config';
            syncEngineBadge('OFFLINE');
        }
    }

    function syncEngineBadge(text) {
        // Keep the SVG icon in the badge, just update the text node
        const svg = activeEngineBadge.querySelector('svg');
        activeEngineBadge.innerHTML = '';
        if (svg) activeEngineBadge.appendChild(svg);
        activeEngineBadge.appendChild(document.createTextNode(`Engine: ${text}`));
    }

    function syncUserBadges() {
        const svg = activeUserBadge.querySelector('svg');
        activeUserBadge.innerHTML = '';
        if (svg) activeUserBadge.appendChild(svg);
        activeUserBadge.appendChild(document.createTextNode(` ${appState.currentRole.toUpperCase()} (${appState.currentUsername})`));
        // Also update avatar seed
        const headerAvatar = document.getElementById('header-avatar');
        if (headerAvatar) {
            headerAvatar.src = `https://api.dicebear.com/7.x/bottts/svg?seed=${appState.currentUsername}`;
        }
    }

    // Settings listeners
    settingsRole.addEventListener('change', (e) => {
        appState.currentRole = e.target.value;
        syncUserBadges();
    });

    settingsUsername.addEventListener('input', (e) => {
        appState.currentUsername = e.target.value.trim() || 'anonymous';
        syncUserBadges();
    });

    settingsProvider.addEventListener('change', (e) => {
        const provider = e.target.value;
        appState.providerOverride = provider;

        // Populate models dropdown
        settingsModel.innerHTML = '';
        const models = modelsByProvider[provider] || [];
        
        if (provider === 'Default' || models.length === 0) {
            settingsModelGroup.classList.add('hidden');
            appState.modelOverride = null;
        } else {
            settingsModelGroup.classList.remove('hidden');
            models.forEach(model => {
                const opt = document.createElement('option');
                opt.value = model;
                opt.textContent = model;
                settingsModel.appendChild(opt);
            });
            appState.modelOverride = settingsModel.value;
        }
    });

    settingsModel.addEventListener('change', (e) => {
        appState.modelOverride = e.target.value;
    });

    // ==============================================================================
    // CHAT & NL2SQL WORKSPACE
    // ==============================================================================
    const USER_AVATAR_SVG = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>`;
    const AI_AVATAR_SVG = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>`;

    function hideWelcome() {
        if (!appState.hasMessages && chatWelcome) {
            appState.hasMessages = true;
            chatWelcome.style.transition = 'opacity 0.25s ease, transform 0.25s ease';
            chatWelcome.style.opacity = '0';
            chatWelcome.style.transform = 'translateY(-8px)';
            setTimeout(() => { chatWelcome.style.display = 'none'; }, 260);
        }
    }

    function appendMessage(sender, content, extraElements = null) {
        const msgDiv = document.createElement('div');
        msgDiv.classList.add('chat-msg', sender);

        const avatar = document.createElement('div');
        avatar.classList.add('msg-avatar');
        avatar.innerHTML = sender === 'user' ? USER_AVATAR_SVG : AI_AVATAR_SVG;
        msgDiv.appendChild(avatar);

        const bubble = document.createElement('div');
        bubble.classList.add('msg-bubble');

        const textSpan = document.createElement('span');
        textSpan.innerHTML = content.replace(/\n/g, '<br>');
        bubble.appendChild(textSpan);

        if (extraElements) {
            bubble.appendChild(extraElements);
        }

        msgDiv.appendChild(bubble);
        chatHistory.appendChild(msgDiv);
        
        // Animate in and scroll to bottom
        requestAnimationFrame(() => { chatHistory.scrollTop = chatHistory.scrollHeight; });
    }

    // Welcome chip click handlers
    welcomeChips.forEach(chip => {
        chip.addEventListener('click', () => {
            const query = chip.getAttribute('data-query');
            chatInput.value = query;
            chatInput.style.height = 'auto';
            chatInput.style.height = `${chatInput.scrollHeight}px`;
            handleQuerySubmit();
        });
    });

    async function handleQuerySubmit() {
        const query = chatInput.value.trim();
        if (!query) return;

        // Clear input & auto shrink textarea
        chatInput.value = '';
        chatInput.style.height = 'auto';

        // Hide welcome screen on first message
        hideWelcome();

        // Add User Bubble
        appendMessage('user', query);

        // Add Assistant "Thinking" Loading bubble
        const thinkingDiv = document.createElement('div');
        thinkingDiv.classList.add('chat-msg', 'assistant', 'thinking-bubble');
        thinkingDiv.innerHTML = `
            <div class="msg-avatar">${AI_AVATAR_SVG}</div>
            <div class="msg-bubble">
                <span class="pulse-loader">Thinking... Running multi-stage reasoning graph</span>
            </div>
        `;
        chatHistory.appendChild(thinkingDiv);
        requestAnimationFrame(() => { chatHistory.scrollTop = chatHistory.scrollHeight; });

        try {
            const payload = {
                query: query,
                user_role: appState.currentRole,
                username: appState.currentUsername
            };

            if (appState.providerOverride !== 'Default') {
                payload.provider = appState.providerOverride;
                if (appState.modelOverride) {
                    payload.model = appState.modelOverride;
                }
            }

            const startTime = performance.now();
            const response = await fetch('/api/v1/ask', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            // Remove thinking bubble
            thinkingDiv.remove();

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || 'Failed to fetch query execution from graph.');
            }

            const data = await response.json();
            const endTime = performance.now();
            const clientDuration = ((endTime - startTime) / 1000).toFixed(2);

            // Save telemetry
            appState.lastQueryTelemetry = data;
            
            // Sync engine badge in header
            if (data.active_provider) {
                syncEngineBadge(data.active_provider.toUpperCase());
            }

            // Prepare extra components (SQL Code Block & results)
            const extraContainer = document.createElement('div');

            // 1. Collapsible SQL Expander
            if (data.sql_query) {
                const sqlExpander = document.createElement('div');
                sqlExpander.classList.add('sql-expander', 'collapsed'); // Start collapsed to maintain clean layout
                
                const header = document.createElement('div');
                header.classList.add('sql-expander-header');
                header.innerHTML = `<span style="display:flex;align-items:center;gap:0.4rem;"><svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg> Generated SQL Query</span>`;
                
                const body = document.createElement('div');
                body.classList.add('sql-expander-body');
                
                const pre = document.createElement('pre');
                pre.classList.add('code-block');
                const code = document.createElement('code');
                code.textContent = data.sql_query;
                pre.appendChild(code);
                body.appendChild(pre);

                sqlExpander.appendChild(header);
                sqlExpander.appendChild(body);

                // Add Toggle click listener
                header.addEventListener('click', () => {
                    sqlExpander.classList.toggle('collapsed');
                });

                extraContainer.appendChild(sqlExpander);
            }

            // 2. Results Data Table
            if (data.results && data.results.length > 0) {
                const tableContainer = document.createElement('div');
                tableContainer.classList.add('table-container');

                const table = document.createElement('table');
                table.classList.add('data-table');

                // Generate table headers
                const headers = Object.keys(data.results[0]);
                const thead = document.createElement('thead');
                const headerRow = document.createElement('tr');
                headers.forEach(h => {
                    const th = document.createElement('th');
                    th.textContent = h;
                    headerRow.appendChild(th);
                });
                thead.appendChild(headerRow);
                table.appendChild(thead);

                // Generate table body
                const tbody = document.createElement('tbody');
                data.results.forEach(row => {
                    const tr = document.createElement('tr');
                    headers.forEach(h => {
                        const td = document.createElement('td');
                        const val = row[h];
                        td.textContent = (val === null || val === undefined) ? 'NULL' : val;
                        tr.appendChild(td);
                    });
                    tbody.appendChild(tr);
                });
                table.appendChild(tbody);
                tableContainer.appendChild(table);
                extraContainer.appendChild(tableContainer);
            }

            // 3. Telemetry Mini-Banner
            const modelInfo = document.createElement('span');
            modelInfo.classList.add('msg-model-info');
            const latencyText = data.metrics && data.metrics.latency && data.metrics.latency.database_execution
                ? data.metrics.latency.database_execution.toFixed(3)
                : clientDuration;
            
            const providerUsed = data.active_provider || 'gemini';
            const modelUsed = data.active_model || 'Unknown';
            modelInfo.textContent = `Generated via ${providerUsed.toUpperCase()} (${modelUsed}) in ${clientDuration}s. See full diagnostics in the Observability tab.`;
            extraContainer.appendChild(modelInfo);

            // Construct Narrative response
            let narrative = '';
            if (data.error) {
                narrative = `Error executing query: ${data.error}`;
                if (data.sql_query) {
                    narrative += `\n\nGenerated query was executed but failed syntax or execution loops.`;
                }
            } else if (data.results && data.results.length > 0) {
                narrative = `Successfully executed and returned ${data.results.length} rows from database schemas.`;
            } else {
                narrative = `Query executed successfully but returned 0 rows.`;
            }

            appendMessage('assistant', narrative, extraContainer);

        } catch (error) {
            thinkingDiv.remove();
            appendMessage('assistant', `An error occurred: ${error.message}`);
        }
    }

    // Submit Triggers
    chatSendBtn.addEventListener('click', handleQuerySubmit);
    chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleQuerySubmit();
        }
    });

    // Auto-grow textarea height
    chatInput.addEventListener('input', () => {
        chatInput.style.height = 'auto';
        chatInput.style.height = `${chatInput.scrollHeight}px`;
    });

    // Sidebar Example Chats clicks
    exampleBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const query = btn.getAttribute('data-query');
            chatInput.value = query;
            chatInput.style.height = 'auto';
            chatInput.style.height = `${chatInput.scrollHeight}px`;
            switchPage('chats');
            handleQuerySubmit();
        });
    });

    // ==============================================================================
    // OBSERVABILITY VIEW RENDERER
    // ==============================================================================
    function renderObservability() {
        const telemetry = appState.lastQueryTelemetry;

        if (!telemetry || !telemetry.metrics) {
            obsNoData.classList.remove('hidden');
            obsDataView.classList.add('hidden');
            return;
        }

        obsNoData.classList.add('hidden');
        obsDataView.classList.remove('hidden');

        const metrics = telemetry.metrics;

        // 1. Render KPIs
        let latencySec = 0;
        if (metrics.latency) {
            latencySec = Object.values(metrics.latency).reduce((sum, val) => sum + val, 0);
        }

        const promptTokens = metrics.tokens ? (metrics.tokens.prompt_tokens || 0) : 0;
        const completionTokens = metrics.tokens ? (metrics.tokens.completion_tokens || 0) : 0;
        const totalTokens = metrics.tokens ? (metrics.tokens.total_tokens || 0) : 0;

        obsKpis.innerHTML = `
            <div class="kpi-card">
                <p>Pipeline Latency</p>
                <h2>${latencySec.toFixed(3)}s</h2>
                <span class="kpi-sub">Total graph traversal</span>
            </div>
            <div class="kpi-card">
                <p>Total Tokens</p>
                <h2>${totalTokens}</h2>
                <span class="kpi-sub">Context window size</span>
            </div>
            <div class="kpi-card">
                <p>Prompt Tokens</p>
                <h2>${promptTokens}</h2>
                <span class="kpi-sub">Input consumption</span>
            </div>
            <div class="kpi-card">
                <p>Completion Tokens</p>
                <h2>${completionTokens}</h2>
                <span class="kpi-sub">Output generation</span>
            </div>
        `;

        // 2. Render Latency Timeline progress bars
        obsLatencyBars.innerHTML = '';
        if (metrics.latency && Object.keys(metrics.latency).length > 0) {
            const totalDuration = Object.values(metrics.latency).reduce((s, v) => s + v, 0);

            // Ensure proper stage naming translations
            const stageLabels = {
                'intent_clarification': 'Intent Clarification',
                'schema_retrieval': 'FAISS Schema Retrieval & RBAC',
                'query_planning': 'Query Planning Node',
                'sql_generation': 'SQL Statement Generation',
                'syntax_validation': 'SQLGlot Syntax & Security Audits',
                'semantic_validation': 'Execution-Aware Semantic Check',
                'database_execution': 'SQLite Database Driver Query',
                'sql_correction_attempt_1': 'AST SQL Repair Trail - Run 1',
                'sql_correction_attempt_2': 'AST SQL Repair Trail - Run 2',
                'sql_correction_attempt_3': 'AST SQL Repair Trail - Run 3'
            };

            for (const [stage, value] of Object.entries(metrics.latency)) {
                const percentage = totalDuration > 0 ? ((value / totalDuration) * 100).toFixed(1) : 0;
                const label = stageLabels[stage] || stage;
                
                const barItem = document.createElement('div');
                barItem.classList.add('progress-item');
                barItem.innerHTML = `
                    <div class="progress-label-row">
                        <span class="progress-label-name">${label}</span>
                        <span>${value.toFixed(3)}s (${percentage}%)</span>
                    </div>
                    <div class="progress-track">
                        <div class="progress-fill" style="width: ${percentage}%"></div>
                    </div>
                `;
                obsLatencyBars.appendChild(barItem);
            }
        } else {
            obsLatencyBars.innerHTML = '<p class="form-help">No latency timeline metrics returned.</p>';
        }

        // 3. Render Tokens Breakdown
        obsTokensTable.innerHTML = `
            <tr>
                <td>Input / Prompt Tokens</td>
                <td style="font-weight:600;">${promptTokens}</td>
            </tr>
            <tr>
                <td>Output / Completion Tokens</td>
                <td style="font-weight:600;">${completionTokens}</td>
            </tr>
            <tr>
                <td>Accrued Transaction Total</td>
                <td style="font-weight:600; color:var(--color-highlight);">${totalTokens}</td>
            </tr>
        `;

        // 4. Render Query Plan
        if (metrics.query_plan) {
            let planStr = '';
            if (typeof metrics.query_plan === 'object') {
                planStr = JSON.stringify(metrics.query_plan, null, 2);
            } else {
                planStr = metrics.query_plan;
            }
            obsQueryPlanDetails.innerHTML = `<pre class="code-block" style="font-size:0.8rem;"><code>${planStr}</code></pre>`;
        } else if (telemetry.refined_query) {
            obsQueryPlanDetails.innerHTML = `
                <p><strong>Refined Query:</strong> ${telemetry.refined_query}</p>
                <p class="form-help">No structured plan detail exported.</p>
            `;
        } else {
            obsQueryPlanDetails.innerHTML = '<p class="form-help">No planning logs generated.</p>';
        }

        // 5. Schema Auditing Panel
        obsSchemaRetrievalDetails.innerHTML = `
            <p><strong>Active Session User Role:</strong> <code>${appState.currentRole}</code></p>
            <p><strong>Database Access Scope:</strong> Restricted schema validation enabled.</p>
            <p><strong>Target Database Structure:</strong> Local SQLite (test.db)</p>
        `;

        // 6. SQL Query Code and Validation Results
        obsSqlCode.textContent = telemetry.sql_query || '-- No SQL generated';
        
        obsValidationResults.innerHTML = '';
        if (metrics.validation) {
            const syntaxVal = metrics.validation.syntax;
            const semanticVal = metrics.validation.semantic;

            // Render Syntax Badge
            const syntaxBadge = document.createElement('div');
            syntaxBadge.classList.add('validation-box');
            if (syntaxVal) {
                syntaxBadge.innerHTML = `
                    <div class="validation-title">Syntax Validation</div>
                    <div class="validation-status ${syntaxVal.is_valid ? 'val-success' : 'val-failed'}">
                        ${syntaxVal.is_valid ? '&#x2713; PASSED' : '&#x2717; FAILED'}
                    </div>
                    <div class="form-help" style="margin-top:0.25rem;">${syntaxVal.reason}</div>
                `;
            } else {
                syntaxBadge.innerHTML = `
                    <div class="validation-title">Syntax Validation</div>
                    <div class="validation-status val-bypassed">&#x2014; BYPASSED / SKIPPED</div>
                `;
            }
            obsValidationResults.appendChild(syntaxBadge);

            // Render Semantic Badge
            const semanticBadge = document.createElement('div');
            semanticBadge.classList.add('validation-box');
            if (semanticVal) {
                semanticBadge.innerHTML = `
                    <div class="validation-title">Semantic Validation</div>
                    <div class="validation-status ${semanticVal.is_valid ? 'val-success' : 'val-failed'}">
                        ${semanticVal.is_valid ? '&#x2713; PASSED' : '&#x2717; FAILED'}
                    </div>
                    <div class="form-help" style="margin-top:0.25rem;">${semanticVal.reason}</div>
                `;
            } else {
                semanticBadge.innerHTML = `
                    <div class="validation-title">Semantic Validation</div>
                    <div class="validation-status val-bypassed">&#x2014; BYPASSED / SKIPPED</div>
                `;
            }
            obsValidationResults.appendChild(semanticBadge);
        }

        // 7. Repair Trails (AST sql corrections)
        if (metrics.correction_history && metrics.correction_history.length > 0) {
            obsCorrectionPanel.classList.remove('hidden');
            obsRepairHistory.innerHTML = '';

            metrics.correction_history.forEach(attempt => {
                const card = document.createElement('div');
                card.classList.add('repair-attempt-card');
                
                let errTaxonomyMarkup = '';
                if (attempt.error_taxonomy) {
                    errTaxonomyMarkup = `
                        <div class="repair-reason" style="margin-top:0.4rem; font-size:0.75rem;">
                            ⚙️ Classified Error: <strong>${attempt.error_taxonomy.error_type || 'Unknown'}</strong><br>
                            Explanation: ${attempt.error_taxonomy.diagnostics || 'N/A'}
                        </div>
                    `;
                }

                card.innerHTML = `
                    <div class="repair-attempt-header">
                        <span>Attempt #${attempt.attempt} at ${attempt.timestamp || ''}</span>
                        <span style="color:var(--color-highlight);">Auto Repair Loop</span>
                    </div>
                    <div class="repair-attempt-body">
                        <div class="repair-error">
                            <strong>Compiler Exception:</strong><br>
                            ${attempt.error_message}
                        </div>
                        <div class="repair-reason">
                            <strong>Reasoning:</strong> ${attempt.thought_process || 'AST repairs applied.'}
                        </div>
                        ${errTaxonomyMarkup}
                        <div>
                            <strong>Original Broken SQL:</strong>
                            <pre class="code-block" style="font-size:0.75rem;"><code>${attempt.failed_sql}</code></pre>
                        </div>
                        <div>
                            <strong>Corrected Output SQL:</strong>
                            <pre class="code-block" style="font-size:0.75rem; border-color:#10b981;"><code>${attempt.corrected_sql}</code></pre>
                        </div>
                    </div>
                `;
                obsRepairHistory.appendChild(card);
            });
        } else {
            obsCorrectionPanel.classList.add('hidden');
        }
    }

    // ==============================================================================
    // BENCHMARKS HISTORICAL LOADER
    // ==============================================================================
    async function loadBenchmarkData(filename) {
        try {
            const response = await fetch(`/api/v1/benchmarks/${filename}?t=${new Date().getTime()}`);
            if (!response.ok) {
                throw new Error('Benchmark data not found');
            }

            const data = await response.json();
            benchNoData.classList.add('hidden');
            benchDataView.classList.remove('hidden');

            appState.currentBenchmarkRuns = data;
            
            // Populate runs select list
            benchmarkRunSelect.innerHTML = '';
            if (Array.isArray(data) && data.length > 0) {
                data.forEach((run, idx) => {
                    const sum = run.summary || {};
                    const runId = sum.run_id || 'N/A';
                    const ts = sum.timestamp || 'N/A';
                    const prov = sum.provider || '';
                    const mod = sum.model || '';
                    
                    let formattedTs = ts;
                    try {
                        const dt = new Date(ts);
                        formattedTs = dt.toLocaleString();
                    } catch (e) {}
                    
                    let label = `${formattedTs} — ${runId}`;
                    if (prov) {
                        label += ` (${prov.toUpperCase()}: ${mod})`;
                    }
                    
                    const opt = document.createElement('option');
                    opt.value = idx;
                    opt.textContent = label;
                    benchmarkRunSelect.appendChild(opt);
                });
                
                // Render the first run (newest)
                renderBenchmarkMetrics(data[0]);
            } else if (data && data.summary) {
                // Single run payload
                appState.currentBenchmarkRuns = [data];
                const opt = document.createElement('option');
                opt.value = 0;
                opt.textContent = `${data.summary.timestamp || 'N/A'} — ${data.summary.run_id || 'N/A'}`;
                benchmarkRunSelect.appendChild(opt);
                renderBenchmarkMetrics(data);
            } else {
                benchNoData.classList.remove('hidden');
                benchDataView.classList.add('hidden');
            }
        } catch (error) {
            console.error('Error fetching benchmarks:', error);
            benchNoData.classList.remove('hidden');
            benchDataView.classList.add('hidden');
        }
    }

    benchmarkSelect.addEventListener('change', (e) => {
        loadBenchmarkData(e.target.value);
    });

    benchmarkRunSelect.addEventListener('change', (e) => {
        const idx = parseInt(e.target.value);
        if (appState.currentBenchmarkRuns && appState.currentBenchmarkRuns[idx]) {
            renderBenchmarkMetrics(appState.currentBenchmarkRuns[idx]);
        }
    });

    function renderBenchmarkMetrics(run) {
        if (!run || !run.summary) {
            benchNoData.classList.remove('hidden');
            benchDataView.classList.add('hidden');
            return;
        }

        const summary = run.summary;
        const passedPct = summary.execution_accuracy_pct !== undefined 
            ? summary.execution_accuracy_pct.toFixed(1)
            : ((summary.passed_cases / summary.total_cases) * 100).toFixed(1);

        // Calculate Practical Correctness
        const totalCases = run.results.length;
        let practicalPassed = 0;
        run.results.forEach(caseResult => {
            const isPipelineCrash = caseResult.error_message && caseResult.error_message.includes("Pipeline Crash");
            const rowCountMatches = caseResult.returned_rows === caseResult.expected_rows;
            const executedSuccessfully = caseResult.generated_sql !== null && !isPipelineCrash;
            
            if (caseResult.success || (executedSuccessfully && rowCountMatches)) {
                practicalPassed++;
            }
        });
        const practicalPct = totalCases > 0 ? ((practicalPassed / totalCases) * 100).toFixed(1) : "0.0";

        // 1. Populate KPI Cards
        benchKpis.innerHTML = `
            <div class="kpi-card">
                <p>Strict Accuracy</p>
                <h2 style="color: var(--color-red);">${passedPct}%</h2>
                <span class="kpi-sub">${summary.passed_cases} / ${summary.total_cases} exact matches</span>
            </div>
            <div class="kpi-card">
                <p>Practical Correctness</p>
                <h2 style="color: var(--color-green);">${practicalPct}%</h2>
                <span class="kpi-sub">${practicalPassed} / ${totalCases} correct rows</span>
            </div>
            <div class="kpi-card">
                <p>Total Cases</p>
                <h2>${summary.total_cases}</h2>
                <span class="kpi-sub">Benchmark size</span>
            </div>
            <div class="kpi-card">
                <p>Avg Latency</p>
                <h2>${(summary.average_latency_seconds || 0).toFixed(2)}s</h2>
                <span class="kpi-sub">Graph response speed</span>
            </div>
            <div class="kpi-card">
                <p>Avg Tokens</p>
                <h2>${(summary.avg_tokens_per_query || 0).toFixed(0)}</h2>
                <span class="kpi-sub">Input/Output totals</span>
            </div>
        `;

        // 2. Populate Difficulty Accuracy bars
        benchDifficultyBars.innerHTML = '';
        if (summary.difficulty_breakdown) {
            for (const [diff, stats] of Object.entries(summary.difficulty_breakdown)) {
                const acc = stats.accuracy_pct !== undefined ? stats.accuracy_pct.toFixed(1) : 0;
                
                const bar = document.createElement('div');
                bar.classList.add('progress-item');
                bar.innerHTML = `
                    <div class="progress-label-row">
                        <span class="progress-label-name" style="text-transform: capitalize;">${diff}</span>
                        <span>${stats.passed}/${stats.total} (${acc}%)</span>
                    </div>
                    <div class="progress-track">
                        <div class="progress-fill green" style="width: ${acc}%"></div>
                    </div>
                `;
                benchDifficultyBars.appendChild(bar);
            }
        } else {
            benchDifficultyBars.innerHTML = '<p class="form-help">No difficulty metrics exported.</p>';
        }

        // 3. Render Error Taxonomy chart/metrics
        benchErrorBars.innerHTML = '';
        // Group failed queries errors
        const errorCategories = {};
        const failuresList = run.results.filter(r => !r.success);
        
        failuresList.forEach(fail => {
            let cat = 'Other Execution Error';
            const msg = fail.error_message || '';
            if (msg.includes('langchain-openai') || msg.includes('Not Found') || msg.includes('API key')) {
                cat = 'LLM Config/Connection';
            } else if (msg.includes('Security Exception') || msg.includes('RBAC') || msg.includes('Permission')) {
                cat = 'Governance Permission Denied';
            } else if (msg.includes('no such table') || msg.includes('no such column')) {
                cat = 'Schema/Syntax AST Mismatch';
            }
            errorCategories[cat] = (errorCategories[cat] || 0) + 1;
        });

        const totalFailures = failuresList.length;
        if (totalFailures > 0) {
            for (const [cat, count] of Object.entries(errorCategories)) {
                const pct = ((count / totalFailures) * 100).toFixed(1);
                const bar = document.createElement('div');
                bar.classList.add('progress-item');
                bar.innerHTML = `
                    <div class="progress-label-row">
                        <span class="progress-label-name">${cat}</span>
                        <span>${count} cases (${pct}%)</span>
                    </div>
                    <div class="progress-track">
                        <div class="progress-fill red" style="width: ${pct}%"></div>
                    </div>
                `;
                benchErrorBars.appendChild(bar);
            }
        } else {
            benchErrorBars.innerHTML = '<p class="form-help" style="color:#10b981;">Zero errors — Perfect execution accuracy score.</p>';
        }

        // 4. Render Latency Distribution List
        benchLatencyDist.innerHTML = '';
        const sortedCases = [...run.results].sort((a, b) => b.latency_seconds - a.latency_seconds).slice(0, 5);
        sortedCases.forEach(c => {
            const bar = document.createElement('div');
            bar.classList.add('progress-item');
            const latency = c.latency_seconds ? c.latency_seconds.toFixed(2) : 0;
            const pct = Math.min((c.latency_seconds / (summary.average_latency_seconds * 3 || 10)) * 100, 100).toFixed(0);
            bar.innerHTML = `
                <div class="progress-label-row">
                    <span class="progress-label-name">Case ${c.case_id}: "${c.query}"</span>
                    <span>${latency}s</span>
                </div>
                <div class="progress-track">
                    <div class="progress-fill" style="width: ${pct}%;"></div>
                </div>
            `;
            benchLatencyDist.appendChild(bar);
        });

        // 5. Render projected Token cost metrics
        benchTokenProjections.innerHTML = `
            <div style="background-color:#1a1a1d; padding:1rem; border-radius:10px; border:1px solid var(--border-color);">
                <div style="font-size:0.8rem; color:var(--text-secondary); margin-bottom:0.5rem;">ESTIMATED RUN METRICS</div>
                <div style="display:flex; justify-content:space-between; margin-bottom:0.4rem;">
                    <span>Accumulated Prompt Tokens:</span>
                    <strong style="color:var(--text-primary);">${summary.total_cases * (summary.avg_tokens_per_query * 0.75).toFixed(0)}</strong>
                </div>
                <div style="display:flex; justify-content:space-between; margin-bottom:0.4rem;">
                    <span>Accumulated Completion Tokens:</span>
                    <strong style="color:var(--text-primary);">${summary.total_cases * (summary.avg_tokens_per_query * 0.25).toFixed(0)}</strong>
                </div>
                <div style="display:flex; justify-content:space-between; border-top:1px solid #333; padding-top:0.4rem;">
                    <span>Projected Run API Cost (Gemini Base):</span>
                    <strong style="color:var(--color-highlight);">$0.00</strong>
                </div>
            </div>
        `;

        // 6. Populate failed query table
        benchFailuresTable.innerHTML = '';
        if (failuresList.length > 0) {
            failuresList.forEach(fail => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td style="font-weight:600;">${fail.case_id}</td>
                    <td style="max-width:240px; word-break:break-word;">${fail.query}</td>
                    <td style="color:#f87171; max-width:300px; word-break:break-word; font-family:monospace; font-size:0.75rem;">${fail.error_message}</td>
                    <td style="text-align:center;">${fail.retry_count || 0}</td>
                    <td style="text-align:center;">${fail.total_tokens || 0}</td>
                `;
                benchFailuresTable.appendChild(tr);
            });
        } else {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td colspan="5" style="text-align:center; color:var(--text-secondary); padding:2rem;">
                    🎉 No execution failures logged for this dataset run target.
                </td>
            `;
            benchFailuresTable.appendChild(tr);
        }
    }

    // ==============================================================================
    // INITIALIZATION RUNS
    // ==============================================================================
    loadBackendConfig();
});
