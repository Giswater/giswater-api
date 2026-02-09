/* ===================================================================
   API Log Viewer — JS Logic
   =================================================================== */

// ── Constants & State ─────────────────────────────────────────────
const API_BASE = resolveApiBase();
let gridApi = null;
let currentOffset = 0;
let currentLimit = 200;
let lastFetchedCount = 0;

function resolveApiBase() {
    // The FastAPI app is mounted at root_path="/api/v1",
    // but static files and the /logs/ui page are served at that root_path.
    // The /logs and /logs/db endpoints live under the same root_path.
    // We derive the base from the current page URL.
    const loc = window.location;
    // The page is served at <root_path>/logs/ui, so strip "/logs/ui"
    const path = loc.pathname.replace(/\/logs\/ui\/?$/, "");
    return `${loc.protocol}//${loc.host}${path}`;
}

// ── Status Helpers ────────────────────────────────────────────────
function statusClass(code) {
    if (code >= 200 && code < 300) return "2xx";
    if (code >= 300 && code < 400) return "3xx";
    if (code >= 400 && code < 500) return "4xx";
    if (code >= 500) return "5xx";
    return "";
}

function rowStyleForStatus(params) {
    const s = params.data?.status;
    const style = {};

    // Status color
    if (s != null) {
        const cls = statusClass(s);
        const map = {
            "2xx": "var(--status-2xx)",
            "3xx": "var(--status-3xx)",
            "4xx": "var(--status-4xx)",
            "5xx": "var(--status-5xx)",
        };
        if (map[cls]) style.background = map[cls];
    }

    // Day separator — thick top border when day changes from previous row
    if (params.data?._isNewDay) {
        style.borderTop = "2px solid var(--day-separator-color)";
    }

    return Object.keys(style).length ? style : undefined;
}

/** Mark the first row of each day with _isNewDay = true. Data is sorted DESC. */
function markDayBoundaries(items) {
    let prevDay = null;
    for (const item of items) {
        if (!item.ts) continue;
        const day = new Date(item.ts).toDateString();
        if (prevDay !== null && day !== prevDay) {
            item._isNewDay = true;
            item._dayLabel = day;
        }
        prevDay = day;
    }
    return items;
}

// ── Cell Renderers ────────────────────────────────────────────────
function timestampFormatter(params) {
    if (!params.value) return "";
    const d = new Date(params.value);
    return d.toLocaleString(undefined, {
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
    });
}

function statusRenderer(params) {
    const v = params.value;
    if (v == null) return "";
    const cls = statusClass(v);
    return `<span class="status-badge s${cls}">${v}</span>`;
}

function methodRenderer(params) {
    const v = params.value;
    if (!v) return "";
    return `<span class="method-badge ${v.toLowerCase()}">${v}</span>`;
}

function dbLogsCellRenderer(params) {
    if (!params.data?.has_db_logs) return "";
    const rid = params.data.request_id;
    if (!rid) return "";
    return `<button class="db-logs-btn" data-rid="${rid}" title="View DB logs">DB</button>`;
}

// ── AG Grid Column Definitions ────────────────────────────────────
const columnDefs = [
    {
        field: "ts",
        headerName: "Timestamp",
        width: 175,
        sortable: true,
        valueFormatter: timestampFormatter,
    },
    {
        field: "method",
        headerName: "Method",
        width: 95,
        sortable: true,
        filter: true,
        cellRenderer: methodRenderer,
    },
    {
        field: "endpoint",
        headerName: "Endpoint",
        flex: 2,
        sortable: true,
        filter: true,
    },
    {
        field: "status",
        headerName: "Status",
        width: 90,
        sortable: true,
        filter: true,
        cellRenderer: statusRenderer,
    },
    {
        field: "duration_ms",
        headerName: "Duration (ms)",
        width: 120,
        sortable: true,
    },
    {
        field: "user_name",
        headerName: "User",
        width: 130,
        sortable: true,
        filter: true,
    },
    {
        field: "client_ip",
        headerName: "IP",
        width: 130,
        sortable: true,
    },
    {
        field: "request_id",
        headerName: "Request ID",
        width: 140,
        valueFormatter: (p) => (p.value ? p.value.substring(0, 8) + "…" : ""),
    },
    {
        headerName: "",
        width: 60,
        cellRenderer: dbLogsCellRenderer,
        sortable: false,
        filter: false,
        suppressSizeToFit: true,
    },
];

