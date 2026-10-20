/**
 * FinPulse AI - Interactive Client Application Logic
 */

// Global State
let currentClientId = "alex_chen";
let clientData = null;
let clientReport = null;
let chatHistory = [];

// Chart References
let radarChartInstance = null;
let donutChartInstance = null;
let mcChartInstance = null;

// Initialization
document.addEventListener("DOMContentLoaded", async () => {
  if (window.lucide) {
    lucide.createIcons();
  }
  await loadClientData(currentClientId);
});

// Tab Switching
function switchTab(tabId) {
  const tabs = ["chat", "budgeting", "forecasting", "debt", "report"];
  tabs.forEach(t => {
    const el = document.getElementById(`view-${t}`);
    const btn = document.getElementById(`tab-btn-${t}`);
    if (el && btn) {
      if (t === tabId) {
        el.classList.remove("hidden");
        el.classList.add("block");
        btn.classList.add("active");
      } else {
        el.classList.remove("block");
        el.classList.add("hidden");
        btn.classList.remove("active");
      }
    }
  });

  // Re-trigger layout/render of charts if tab was hidden
  if (tabId === "forecasting" && mcChartInstance) {
    mcChartInstance.resize();
  }
  if (tabId === "budgeting" && donutChartInstance) {
    donutChartInstance.resize();
  }
  if (tabId === "chat" && radarChartInstance) {
    radarChartInstance.resize();
  }

  if (window.lucide) {
    lucide.createIcons();
  }
}

// Client Switching
async function changeClient(clientId) {
  currentClientId = clientId;
  chatHistory = [];
  await loadClientData(clientId);
}

// Fetch Client & Report Data
async function loadClientData(clientId) {
  try {
    const res = await fetch(`/api/client/${clientId}`);
    if (!res.ok) throw new Error("Failed to load client profile");
    const data = await res.json();
    
    clientData = data.profile;
    clientReport = data.report;

    updateTopStrip();
    renderChatGreeting();
    renderRadarChart();
    renderGoals();
    renderBudgetView();
    renderMonteCarloView();
    renderDebtView();
    renderReportView();

    if (window.lucide) {
      lucide.createIcons();
    }
  } catch (err) {
    console.error("Error loading client:", err);
  }
}

// Top Metrics Ribbon Update
function updateTopStrip() {
  if (!clientReport) return;
  const rep = clientReport;
  const netWorth = rep.balance_sheet.net_worth;
  const cashflow = rep.budget_analysis.net_cashflow;
  const emergencyMo = rep.scorecard.emergency_months;
  const debt = rep.balance_sheet.total_debt;
  const risk = rep.client.risk_tolerance;
  const score = rep.scorecard.overall_health;

  document.getElementById("strip-net-worth").textContent = `$${netWorth.toLocaleString()}`;
  document.getElementById("strip-cashflow").textContent = `${cashflow >= 0 ? '+' : ''}$${cashflow.toLocaleString()}/mo`;
  document.getElementById("strip-cashflow").className = `text-sm font-bold ${cashflow >= 0 ? 'text-emerald-400' : 'text-rose-400'}`;
  document.getElementById("strip-emergency").textContent = `${emergencyMo} Months`;
  document.getElementById("strip-debt").textContent = `$${debt.toLocaleString()}`;
  document.getElementById("strip-risk").textContent = risk;
  document.getElementById("strip-score").textContent = `${score} / 100`;

  let grade = "Good";
  let gradeClass = "bg-amber-500/20 text-amber-300";
  if (score >= 85) {
    grade = "Excellent";
    gradeClass = "bg-emerald-500/20 text-emerald-300";
  } else if (score < 60) {
    grade = "At Risk";
    gradeClass = "bg-rose-500/20 text-rose-300";
  }
  const gradeEl = document.getElementById("strip-grade");
  gradeEl.textContent = grade;
  gradeEl.className = `px-1.5 py-0.2 rounded text-[10px] font-bold ${gradeClass}`;
}

