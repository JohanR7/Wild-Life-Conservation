import React, { useState, useEffect, useRef } from 'react';
import { 
  Activity, 
  AlertTriangle, 
  Mic, 
  MicOff, 
  MapPin, 
  Volume2, 
  Clock, 
  Shield,
  TrendingUp,
  Radio,
  Play,
  Pause,
  Settings,
  Bell,
  Filter,
  Download,
  BarChart3,
  Thermometer,
  Users,
  ChevronRight
} from 'lucide-react';

const Dashboard = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [isConnected, setIsConnected] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [alerts, setAlerts] = useState([]);
  const [detections, setDetections] = useState([]);
  const [liveAudioLevel, setLiveAudioLevel] = useState(0);
  const [audioVisualization, setAudioVisualization] = useState([]);
  const [realTimeDetections, setRealTimeDetections] = useState([]);
  const audioRef = useRef(null);

  // Mock real-time data generation
  useEffect(() => {
    const generateMockData = () => {
      if (activeTab === 'dashboard') {
        // Generate random detection for dashboard
        if (Math.random() < 0.1) {
          const newDetection = {
            id: Date.now(),
            type: Math.random() < 0.3 ? 'gunshot' : 'wildlife',
            confidence: 0.7 + Math.random() * 0.3,
            location: `Zone ${Math.floor(Math.random() * 5) + 1}`,
            timestamp: new Date().toISOString(),
            coordinates: [Math.random() * 180 - 90, Math.random() * 360 - 180]
          };
          setDetections(prev => [newDetection, ...prev.slice(0, 9)]);
        }
      }
      
      // Generate real-time audio visualization
      if (isRecording && activeTab === 'live-recording') {
        setLiveAudioLevel(Math.random() * 100);
        setAudioVisualization(prev => {
          const newData = Array.from({length: 50}, () => Math.random() * 80 + 10);
          return newData;
        });
        
        // Generate real-time detections
        if (Math.random() < 0.15) {
          const detection = {
            id: Date.now(),
            type: Math.random() < 0.4 ? 'gunshot' : 'wildlife',
            confidence: 0.6 + Math.random() * 0.4,
            timestamp: new Date().toISOString()
          };
          setRealTimeDetections(prev => [detection, ...prev.slice(0, 4)]);
        }
      }
    };

    const interval = setInterval(generateMockData, 500);
    return () => clearInterval(interval);
  }, [activeTab, isRecording]);

  // Mock socket connection
  useEffect(() => {
    const connectSocket = () => {
      setTimeout(() => setIsConnected(Math.random() > 0.5), 1000);
    };
    connectSocket();
    const interval = setInterval(connectSocket, 5000);
    return () => clearInterval(interval);
  }, []);

  const toggleRecording = () => {
    setIsRecording(!isRecording);
    if (!isRecording) {
      console.log('Starting live audio transmission...');
      setRealTimeDetections([]);
    } else {
      console.log('Stopping live audio transmission...');
      setLiveAudioLevel(0);
      setAudioVisualization([]);
    }
  };

  const SidebarItem = ({ icon: Icon, label, isActive, onClick, hasAlert = false }) => (
    <button
      onClick={onClick}
      className={`w-full flex items-center space-x-3 px-4 py-3 text-left rounded-lg transition-colors ${
        isActive 
          ? 'bg-blue-600 text-white' 
          : 'text-gray-700 hover:bg-gray-100'
      }`}
    >
      <Icon className="w-5 h-5" />
      <span className="font-medium">{label}</span>
      {hasAlert && !isActive && (
        <div className="w-2 h-2 bg-red-500 rounded-full ml-auto" />
      )}
    </button>
  );

  const StatCard = ({ title, value, subtitle, color, icon: Icon }) => (
    <div className="bg-white p-6 rounded-lg border border-gray-200">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-medium text-gray-600">{title}</h3>
        <Icon className={`w-5 h-5 ${color}`} />
      </div>
      <div className="text-3xl font-bold text-gray-900 mb-1">{value}</div>
      <p className="text-sm text-gray-500">{subtitle}</p>
    </div>
  );

  const AudioVisualizer = ({ data, height = 200 }) => (
    <div className="bg-gray-900 rounded-lg p-4 flex items-end justify-center space-x-1" style={{ height }}>
      {data.map((value, index) => (
        <div
          key={index}
          className="bg-blue-400 rounded-sm transition-all duration-75"
          style={{
            height: `${(value / 100) * (height - 32)}px`,
            width: '6px'
          }}
        />
      ))}
    </div>
  );

  const DetectionItem = ({ detection, showTime = false }) => (
    <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
      <div className="flex items-center space-x-3">
        <div className={`w-3 h-3 rounded-full ${
          detection.type === 'gunshot' ? 'bg-red-500' : 'bg-green-500'
        }`} />
        <div>
          <p className="font-medium text-gray-900 capitalize">{detection.type}</p>
          {showTime && (
            <p className="text-sm text-gray-500">
              {new Date(detection.timestamp).toLocaleTimeString()}
            </p>
          )}
        </div>
      </div>
      <div className="text-right">
        <p className="text-sm font-medium text-gray-900">
          {(detection.confidence * 100).toFixed(1)}%
        </p>
        <p className="text-xs text-gray-500">confidence</p>
      </div>
    </div>
  );

  const renderDashboard = () => (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Wildlife Protection Dashboard</h1>
          <p className="text-gray-600">Real-time gunshot and wildlife sound detection</p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <div className={`w-3 h-3 rounded-full ${
              isConnected ? 'bg-green-500' : 'bg-red-500'
            }`} />
            <span className="text-sm text-gray-600">
              {isConnected ? 'Connected' : 'Disconnected'}
            </span>
          </div>
          <button className="bg-gray-600 text-white px-4 py-2 rounded-lg flex items-center space-x-2">
            <Mic className="w-4 h-4" />
            <span>Start Live Recording</span>
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Detections"
          value="0"
          subtitle="Last 24 hours"
          icon={TrendingUp}
          color="text-blue-500"
        />
        <StatCard
          title="Gunshot Alerts"
          value="0"
          subtitle="Requires immediate attention"
          icon={AlertTriangle}
          color="text-red-500"
        />
        <StatCard
          title="Wildlife Sounds"
          value="0"
          subtitle="Normal activity detected"
          icon={Volume2}
          color="text-green-500"
        />
        <StatCard
          title="System Status"
          value="Offline"
          subtitle="Accuracy: 0.0%"
          icon={Activity}
          color="text-gray-500"
        />
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Detections */}
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Detections</h3>
          <div className="text-center py-12">
            <p className="text-gray-500">No detections yet. Start monitoring to see results.</p>
          </div>
        </div>

        {/* Live Audio Visualization */}
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Live Audio Visualization</h3>
          <div className="text-center py-12">
            <Mic className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500">Click "Start Live Recording" to see audio visualization</p>
          </div>
        </div>
      </div>
    </div>
  );

  const renderLiveRecording = () => (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Live Audio Recording</h1>
          <p className="text-gray-600">Real-time gunshot and wildlife sound classification</p>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 bg-red-500 rounded-full" />
          <span className="text-sm text-gray-600">Server Disconnected</span>
        </div>
      </div>

      {/* Audio Recording Controls */}
      <div className="bg-white p-6 rounded-lg border border-gray-200">
        <div className="flex items-center space-x-2 mb-4">
          <TrendingUp className="w-5 h-5 text-gray-600" />
          <h3 className="text-lg font-semibold text-gray-900">Audio Recording Controls</h3>
        </div>
        
        <div className="text-center py-6">
          <button
            onClick={toggleRecording}
            disabled={!isConnected}
            className={`px-6 py-3 rounded-lg font-medium transition-colors ${
              isRecording 
                ? 'bg-red-600 text-white hover:bg-red-700' 
                : 'bg-gray-600 text-white hover:bg-gray-700'
            } ${!isConnected ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            <div className="flex items-center space-x-2">
              <Mic className="w-5 h-5" />
              <span>{isRecording ? 'Stop Recording' : 'Start Recording'}</span>
            </div>
          </button>
          
          {!isConnected && (
            <p className="text-red-500 text-sm mt-2">Connect to server to enable live recording</p>
          )}
        </div>
      </div>

      {/* Live Audio Visualization */}
      <div className="bg-white p-6 rounded-lg border border-gray-200">
        <div className="flex items-center space-x-2 mb-4">
          <Volume2 className="w-5 h-5 text-gray-600" />
          <h3 className="text-lg font-semibold text-gray-900">Live Audio Visualization</h3>
        </div>
        
        {isRecording ? (
          <AudioVisualizer data={audioVisualization} height={300} />
        ) : (
          <div className="bg-gray-900 rounded-lg flex items-center justify-center" style={{ height: 300 }}>
            <div className="text-center">
              <Mic className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-400">Audio visualization will appear here when recording</p>
            </div>
          </div>
        )}
      </div>

      {/* Real-time Detections */}
      <div className="bg-white p-6 rounded-lg border border-gray-200">
        <div className="flex items-center space-x-2 mb-4">
          <AlertTriangle className="w-5 h-5 text-gray-600" />
          <h3 className="text-lg font-semibold text-gray-900">Real-time Detections</h3>
        </div>
        
        {realTimeDetections.length > 0 ? (
          <div className="space-y-3">
            {realTimeDetections.map(detection => (
              <DetectionItem key={detection.id} detection={detection} showTime={true} />
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <Mic className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500">Start recording to see real-time classifications</p>
          </div>
        )}
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <div className="w-64 bg-white shadow-sm border-r border-gray-200">
        <div className="p-6">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <Shield className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">Wildlife Guard</h1>
              <p className="text-sm text-gray-500">ML Detection System</p>
            </div>
          </div>
        </div>

        <nav className="px-4 pb-4">
          <div className="space-y-2">
            <SidebarItem
              icon={BarChart3}
              label="Dashboard"
              isActive={activeTab === 'dashboard'}
              onClick={() => setActiveTab('dashboard')}
            />
            <SidebarItem
              icon={Mic}
              label="Live Recording"
              isActive={activeTab === 'live-recording'}
              onClick={() => setActiveTab('live-recording')}
            />
            <SidebarItem
              icon={AlertTriangle}
              label="Detections"
              isActive={activeTab === 'detections'}
              onClick={() => setActiveTab('detections')}
              hasAlert={true}
            />
            <SidebarItem
              icon={Volume2}
              label="Audio Analysis"
              isActive={activeTab === 'audio-analysis'}
              onClick={() => setActiveTab('audio-analysis')}
            />
            <SidebarItem
              icon={Thermometer}
              label="Heat Map"
              isActive={activeTab === 'heat-map'}
              onClick={() => setActiveTab('heat-map')}
            />
            <SidebarItem
              icon={TrendingUp}
              label="System Status"
              isActive={activeTab === 'system-status'}
              onClick={() => setActiveTab('system-status')}
            />
            <SidebarItem
              icon={Settings}
              label="Settings"
              isActive={activeTab === 'settings'}
              onClick={() => setActiveTab('settings')}
            />
          </div>
        </nav>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-hidden">
        <div className="h-full overflow-y-auto">
          <div className="p-8">
            {activeTab === 'dashboard' && renderDashboard()}
            {activeTab === 'live-recording' && renderLiveRecording()}
            {activeTab === 'detections' && (
              <div className="text-center py-20">
                <AlertTriangle className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <h2 className="text-xl font-semibold text-gray-900 mb-2">Detections Page</h2>
                <p className="text-gray-500">Detection history and analysis will be displayed here</p>
              </div>
            )}
            {activeTab === 'audio-analysis' && (
              <div className="text-center py-20">
                <Volume2 className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <h2 className="text-xl font-semibold text-gray-900 mb-2">Audio Analysis</h2>
                <p className="text-gray-500">Detailed audio analysis tools will be available here</p>
              </div>
            )}
            {activeTab === 'heat-map' && (
              <div className="text-center py-20">
                <MapPin className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <h2 className="text-xl font-semibold text-gray-900 mb-2">Heat Map</h2>
                <p className="text-gray-500">Geographic heat map of detections will be shown here</p>
              </div>
            )}
            {activeTab === 'system-status' && (
              <div className="text-center py-20">
                <Activity className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <h2 className="text-xl font-semibold text-gray-900 mb-2">System Status</h2>
                <p className="text-gray-500">System health and performance metrics will be displayed here</p>
              </div>
            )}
            {activeTab === 'settings' && (
              <div className="text-center py-20">
                <Settings className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <h2 className="text-xl font-semibold text-gray-900 mb-2">Settings</h2>
                <p className="text-gray-500">Configuration options will be available here</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;