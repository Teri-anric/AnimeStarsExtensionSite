import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';
import { AuthProvider } from './context/AuthContext';
import { DomainProvider } from './context/DomainContext';
import { 
  LoginPage,
  RegisterPage,
  CardsPage, 
  CardDetailPage,
  RandomAnimeGifPage, 
  AccountSettingsPage,
  SessionsPage
} from './pages';
import { DecksListPage, DeckDetailPage } from './pages/decks';
import Header from './components/Header';
import ProtectedRoute from './components/ProtectedRoute';
import ExtensionTokenModal from './components/ExtensionTokenModal';

function App() {
  return (
    <Router>
      <AuthProvider>
        <DomainProvider>
          <div className="app">
            <Header />
            <main className="app-content">
              <Routes>
                <Route path="/login" element={<LoginPage />} />
                <Route path="/register" element={<RegisterPage />} />
                <Route path="/auth" element={<Navigate to="/login" replace />} />
                  <Route path="/random-gif" element={
                    <ProtectedRoute>
                      <RandomAnimeGifPage />
                    </ProtectedRoute>
                  } />
                  <Route path="/cards" element={
                    <ProtectedRoute>
                      <CardsPage />
                    </ProtectedRoute>
                  } />
                  <Route path="/card/:cardId" element={
                    <ProtectedRoute>
                      <CardDetailPage />
                    </ProtectedRoute>
                  } />
                  <Route path="/decks" element={
                    <ProtectedRoute>
                      <DecksListPage />
                    </ProtectedRoute>
                  } />
                  <Route path="/deck/:anime_link" element={
                    <ProtectedRoute>
                      <DeckDetailPage />
                    </ProtectedRoute>
                  } />
                  <Route path="/settings" element={
                    <ProtectedRoute>
                      <AccountSettingsPage />
                    </ProtectedRoute>
                  } />
                  <Route path="/sessions" element={
                    <ProtectedRoute>
                      <SessionsPage />
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
          
          {/* Extension Token Modal - Always available for extension requests */}
          <ExtensionTokenModal />
        </DomainProvider>
      </AuthProvider>
    </Router>
  );
}

export default App;
