import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { AlertCircle, Check, Clock, TrendingUp } from 'lucide-react';

const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export default function Dashboard() {
  const [incidents, setIncidents] = useState([]);
  const [stats, setStats] = useState({
    totalIncidents: 0,
    resolved: 0,
    inProgress: 0,
    avgMTTR: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      const [incidentRes, statsRes] = await Promise.all([
        axios.get(`${apiUrl}/api/incidents`),
        axios.get(`${apiUrl}/api/status`),
      ]);

      setIncidents(incidentRes.data || []);
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
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
              🛡️ DevSecOps Agent
            </h1>
            <div className="flex items-center gap-4">
              <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
                ✓ Operational
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
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
            value="2.3m"
            icon={<TrendingUp className="w-8 h-8 text-purple-600" />}
            color="purple"
          />
        </div>

        {/* Incidents Table */}
        <div className="bg-white shadow rounded-lg">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Recent Incidents</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase">
                    Component
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase">
                    Issue
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase">
                    Severity
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase">
                    Detected
                  </th>
                </tr>
              </thead>
              <tbody>
                {incidents.length > 0 ? (
                  incidents.map((incident) => (
                    <tr key={incident.id} className="border-b border-gray-200 hover:bg-gray-50">
                      <td className="px-6 py-4 text-sm text-gray-900 font-medium">
                        {incident.component}
                      </td>
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
                    <td colSpan="5" className="px-6 py-4 text-center text-gray-500">
                      No incidents detected
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Quick Links */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
          <QuickLink
            title="View Metrics"
            description="Go to Grafana dashboard"
            href="http://localhost:3000"
            color="blue"
          />
          <QuickLink
            title="API Docs"
            description="FastAPI interactive docs"
            href="http://localhost:8000/docs"
            color="green"
          />
          <QuickLink
            title="Remediation Rules"
            description="Manage auto-remediation"
            href="/api/remediation/rules"
            color="purple"
          />
        </div>
      </main>
    </div>
  );
}

function StatCard({ title, value, icon, color }) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-gray-600 text-sm font-medium">{title}</p>
          <p className="text-3xl font-bold text-gray-900 mt-2">{value}</p>
        </div>
        <div className="opacity-50">{icon}</div>
      </div>
    </div>
  );
}

function QuickLink({ title, description, href, color }) {
  const colorClasses = {
    blue: 'bg-blue-50 hover:bg-blue-100 border-blue-200',
    green: 'bg-green-50 hover:bg-green-100 border-green-200',
    purple: 'bg-purple-50 hover:bg-purple-100 border-purple-200',
  };

  return (
    <a href={href} target="_blank" rel="noopener noreferrer">
      <div className={`border rounded-lg p-6 cursor-pointer transition ${colorClasses[color]}`}>
        <h3 className="font-semibold text-gray-900">{title}</h3>
        <p className="text-sm text-gray-600 mt-1">{description}</p>
      </div>
    </a>
  );
}
