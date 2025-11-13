import { BrowserRouter, Routes, Route, Outlet } from "react-router-dom";

import "./App.css";
import Home from "./pages/Home";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Outlet />}>
          <Route index element={<Home />} />
        </Route>

        <Route path="*" element={<h1>Hello World!</h1>} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
