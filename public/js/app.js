const { useState } = React;

function OutputCard({ result, policyName, languageLabel }) {
  const [copied, setCopied] = useState(false);

  function buildPlainText() {
    return [
      `PolicyLens AI — ${policyName}`,
      '',
      'Simple Explanation',
      result.simple_explanation,
      '',
      'Why It Was Introduced',
      result.why_introduced,
      '',
      'Impact on You',
      result.personal_impact,
      '',
      'Benefits',
      ...result.pros.map(p => `• ${p}`),
      '',
      'Drawbacks',
      ...result.cons.map(c => `• ${c}`),
      '',
      'Summary',
      result.summary,
    ].join('\n');
  }

  function handleCopy() {
    navigator.clipboard.writeText(buildPlainText()).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2200);
    });
  }

  return (
    <div className="card output-card">
      <div className="output-header">
        <div>
          <div className="output-title">{policyName}</div>
          <div className="lang-badge">{languageLabel}</div>
        </div>
        <button
          className={`btn-copy${copied ? ' copied' : ''}`}
          onClick={handleCopy}
        >
          {copied ? '✓ Copied' : 'Copy'}
        </button>
      </div>

      <div className="section s1">
        <div className="section-tag">Simple Explanation</div>
        <div className="section-body">{result.simple_explanation}</div>
      </div>

      <div className="divider" />

      <div className="section s2">
        <div className="section-tag">Why It Was Introduced</div>
        <div className="section-body">{result.why_introduced}</div>
      </div>

      <div className="divider" />

      <div className="section s3">
        <div className="section-tag">Impact on You</div>
        <div className="section-body">{result.personal_impact}</div>
      </div>

      <div className="divider" />

      <div className="pros-cons-grid">
        <div className="section s4">
          <div className="section-tag">Benefits</div>
          <ul className="bullet-list pros-list">
            {result.pros.map((p, i) => <li key={i}>{p}</li>)}
          </ul>
        </div>
        <div className="section s5">
          <div className="section-tag">Drawbacks</div>
          <ul className="bullet-list cons-list">
            {result.cons.map((c, i) => <li key={i}>{c}</li>)}
          </ul>
        </div>
      </div>

      <div className="divider" />

      <div className="section s6">
        <div className="section-tag">Summary</div>
        <div className="summary-box">{result.summary}</div>
      </div>
    </div>
  );
}

function App() {
  const [policy, setPolicy]               = useState('');
  const [userType, setUserType]           = useState('general');
  const [language, setLanguage]           = useState('hinglish');
  const [loading, setLoading]             = useState(false);
  const [result, setResult]               = useState(null);
  const [error, setError]                 = useState('');
  const [displayPolicy, setDisplayPolicy] = useState('');
  const [displayLang, setDisplayLang]     = useState('');

  async function handleSubmit(e) {
    e.preventDefault();
    if (!policy.trim()) return;

    setLoading(true);
    setResult(null);
    setError('');
    setDisplayPolicy(policy.trim());
    setDisplayLang(LANGUAGES.find(l => l.value === language)?.label || '');

    try {
      const res = await fetch('/api/explain', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ policy: policy.trim(), userType, language }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Request failed');
      setResult(data.result);
    } catch (err) {
      setError(err.message || 'Something went wrong. Please try again.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <div className="header">
        <div className="ai-badge">Made for Bharat 🇮🇳</div>
        <h1>Policy<span className="gradient">Lens</span> AI</h1>
        <p className="tagline">Understand any government policy — in your language</p>
        <div className="tricolor-stripe">
          <span className="tc-saffron" />
          <span className="tc-white" />
          <span className="tc-green" />
        </div>
      </div>

      <div className="container">
        <div className="card">
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Policy Name</label>
              <input
                type="text"
                value={policy}
                onChange={e => setPolicy(e.target.value)}
                placeholder="e.g. GST, Budget 2024, NEP, Farm Bills, MGNREGA…"
                disabled={loading}
                autoFocus
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Who are you?</label>
                <div className="select-wrapper">
                  <select
                    value={userType}
                    onChange={e => setUserType(e.target.value)}
                    disabled={loading}
                  >
                    {USER_TYPES.map(t => (
                      <option key={t.value} value={t.value}>{t.label}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="form-group">
                <label>Language</label>
                <div className="select-wrapper">
                  <select
                    value={language}
                    onChange={e => setLanguage(e.target.value)}
                    disabled={loading}
                  >
                    {LANGUAGES.map(l => (
                      <option key={l.value} value={l.value}>{l.label}</option>
                    ))}
                  </select>
                </div>
              </div>
            </div>

            <button
              type="submit"
              className="btn-explain"
              disabled={loading || !policy.trim()}
            >
              {loading ? '⏳ Analyzing…' : '🔍 Explain Policy'}
            </button>
          </form>
        </div>

        {loading && (
          <div className="loading-wrap">
            <div className="spinner" />
            <div className="loading-text">Analyzing policy, please wait… 🙏</div>
          </div>
        )}

        {error && !loading && (
          <div className="error-box">⚠️ {error}</div>
        )}

        {result && !loading && (
          <OutputCard result={result} policyName={displayPolicy} languageLabel={displayLang} />
        )}
      </div>

      <div className="footer">
        PolicyLens AI &nbsp;·&nbsp; Powered by AI &nbsp;·&nbsp; Made with ♥ for Bharat 🇮🇳
      </div>
    </>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(<App />);
