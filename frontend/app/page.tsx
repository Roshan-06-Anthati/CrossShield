'use client';

import { useState } from 'react';

export default function Home() {
  const [emailText, setEmailText] = useState('');
  const [file, setFile] = useState(null);
  const [mode, setMode] = useState('email'); // 'email' or 'attachment'
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleEmailScan = async () => {
    if (!emailText.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch('http://127.0.0.1:8000/api/scan/email', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: emailText }),
      });
      if (!response.ok) throw new Error('Scan failed');
      const data = await response.json();
      setResult({ type: 'email', data });
    } catch (err) {
      setError('Could not reach the backend. Make sure the server is running.');
    } finally {
      setLoading(false);
    }
  };

  const handlePdfScan = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('http://127.0.0.1:8000/api/attachment/analyze', {
        method: 'POST',
        body: formData,
      });
      if (!response.ok) throw new Error('Scan failed');
      const data = await response.json();
      setResult({ type: 'attachment', data });
    } catch (err) {
      setError('Could not reach the backend. Make sure the server is running.');
    } finally {
      setLoading(false);
    }
  };

  const getVerdictColor = (score) => {
    if (score >= 70) return 'text-red-600 bg-red-50';
    if (score >= 40) return 'text-yellow-600 bg-yellow-50';
    return 'text-green-600 bg-green-50';
  };

  return (
    <main className="min-h-screen bg-gray-100 py-12 px-4">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          CrossShield — Fraud Detection
        </h1>
        <p className="text-gray-600 mb-8">
          Check an email or a PDF attachment for phishing and fraud indicators.
        </p>

        {/* Mode toggle */}
        <div className="flex gap-2 mb-6">
          <button
            onClick={() => { setMode('email'); setResult(null); setError(null); }}
            className={`px-4 py-2 rounded-md font-medium transition ${mode === 'email' ? 'bg-blue-600 text-white' : 'bg-white text-gray-700 border border-gray-300'
              }`}
          >
            Scan Email
          </button>
          <button
            onClick={() => { setMode('attachment'); setResult(null); setError(null); }}
            className={`px-4 py-2 rounded-md font-medium transition ${mode === 'attachment' ? 'bg-blue-600 text-white' : 'bg-white text-gray-700 border border-gray-300'
              }`}
          >
            Scan PDF Attachment
          </button>
        </div>

        <div className="bg-white rounded-lg shadow p-6 mb-6">
          {mode === 'email' ? (
            <>
              <textarea
                value={emailText}
                onChange={(e) => setEmailText(e.target.value)}
                placeholder="Paste the email text here..."
                className="w-full h-40 p-4 border border-gray-300 rounded-md text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button
                onClick={handleEmailScan}
                disabled={loading}
                className="mt-4 bg-blue-600 text-white px-6 py-2 rounded-md font-medium hover:bg-blue-700 disabled:bg-gray-400 transition"
              >
                {loading ? 'Scanning...' : 'Analyze Email'}
              </button>
            </>
          ) : (
            <>
              <input
                type="file"
                accept="application/pdf"
                onChange={(e) => setFile(e.target.files[0])}
                className="block w-full text-sm text-gray-700 border border-gray-300 rounded-md p-3 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
              />
              <button
                onClick={handlePdfScan}
                disabled={loading || !file}
                className="mt-4 bg-blue-600 text-white px-6 py-2 rounded-md font-medium hover:bg-blue-700 disabled:bg-gray-400 transition"
              >
                {loading ? 'Scanning...' : 'Analyze PDF'}
              </button>
            </>
          )}
        </div>

        {error && (
          <div className="bg-red-50 text-red-700 p-4 rounded-md mb-6">
            {error}
          </div>
        )}

        {/* Email scan results */}
        {result && result.type === 'email' && (
          <div className="bg-white rounded-lg shadow p-6 space-y-6">
            <div className={`p-4 rounded-md ${getVerdictColor(result.data.unified_result.final_risk_score)}`}>
              <div className="text-sm font-medium">Unified Risk Score</div>
              <div className="text-3xl font-bold">
                {result.data.unified_result.final_risk_score}%
              </div>
              <div className="text-sm mt-1">{result.data.unified_result.verdict}</div>
            </div>

            <div>
              <h3 className="font-semibold text-gray-800 mb-2">Email Analysis</h3>
              <div className="text-sm text-gray-600">
                Verdict: <span className="font-medium">{result.data.email_analysis.verdict}</span>
                {' '}({result.data.email_analysis.risk_score}%)
              </div>
            </div>

            {result.data.urls_found.length > 0 && (
              <div>
                <h3 className="font-semibold text-gray-800 mb-2">URLs Found</h3>
                {result.data.website_analysis.map((site, i) => (
                  <div key={i} className="text-sm text-gray-600 mb-2 p-3 bg-gray-50 rounded">
                    <div className="font-mono">{site.domain}</div>
                    <div>Risk: {site.risk_score}% — {site.reasons.join(', ')}</div>
                  </div>
                ))}
              </div>
            )}

            {result.data.sandbox_analysis.length > 0 && (
              <div>
                <h3 className="font-semibold text-gray-800 mb-2">Link Behavior Check</h3>
                {result.data.sandbox_analysis.map((sandbox, i) => (
                  <div key={i} className="text-sm text-gray-600 mb-2 p-3 bg-gray-50 rounded">
                    <div>Risk: {sandbox.risk_score}%</div>
                    <div>{sandbox.reasons.join(', ')}</div>
                  </div>
                ))}
              </div>
            )}

            <div>
              <h3 className="font-semibold text-gray-800 mb-2">Score Breakdown</h3>
              <div className="text-sm text-gray-600 space-y-1">
                <div>Email: {result.data.unified_result.breakdown.email_contribution}</div>
                <div>Website: {result.data.unified_result.breakdown.website_contribution}</div>
                <div>Sandbox: {result.data.unified_result.breakdown.sandbox_contribution}</div>
              </div>
            </div>
          </div>
        )}

        {/* PDF scan results */}
        {result && result.type === 'attachment' && (
          <div className="bg-white rounded-lg shadow p-6 space-y-6">
            <div className={`p-4 rounded-md ${getVerdictColor(result.data.risk_score)}`}>
              <div className="text-sm font-medium">Risk Score</div>
              <div className="text-3xl font-bold">{result.data.risk_score}%</div>
              <div className="text-sm mt-1">{result.data.verdict}</div>
            </div>

            <div>
              <h3 className="font-semibold text-gray-800 mb-2">Extracted Text (preview)</h3>
              <div className="text-sm text-gray-600 p-3 bg-gray-50 rounded max-h-40 overflow-y-auto">
                {result.data.extracted_text || 'No text could be extracted'}
              </div>
            </div>

            <div className="text-xs text-gray-400">
              Note: this classifier is trained on email-style text. Results on structurally
              different documents (e.g. resumes) may be less reliable.
            </div>
          </div>
        )}
      </div>
    </main>
  );
}