// -------------------------------------------------------------
// CHATBOT IMPLEMENTATION
// -------------------------------------------------------------
function renderChatGreeting() {
  const container = document.getElementById("chat-messages");
  container.innerHTML = "";

  const name = clientData ? clientData.name : "there";
  const initialBotMsg = `
    Hello **${name}**! 👋 I am your **FinPulse 24/7 AI Financial Advisor**.\n\n
    I've analyzed your cash flow, debts, and retirement projections. Here are a few things we can explore right now:\n
    - **Optimize Budgeting**: Identify unnecessary recurring subscriptions.\n
    - **Home Affordability**: Test whether you're ready to purchase a home or condo.\n
    - **Monte Carlo Stress Test**: Assess early retirement readiness under bear market scenarios.\n
    - **Debt Payoff**: Run Avalanche vs Snowball payoff strategies.\n\n
    *How can I help you take control of your financial future today?*
  `;
  appendMessage("bot", initialBotMsg);
}

function appendMessage(sender, text, keyMetrics = null, cfpEscalation = null) {
  const container = document.getElementById("chat-messages");
  const bubble = document.createElement("div");
  bubble.className = `message-bubble ${sender} fade-in`;

  // Basic markdown formatting
  let formatted = text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/^### (.*$)/gim, '<h3>$1</h3>')
    .replace(/^#### (.*$)/gim, '<h4>$1</h4>')
    .replace(/\n\n/g, '<br/><br/>')
    .replace(/\n- /g, '<br/>• ');

  // Markdown tables
  if (text.includes('| Strategy |') || text.includes('|---')) {
    formatted = parseMarkdownTable(text);
  }

  let htmlContent = `<div>${formatted}</div>`;

  // Render Key Metrics Pills if available
  if (keyMetrics && Object.keys(keyMetrics).length > 0) {
    htmlContent += `<div class="metrics-pill-grid">`;
    for (const [k, v] of Object.entries(keyMetrics)) {
      htmlContent += `
        <div class="metric-pill">
          <div class="label">${k}</div>
          <div class="val">${v}</div>
        </div>
      `;
    }
    htmlContent += `</div>`;
  }

  // CFP Escalation Alert if required
  if (cfpEscalation && cfpEscalation.needs_human_cfp) {
    htmlContent += `
      <div class="mt-3 p-3 rounded-lg bg-amber-500/15 border border-amber-500/30 text-amber-200 text-xs flex items-center justify-between">
        <div class="flex items-center gap-2">
          <i data-lucide="shield-alert" class="w-4 h-4 text-amber-400"></i>
          <span>${cfpEscalation.cfp_reason}</span>
        </div>
        <button onclick="requestCFPModal()" class="px-2.5 py-1 rounded bg-amber-600 hover:bg-amber-500 text-white font-semibold text-[11px] whitespace-nowrap ml-2">
          Schedule CFP
        </button>
      </div>
    `;
  }

  bubble.innerHTML = htmlContent;
  container.appendChild(bubble);
  container.scrollTop = container.scrollHeight;

  if (window.lucide) {
    lucide.createIcons();
  }
}

function parseMarkdownTable(rawText) {
  const lines = rawText.split('\n');
  let inTable = false;
  let tableHtml = '<div class="overflow-x-auto"><table class="w-full">';
  let outText = '';

  for (let line of lines) {
    line = line.trim();
    if (line.startsWith('|') && line.endsWith('|')) {
      if (!inTable) {
        inTable = true;
      }
      if (line.includes('---')) continue; // separator line

      const cells = line.split('|').slice(1, -1).map(c => c.trim());
      tableHtml += '<tr>';
      cells.forEach(c => {
        let clean = c.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        tableHtml += `<td>${clean}</td>`;
      });
      tableHtml += '</tr>';
    } else {
      if (inTable) {
        tableHtml += '</table></div>';
        outText += tableHtml;
        inTable = false;
        tableHtml = '<div class="overflow-x-auto"><table class="w-full">';
      }
      outText += line + '<br/>';
    }
  }

  if (inTable) {
    tableHtml += '</table></div>';
    outText += tableHtml;
  }

  return outText
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/^### (.*$)/gim, '<h3>$1</h3>')
    .replace(/^#### (.*$)/gim, '<h4>$1</h4>');
}

async function handleChatSubmit(event) {
  event.preventDefault();
  const input = document.getElementById("chat-input");
  const msg = input.value.trim();
  if (!msg) return;

  input.value = "";
  appendMessage("user", msg);

  // Show typing loader indicator
  const typingIndicator = document.createElement("div");
  typingIndicator.id = "bot-typing";
  typingIndicator.className = "message-bubble bot text-xs text-slate-400 italic flex items-center gap-2";
  typingIndicator.innerHTML = `
    <span class="inline-block w-2 h-2 rounded-full bg-blue-400 animate-ping"></span>
    FinPulse AI is analyzing portfolio models and calculating scenarios...
  `;
  document.getElementById("chat-messages").appendChild(typingIndicator);
  document.getElementById("chat-messages").scrollTop = document.getElementById("chat-messages").scrollHeight;

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        client_id: currentClientId,
        message: msg,
        history: chatHistory
      })
    });

    const indicator = document.getElementById("bot-typing");
    if (indicator) indicator.remove();

    if (!res.ok) throw new Error("API call error");
    const data = await res.json();

    chatHistory.push({ user: msg, bot: data.response });
    appendMessage("bot", data.response, data.key_metrics, {
      needs_human_cfp: data.needs_human_cfp,
      cfp_reason: data.cfp_reason
    });

    // Update suggested prompts
    if (data.suggested_prompts && data.suggested_prompts.length > 0) {
      updateQuickPrompts(data.suggested_prompts);
    }
  } catch (err) {
    const indicator = document.getElementById("bot-typing");
    if (indicator) indicator.remove();
    appendMessage("bot", "I apologize, but I encountered an issue evaluating your request. Please try again.");
    console.error(err);
  }
}

