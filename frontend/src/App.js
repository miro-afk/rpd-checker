// App.js
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import FileUploader from './components/FileUploader';
import ResultPage from './components/ResultPage';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<FileUploader />} />
        <Route path="/result/:file_id" element={<ResultPage />} />
      </Routes>
    </Router>
  );
}

export default App;