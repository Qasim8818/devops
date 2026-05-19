import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { AlertCircle, Check, Clock, TrendingUp, Activity, Shield, Zap, FileText, BarChart3, Settings } from 'lucide-react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState('overview');
  const [incidents, setIncidents] = useState([]);
  const [remediationRules, setRemediationRules] = useState([]);
  const [stats, setStats] = useState({
    totalIncidents: 0,
    resolved: 0,
    inProgress: 0,
    avgMTTR: 0,
  });
  const [loading, setLoading] = useState(true);
  const [apiStatus, setApiStatus] = useState({
    auto_remediation: true,
    slack_integration: false,
    cve_scanner: false,
    pdf_reports: true,
  });

  // Chart data
  const [incidentTrend, setIncidentTrend] = useState([
    { time: '00:00', count: 2 },
    { time: '04:00', count: 4 },
    { time: '08:00', count: 3 },
    { time: '12:00', count: 5 },
    { time: '16:00', count: 3 },
    { time: '20:00', count: 6 },
  ]);

  const [costData, setCostData] = useState([
    { service: 'EC2', cost: 3500 },
    { service: 'RDS', cost: 2100 },
    { service: 'S3', cost: 1200 },
    { service: 'Lambda', cost: 800 },
    { service: 'Other', cost: 1400 },
  ]);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      const [incidentRes, statusRes, rulesRes] = await Promise.all([
        axios.get(`${apiUrl}/api/incidents`).catch(() => ({ data: [] })),
        axios.get(`${apiUrl}/api/status`).catch(() => ({ data: {} })),
        axios.get(`${apiUrl}/api/remediation/rules`).catch(() => ({ data: [] })),
      ]);

      setIncidents(incidentRes.data || []);
      setApiStatus(statusRes.data?.features || apiStatus);
      setRemediationRules(rulesRes.data || []);
      setStats(prev => ({
        ...prev,
        totalIncidents: incidentRes.data?.length || 0,
      }));
      setLoading(false);
    } catch (err) {
      console.error('Failed to fetch data:', err);
      setLoading(false);
    }
  };

  const getSeverityColor = (severity) => {
    const colors = {
      critical: 'bg-red-100 text-red-800 border-red-300',
      high: 'bg-orange-100 text-orange-800 border-orange-300',
      medium: 'bg-yellow-100 text-yellow-800 border-yellow-300',
      low: 'bg-green-100 text-green-800 border-green-300',
    };
    return colors[severity] || colors.low;
  };

  const getStatusIcon = (status) => {
    if (status === 'resolved') return <Check className="w-5 h-5 text-green-600" />;
    if (status === 'inProgress') return <Clock className="w-5 h-5 text-blue-600" />;
    return <AlertCircle className="w-5 h-5 text-red-600" />;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Shield className="w-8 h-8 text-blue-600" />
              <h1 className="text-3xl font-bold text-gray-900">🛡️ DevSecOps Agent</h1>
            </div>
            <div className="flex items-center gap-4">
              <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
                ✓ Operational
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex gap-8 overflow-x-auto">
            {[
              { id: 'overview', label: 'Overview', icon: Activity },
              { id: 'incidents', label: 'Incidents', icon: AlertCircle },
              { id: 'remediation', label: 'Remediation', icon: Zap },
              { id: 'reports', label: 'Reports', icon: FileText },
              { id: 'costs', label: 'Cost Analysis', icon: BarChart3 },
              { id: 'settings', label: 'Settings', icon: Settings },
            ].map(tab => {
              const TabIcon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center gap-2 ${
                    activeTab === tab.id
                      ? 'border-blue-600 text-blue-600'
                      : 'border-transparent text-gray-600 hover:text-gray-900 hover:border-gray-300'
                  }`}
                >
                  <TabIcon className="w-4 h-4" />
                  {tab.label}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        {/* OVERVIEW TAB */}
        {activeTab === 'overview' && (
          <>
            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
              <StatCard
                title="Total Incidents"
                value={stats.totalIncidents}
                icon={<AlertCircle className="w-8 h-8 text-red-600" />}
                color="red"
              />
              <StatCard
                title="Resolved"
                value={stats.resolved}
                icon={<Check className="w-8 h-8 text-green-600" />}
                color="green"
              />
              <StatCard
                title="In Progress"
                value={stats.inProgress}
                icon={<Clock className="w-8 h-8 text-blue-600" />}
                color="blue"
              />
              <StatCard
                title="Avg MTTR"
                value="2:45m"
                icon={<TrendingUp className="w-8 h-8 text-purple-600" />}
                color="purple"
              />
            </div>

            {/* Charts Row */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
              {/* Incident Trend */}
              <Card title="Incident Trend (24h)">
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={incidentTrend}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="time" />
                    <YAxis />
                    <Tooltip />
                    <Line type="monotone" dataKey="count" stroke="#2563eb" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </Card>

              {/* Cost Breakdown */}
              <Card title="AWS Cost Breakdown">
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={costData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="service" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="cost" fill="#3b82f6" />
                  </BarChart>
                </ResponsiveContainer>
              </Card>
            </div>

            {/* Feature Status */}
            <Card title="Enabled Features">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                {[
                  { name: 'Auto Remediation', enabled: apiStatus.auto_remediation },
                  { name: 'Slack Integration', enabled: apiStatus.slack_integration },
                  { name: 'CVE Scanner', enabled: apiStatus.cve_scanner },
                  { name: 'PDF Reports', enabled: apiStatus.pdf_reports },
                ].map(feature => (
                  <div key={feature.name} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                    {feature.enabled ? (
                      <Check className="w-6 h-6 text-green-600" />
                    ) : (
                      <AlertCircle className="w-6 h-6 text-gray-400" />
                    )}
                    <span className={feature.enabled ? 'text-green-700 font-medium' : 'text-gray-600'}>
                      {feature.name}
                    </span>
                  </div>
                ))}
              </div>
            </Card>
          </>
        )}

        {/* INCIDENTS TAB */}
        {activeTab === 'incidents' && (
          <Card title="Recent Incidents">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Component</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Issue</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Severity</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Status</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Detected</th>
                  </tr>
                </thead>
                <tbody>
                  {incidents.length > 0 ? (
                    incidents.map((incident) => (
                      <tr key={incident.id} className="border-b border-gray-200 hover:bg-gray-50">
                        <td className="px-6 py-4 text-sm text-gray-900 font-medium">{incident.component}</td>
                        <td className="px-6 py-4 text-sm text-gray-600">{incident.title}</td>
                        <td className="px-6 py-4">
                          <span className={`inline-flex px-3 py-1 rounded-full text-xs font-medium ${getSeverityColor(incident.severity)}`}>
                            {incident.severity}
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-2">
                            {getStatusIcon(incident.status)}
                            <span className="text-sm text-gray-600">{incident.status}</span>
                          </div>
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-600">
                          {new Date(incident.detected_at).toLocaleString()}
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="5" className="px-6 py-8 text-center text-gray-500">
                        ✓ No incidents detected - System healthy
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </Card>
        )}

        {/* REMEDIATION TAB */}
        {activeTab === 'remediation' && (
          <Card title="Auto-Remediation Rules">
            <div className="space-y-4">
              {remediationRules.length > 0 ? (
                remediationRules.map((rule) => (
                  <div key={rule.rule_id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50">
                    <div>
                      <h3 className="font-semibold text-gray-900">{rule.name}</h3>
                      <p className="text-sm text-gray-600">Pattern: {rule.pattern}</p>
                      <p className="text-sm text-gray-600">Action: <kbd className="px-2 py-1 bg-gray-100 rounded">{rule.remediation_command}</kbd></p>
                    </div>
                    <div className="flex items-center gap-4">
                      <span className={`inline-flex px-3 py-1 rounded-full text-sm font-medium ${
                        rule.enabled ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                      }`}>
                        {rule.enabled ? 'Enabled' : 'Disabled'}
                      </span>
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-center text-gray-500 py-8">No remediation rules configured</p>
              )}
            </div>
          </Card>
        )}

        {/* REPORTS TAB */}
        {activeTab === 'reports' && (
          <div className="space-y-6">
            <Card title="Generate Reports">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <ReportButton
                  title="📋 Audit Report"
                  description="Generate comprehensive audit report"
                  action={() => alert('Generating audit report...')}
                />
                <ReportButton
                  title="🔍 CVE Scan"
                  description="Scan for vulnerabilities"
                  action={() => alert('Scanning for CVEs...')}
                />
                <ReportButton
                  title="💰 Cost Analysis"
                  description="Generate cost anomaly report"
                  action={() => alert('Analyzing costs...')}
                />
              </div>
            </Card>
          </div>
        )}

        {/* COSTS TAB */}
        {activeTab === 'costs' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <StatCard
                title="Daily Spend"
                value="$245.50"
                icon={<BarChart3 className="w-8 h-8 text-green-600" />}
                color="green"
              />
              <StatCard
                title="Baseline"
                value="$198.30"
                icon={<BarChart3 className="w-8 h-8 text-blue-600" />}
                color="blue"
              />
              <StatCard
                title="Variance"
                value="+23.8%"
                icon={<TrendingUp className="w-8 h-8 text-red-600" />}
                color="red"
              />
            </div>
            <Card title="Cost Anomalies">
              <div className="space-y-3">
                {[
                  { service: 'EC2', increase: '+$45.20', severity: 'high' },
                  { service: 'RDS', increase: '+$23.50', severity: 'medium' },
                ].map((anomaly) => (
                  <div key={anomaly.service} className="flex items-center justify-between p-3 border border-gray-200 rounded-lg">
                    <div>
                      <p className="font-medium text-gray-900">{anomaly.service}</p>
                      <p className="text-sm text-gray-600">Unexpected cost increase</p>
                    </div>
                    <div className="text-right">
                      <p className="font-semibold text-red-600">{anomaly.increase}</p>
                      <span className={`inline-block mt-1 px-2 py-1 rounded text-xs font-medium ${
                        anomaly.severity === 'high' ? 'bg-red-100 text-red-800' : 'bg-yellow-100 text-yellow-800'
                      }`}>
                        {anomaly.severity}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        )}

        {/* SETTINGS TAB */}
        {activeTab === 'settings' && (
          <Card title="System Settings">
            <div className="space-y-6">
              {[
                { name: 'Auto-Remediation', enabled: true, description: 'Automatically fix detected issues' },
                { name: 'Slack Integration', enabled: false, description: 'Send alerts to Slack' },
                { name: 'CVE Scanner', enabled: false, description: 'Scan for security vulnerabilities' },
                { name: 'PDF Reports', enabled: true, description: 'Generate downloadable reports' },
              ].map((setting) => (
                <div key={setting.name} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                  <div>
                    <p className="font-medium text-gray-900">{setting.name}</p>
                    <p className="text-sm text-gray-600">{setting.description}</p>
                  </div>
                  <button className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                    setting.enabled
                      ? 'bg-green-100 text-green-800 hover:bg-green-200'
                      : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
                  }`}>
                    {setting.enabled ? 'Enabled' : 'Disabled'}
                  </button>
                </div>
              ))}
            </div>
          </Card>
        )}

        {/* Quick Links */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
          <QuickLink
            title="View Metrics"
            description="Go to Grafana dashboard"
            href="http://localhost:3000"
            icon="📊"
          />
          <QuickLink
            title="API Docs"
            description="FastAPI interactive docs"
            href="http://localhost:8000/docs"
            icon="📚"
          />
          <QuickLink
            title="System Health"
            description="Check all components"
            href="/health/status"
            icon="❤️"
          />
        </div>
      </main>
    </div>
  );
}