function sendQuickPrompt(promptText) {
  const input = document.getElementById("chat-input");
  input.value = promptText;
  document.getElementById("chat-send-btn").click();
}

function updateQuickPrompts(prompts) {
  const container = document.getElementById("quick-prompts-container");
  container.innerHTML = "";
  prompts.forEach(p => {
    const btn = document.createElement("button");
    btn.className = "prompt-chip";
    btn.textContent = `💡 ${p}`;
    btn.onclick = () => sendQuickPrompt(p);
    container.appendChild(btn);
  });
}

// -------------------------------------------------------------
// RADAR CHART & GOALS (SIDEBAR)
// -------------------------------------------------------------
function renderRadarChart() {
  if (!clientReport) return;
  const rep = clientReport.scorecard;
  const canvas = document.getElementById("healthRadarChart");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");

  if (radarChartInstance) {
    radarChartInstance.destroy();
  }

  document.getElementById("sidebar-overall-score").textContent = `${rep.overall_health} / 100`;
  document.getElementById("score-liquidity-txt").textContent = `${rep.liquidity_score} / 100`;
  document.getElementById("score-debt-txt").textContent = `${rep.debt_score} / 100`;
  document.getElementById("score-budget-txt").textContent = `${rep.budget_score} / 100`;
  document.getElementById("score-retirement-txt").textContent = `${rep.retirement_score} / 100`;

  radarChartInstance = new Chart(ctx, {
    type: 'radar',
    data: {
      labels: ['Emergency Liquidity', 'Debt Health', 'Budget Discipline', 'Retirement Durability', 'Tax/Asset Balance'],
      datasets: [{
        label: 'Client Health Score',
        data: [rep.liquidity_score, rep.debt_score, rep.budget_score, rep.retirement_score, 85],
        backgroundColor: 'rgba(59, 130, 246, 0.25)',
        borderColor: '#3b82f6',
        pointBackgroundColor: '#60a5fa',
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: '#3b82f6'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        r: {
          angleLines: { color: 'rgba(255, 255, 255, 0.08)' },
          grid: { color: 'rgba(255, 255, 255, 0.08)' },
          pointLabels: {
            color: '#94a3b8',
            font: { size: 10 }
          },
          ticks: {
            display: false,
            min: 0,
            max: 100
          }
        }
      },
      plugins: {
        legend: { display: false }
      }
    }
  });
}

function renderGoals() {
  const container = document.getElementById("goals-list-container");
  if (!container || !clientData) return;
  container.innerHTML = "";

  (clientData.goals || []).forEach(g => {
    const pct = Math.min(100, Math.round((g.current / g.target) * 100));
    const card = document.createElement("div");
    card.className = "p-3 rounded-lg bg-slate-900/50 border border-slate-800 text-xs";
    card.innerHTML = `
      <div class="flex justify-between items-center mb-1">
        <span class="font-medium text-white">${g.name}</span>
        <span class="font-bold text-emerald-400">${pct}%</span>
      </div>
      <div class="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden mb-1.5">
        <div class="bg-gradient-to-r from-blue-500 to-emerald-400 h-1.5 rounded-full" style="width: ${pct}%"></div>
      </div>
      <div class="flex justify-between text-[10px] text-slate-500">
        <span>$${g.current.toLocaleString()} saved</span>
        <span>Target: $${g.target.toLocaleString()} (${g.deadline})</span>
      </div>
    `;
    container.appendChild(card);
  });
}

// -------------------------------------------------------------
// BUDGET & SPENDING VIEW
// -------------------------------------------------------------
function renderBudgetView() {
  if (!clientReport) return;
  const b = clientReport.budget_analysis;
  const fifty = b.fifty_thirty_twenty;

  // 50/30/20 values
  document.getElementById("fifty-needs-val").textContent = `${fifty.needs.percent}% / 50%`;
  document.getElementById("fifty-needs-bar").style.width = `${Math.min(100, fifty.needs.percent)}%`;

  document.getElementById("fifty-wants-val").textContent = `${fifty.wants.percent}% / 30%`;
  document.getElementById("fifty-wants-bar").style.width = `${Math.min(100, fifty.wants.percent)}%`;

  document.getElementById("fifty-savings-val").textContent = `${fifty.savings.percent}% / 20%`;
  document.getElementById("fifty-savings-bar").style.width = `${Math.min(100, fifty.savings.percent)}%`;

  // Insights
  const insightBox = document.getElementById("budget-insight-box");
  insightBox.innerHTML = b.insights.map(i => `<p class="mb-1">• ${i}</p>`).join("");

  // Category Donut Chart
  renderDonutChart(b.category_breakdown);

  // Subscriptions List
  const subsContainer = document.getElementById("subscriptions-container");
  subsContainer.innerHTML = "";
  document.getElementById("subs-count-badge").textContent = `${b.subscriptions.length} Active`;
  document.getElementById("subs-annual-cost").textContent = `$${b.total_subscription_annual.toLocaleString()} / year`;

  b.subscriptions.forEach(s => {
    const item = document.createElement("div");
    item.className = "flex justify-between items-center p-2 rounded bg-slate-900/40 border border-slate-800 text-xs";
    item.innerHTML = `
      <div class="flex items-center space-x-2">
        <i data-lucide="check-circle" class="w-3.5 h-3.5 text-blue-400"></i>
        <span class="text-white">${s.merchant}</span>
      </div>
      <div class="text-right">
        <span class="text-rose-400 font-bold">$${s.monthly_cost}/mo</span>
        <span class="text-[10px] text-slate-500 block">$${s.annual_cost}/yr</span>
      </div>
    `;
    subsContainer.appendChild(item);
  });

  // Transactions Table
  renderTransactionsTable(b.transactions);
}

function renderDonutChart(catBreakdown) {
  const canvas = document.getElementById("spendingDonutChart");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");

  if (donutChartInstance) {
    donutChartInstance.destroy();
  }

  const labels = Object.keys(catBreakdown);
  const dataVals = Object.values(catBreakdown);
  const colors = [
    '#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899',
    '#06b6d4', '#84cc16', '#64748b', '#f43f5e', '#a855f7'
  ];

  donutChartInstance = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: labels,
      datasets: [{
        data: dataVals,
        backgroundColor: colors.slice(0, labels.length),
        borderWidth: 1,
        borderColor: '#1e293b'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'right',
          labels: {
            boxWidth: 10,
            color: '#94a3b8',
            font: { size: 10 }
          }
        }
      },
      cutout: '65%'
    }
  });
}

