import { useCallback, useEffect, useMemo, useState } from 'react'
import {
  Activity, AlertTriangle, ArrowDownRight, ArrowLeft, ArrowUpRight, Bell,
  BrainCircuit, CheckCircle2, ChevronDown, ChevronRight, Clock3, Cpu,
  Database, Download, Gauge, LayoutDashboard, Menu, RefreshCw, Search,
  Server, ShieldCheck, SlidersHorizontal, X, Zap,
} from 'lucide-react'
import {
  Area, AreaChart, CartesianGrid, Cell, Pie, PieChart, ResponsiveContainer,
  Tooltip, XAxis, YAxis,
} from 'recharts'
import { api } from './api'

const RISK_COLORS = { Critical: '#f46d76', Watch: '#eab866', Healthy: '#37c5a0' }

function formatNumber(value, digits = 1) {
  return Number(value ?? 0).toLocaleString(undefined, { maximumFractionDigits: digits })
}

function RiskPill({ risk }) {
  return <span className={`risk-pill ${risk || 'healthy'}`}><i />{risk || 'unknown'}</span>
}

function StatCard({ label, value, suffix, detail, icon: Icon, tone = 'blue', trend }) {
  return (
    <article className="stat-card">
      <div className="stat-top"><span>{label}</span><span className={`stat-icon ${tone}`}><Icon size={17} /></span></div>
      <div className="stat-value">{value}<small>{suffix}</small></div>
      <div className="stat-detail">{trend && <span className={`trend ${trend.direction}`}>
        {trend.direction === 'up' ? <ArrowUpRight size={13} /> : <ArrowDownRight size={13} />}{trend.text}
      </span>}{detail}</div>
    </article>
  )
}

function EmptyState({ title, detail }) {
  return <div className="empty-state"><Database size={25} /><strong>{title}</strong><span>{detail}</span></div>
}