// ── AG Grid Setup ─────────────────────────────────────────────────
const gridOptions = {
    columnDefs: columnDefs,
    defaultColDef: {
        resizable: true,
    },
    rowData: [],
    getRowStyle: rowStyleForStatus,
    suppressCellFocus: true,
    onRowClicked: (event) => {
        // Ignore clicks on the DB button column
        if (event.event?.target?.closest(".db-logs-btn")) return;
        openDrawer(event.data);
    },
    onCellClicked: (event) => {
        const btn = event.event?.target?.closest(".db-logs-btn");
        if (btn) {
            event.event.stopPropagation();
            openDrawer(event.data, true);
        }
    },
};

// ── API Calls ─────────────────────────────────────────────────────
async function fetchLogs() {
    const params = new URLSearchParams();

    const from = document.getElementById("filter-from").value;
    const to = document.getElementById("filter-to").value;
    const endpoint = document.getElementById("filter-endpoint").value.trim();
    const method = document.getElementById("filter-method").value;
    const status = document.getElementById("filter-status").value.trim();
    const user = document.getElementById("filter-user").value.trim();
    const limit = document.getElementById("filter-limit").value.trim();

    if (from) params.set("from", new Date(from).toISOString());
    if (to) params.set("to", new Date(to).toISOString());
    if (endpoint) params.set("endpoint", endpoint);
    if (method) params.set("method", method);
    if (status) params.set("status", status);
    if (user) params.set("user", user);

    currentLimit = parseInt(limit, 10) || 200;
    params.set("limit", currentLimit);
    params.set("offset", currentOffset);

    try {
        const resp = await fetch(`${API_BASE}/logs?${params}`);
        if (!resp.ok) {
            console.error("Fetch logs failed:", resp.status, resp.statusText);
            return;
        }
        const data = await resp.json();
        lastFetchedCount = data.count || 0;
        const items = markDayBoundaries(data.items || []);
        gridApi.setGridOption("rowData", items);
        updatePagination();
        updateResultCount();
    } catch (err) {
        console.error("Fetch logs error:", err);
    }
}

async function fetchDbLogs(requestId) {
    try {
        const resp = await fetch(
            `${API_BASE}/logs/db?request_id=${encodeURIComponent(requestId)}`
        );
        if (!resp.ok) return [];
        const data = await resp.json();
        return data.items || [];
    } catch (err) {
        console.error("Fetch DB logs error:", err);
        return [];
    }
}

// ── Pagination ────────────────────────────────────────────────────
function nextPage() {
    currentOffset += currentLimit;
    fetchLogs();
}

function prevPage() {
    currentOffset = Math.max(0, currentOffset - currentLimit);
    fetchLogs();
}

function resetPagination() {
    currentOffset = 0;
}

function updatePagination() {
    const btnPrev = document.getElementById("btn-prev");
    const btnNext = document.getElementById("btn-next");
    const pageInfo = document.getElementById("page-info");

    btnPrev.disabled = currentOffset === 0;
    btnNext.disabled = lastFetchedCount < currentLimit;

    const pageStart = currentOffset + 1;
    const pageEnd = currentOffset + lastFetchedCount;
    pageInfo.textContent =
        lastFetchedCount > 0
            ? `Showing ${pageStart}–${pageEnd}`
            : "No results";
}

function updateResultCount() {
    const el = document.getElementById("result-count");
    el.textContent =
        lastFetchedCount > 0 ? `${lastFetchedCount} rows loaded` : "";
}

// ── Detail Drawer ─────────────────────────────────────────────────
function openDrawer(rowData, scrollToDbLogs = false) {
    const overlay = document.getElementById("drawer-overlay");
    const drawer = document.getElementById("detail-drawer");
    const body = document.getElementById("drawer-body");

    body.innerHTML = buildDrawerContent(rowData);
    overlay.classList.add("open");
    drawer.classList.add("open");

    // Set up collapsible toggles
    body.querySelectorAll(".collapsible-toggle").forEach((toggle) => {
        toggle.addEventListener("click", () => {
            toggle.classList.toggle("collapsed");
            const content = toggle.nextElementSibling;
            if (content) content.classList.toggle("collapsed");
        });
    });

    // Copy cURL button
    const curlBtn = document.getElementById("copy-curl-btn");
    if (curlBtn) {
        curlBtn.addEventListener("click", () => {
            copyToClipboard(buildCurlCommand(rowData), curlBtn);
        });
    }

    // Fetch DB logs
    if (rowData.request_id) {
        loadDbLogs(rowData.request_id, scrollToDbLogs);
    }
}