function renderTransactionsTable(txs) {
  const tbody = document.getElementById("transactions-table-body");
  if (!tbody) return;
  tbody.innerHTML = "";

  txs.forEach(t => {
    const tr = document.createElement("tr");
    tr.className = "hover:bg-slate-900/60 transition";
    
    let typeClass = "bg-blue-500/10 text-blue-400 border border-blue-500/20";
    if (t.classification === "Wants") typeClass = "bg-amber-500/10 text-amber-400 border border-amber-500/20";
    if (t.classification === "Savings") typeClass = "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20";

    tr.innerHTML = `
      <td class="py-2.5 px-3 text-slate-400">${t.date}</td>
      <td class="py-2.5 px-3 text-white font-medium">${t.description}</td>
      <td class="py-2.5 px-3 text-slate-300">${t.category}</td>
      <td class="py-2.5 px-3"><span class="px-2 py-0.5 rounded text-[10px] ${typeClass}">${t.classification}</span></td>
      <td class="py-2.5 px-3 text-right font-bold text-white">$${t.amount.toFixed(2)}</td>
    `;
    tbody.appendChild(tr);
  });
}

function filterTransactions(keyword) {
  if (!clientReport) return;
  const kw = keyword.toLowerCase();
  const txs = clientReport.budget_analysis.transactions;
  const filtered = txs.filter(t => 
    t.description.toLowerCase().includes(kw) || 
    t.category.toLowerCase().includes(kw) ||
    t.classification.toLowerCase().includes(kw)
  );
  renderTransactionsTable(filtered);
}

