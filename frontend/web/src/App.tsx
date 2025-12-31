import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Satellites from './pages/Satellites';
import GroundStations from './pages/GroundStations';
import Scheduling from './pages/Scheduling';
import OpsCoPilot from './pages/OpsCoPilot';

function App() {
    return (
        <Layout>
            <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/satellites" element={<Satellites />} />
                <Route path="/ground-stations" element={<GroundStations />} />
                <Route path="/scheduling" element={<Scheduling />} />
                <Route path="/ops-copilot" element={<OpsCoPilot />} />
            </Routes>
        </Layout>
    );
}

export default App;