function closeDrawer() {
    document.getElementById("drawer-overlay").classList.remove("open");
    document.getElementById("detail-drawer").classList.remove("open");
}

// ── Popup (lightweight modal for viewing SQL / JSON) ──────────────
function openPopup(title, text) {
    // Remove any existing popup
    closePopup();

    const backdrop = document.createElement("div");
    backdrop.className = "popup-backdrop";
    backdrop.addEventListener("click", closePopup);

    const popup = document.createElement("div");
    popup.className = "popup";
    popup.innerHTML = `
        <div class="popup-header">
            <span class="popup-title">${escapeHtml(title)}</span>
            <div class="popup-header-actions">
                <button class="icon-btn" id="popup-copy-btn" title="Copy to clipboard">&#128203;</button>
                <button class="popup-close" title="Close">&times;</button>
            </div>
        </div>
        <pre class="popup-body">${escapeHtml(text)}</pre>
    `;

    document.body.appendChild(backdrop);
    document.body.appendChild(popup);

    popup.querySelector(".popup-close").addEventListener("click", closePopup);
    popup.querySelector("#popup-copy-btn").addEventListener("click", (e) => {
        copyToClipboard(text, e.currentTarget);
    });

    // Close on Escape (but don't close the drawer behind it)
    popup._escHandler = (e) => {
        if (e.key === "Escape") {
            e.stopImmediatePropagation();
            closePopup();
        }
    };
    document.addEventListener("keydown", popup._escHandler, true);
}

function closePopup() {
    const backdrop = document.querySelector(".popup-backdrop");
    const popup = document.querySelector(".popup");
    if (popup?._escHandler) {
        document.removeEventListener("keydown", popup._escHandler, true);
    }
    backdrop?.remove();
    popup?.remove();
}

function buildDrawerContent(d) {
    const sections = [];

    // Summary + Copy curl
    sections.push(`
        <div class="drawer-section">
            <div class="drawer-section-title" style="display:flex;align-items:center;justify-content:space-between">
                Summary
                <button class="copy-btn" id="copy-curl-btn" title="Copy as cURL command">Copy cURL</button>
            </div>
            <div class="drawer-summary">
                <div class="drawer-field">
                    <span class="field-label">Method</span>
                    <span class="field-value">${methodRenderer({ value: d.method })}</span>
                </div>
                <div class="drawer-field">
                    <span class="field-label">Status</span>
                    <span class="field-value">${statusRenderer({ value: d.status })}</span>
                </div>
                <div class="drawer-field full-width">
                    <span class="field-label">Endpoint</span>
                    <span class="field-value">${escapeHtml(d.endpoint || "")}</span>
                </div>
                <div class="drawer-field">
                    <span class="field-label">Duration</span>
                    <span class="field-value">${d.duration_ms != null ? d.duration_ms + " ms" : "—"}</span>
                </div>
                <div class="drawer-field">
                    <span class="field-label">User</span>
                    <span class="field-value">${escapeHtml(d.user_name || "—")}</span>
                </div>
                <div class="drawer-field">
                    <span class="field-label">Client IP</span>
                    <span class="field-value">${escapeHtml(d.client_ip || "—")}</span>
                </div>
                <div class="drawer-field">
                    <span class="field-label">Timestamp</span>
                    <span class="field-value">${d.ts ? new Date(d.ts).toLocaleString() : "—"}</span>
                </div>
                <div class="drawer-field full-width">
                    <span class="field-label">Request ID</span>
                    <span class="field-value">${escapeHtml(d.request_id || "—")}</span>
                </div>
            </div>
        </div>
    `);

    // Query Params
    if (d.query_params && Object.keys(d.query_params).length > 0) {
        sections.push(collapsibleSection("Query Params", formatJson(d.query_params)));
    }

    // Request Headers
    if (d.request_headers && Object.keys(d.request_headers).length > 0) {
        sections.push(collapsibleSection("Request Headers", formatJson(d.request_headers)));
    }

    // Request Body
    if (d.request_body) {
        sections.push(collapsibleSection("Request Body", formatJsonOrText(d.request_body)));
    }

    // Response Headers
    if (d.response_headers && Object.keys(d.response_headers).length > 0) {
        sections.push(collapsibleSection("Response Headers", formatJson(d.response_headers), true));
    }

    // Response Body
    if (d.response_body) {
        sections.push(collapsibleSection("Response Body", formatJsonOrText(d.response_body), true));
    }

    // DB Logs placeholder
    sections.push(`
        <div class="drawer-section" id="db-logs-section">
            <div class="drawer-section-title">DB Logs</div>
            <div id="db-logs-content" class="db-logs-loading">Loading DB logs…</div>
        </div>
    `);

    return sections.join("");
}