function simulateCancelSubs() {
  alert("Simulation: Canceling 2 entertainment subscriptions recaptures $42/month ($504/year). At 7.5% annual return, this adds ~$8,400 to your 10-year wealth projection!");
}

// -------------------------------------------------------------
// MONTE CARLO FORECASTING VIEW
// -------------------------------------------------------------
function renderMonteCarloView() {
  if (!clientReport || !clientData) return;
  const fc = clientReport.forecasting;
  const fire = clientReport.fire_metrics;

  // Form parameters
  document.getElementById("mc-param-current").value = clientReport.balance_sheet.total_investments;
  document.getElementById("mc-param-contribution").value = clientData.monthly_savings_current || 1600;
  document.getElementById("mc-param-years").value = fc.years_to_retirement;
  document.getElementById("mc-param-spend").value = clientData.target_annual_retirement_spend || 70000;

  // Probability Dial
  document.getElementById("mc-success-pct").textContent = `${fc.probability_of_success}%`;
  document.getElementById("mc-assessment-text").textContent = fc.health_assessment;

  // FIRE Cards
  document.getElementById("fire-target-val").textContent = `$${fire.fire_target.toLocaleString()}`;
  document.getElementById("coast-fire-val").textContent = `$${fire.coast_fire_needed.toLocaleString()}`;
  document.getElementById("coast-fire-status").textContent = fire.is_coast_fire ? "Threshold Achieved!" : "Progressing toward target";
  document.getElementById("lean-fire-val").textContent = `$${fire.lean_fire_target.toLocaleString()}`;
  document.getElementById("median-retirement-val").textContent = `$${fc.median_at_retirement.toLocaleString()}`;

  // Multi-line Chart
  renderMonteCarloChart(fc);
}

function renderMonteCarloChart(fc) {
  const canvas = document.getElementById("monteCarloChart");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");

  if (mcChartInstance) {
    mcChartInstance.destroy();
  }

  mcChartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: fc.labels,
      datasets: [
        {
          label: '90th Percentile (Bullish)',
          data: fc.p90_trajectory,
          borderColor: '#10b981',
          borderWidth: 2,
          pointRadius: 0,
          tension: 0.3
        },
        {
          label: '50th Percentile (Median)',
          data: fc.p50_trajectory,
          borderColor: '#3b82f6',
          borderWidth: 2.5,
          pointRadius: 0,
          tension: 0.3,
          backgroundColor: 'rgba(59, 130, 246, 0.08)',
          fill: true
        },
        {
          label: '10th Percentile (Bearish Sequence)',
          data: fc.p10_trajectory,
          borderColor: '#f43f5e',
          borderWidth: 2,
          pointRadius: 0,
          tension: 0.3
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        intersect: false,
        mode: 'index'
      },
      scales: {
        x: {
          grid: { color: 'rgba(255, 255, 255, 0.05)' },
          ticks: { color: '#64748b', maxTicksLimit: 12 }
        },
        y: {
          grid: { color: 'rgba(255, 255, 255, 0.05)' },
          ticks: {
            color: '#64748b',
            callback: function(value) {
              return '$' + (value >= 1000000 ? (value / 1000000).toFixed(1) + 'M' : (value / 1000).toFixed(0) + 'k');
            }
          }
        }
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: function(context) {
              return `${context.dataset.label}: $${Number(context.raw).toLocaleString()}`;
            }
          }
        }
      }
    }
  });
}

