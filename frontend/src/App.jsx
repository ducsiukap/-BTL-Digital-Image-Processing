import { BrowserRouter, Routes, Route, Outlet } from "react-router-dom";

import "./App.css";
import Home from "./pages/Home";
import BetaHome from "./pages/BetaHome";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Outlet />}>
          <Route index element={<Home />} />
          <Route path="beta" element= {<BetaHome />} />
        </Route>

        <Route path="*" element={<h1>Hello World!</h1>} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
