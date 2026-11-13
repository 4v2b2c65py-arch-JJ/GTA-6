module.exports = (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Cache-Control', 'no-store');
  res.status(200).json({ ok: true, api: 'health', service: 'spatial-avy', time: new Date().toISOString(), vercel: process.env.VERCEL_ENV || null });
};