async function runCustomMonteCarlo() {
  const current = parseFloat(document.getElementById("mc-param-current").value) || 50000;
  const contrib = parseFloat(document.getElementById("mc-param-contribution").value) || 1000;
  const years = parseInt(document.getElementById("mc-param-years").value) || 25;
  const spend = parseFloat(document.getElementById("mc-param-spend").value) || 60000;
  const ret = (parseFloat(document.getElementById("mc-param-return").value) || 7.5) / 100.0;
  const vol = (parseFloat(document.getElementById("mc-param-volatility").value) || 15.0) / 100.0;

  try {
    const res = await fetch("/api/monte-carlo", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        current_wealth: current,
        monthly_contribution: contrib,
        years_to_retirement: years,
        annual_retirement_spend: spend,
        expected_return: ret,
        volatility: vol,
        num_simulations: 1000
      })
    });
    const data = await res.json();
    document.getElementById("mc-success-pct").textContent = `${data.probability_of_success}%`;
    document.getElementById("mc-assessment-text").textContent = data.health_assessment;
    document.getElementById("median-retirement-val").textContent = `$${data.median_at_retirement.toLocaleString()}`;
    renderMonteCarloChart(data);
  } catch (err) {
    console.error("Monte Carlo run failed:", err);
  }
}

// -------------------------------------------------------------
// DEBT PAYOFF STUDIO
// -------------------------------------------------------------
function renderDebtView() {
  if (!clientReport || !clientData) return;
  const debts = clientData.debts || [];
  const tbody = document.getElementById("debts-table-body");
  if (!tbody) return;
  tbody.innerHTML = "";

  if (debts.length === 0) {
    tbody.innerHTML = `<tr><td colspan="5" class="p-4 text-center text-emerald-400 font-medium">No outstanding consumer debt! Fully debt-free.</td></tr>`;
    return;
  }

  // Sort by APR descending for Avalanche Priority
  const sortedDebts = [...debts].sort((a, b) => b.apr - a.apr);
  sortedDebts.forEach((d, idx) => {
    const tr = document.createElement("tr");
    tr.className = "hover:bg-slate-900/60 transition";
    tr.innerHTML = `
      <td class="py-2.5 px-3 text-white font-medium">${d.name}</td>
      <td class="py-2.5 px-3 text-right text-rose-400 font-bold">$${d.balance.toLocaleString()}</td>
      <td class="py-2.5 px-3 text-right font-semibold ${d.apr > 15 ? 'text-rose-400' : 'text-blue-400'}">${d.apr}%</td>
      <td class="py-2.5 px-3 text-right text-slate-300">$${d.min_payment}/mo</td>
      <td class="py-2.5 px-3 text-center">
        <span class="px-2 py-0.5 rounded text-[10px] font-bold ${idx === 0 ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30' : 'bg-slate-800 text-slate-400'}">
          Target #${idx + 1}
        </span>
      </td>
    `;
    tbody.appendChild(tr);
  });

  updateDebtSimulation(300);
}