// Helper Components

function StatCard({ title, value, icon, color }) {
  const bgColors = {
    red: 'bg-red-50',
    green: 'bg-green-50',
    blue: 'bg-blue-50',
    purple: 'bg-purple-50',
  };

  return (
    <div className={`${bgColors[color]} p-6 rounded-lg shadow-sm border border-gray-200`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-gray-600 text-sm font-medium">{title}</p>
          <p className="text-3xl font-bold text-gray-900 mt-2">{value}</p>
        </div>
        <div className="opacity-70">{icon}</div>
      </div>
    </div>
  );
}

function Card({ title, children }) {
  return (
    <div className="bg-white shadow-sm rounded-lg border border-gray-200">
      <div className="px-6 py-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900">{title}</h2>
      </div>
      <div className="p-6">
        {children}
      </div>
    </div>
  );
}

function QuickLink({ title, description, href, icon }) {
  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="block p-6 bg-white border border-gray-200 rounded-lg hover:shadow-lg transition-shadow"
    >
      <div className="text-3xl mb-2">{icon}</div>
      <h3 className="font-semibold text-gray-900">{title}</h3>
      <p className="text-sm text-gray-600 mt-1">{description}</p>
    </a>
  );
}

function ReportButton({ title, description, action }) {
  return (
    <button
      onClick={action}
      className="p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-all text-left"
    >
      <p className="font-semibold text-gray-900">{title}</p>
      <p className="text-sm text-gray-600 mt-1">{description}</p>
    </button>
  );
}