function EngineTable({ engines, onSelect, compact = false }) {
  if (!engines?.length) return <EmptyState title="No engines found" detail="Try changing the search or filter." />
  return (
    <div className="table-wrap">
      <table className="engine-table">
        <thead><tr><th>ENGINE ID</th><th>RISK LEVEL</th><th>REMAINING USEFUL LIFE</th><th>LAST CYCLE</th><th>MODEL</th><th /></tr></thead>
        <tbody>
          {engines.map((engine) => (
            <tr key={engine.engine_id} onClick={() => onSelect(engine.engine_id)} tabIndex="0"
              onKeyDown={(event) => event.key === 'Enter' && onSelect(engine.engine_id)}>
              <td><div className="engine-id"><span className="engine-mini"><Cpu size={15} /></span><strong>{engine.engine_id}</strong></div></td>
              <td><RiskPill risk={engine.risk_level} /></td>
              <td><div className="rul-cell"><strong>{formatNumber(engine.predicted_rul, 0)}</strong><span>cycles</span></div></td>
              <td className="muted-cell">{engine.last_cycle.toLocaleString()}</td>
              <td><span className="model-tag">{engine.model_version}</span></td>
              <td><button className="table-arrow" aria-label={`View ${engine.engine_id}`}><ChevronRight size={16} /></button></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function Sidebar({ page, setPage, open, setOpen, engineCount }) {
  const navItems = [
    { id: 'overview', label: 'Overview', icon: LayoutDashboard },
    { id: 'fleet', label: 'Engine fleet', icon: Cpu },
    { id: 'model', label: 'Model lab', icon: BrainCircuit },
  ]
  return (
    <>
      {open && <button className="mobile-scrim" onClick={() => setOpen(false)} aria-label="Close navigation" />}
      <aside className={`sidebar ${open ? 'sidebar-open' : ''}`}>
        <div className="brand"><div className="brand-mark"><Activity size={22} strokeWidth={2.4} /></div><div><strong>AEROPULSE</strong><span>ENGINE INTELLIGENCE</span></div></div>
        <div className="workspace-label">WORKSPACE</div>
        <nav className="side-nav">
          {navItems.map(({ id, label, icon: Icon }) => (
            <button key={id} className={`nav-item ${page === id ? 'active' : ''}`} onClick={() => { setPage(id); setOpen(false) }}>
              <Icon size={17} /><span>{label}</span>{id === 'fleet' && <span className="nav-count">{engineCount}</span>}
            </button>
          ))}
        </nav>
        <div className="side-divider" />
        <div className="workspace-label">PLATFORM</div>
        <div className="platform-list">
          <div><Database size={16} /><span>Data pipeline</span><span className="status-dot" /></div>
          <div><Server size={16} /><span>API service</span><span className="status-dot" /></div>
          <div><ShieldCheck size={16} /><span>Quality checks</span><span className="status-dot" /></div>
        </div>
        <div className="sidebar-spacer" />
        <div className="sidebar-note"><div className="note-icon"><Zap size={15} /></div><div><strong>Predict before failure.</strong><span>Turn sensor signals into maintenance intelligence.</span></div></div>
        <div className="profile"><div className="profile-avatar">AP</div><div><strong>Portfolio workspace</strong><span>Local environment</span></div><ChevronDown size={15} /></div>
      </aside>
    </>
  )
}

function Header({ title, eyebrow, onRefresh, refreshing, searchValue, setSearchValue, showSearch = false, online = false }) {
  return (
    <header className="topbar">
      <div className="topbar-title"><div className="eyebrow">AEROPULSE / {eyebrow}</div><h1>{title}</h1></div>
      <div className="topbar-actions">
        {showSearch && <label className="top-search"><Search size={16} /><input value={searchValue} onChange={(e) => setSearchValue(e.target.value)} placeholder="Find an engine..." /></label>}
        <span className={`system-status ${online ? 'online' : 'offline'}`}><i />{online ? 'API CONNECTED' : 'API OFFLINE'}</span>
        <button className={`icon-button ${refreshing ? 'spinning' : ''}`} onClick={onRefresh} title="Refresh data"><RefreshCw size={17} /></button>
        <button className="icon-button notification-button" title="Notifications"><Bell size={17} /><i /></button>
      </div>
    </header>
  )
}

function OverviewPage({ overview, engines, metrics, onSelect, onNavigate }) {
  const priorityEngines = engines.slice(0, 6)
  return (
    <>
      <div className="intro-row"><div><h2>Fleet overview</h2><p>Operational health signals across your monitored engine fleet.</p></div>
        <div className="dataset-chip"><span className="pulse-dot" />{metrics?.dataset?.includes('NASA') ? 'NASA C-MAPSS FD001' : 'SYNTHETIC DEMO DATA'}<ChevronDown size={13} /></div>
      </div>
      <section className="stats-grid">
        <StatCard label="MONITORED ENGINES" value={overview?.total_engines ?? '—'} detail="Engine histories in workspace" icon={Cpu} tone="blue" />
        <StatCard label="CRITICAL ATTENTION" value={overview?.critical_engines ?? '—'} detail="Predicted RUL ≤ 20 cycles" icon={AlertTriangle} tone="red" />
        <StatCard label="WATCHLIST" value={overview?.watchlist_engines ?? '—'} detail="Predicted RUL between 21–50" icon={Clock3} tone="amber" />
        <StatCard label="AVG. PREDICTED RUL" value={overview ? formatNumber(overview.average_predicted_rul, 0) : '—'} suffix=" cycles" detail="Model estimate across fleet" icon={Gauge} tone="green" />
      </section>

      <section className="chart-grid">
        <article className="panel trend-panel">
          <div className="panel-heading"><div><span className="panel-kicker">SENSOR INTELLIGENCE</span><h3>Fleet sensor trend</h3><p>Mean sensor 15 reading by 10-cycle interval</p></div><div className="chart-legend"><i />SENSOR 15</div></div>
          {overview?.fleet_trend?.length ? <div className="trend-chart"><ResponsiveContainer width="100%" height="100%"><AreaChart data={overview.fleet_trend} margin={{ top: 12, right: 8, left: -18, bottom: 0 }}>
            <defs><linearGradient id="sensorFill" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#42a9f5" stopOpacity={0.28} /><stop offset="100%" stopColor="#42a9f5" stopOpacity={0.01} /></linearGradient></defs>
            <CartesianGrid stroke="#202b3d" strokeDasharray="3 5" vertical={false} />
            <XAxis dataKey="cycle" tick={{ fill: '#718096', fontSize: 11 }} axisLine={false} tickLine={false} tickFormatter={(v) => `${v}`} />
            <YAxis tick={{ fill: '#718096', fontSize: 11 }} axisLine={false} tickLine={false} domain={['auto', 'auto']} />
            <Tooltip contentStyle={{ background: '#101a2a', border: '1px solid #26364c', borderRadius: 9, color: '#e7edf7' }} labelFormatter={(v) => `Cycle ${v}`} />
            <Area type="monotone" dataKey="mean_sensor_s15" stroke="#43aaf5" strokeWidth={2.3} fill="url(#sensorFill)" activeDot={{ r: 4, fill: '#43aaf5', stroke: '#0c1523', strokeWidth: 2 }} />
          </AreaChart></ResponsiveContainer></div> : <EmptyState title="No trend available" detail="Load a dataset to populate sensor analytics." />}
          <div className="chart-foot"><span>ENGINE CYCLE</span><span>Historical sensor measurements · not live telemetry</span></div>
        </article>
        <article className="panel distribution-panel">
          <div className="panel-heading"><div><span className="panel-kicker">RISK MONITORING</span><h3>Engine risk distribution</h3><p>Current model classification</p></div><button className="more-button" onClick={onNavigate}>View fleet <ChevronRight size={14} /></button></div>
          <div className="distribution-content">
            {overview?.total_engines ? <><div className="donut-wrap"><ResponsiveContainer width="100%" height="100%"><PieChart><Pie data={overview.risk_distribution} dataKey="value" nameKey="name" innerRadius={58} outerRadius={79} paddingAngle={4} stroke="none" cornerRadius={3}>{overview.risk_distribution.map((entry) => <Cell key={entry.name} fill={RISK_COLORS[entry.name]} />)}</Pie><Tooltip contentStyle={{ background: '#101a2a', border: '1px solid #26364c', borderRadius: 8, color: '#e7edf7' }} /></PieChart></ResponsiveContainer><div className="donut-center"><strong>{overview.total_engines}</strong><span>ENGINES</span></div></div>
              <div className="risk-legend">{overview.risk_distribution.map((item) => <div key={item.name}><span><i style={{ background: RISK_COLORS[item.name] }} />{item.name}</span><strong>{item.value}<small>{overview.total_engines ? `${Math.round(item.value / overview.total_engines * 100)}%` : '0%'}</small></strong></div>)}</div></> : <EmptyState title="No risk data" detail="The distribution will appear after ingestion." />}
          </div>
          <div className="distribution-foot"><ShieldCheck size={14} /><span>Thresholds are configurable in the backend.</span></div>
        </article>
      </section>

      <section className="panel priority-panel">
        <div className="panel-heading"><div><span className="panel-kicker">MAINTENANCE PRIORITY</span><h3>Engines requiring attention</h3><p>Sorted by lowest predicted remaining useful life.</p></div><button className="text-button" onClick={onNavigate}>All engines <ArrowUpRight size={15} /></button></div>
        <EngineTable engines={priorityEngines} onSelect={onSelect} compact />
      </section>
      <div className="bottom-grid">
        <article className="panel model-summary"><div className="model-summary-icon"><BrainCircuit size={19} /></div><div><span className="panel-kicker">PREDICTIVE MODEL</span><h3>{metrics?.model_name || 'Model not trained'}</h3><p>{metrics?.evaluation_method || 'Run the data pipeline to train and evaluate the baseline model.'}</p></div><div className="model-summary-metric"><strong>{metrics?.mae != null ? formatNumber(metrics.mae, 1) : '—'}</strong><span>MAE · cycles</span></div></article>
        <article className="data-notice"><div className="notice-symbol"><AlertTriangle size={17} /></div><div><strong>Research prototype — not an aviation safety system</strong><p>Predictions are educational estimates from simulated benchmark data. They must not be used to make real-world maintenance or flight-safety decisions.</p></div></article>
      </div>
    </>
  )
}

function FleetPage({ engines, onSelect, searchValue, setSearchValue, onExport }) {
  const [risk, setRisk] = useState('all')
  const visible = useMemo(() => engines.filter((engine) => {
    const matchesRisk = risk === 'all' || engine.risk_level === risk
    const matchesSearch = engine.engine_id.toLowerCase().includes(searchValue.toLowerCase())
    return matchesRisk && matchesSearch
  }), [engines, risk, searchValue])
  return (
    <>
      <div className="intro-row"><div><h2>Engine fleet</h2><p>Inspect engine histories, risk classifications and model estimates.</p></div><div className="fleet-actions"><button className="export-button" onClick={onExport}><Download size={14} /> Export CSV</button><div className="fleet-filter"><SlidersHorizontal size={15} /><select value={risk} onChange={(e) => setRisk(e.target.value)}><option value="all">All risk levels</option><option value="critical">Critical</option><option value="watch">Watch</option><option value="healthy">Healthy</option></select></div></div></div>
      <section className="panel fleet-panel"><div className="panel-heading"><div><span className="panel-kicker">ASSET REGISTER</span><h3>Monitored engines <span className="count-badge">{visible.length}</span></h3><p>Select an engine to inspect its sensor history and prediction.</p></div></div><EngineTable engines={visible} onSelect={onSelect} /></section>
    </>
  )
}

function ModelPage({ metrics }) {
  const metricCards = [
    { label: 'MEAN ABSOLUTE ERROR', value: metrics?.mae, description: 'Average absolute prediction error', unit: 'cycles' },
    { label: 'ROOT MEAN SQUARED ERROR', value: metrics?.rmse, description: 'Penalizes larger prediction errors', unit: 'cycles' },
    { label: 'R² SCORE', value: metrics?.r2, description: 'Variance explained on held-out engines', unit: 'score' },
  ]
  return (
    <>
      <div className="intro-row"><div><h2>Model laboratory</h2><p>Understand the baseline model, its evaluation and its limitations.</p></div><span className="model-tag large">{metrics?.model_version || 'not trained'}</span></div>
      <section className="panel model-hero"><div className="model-hero-icon"><BrainCircuit size={25} /></div><div><span className="panel-kicker">REGRESSION MODEL</span><h3>{metrics?.model_name || 'Random Forest Regressor'}</h3><p>Estimates remaining useful life (RUL) from current engine cycle, operating conditions and sensor measurements.</p></div><div className="model-hero-status"><span className="status-dot" /> BASELINE MODEL</div></section>
      <section className="stats-grid model-metrics-grid">{metricCards.map((metric) => <article className="stat-card metric-card" key={metric.label}><span className="panel-kicker">{metric.label}</span><div className="stat-value">{metric.value == null ? '—' : formatNumber(metric.value, 3)}<small>{metric.unit}</small></div><div className="stat-detail">{metric.description}</div></article>)}</section>
      <section className="panel evaluation-panel"><div className="panel-heading"><div><span className="panel-kicker">EVALUATION DESIGN</span><h3>How this model is assessed</h3></div></div>
        <div className="evaluation-steps"><div><span>01</span><div><strong>Train on complete engine histories</strong><p>The model learns from labeled run-to-failure trajectories. RUL is calculated as the number of cycles remaining until the end of each training trajectory, capped at 125 cycles.</p></div></div><div><span>02</span><div><strong>Hold out entire engines</strong><p>Evaluation uses different engines from those used for fitting. The final observed cycle of each held-out engine is used for a prediction.</p></div></div><div><span>03</span><div><strong>Compare predictions with target RUL</strong><p>MAE, RMSE and R² summarize error on the held-out engine set. The test targets are used for evaluation, not displayed as operational predictions.</p></div></div></div>
      </section>
      <section className="data-notice model-warning"><div className="notice-symbol"><AlertTriangle size={17} /></div><div><strong>Model limitations</strong><p>{metrics?.note || 'This is a baseline educational model. Performance may vary across operating conditions and fault modes. It is not certified for real aircraft maintenance.'}</p></div></section>
      <section className="panel metadata-panel"><div className="panel-heading"><div><span className="panel-kicker">EXPERIMENT METADATA</span><h3>Reproducibility record</h3></div></div><dl><div><dt>Dataset</dt><dd>{metrics?.dataset || 'Not loaded'}</dd></div><div><dt>Evaluation protocol</dt><dd>{metrics?.evaluation_method || 'Not available'}</dd></div><div><dt>Evaluated engines</dt><dd>{metrics?.evaluated_engines ?? '—'}</dd></div><div><dt>Model version</dt><dd>{metrics?.model_version || '—'}</dd></div></dl></section>
    </>
  )
}

function EngineDetailPage({ engine, onBack }) {
  if (!engine) return <EmptyState title="Loading engine details" detail="Retrieving sensor history from the API." />
  const latest = engine.observations?.[engine.observations.length - 1]
  const series = engine.observations?.map((item) => ({ cycle: item.cycle, sensor_15: item.sensors.s15 })) || []
  return (
    <>
      <div className="detail-back"><button className="back-button" onClick={onBack}><ArrowLeft size={16} /> Back to fleet</button><span>ASSET PROFILE / {engine.engine_id}</span></div>
      <div className="detail-title-row"><div><span className="panel-kicker">ENGINE PROFILE</span><h2>{engine.engine_id}</h2><p>Sensor history and remaining useful life estimate.</p></div><RiskPill risk={engine.risk_level} /></div>
      <section className="stats-grid detail-stats"><StatCard label="PREDICTED RUL" value={formatNumber(engine.predicted_rul, 0)} suffix=" cycles" detail="Model estimate · not ground truth" icon={Gauge} tone="blue" /><StatCard label="LAST OBSERVED CYCLE" value={engine.last_cycle} detail="Latest available measurement" icon={Activity} tone="green" /><StatCard label="OBSERVATIONS" value={engine.observations?.length ?? 0} detail="Historical sensor rows" icon={Database} tone="amber" /><StatCard label="MODEL VERSION" value={engine.model_version} detail="Prediction provenance" icon={BrainCircuit} tone="blue" /></section>
      <section className="panel detail-chart-panel"><div className="panel-heading"><div><span className="panel-kicker">SENSOR TELEMETRY</span><h3>Selected sensor history</h3><p>Three example sensor channels across the observed trajectory.</p></div></div>
        <div className="sensor-legend"><span><i className="s15" />Sensor 15</span><span className="legend-note">One measurement scale per chart</span></div>
        <div className="detail-chart"><ResponsiveContainer width="100%" height="100%"><AreaChart data={series} margin={{ top: 12, right: 12, left: -15, bottom: 0 }}><CartesianGrid stroke="#202b3d" strokeDasharray="3 5" vertical={false} /><XAxis dataKey="cycle" tick={{ fill: '#718096', fontSize: 11 }} axisLine={false} tickLine={false} /><YAxis tick={{ fill: '#718096', fontSize: 11 }} axisLine={false} tickLine={false} domain={['auto', 'auto']} /><Tooltip contentStyle={{ background: '#101a2a', border: '1px solid #26364c', borderRadius: 9, color: '#e7edf7' }} /><Area type="monotone" dataKey="sensor_15" stroke="#eab866" fill="none" strokeWidth={2} dot={false} /></AreaChart></ResponsiveContainer></div>
      </section>
      <section className="panel latest-panel"><div className="panel-heading"><div><span className="panel-kicker">LATEST MEASUREMENT</span><h3>Current sensor snapshot</h3><p>Values from the last recorded cycle: {latest?.cycle ?? '—'}.</p></div></div>
        <div className="sensor-grid">{Object.entries(latest?.sensors || {}).map(([sensor, value]) => <div className="sensor-value-card" key={sensor}><span>{sensor.toUpperCase()}</span><strong>{formatNumber(value, 3)}</strong></div>)}</div>
      </section>
    </>
  )
}

export default function App() {
  const [page, setPage] = useState('overview')
  const [overview, setOverview] = useState(null)
  const [engines, setEngines] = useState([])
  const [metrics, setMetrics] = useState(null)
  const [selectedEngine, setSelectedEngine] = useState(null)
  const [engineDetail, setEngineDetail] = useState(null)
  const [searchValue, setSearchValue] = useState('')
  const [refreshing, setRefreshing] = useState(false)
  const [error, setError] = useState('')
  const [online, setOnline] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(false)

  const loadData = useCallback(async () => {
    setRefreshing(true)
    try {
      const [health, nextOverview, nextEngines, nextMetrics] = await Promise.all([api.health(), api.overview(), api.engines({ sort: 'predicted_rul', order: 'asc', limit: 500 }), api.metrics()])
      setOnline(health.status === 'ok')
      setOverview(nextOverview)
      setEngines(nextEngines)
      setMetrics(nextMetrics)
      setError('')
    } catch (err) {
      setOnline(false)
      setError(err.message || 'Unable to connect to the API.')
    } finally {
      setRefreshing(false)
    }
  }, [])

  useEffect(() => { loadData() }, [loadData])
  useEffect(() => {
    if (!selectedEngine) { setEngineDetail(null); return }
    let active = true
    api.engine(selectedEngine).then((result) => { if (active) setEngineDetail(result) }).catch((err) => { if (active) setError(err.message) })
    return () => { active = false }
  }, [selectedEngine])

  const selectEngine = (id) => { setSelectedEngine(id); setEngineDetail(null) }
  const exportCsv = () => {
    const headers = ['engine_id', 'risk_level', 'predicted_rul', 'last_cycle', 'model_version']
    const rows = engines.map((engine) => headers.map((key) => JSON.stringify(engine[key] ?? '')).join(','))
    const blob = new Blob([[headers.join(','), ...rows].join('\n')], { type: 'text/csv;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const anchor = document.createElement('a')
    anchor.href = url; anchor.download = 'aeropulse-engine-fleet.csv'; anchor.click()
    URL.revokeObjectURL(url)
  }

  const pageTitle = selectedEngine ? 'Engine profile' : ({ overview: 'Overview', fleet: 'Engine fleet', model: 'Model laboratory' }[page])
  const filteredEngines = useMemo(() => engines.filter((engine) => engine.engine_id.toLowerCase().includes(searchValue.toLowerCase())), [engines, searchValue])

  return (
    <div className="app-shell">
      <Sidebar page={page} setPage={(next) => { setSelectedEngine(null); setPage(next) }} open={sidebarOpen} setOpen={setSidebarOpen} engineCount={engines.length} />
      <main className="main-area">
        <Header title={pageTitle} eyebrow={selectedEngine ? 'ENGINE PROFILE' : page.toUpperCase()} onRefresh={loadData} refreshing={refreshing} searchValue={searchValue} setSearchValue={setSearchValue} showSearch={!selectedEngine && page !== 'model'} online={online} />
        <div className="content-area">
          {error && <div className="error-banner"><AlertTriangle size={16} /><span>{error}. Start the API and initialize a dataset, then refresh.</span><button onClick={() => setError('')}><X size={15} /></button></div>}
          {!overview && !error && <div className="loading-state"><RefreshCw className="spinning" size={20} /><span>Connecting to AeroPulse API…</span></div>}
          {selectedEngine ? <EngineDetailPage engine={engineDetail} onBack={() => setSelectedEngine(null)} /> : page === 'overview' ? <OverviewPage overview={overview} engines={filteredEngines} metrics={metrics} onSelect={selectEngine} onNavigate={() => setPage('fleet')} /> : page === 'fleet' ? <FleetPage engines={filteredEngines} onSelect={selectEngine} searchValue={searchValue} setSearchValue={setSearchValue} onExport={exportCsv} /> : <ModelPage metrics={metrics} />}
          <footer className="footer"><span>© 2026 AEROPULSE · ENGINEERING INTELLIGENCE</span><span><i /> HEALTH-CHECK STATUS <b>·</b> BUILD 1.0.0</span></footer>
        </div>
      </main>
      <button className="mobile-menu" onClick={() => setSidebarOpen(true)} aria-label="Open navigation"><Menu size={19} /></button>
    </div>
  )
}
