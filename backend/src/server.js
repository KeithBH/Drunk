import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';

dotenv.config();

const app = express();
const port = Number(process.env.PORT || 4000);
const maxUploadSizeMb = Number(process.env.MAX_UPLOAD_SIZE_MB || 10);

app.use(cors({ origin: process.env.CORS_ORIGIN || '*' }));
app.use(express.json({ limit: `${maxUploadSizeMb}mb` }));

const fakeStats = {
  totalUploads: 126,
  totalRecognitions: 118,
  accuracyRate: 0.92,
  favoriteDrink: 'Mojito'
};

const fakePreferences = {
  language: 'zh-CN',
  notifications: true,
  cameraUploadDefault: true,
  privacyLevel: 'friends'
};

app.get('/api/health', (_req, res) => {
  res.json({ status: 'ok', service: process.env.APP_NAME || 'Drunk Recognizer' });
});

app.post('/api/uploads', (req, res) => {
  const { fileName, mimeType, size } = req.body || {};

  if (!fileName) {
    return res.status(400).json({ message: 'fileName is required' });
  }

  return res.status(201).json({
    uploadId: `upl_${Date.now()}`,
    fileName,
    mimeType: mimeType || 'image/jpeg',
    size: size || 0,
    status: 'uploaded'
  });
});

app.post('/api/recognize', (req, res) => {
  const { uploadId } = req.body || {};

  if (!uploadId) {
    return res.status(400).json({ message: 'uploadId is required' });
  }

  return res.json({
    uploadId,
    label: 'Whiskey Sour',
    confidence: 0.88,
    tags: ['whiskey', 'citrus', 'sweet']
  });
});

app.get('/api/stats', (_req, res) => {
  res.json(fakeStats);
});

app.get('/api/profile/preferences', (_req, res) => {
  res.json(fakePreferences);
});

app.post('/api/share', (req, res) => {
  const { resultId, target } = req.body || {};

  if (!resultId || !target) {
    return res.status(400).json({ message: 'resultId and target are required' });
  }

  return res.status(201).json({
    shareId: `shr_${Date.now()}`,
    resultId,
    target,
    status: 'sent'
  });
});

app.listen(port, () => {
  console.log(`Backend API listening on http://localhost:${port}`);
});
