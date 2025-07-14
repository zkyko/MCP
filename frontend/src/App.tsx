import { useEffect, useState, useRef } from 'react';
import axios from 'axios';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import Plot from 'react-plotly.js';
import { Upload, TrendingUp, ImageIcon, BarChart3, DollarSign, Target, Trophy } from 'lucide-react';

const API_BASE = "http://localhost:8001";

function App() {
  const [images, setImages] = useState<any[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [uploading, setUploading] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadMsg, setUploadMsg] = useState("");
  const [dragActive, setDragActive] = useState(false);
  const fileInput = useRef<HTMLInputElement>(null);

  // Fetch images
  useEffect(() => {
    axios.get(`${API_BASE}/list-images`).then(res => {
      setImages(res.data.data.images || []);
    }).catch(err => console.error('Failed to fetch images:', err));
    
    axios.get(`${API_BASE}/trading-stats`).then(res => {
      setStats(res.data.data);
    }).catch(err => console.error('Failed to fetch stats:', err));
  }, [uploadMsg]);

  // Handle file upload
  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) return;
    setUploading(true);
    setUploadMsg("");
    const formData = new FormData();
    formData.append('file', selectedFile);
    try {
      const res = await axios.post(`${API_BASE}/extract-trade-upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setUploadMsg(res.data.message || "Upload successful!");
      setSelectedFile(null);
      if (fileInput.current) fileInput.current.value = "";
    } catch (err: any) {
      setUploadMsg(err?.response?.data?.detail || "Upload failed");
    } finally {
      setUploading(false);
    }
  };

  // Handle drag and drop
  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setSelectedFile(e.dataTransfer.files[0]);
    }
  };

  // Prepare PnL chart data
  const pnlData = stats?.pnl_history || [];
  const pnlChart = pnlData.length > 0 ? (
    <Plot
      data={[{
        x: pnlData.map((d: any) => d.date),
        y: pnlData.map((d: any) => d.pnl),
        type: 'scatter',
        mode: 'lines+markers',
        marker: { color: '#10b981', size: 6 },
        line: { color: '#10b981', width: 2 },
        name: 'PnL',
        fill: 'tonexty',
        fillcolor: 'rgba(16, 185, 129, 0.1)',
      }]}
      layout={{
        title: {
          text: 'PnL Over Time',
          font: { size: 16, color: '#374151' }
        },
        autosize: true,
        height: 280,
        margin: { t: 40, l: 60, r: 20, b: 40 },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        xaxis: {
          gridcolor: '#e5e7eb',
          tickfont: { color: '#6b7280' }
        },
        yaxis: {
          gridcolor: '#e5e7eb',
          tickfont: { color: '#6b7280' }
        }
      }}
      style={{ width: '100%' }}
      config={{ displayModeBar: false }}
    />
  ) : (
    <div className="flex flex-col items-center justify-center h-64 text-gray-400">
      <BarChart3 className="w-12 h-12 mb-2" />
      <p>No PnL data available</p>
    </div>
  );

  const formatCurrency = (value: number | null) => {
    if (value === null || value === undefined) return '-';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(value);
  };

  const getWinRateColor = (rate: number) => {
    if (rate >= 0.6) return 'text-green-600';
    if (rate >= 0.4) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 p-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-3">
            Trading Analysis Dashboard
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Upload trading screenshots, analyze your performance, and track your trading journey with advanced analytics.
          </p>
        </div>

        {/* Upload Section */}
        <Card className="mb-8 border-0 shadow-lg bg-white/70 backdrop-blur-sm">
          <CardHeader className="pb-4">
            <CardTitle className="flex items-center gap-2 text-xl">
              <Upload className="w-5 h-5 text-blue-600" />
              Upload Trade Screenshot
            </CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleUpload} className="space-y-4">
              <div
                className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                  dragActive 
                    ? 'border-blue-500 bg-blue-50' 
                    : 'border-gray-300 hover:border-gray-400'
                }`}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
              >
                <div className="flex flex-col items-center space-y-2">
                  <Upload className="w-12 h-12 text-gray-400" />
                  <div>
                    <p className="text-lg font-medium text-gray-700">
                      {selectedFile ? selectedFile.name : 'Drag & drop your screenshot here'}
                    </p>
                    <p className="text-sm text-gray-500">or click to browse</p>
                  </div>
                  <input
                    type="file"
                    accept="image/*"
                    ref={fileInput}
                    onChange={e => setSelectedFile(e.target.files?.[0] || null)}
                    className="hidden"
                    disabled={uploading}
                  />
                  <Button 
                    type="button" 
                    variant="outline" 
                    onClick={() => fileInput.current?.click()}
                    disabled={uploading}
                  >
                    Choose File
                  </Button>
                </div>
              </div>
              
              <div className="flex justify-center">
                <Button 
                  type="submit" 
                  disabled={uploading || !selectedFile}
                  className="px-8 py-2 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
                >
                  {uploading ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Uploading...
                    </>
                  ) : (
                    <>
                      <Upload className="w-4 h-4 mr-2" />
                      Upload & Analyze
                    </>
                  )}
                </Button>
              </div>
              
              {uploadMsg && (
                <div className={`text-center p-3 rounded-lg ${
                  uploadMsg.includes('successful') || uploadMsg.includes('Upload successful') 
                    ? 'bg-green-100 text-green-700' 
                    : 'bg-red-100 text-red-700'
                }`}>
                  {uploadMsg}
                </div>
              )}
            </form>
          </CardContent>
        </Card>

        {/* Stats and Chart Grid */}
        <div className="grid lg:grid-cols-2 gap-6 mb-8">
          {/* Trading Stats */}
          <Card className="border-0 shadow-lg bg-white/70 backdrop-blur-sm">
            <CardHeader className="pb-4">
              <CardTitle className="flex items-center gap-2 text-xl">
                <TrendingUp className="w-5 h-5 text-green-600" />
                Trading Performance
              </CardTitle>
            </CardHeader>
            <CardContent>
              {stats ? (
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-blue-50 p-4 rounded-lg">
                      <div className="flex items-center gap-2 mb-1">
                        <Target className="w-4 h-4 text-blue-600" />
                        <span className="text-sm font-medium text-blue-700">Total Trades</span>
                      </div>
                      <div className="text-2xl font-bold text-blue-800">
                        {stats.total_trades ?? '-'}
                      </div>
                    </div>
                    
                    <div className="bg-purple-50 p-4 rounded-lg">
                      <div className="flex items-center gap-2 mb-1">
                        <Trophy className="w-4 h-4 text-purple-600" />
                        <span className="text-sm font-medium text-purple-700">Win Rate</span>
                      </div>
                      <div className={`text-2xl font-bold ${stats.win_rate ? getWinRateColor(stats.win_rate) : 'text-gray-400'}`}>
                        {stats.win_rate ? `${(stats.win_rate * 100).toFixed(1)}%` : '-'}
                      </div>
                    </div>
                  </div>
                  
                  <div className="bg-gradient-to-r from-green-50 to-emerald-50 p-4 rounded-lg">
                    <div className="flex items-center gap-2 mb-1">
                      <DollarSign className="w-4 h-4 text-green-600" />
                      <span className="text-sm font-medium text-green-700">Total PnL</span>
                    </div>
                    <div className="text-2xl font-bold text-green-800">
                      {formatCurrency(stats.total_pnl)}
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-emerald-50 p-3 rounded-lg">
                      <div className="text-xs font-medium text-emerald-700 mb-1">Best Trade</div>
                      <div className="text-lg font-bold text-emerald-800">
                        {formatCurrency(stats.best_trade)}
                      </div>
                    </div>
                    
                    <div className="bg-red-50 p-3 rounded-lg">
                      <div className="text-xs font-medium text-red-700 mb-1">Worst Trade</div>
                      <div className="text-lg font-bold text-red-800">
                        {formatCurrency(stats.worst_trade)}
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="flex items-center justify-center h-64 text-gray-400">
                  <div className="text-center">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-400 mx-auto mb-4"></div>
                    <p>Loading trading stats...</p>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* PnL Chart */}
          <Card className="border-0 shadow-lg bg-white/70 backdrop-blur-sm">
            <CardHeader className="pb-4">
              <CardTitle className="flex items-center gap-2 text-xl">
                <BarChart3 className="w-5 h-5 text-purple-600" />
                PnL Trend
              </CardTitle>
            </CardHeader>
            <CardContent>
              {pnlChart}
            </CardContent>
          </Card>
        </div>

        {/* Images Gallery */}
        <Card className="border-0 shadow-lg bg-white/70 backdrop-blur-sm">
          <CardHeader className="pb-4">
            <CardTitle className="flex items-center gap-2 text-xl">
              <ImageIcon className="w-5 h-5 text-indigo-600" />
              Trade Screenshots Gallery
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
              {images.length === 0 ? (
                <div className="col-span-full flex flex-col items-center justify-center py-12 text-gray-400">
                  <ImageIcon className="w-16 h-16 mb-4" />
                  <p className="text-lg font-medium">No screenshots uploaded yet</p>
                  <p className="text-sm">Upload your first trade screenshot to get started</p>
                </div>
              ) : (
                images.map((img, index) => (
                  <div key={img.path} className="group relative">
                    <div className="aspect-square bg-gray-100 rounded-lg overflow-hidden shadow-md hover:shadow-lg transition-shadow">
                      <img
                        src={`${API_BASE}/uploads/${img.filename}`}
                        alt={`Trade screenshot ${index + 1}`}
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-200"
                        loading="lazy"
                      />
                    </div>
                    <div className="absolute inset-0 bg-black/0 group-hover:bg-black/10 transition-colors rounded-lg"></div>
                    <div className="mt-2">
                      <p className="text-xs text-gray-600 truncate font-medium">
                        {img.filename}
                      </p>
                    </div>
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

export default App;