async function updateDebtSimulation(extraPayment) {
  document.getElementById("debt-extra-label").textContent = `+$${extraPayment}/mo`;
  if (!clientData || !clientData.debts || clientData.debts.length === 0) return;

  try {
    const res = await fetch("/api/debt-payoff", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        debts: clientData.debts,
        extra_monthly_payment: parseFloat(extraPayment)
      })
    });
    const d = await res.json();
    
    // Avalanche Card
    document.getElementById("av-time").textContent = `${d.avalanche.years_to_debt_free} Years (${d.avalanche.months_to_debt_free} mos)`;
    document.getElementById("av-interest").textContent = `$${d.avalanche.total_interest_paid.toLocaleString()}`;
    document.getElementById("av-saved").textContent = `+$${d.interest_saved_vs_minimums.toLocaleString()} saved`;

    // Snowball Card
    document.getElementById("sb-time").textContent = `${d.snowball.years_to_debt_free} Years (${d.snowball.months_to_debt_free} mos)`;
    document.getElementById("sb-interest").textContent = `$${d.snowball.total_interest_paid.toLocaleString()}`;
    document.getElementById("sb-saved").textContent = `+$${(d.minimums_only.total_interest_paid - d.snowball.total_interest_paid).toLocaleString()} saved`;

    // Minimums Card
    document.getElementById("min-time").textContent = `${d.minimums_only.years_to_debt_free} Years (${d.minimums_only.months_to_debt_free} mos)`;
    document.getElementById("min-interest").textContent = `$${d.minimums_only.total_interest_paid.toLocaleString()}`;
    document.getElementById("min-lost").textContent = `-$${d.interest_saved_vs_minimums.toLocaleString()} to interest`;
  } catch (err) {
    console.error("Debt calculation error:", err);
  }
}

// -------------------------------------------------------------
// EXECUTIVE REPORT VIEW
// -------------------------------------------------------------
function renderReportView() {
  if (!clientReport || !clientData) return;
  const rep = clientReport;
  const score = rep.scorecard;
  const bs = rep.balance_sheet;

  document.getElementById("rep-client-name").textContent = rep.client.name;
  document.getElementById("rep-client-meta").textContent = `Age: ${rep.client.age} | Occupation: ${rep.client.occupation} | Risk Profile: ${rep.client.risk_tolerance}`;

  // Scorecards
  document.getElementById("rep-score-overall").textContent = `${score.overall_health} / 100`;
  document.getElementById("rep-score-liquidity").textContent = `${score.liquidity_score} / 100`;
  document.getElementById("rep-score-debt").textContent = `${score.debt_score} / 100`;
  document.getElementById("rep-score-budget").textContent = `${score.budget_score} / 100`;
  document.getElementById("rep-score-retirement").textContent = `${score.retirement_score}%`;

  // Balance sheet
  document.getElementById("rep-asset-cash").textContent = `$${bs.emergency_fund.toLocaleString()}`;
  document.getElementById("rep-asset-inv").textContent = `$${bs.total_investments.toLocaleString()}`;
  document.getElementById("rep-debt-total").textContent = `$${bs.total_debt.toLocaleString()}`;

  // Action items
  const actionsContainer = document.getElementById("rep-actions-container");
  actionsContainer.innerHTML = "";
  (rep.action_items || []).forEach(item => {
    const card = document.createElement("div");
    let badgeColor = "bg-rose-500/10 text-rose-400 border border-rose-500/30";
    if (item.priority === "MEDIUM") badgeColor = "bg-amber-500/10 text-amber-400 border border-amber-500/30";
    if (item.priority === "LOW") badgeColor = "bg-blue-500/10 text-blue-400 border border-blue-500/30";

    card.className = "p-3 rounded-lg bg-slate-900 border border-slate-800 flex items-start gap-3 text-xs";
    card.innerHTML = `
      <span class="px-2 py-0.5 rounded font-bold text-[10px] ${badgeColor}">${item.priority}</span>
      <div>
        <span class="font-bold text-white block mb-0.5">${item.category}</span>
        <span class="text-slate-300">${item.text}</span>
      </div>
    `;
    actionsContainer.appendChild(card);
  });
}

// -------------------------------------------------------------
// CFP MODAL INTERACTIONS
// -------------------------------------------------------------
function requestCFPModal() {
  document.getElementById("cfp-modal").classList.remove("hidden");
}

function closeCFPModal() {
  document.getElementById("cfp-modal").classList.add("hidden");
}

function submitCFPEscalation() {
  closeCFPModal();
  appendMessage("bot", "✅ **CFP Dossier Generated**: Your current portfolio metrics, Monte Carlo simulations, and conversation history have been transmitted to our partner Fiduciary Advisory Desk. A certified human planner will contact you within 24 hours.");
}
