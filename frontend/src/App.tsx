import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';
import { AuthProvider } from './context/AuthContext';
import { DomainProvider } from './context/DomainContext';
import AuthPage from './components/AuthPage';
import Header from './components/Header';
import RandomAnimeGif from './components/RandomAnimeGif';
import Cards from './components/Cards';
import AccountSettings from './components/AccountSettings';
import ProtectedRoute from './components/ProtectedRoute';
import DecksPage from './components/DecksPage';

function App() {
  return (
    <Router>
      <AuthProvider>
        <DomainProvider>
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
                  <Route path="/cards" element={
                    <ProtectedRoute>
                      <Cards />
                    </ProtectedRoute>
                  } />
                  <Route path="/decks" element={
                    <ProtectedRoute>
                      <DecksPage />
                    </ProtectedRoute>
                  } />
                  <Route path="/settings" element={
                    <ProtectedRoute>
                      <AccountSettings />
                    </ProtectedRoute>
                  } />
                  <Route path="/" element=
                    {
                    <ProtectedRoute>
                      <Navigate to="/random-gif" replace />
                    </ProtectedRoute>
                    } />

              </Routes>
            </main>
          </div>
        </DomainProvider>
      </AuthProvider>
    </Router>
  );
}

export default App;
