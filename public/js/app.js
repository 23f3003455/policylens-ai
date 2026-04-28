const { useState } = React;
const e = React.createElement;

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

  return e('div', { className: 'card output-card' },
    e('div', { className: 'output-header' },
      e('div', null,
        e('div', { className: 'output-title' }, policyName),
        e('div', { className: 'lang-badge' }, languageLabel)
      ),
      e('button', { className: `btn-copy${copied ? ' copied' : ''}`, onClick: handleCopy },
        copied ? '✓ Copied' : 'Copy'
      )
    ),
    e('div', { className: 'section s1' },
      e('div', { className: 'section-tag' }, 'Simple Explanation'),
      e('div', { className: 'section-body' }, result.simple_explanation)
    ),
    e('div', { className: 'divider' }),
    e('div', { className: 'section s2' },
      e('div', { className: 'section-tag' }, 'Why It Was Introduced'),
      e('div', { className: 'section-body' }, result.why_introduced)
    ),
    e('div', { className: 'divider' }),
    e('div', { className: 'section s3' },
      e('div', { className: 'section-tag' }, 'Impact on You'),
      e('div', { className: 'section-body' }, result.personal_impact)
    ),
    e('div', { className: 'divider' }),
    e('div', { className: 'pros-cons-grid' },
      e('div', { className: 'section s4' },
        e('div', { className: 'section-tag' }, 'Benefits'),
        e('ul', { className: 'bullet-list pros-list' },
          result.pros.map((p, i) => e('li', { key: i }, p))
        )
      ),
      e('div', { className: 'section s5' },
        e('div', { className: 'section-tag' }, 'Drawbacks'),
        e('ul', { className: 'bullet-list cons-list' },
          result.cons.map((c, i) => e('li', { key: i }, c))
        )
      )
    ),
    e('div', { className: 'divider' }),
    e('div', { className: 'section s6' },
      e('div', { className: 'section-tag' }, 'Summary'),
      e('div', { className: 'summary-box' }, result.summary)
    )
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

  async function handleSubmit(ev) {
    ev.preventDefault();
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

  return e(React.Fragment, null,
    e('div', { className: 'header' },
      e('div', { className: 'ai-badge' }, 'Made for INDIA 🇮🇳'),
      e('h1', null, 'Policy', e('span', { className: 'gradient' }, 'Lens'), ' AI'),
      e('p', { className: 'tagline' }, 'Understand any government policy — in your language'),
      e('div', { className: 'tricolor-stripe' },
        e('span', { className: 'tc-saffron' }),
        e('span', { className: 'tc-white' }),
        e('span', { className: 'tc-green' })
      )
    ),

    e('div', { className: 'container' },
      e('div', { className: 'card' },
        e('form', { onSubmit: handleSubmit },
          e('div', { className: 'form-group' },
            e('label', null, 'Policy Name'),
            e('input', {
              type: 'text',
              value: policy,
              onChange: ev => setPolicy(ev.target.value),
              placeholder: 'e.g. GST, Budget 2024, NEP, Farm Bills, MGNREGA…',
              disabled: loading,
              autoFocus: true,
            })
          ),
          e('div', { className: 'form-row' },
            e('div', { className: 'form-group' },
              e('label', null, 'User Type'),
              e('div', { className: 'select-wrapper' },
                e('select', { value: userType, onChange: ev => setUserType(ev.target.value), disabled: loading },
                  USER_TYPES.map(t => e('option', { key: t.value, value: t.value }, t.label))
                )
              )
            ),
            e('div', { className: 'form-group' },
              e('label', null, 'Language'),
              e('div', { className: 'select-wrapper' },
                e('select', { value: language, onChange: ev => setLanguage(ev.target.value), disabled: loading },
                  LANGUAGES.map(l => e('option', { key: l.value, value: l.value }, l.label))
                )
              )
            )
          ),
          e('button', { type: 'submit', className: 'btn-explain', disabled: loading || !policy.trim() },
            loading ? '⏳ Analyzing…' : '🔍 Explain Policy'
          )
        )
      ),

      loading && e('div', { className: 'loading-wrap' },
        e('div', { className: 'spinner' }),
        e('div', { className: 'loading-text' }, 'Analyzing policy, please wait… 🙏')
      ),

      error && !loading && e('div', { className: 'error-box' }, '⚠️ ' + error),

      result && !loading && e(OutputCard, { result, policyName: displayPolicy, languageLabel: displayLang })
    ),

    e('div', { className: 'footer' },
      'PolicyLens-AI  ·  Powered by Claude AI  ·  Made with ♥ for INDIA 🇮🇳'
    )
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(e(App, null));
