import { Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import Satellites from "./pages/Satellites";
import GroundStations from "./pages/GroundStations";
import Scheduling from "./pages/Scheduling";
import OpsCoPilot from "./pages/OpsCoPilot";
import TLEAdmin from "./pages/TLEAdmin";
import Login from "./pages/Login";

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<Dashboard />} />
        <Route path="/satellites" element={<Satellites />} />
        <Route path="/ground-stations" element={<GroundStations />} />
        <Route path="/scheduling" element={<Scheduling />} />
        <Route path="/ops-copilot" element={<OpsCoPilot />} />
        <Route path="/tle-admin" element={<TLEAdmin />} />
      </Routes>
    </Layout>
  );
}

export default App;
