import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';
import { AuthProvider } from './context/AuthContext';
import AuthPage from './components/AuthPage';
import Header from './components/Header';
import RandomAnimeGif from './components/RandomAnimeGif';
import ProtectedRoute from './components/ProtectedRoute';

function App() {
  return (
    <Router>
      <AuthProvider>
        <div className="app">
          <Header />
          <main className="app-content">
            <Routes>
              <Route path="/auth" element={<AuthPage />} />
              <Route path="/random-gif" element={
                <ProtectedRoute>
                  <RandomAnimeGif />
                </ProtectedRoute>
              } />
              <Route path="/" element={<Navigate to="/random-gif" replace />} />
            </Routes>
          </main>
        </div>
      </AuthProvider>
    </Router>
  );
}

export default App;
