import { Routes, Route } from 'react-router-dom';
import Layout from './Layout';
import Dashboard from './Dashboard';
export default function App() { return (<Routes><Route path="/" element={<Layout />}><Route index element={<Dashboard />} /></Route></Routes>); }