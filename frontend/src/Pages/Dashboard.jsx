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
  ChevronRight,
  Upload,
  FileAudio
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
  const [stats, setStats] = useState({
    total_detections: 0,
    gunshot_alerts: 0,
    wildlife_sounds: 0,
    avg_confidence: 0.0
  });
  const [animalCounts, setAnimalCounts] = useState([]);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [fileAnalysis, setFileAnalysis] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  
  const audioRef = useRef(null);
  const wsRef = useRef(null);
  const fileInputRef = useRef(null);

  // WebSocket connection
  useEffect(() => {
    const connectWebSocket = () => {
      try {
        wsRef.current = new WebSocket('ws://localhost:8000/ws');
        
        wsRef.current.onopen = () => {
          console.log('WebSocket connected');
          setIsConnected(true);
        };
        
        wsRef.current.onmessage = (event) => {
          const message = JSON.parse(event.data);
          handleWebSocketMessage(message);
        };
        
        wsRef.current.onclose = () => {
          console.log('WebSocket disconnected');
          setIsConnected(false);
          // Attempt to reconnect after 3 seconds
          setTimeout(connectWebSocket, 3000);
        };
        
        wsRef.current.onerror = (error) => {
          console.error('WebSocket error:', error);
          setIsConnected(false);
        };
      } catch (error) {
        console.error('Failed to connect WebSocket:', error);
        setIsConnected(false);
      }
    };

    connectWebSocket();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const handleWebSocketMessage = (message) => {
    switch (message.type) {
      case 'live_detection':
        // Handle real-time detection results
        const detection = {
          id: Date.now(),
          timestamp: message.data.chunk_timestamp,
          results: message.data.results,
          audio_level: message.data.audio_level
        };
        setRealTimeDetections(prev => [detection, ...prev.slice(0, 4)]);
        setLiveAudioLevel(message.data.audio_level);
        break;
        
      case 'recording_status':
        setIsRecording(message.status === 'started');
        break;
        
      case 'audio_visualization':
        setAudioVisualization(message.data);
        break;
        
      default:
        console.log('Unknown WebSocket message:', message);
    }
  };

  // Fetch data functions
  const fetchDetectionStats = async () => {
    try {
      const response = await fetch('http://localhost:8000/detections/stats');
      if (response.ok) {
        const data = await response.json();
        setStats(data.stats);
      }
    } catch (error) {
      console.error('Failed to fetch detection stats:', error);
    }
  };

  const fetchRecentDetections = async () => {
    try {
      const response = await fetch('http://localhost:8000/detections/recent?limit=10');
      if (response.ok) {
        const data = await response.json();
        setDetections(data.detections);
      }
    } catch (error) {
      console.error('Failed to fetch recent detections:', error);
    }
  };

  const fetchAnimalCounts = async () => {
    try {
      const response = await fetch('http://localhost:8000/wildlife/counts');
      if (response.ok) {
        const data = await response.json();
        setAnimalCounts(data.animal_counts);
      }
    } catch (error) {
      console.error('Failed to fetch animal counts:', error);
    }
  };

  // Fetch data on component mount and tab change
  useEffect(() => {
    if (activeTab === 'dashboard') {
      fetchDetectionStats();
      fetchRecentDetections();
      fetchAnimalCounts();
    }
  }, [activeTab]);

  // Auto-refresh data every 30 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      if (activeTab === 'dashboard') {
        fetchDetectionStats();
        fetchRecentDetections();
      }
    }, 30000);

    return () => clearInterval(interval);
  }, [activeTab]);

  const toggleRecording = async () => {
    try {
      const endpoint = isRecording ? '/live-recording/stop' : '/live-recording/start';
      const response = await fetch(`http://localhost:8000${endpoint}`, {
        method: 'POST'
      });
      
      if (response.ok) {
        const data = await response.json();
        console.log('Recording toggle response:', data);
        // State will be updated via WebSocket message
      } else {
        console.error('Failed to toggle recording');
      }
    } catch (error) {
      console.error('Error toggling recording:', error);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setUploadedFile(file);
    setIsAnalyzing(true);
    setFileAnalysis(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('http://localhost:8000/upload/single', {
        method: 'POST',
        body: formData
      });

      if (response.ok) {
        const result = await response.json();
        setFileAnalysis(result);
        
        // Refresh detections to show the new upload
        await fetchRecentDetections();
        await fetchDetectionStats();
      } else {
        console.error('Failed to analyze file');
        setFileAnalysis({ error: 'Failed to analyze file' });
      }
    } catch (error) {
      console.error('Error uploading file:', error);
      setFileAnalysis({ error: 'Upload failed' });
    } finally {
      setIsAnalyzing(false);
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
          <button 
            onClick={() => setActiveTab('live-recording')}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center space-x-2 hover:bg-blue-700"
          >
            <Mic className="w-4 h-4" />
            <span>Go to Live Recording</span>
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Detections"
          value={stats.total_detections.toString()}
          subtitle="Last 24 hours"
          icon={TrendingUp}
          color="text-blue-500"
        />
        <StatCard
          title="Gunshot Alerts"
          value={stats.gunshot_alerts.toString()}
          subtitle="Requires immediate attention"
          icon={AlertTriangle}
          color="text-red-500"
        />
        <StatCard
          title="Wildlife Sounds"
          value={stats.wildlife_sounds.toString()}
          subtitle="Normal activity detected"
          icon={Volume2}
          color="text-green-500"
        />
        <StatCard
          title="System Status"
          value={isConnected ? 'Online' : 'Offline'}
          subtitle={`Accuracy: ${(stats.avg_confidence * 100).toFixed(1)}%`}
          icon={Activity}
          color={isConnected ? "text-green-500" : "text-gray-500"}
        />
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Detections */}
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Recent Detections</h3>
            <button 
              onClick={() => setActiveTab('detections')}
              className="text-blue-600 hover:text-blue-800 text-sm flex items-center space-x-1"
            >
              <span>View All</span>
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
          
          {detections.length > 0 ? (
            <div className="space-y-3">
              {detections.slice(0, 5).map(detection => (
                <div key={detection.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className={`w-3 h-3 rounded-full ${
                      detection.detection_type === 'gunshot' ? 'bg-red-500' : 'bg-green-500'
                    }`} />
                    <div>
                      <p className="font-medium text-gray-900 capitalize">{detection.prediction}</p>
                      <p className="text-sm text-gray-500">{detection.model_name}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium text-gray-900">
                      {(detection.confidence * 100).toFixed(1)}%
                    </p>
                    <p className="text-xs text-gray-500">confidence</p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <AlertTriangle className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500">No detections yet. Start monitoring to see results.</p>
            </div>
          )}
        </div>

        {/* File Upload Section */}
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <div className="flex items-center space-x-2 mb-4">
            <Upload className="w-5 h-5 text-gray-600" />
            <h3 className="text-lg font-semibold text-gray-900">Audio File Analysis</h3>
          </div>
          
          <div className="space-y-4">
            <div 
              className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-gray-400 transition-colors cursor-pointer"
              onClick={() => fileInputRef.current?.click()}
            >
              <FileAudio className="w-12 h-12 text-gray-400 mx-auto mb-2" />
              <p className="text-gray-600 mb-1">Click to upload audio file</p>
              <p className="text-sm text-gray-500">Supports WAV, MP3, FLAC, M4A, OGG</p>
            </div>
            
            <input
              ref={fileInputRef}
              type="file"
              accept=".wav,.mp3,.flac,.m4a,.ogg"
              onChange={handleFileUpload}
              className="hidden"
            />
            
            {isAnalyzing && (
              <div className="text-center py-4">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
                <p className="text-sm text-gray-600">Analyzing audio file...</p>
              </div>
            )}
            
            {fileAnalysis && !isAnalyzing && (
              <div className="bg-gray-50 rounded-lg p-4">
                {fileAnalysis.error ? (
                  <div className="text-red-600">
                    <p className="font-medium">Analysis Failed</p>
                    <p className="text-sm">{fileAnalysis.error}</p>
                  </div>
                ) : (
                  <div>
                    <p className="font-medium text-gray-900 mb-2">Analysis Complete</p>
                    <p className="text-sm text-gray-600">
                      Processing time: {fileAnalysis.processing_time?.toFixed(2)}s
                    </p>
                    {fileAnalysis.best_prediction && (
                      <div className="mt-2 p-2 bg-blue-50 rounded">
                        <p className="text-sm font-medium text-blue-900">
                          Best Match: {fileAnalysis.best_prediction.prediction}
                        </p>
                        <p className="text-sm text-blue-700">
                          Confidence: {(fileAnalysis.best_prediction.confidence * 100).toFixed(1)}%
                        </p>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Animal Counts Section */}
      {animalCounts.length > 0 && (
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Wildlife Activity</h3>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
            {animalCounts.slice(0, 10).map(animal => (
              <div key={animal.animal_name} className="text-center p-3 bg-green-50 rounded-lg">
                <p className="font-medium text-gray-900">{animal.animal_name.replace('_', ' ')}</p>
                <p className="text-2xl font-bold text-green-600">{animal.count}</p>
                <p className="text-xs text-gray-500">detections</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );

  const renderLiveRecording = () => (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Live Audio Recording</h1>
          <p className="text-gray-600">Real-time gunshot and wildlife sound classification (30-second chunks)</p>
        </div>
        <div className="flex items-center space-x-2">
          <div className={`w-3 h-3 rounded-full ${
            isConnected ? 'bg-green-500' : 'bg-red-500'
          }`} />
          <span className="text-sm text-gray-600">
            {isConnected ? 'Server Connected' : 'Server Disconnected'}
          </span>
        </div>
      </div>

      {/* Audio Recording Controls */}
      <div className="bg-white p-6 rounded-lg border border-gray-200">
        <div className="flex items-center space-x-2 mb-4">
          <Radio className="w-5 h-5 text-gray-600" />
          <h3 className="text-lg font-semibold text-gray-900">Recording Controls</h3>
        </div>
        
        <div className="text-center py-6">
          <button
            onClick={toggleRecording}
            disabled={!isConnected}
            className={`px-8 py-4 rounded-lg font-medium transition-colors text-lg ${
              isRecording 
                ? 'bg-red-600 text-white hover:bg-red-700' 
                : 'bg-blue-600 text-white hover:bg-blue-700'
            } ${!isConnected ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            <div className="flex items-center space-x-3">
              {isRecording ? <MicOff className="w-6 h-6" /> : <Mic className="w-6 h-6" />}
              <span>{isRecording ? 'Stop Recording' : 'Start Recording'}</span>
            </div>
          </button>
          
          {!isConnected && (
            <p className="text-red-500 text-sm mt-4">Connect to server to enable live recording</p>
          )}
          
          {isRecording && (
            <p className="text-blue-600 text-sm mt-4">
              🔴 Recording... Audio is processed in 30-second chunks
            </p>
          )}
        </div>

        {/* Audio Level Indicator */}
        {isRecording && (
          <div className="mt-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-600">Audio Level</span>
              <span className="text-sm font-medium text-gray-900">{liveAudioLevel.toFixed(0)}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div 
                className="bg-blue-600 h-3 rounded-full transition-all duration-300"
                style={{ width: `${Math.min(100, liveAudioLevel)}%` }}
              ></div>
            </div>
          </div>
        )}
      </div>

      {/* Live Audio Visualization */}
      <div className="bg-white p-6 rounded-lg border border-gray-200">
        <div className="flex items-center space-x-2 mb-4">
          <Volume2 className="w-5 h-5 text-gray-600" />
          <h3 className="text-lg font-semibold text-gray-900">Audio Visualization</h3>
        </div>
        
        {isRecording ? (
          <AudioVisualizer data={audioVisualization} height={300} />
        ) : (
          <div className="bg-gray-900 rounded-lg flex items-center justify-center" style={{ height: 300 }}>
            <div className="text-center">
              <Mic className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-400">Audio visualization will appear here when recording</p>
              <p className="text-gray-500 text-sm mt-2">30-second chunks are processed automatically</p>
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
              <div key={detection.id} className="border border-gray-200 rounded-lg p-4 bg-gray-50">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-500">
                    Chunk processed at {new Date(detection.timestamp * 1000).toLocaleTimeString()}
                  </span>
                  <span className="text-xs text-blue-600">
                    Audio Level: {detection.audio_level?.toFixed(0)}%
                  </span>
                </div>
                
                {detection.results && detection.results.length > 0 ? (
                  <div className="space-y-2">
                    {detection.results.slice(0, 3).map((result, index) => (
                      <div key={index} className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <div className={`w-2 h-2 rounded-full ${
                            result.model_type === 'gunshot' ? 'bg-red-500' : 'bg-green-500'
                          }`} />
                          <span className="text-sm font-medium">{result.prediction}</span>
                          <span className="text-xs text-gray-500">({result.model_type})</span>
                        </div>
                        <span className="text-sm font-medium text-gray-900">
                          {(result.confidence * 100).toFixed(1)}%
                        </span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-gray-500">No significant detections in this chunk</p>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <Mic className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500">Start recording to see real-time classifications</p>
            <p className="text-gray-400 text-sm mt-2">Detections appear every 30 seconds</p>
          </div>
        )}
      </div>
    </div>
  );

  const renderDetections = () => (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Detection History</h1>
          <p className="text-gray-600">Browse all audio detections and analysis results</p>
        </div>
        <div className="flex items-center space-x-4">
          <button 
            onClick={fetchRecentDetections}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center space-x-2 hover:bg-blue-700"
          >
            <Activity className="w-4 h-4" />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Filter Controls */}
      <div className="bg-white p-4 rounded-lg border border-gray-200">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <Filter className="w-4 h-4 text-gray-500" />
            <span className="text-sm text-gray-700">Filter by:</span>
          </div>
          <button className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
            All Types
          </button>
          <button className="px-3 py-1 bg-gray-100 text-gray-600 rounded-full text-sm hover:bg-gray-200">
            Gunshots
          </button>
          <button className="px-3 py-1 bg-gray-100 text-gray-600 rounded-full text-sm hover:bg-gray-200">
            Wildlife
          </button>
        </div>
      </div>

      {/* Detections List */}
      <div className="bg-white rounded-lg border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">
            Recent Detections ({detections.length})
          </h3>
        </div>
        
        {detections.length > 0 ? (
          <div className="divide-y divide-gray-200">
            {detections.map(detection => (
              <div key={detection.id} className="p-6 hover:bg-gray-50">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className={`w-4 h-4 rounded-full ${
                      detection.detection_type === 'gunshot' ? 'bg-red-500' : 'bg-green-500'
                    }`} />
                    <div>
                      <p className="font-medium text-gray-900">{detection.prediction}</p>
                      <div className="flex items-center space-x-4 text-sm text-gray-500">
                        <span>Model: {detection.model_name}</span>
                        <span>Type: {detection.detection_type}</span>
                        {detection.audio_filename && (
                          <span>File: {detection.audio_filename}</span>
                        )}
                        {detection.is_live_recording && (
                          <span className="bg-red-100 text-red-800 px-2 py-1 rounded">Live</span>
                        )}
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-lg font-semibold text-gray-900">
                      {(detection.confidence * 100).toFixed(1)}%
                    </p>
                    <p className="text-sm text-gray-500">
                      {new Date(detection.timestamp).toLocaleString()}
                    </p>
                    {detection.processing_time && (
                      <p className="text-xs text-gray-400">
                        {detection.processing_time.toFixed(2)}s processing
                      </p>
                    )}
                  </div>
                </div>
                
                {/* Probability Details */}
                {detection.probabilities && (
                  <div className="mt-3 pt-3 border-t border-gray-100">
                    <details className="group">
                      <summary className="cursor-pointer text-sm text-blue-600 hover:text-blue-800">
                        View probability details
                      </summary>
                      <div className="mt-2 grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2 text-sm">
                        {Object.entries(JSON.parse(detection.probabilities)).map(([className, prob]) => (
                          <div key={className} className="bg-gray-50 p-2 rounded">
                            <span className="font-medium">{className.replace('_', ' ')}</span>
                            <span className="block text-gray-600">{(prob * 100).toFixed(1)}%</span>
                          </div>
                        ))}
                      </div>
                    </details>
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <AlertTriangle className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No Detections Found</h3>
            <p className="text-gray-500">Start live recording or upload audio files to see detections here</p>
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
            {activeTab === 'detections' && renderDetections()}
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