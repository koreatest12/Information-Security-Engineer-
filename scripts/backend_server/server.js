import express from 'express'; import path from 'path'; import { fileURLToPath } from 'url';
const app = express(); const PORT = process.env.PORT || 5000;
const __dirname = path.dirname(fileURLToPath(import.meta.url));
app.use(express.static(path.join(__dirname, '../frontend/dist')));
app.get('*', (req, res) => res.sendFile(path.join(__dirname, '../frontend/dist/index.html')));
app.listen(PORT, () => console.log('Server Ready'));