function collapsibleSection(title, content, startCollapsed = false) {
    const collapsedClass = startCollapsed ? " collapsed" : "";
    return `
        <div class="drawer-section">
            <div class="collapsible-toggle${collapsedClass}">
                <span class="arrow">&#9660;</span>
                <span class="drawer-section-title" style="border:none;margin:0;padding:0">${title}</span>
            </div>
            <div class="collapsible-content${collapsedClass}">
                <div class="json-block">${content}</div>
            </div>
        </div>
    `;
}

async function loadDbLogs(requestId, scrollTo = false) {
    const container = document.getElementById("db-logs-content");
    if (!container) return;

    container.innerHTML = '<span class="db-logs-loading">Loading DB logs…</span>';
    const items = await fetchDbLogs(requestId);

    if (items.length === 0) {
        container.innerHTML = '<span class="db-logs-empty">No DB logs for this request.</span>';
        return;
    }

    // Store items for action buttons
    container._dbLogItems = items;

    let rows = "";
    for (let i = 0; i < items.length; i++) {
        const item = items[i];
        const statusCls = item.error ? "error" : "ok";
        const hasSql = !!item.sql_text;
        const hasJson = !!item.response_json;
        rows += `
            <tr>
                <td>${escapeHtml(item.function_name || "—")}</td>
                <td>${escapeHtml(item.schema_name || "—")}</td>
                <td class="db-actions-cell">
                    <div class="db-actions-group">
                        <span class="db-actions-label">SQL</span>
                        <button class="icon-btn" data-action="view-sql" data-idx="${i}" title="View SQL" ${hasSql ? "" : "disabled"}>&#128065;</button>
                        <button class="icon-btn" data-action="copy-sql" data-idx="${i}" title="Copy SQL" ${hasSql ? "" : "disabled"}>&#128203;</button>
                    </div>
                    <div class="db-actions-group">
                        <span class="db-actions-label">JSON</span>
                        <button class="icon-btn" data-action="view-json" data-idx="${i}" title="View Response JSON" ${hasJson ? "" : "disabled"}>&#128065;</button>
                        <button class="icon-btn" data-action="copy-json" data-idx="${i}" title="Copy Response JSON" ${hasJson ? "" : "disabled"}>&#128203;</button>
                    </div>
                </td>
                <td>${item.duration_ms != null ? item.duration_ms : "—"}</td>
                <td><span class="db-logs-status ${statusCls}">${escapeHtml(item.status || "—")}</span></td>
                <td>${escapeHtml(truncate(item.error, 80) || "—")}</td>
            </tr>
        `;
    }

    container.innerHTML = `
        <table class="db-logs-table">
            <thead>
                <tr>
                    <th>Function</th>
                    <th>Schema</th>
                    <th>SQL / Response</th>
                    <th>ms</th>
                    <th>Status</th>
                    <th>Error</th>
                </tr>
            </thead>
            <tbody>${rows}</tbody>
        </table>
    `;

    // Wire up action buttons
    container.querySelectorAll(".icon-btn[data-action]").forEach((btn) => {
        btn.addEventListener("click", (e) => {
            e.stopPropagation();
            const idx = parseInt(btn.dataset.idx, 10);
            const item = container._dbLogItems[idx];
            if (!item) return;
            const action = btn.dataset.action;
            if (action === "view-sql") {
                openPopup("SQL Query", item.sql_text || "");
            } else if (action === "copy-sql") {
                copyToClipboard(item.sql_text || "", btn);
            } else if (action === "view-json") {
                let text = item.response_json || "";
                try { text = JSON.stringify(JSON.parse(text), null, 2); } catch { /* keep as-is */ }
                openPopup("Response JSON", text);
            } else if (action === "copy-json") {
                let text = item.response_json || "";
                try { text = JSON.stringify(JSON.parse(text), null, 2); } catch { /* keep as-is */ }
                copyToClipboard(text, btn);
            }
        });
    });

    if (scrollTo) {
        const section = document.getElementById("db-logs-section");
        if (section) section.scrollIntoView({ behavior: "smooth" });
    }
}

