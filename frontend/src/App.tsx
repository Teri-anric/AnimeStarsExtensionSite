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
  SettingsPage,
  FQAPage
} from './pages';
import { DecksListPage, DeckDetailPage } from './pages/decks';
import Header from './components/Header';
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
                <Route path="/random-gif" element={<RandomAnimeGifPage />} />
                <Route path="/cards" element={<CardsPage />} />
                <Route path="/card/:cardId" element={<CardDetailPage />} />
                <Route path="/decks" element={<DecksListPage />} />
                <Route path="/deck/:deck_id" element={<DeckDetailPage />} />
                <Route path="/settings/*" element={<SettingsPage />} />
                <Route path="/fqa" element={<FQAPage />} />
                <Route path="/" element={<Navigate to="/random-gif" replace />} />

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
