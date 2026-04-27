require('dotenv').config();
const express = require('express');
const Anthropic = require('@anthropic-ai/sdk');
const path = require('path');

const app = express();
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });

const USER_TYPE_LABELS = {
  student: 'Student',
  job_seeker: 'Job Seeker',
  business_owner: 'Business Owner',
  general: 'General Citizen',
};

app.post('/api/explain', async (req, res) => {
  const { policy, userType } = req.body;

  if (!policy || !policy.trim()) {
    return res.status(400).json({ error: 'Policy name is required' });
  }

  const userLabel = USER_TYPE_LABELS[userType] || 'General Citizen';

  const prompt = `You are an expert on Indian government policies. Explain policies in simple Hinglish — the natural mix of Hindi and English that urban Indians use in daily conversation (e.g., "Yeh policy basically tax ko simplify karti hai").

Policy to explain: "${policy.trim()}"
Target user: ${userLabel}

Return ONLY a valid JSON object with exactly these keys (no markdown, no extra text):
{
  "simple_explanation": "3-4 sentences in simple Hinglish explaining what this policy is. Use everyday words.",
  "why_introduced": "2-3 sentences in Hinglish about why the government introduced this policy.",
  "personal_impact": "3-4 sentences in Hinglish explaining specifically how this policy affects a ${userLabel}. Be concrete and relatable.",
  "pros": ["benefit 1 in Hinglish", "benefit 2 in Hinglish", "benefit 3 in Hinglish"],
  "cons": ["drawback 1 in Hinglish", "drawback 2 in Hinglish", "drawback 3 in Hinglish"],
  "summary": "Exactly 2 lines. The most important takeaway for a ${userLabel} in Hinglish."
}`;

  try {
    const message = await client.messages.create({
      model: 'claude-sonnet-4-6',
      max_tokens: 1500,
      system: 'You are a helpful assistant that explains Indian government policies in simple Hinglish. Always respond with valid JSON only.',
      messages: [{ role: 'user', content: prompt }],
    });

    const text = message.content[0].text.trim();

    let parsed;
    try {
      // Strip markdown code fences if present
      const clean = text.replace(/^```(?:json)?\s*/i, '').replace(/\s*```$/, '');
      parsed = JSON.parse(clean);
    } catch {
      return res.status(500).json({ error: 'Could not parse AI response. Please try again.' });
    }

    res.json({ result: parsed });
  } catch (err) {
    console.error('Anthropic API error:', err.message);
    res.status(500).json({ error: err.message || 'Something went wrong. Please try again.' });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`\n🔍 PolicyLens AI running at http://localhost:${PORT}\n`);
});