// ── Copy Helpers ──────────────────────────────────────────────────
async function copyToClipboard(text, btnEl) {
    try {
        await navigator.clipboard.writeText(text);
        if (btnEl) {
            const orig = btnEl.textContent;
            btnEl.textContent = "Copied!";
            setTimeout(() => (btnEl.textContent = orig), 1500);
        }
    } catch {
        // Fallback
        const ta = document.createElement("textarea");
        ta.value = text;
        ta.style.position = "fixed";
        ta.style.opacity = "0";
        document.body.appendChild(ta);
        ta.select();
        document.execCommand("copy");
        document.body.removeChild(ta);
        if (btnEl) {
            const orig = btnEl.textContent;
            btnEl.textContent = "Copied!";
            setTimeout(() => (btnEl.textContent = orig), 1500);
        }
    }
}

function buildCurlCommand(d) {
    const fullUrl = `${API_BASE}${d.endpoint || "/"}`;
    const qp = d.query_params && Object.keys(d.query_params).length
        ? "?" + new URLSearchParams(d.query_params).toString()
        : "";
    const parts = [`curl -X ${d.method || "GET"} '${fullUrl}${qp}'`];

    // Headers
    if (d.request_headers && typeof d.request_headers === "object") {
        for (const [k, v] of Object.entries(d.request_headers)) {
            parts.push(`  -H '${k}: ${v}'`);
        }
    }

    // Body
    if (d.request_body) {
        let body = d.request_body;
        // Try to minify JSON for a cleaner curl
        try {
            body = JSON.stringify(JSON.parse(body));
        } catch { /* keep as-is */ }
        parts.push(`  -d '${body.replace(/'/g, "'\\''")}'`);
    }

    return parts.join(" \\\n");
}

// ── Utility Functions ─────────────────────────────────────────────
function escapeHtml(str) {
    if (str == null) return "";
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");
}

function formatJson(obj) {
    try {
        return escapeHtml(JSON.stringify(obj, null, 2));
    } catch {
        return escapeHtml(String(obj));
    }
}

function formatJsonOrText(raw) {
    if (typeof raw === "string") {
        try {
            const parsed = JSON.parse(raw);
            return escapeHtml(JSON.stringify(parsed, null, 2));
        } catch {
            return escapeHtml(raw);
        }
    }
    return formatJson(raw);
}

function truncate(str, maxLen) {
    if (!str) return "";
    if (str.length <= maxLen) return str;
    return str.substring(0, maxLen) + "…";
}

function setDefaultDates() {
    const now = new Date();
    const yesterday = new Date(now.getTime() - 24 * 60 * 60 * 1000);

    // Format to local datetime-local input value
    const toLocal = (d) => {
        const pad = (n) => String(n).padStart(2, "0");
        return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
    };

    document.getElementById("filter-from").value = toLocal(yesterday);
    document.getElementById("filter-to").value = toLocal(now);
}

// ── Init ──────────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
    // Create grid
    const gridDiv = document.getElementById("log-grid");
    gridApi = agGrid.createGrid(gridDiv, gridOptions);

    // Set default date range (last 24h)
    setDefaultDates();

    // Wire up search button
    document.getElementById("btn-search").addEventListener("click", () => {
        resetPagination();
        fetchLogs();
    });

    // Wire up Enter key on filter inputs
    document.querySelectorAll(".filter-bar input, .filter-bar select").forEach((el) => {
        el.addEventListener("keydown", (e) => {
            if (e.key === "Enter") {
                resetPagination();
                fetchLogs();
            }
        });
    });

    // Pagination
    document.getElementById("btn-prev").addEventListener("click", prevPage);
    document.getElementById("btn-next").addEventListener("click", nextPage);

    // Drawer close
    document.getElementById("drawer-close").addEventListener("click", closeDrawer);
    document.getElementById("drawer-overlay").addEventListener("click", closeDrawer);
    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape") closeDrawer();
    });

    // Initial fetch
    fetchLogs();
});
