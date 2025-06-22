import { useEffect, useState } from "react";
import { useAuth } from "../../context/AuthContext";
import { createAuthenticatedClient } from "../../utils/apiClient";
import { HealthApi } from "../../client";

interface GifHistoryItem {
    id: string;
    url: string;
    reaction: string;
    timestamp: number;
}

interface HealthInfo {
    status: string;
    ping: number;
    uptime_formatted: string;
    database_stats: {
        total_cards: number;
        total_users: number;
        cards_with_stats: number;
        cards_stats_today: number;
    };
}

const fetchAllReactions = async (token?: string) => {
    const response = await fetch('https://api.otakugifs.xyz/gif/allreactions', {
        headers: token ? { 'Authorization': `Bearer ${token}` } : {}
    });
    const data = await response.json();
    return data.reactions;
}

const fetchGif = async (reaction: string, token?: string) => {
    const response = await fetch(`https://api.otakugifs.xyz/gif?reaction=${reaction}`, {
        headers: token ? { 'Authorization': `Bearer ${token}` } : {}
    });
    const data = await response.json();
    return data.url;
};

const RandomAnimeGifPage = () => {
    const [gif, setGif] = useState<string>('');
    const [currentReaction, setCurrentReaction] = useState<string>('');
    const [loading, setLoading] = useState<boolean>(true);
    const [healthInfo, setHealthInfo] = useState<HealthInfo | null>(null);
    const [gifHistory, setGifHistory] = useState<GifHistoryItem[]>([]);
    const [showHistory, setShowHistory] = useState<boolean>(false);
    const { token } = useAuth();

    // Load gif history from localStorage
    useEffect(() => {
        const saved = localStorage.getItem('anime-gif-history');
        if (saved) {
            try {
                setGifHistory(JSON.parse(saved));
            } catch (e) {
                console.error('Failed to parse gif history:', e);
            }
        }
    }, []);

    // Save gif to history
    const saveGifToHistory = (url: string, reaction: string) => {
        const newItem: GifHistoryItem = {
            id: Date.now().toString(),
            url,
            reaction,
            timestamp: Date.now()
        };
        
        setGifHistory(prev => {
            const updated = [newItem, ...prev].slice(0, 20);
            localStorage.setItem('anime-gif-history', JSON.stringify(updated));
            return updated;
        });
    };

    // Check backend health status
    useEffect(() => {
        const checkHealth = async () => {
            try {
                const healthApi = createAuthenticatedClient(HealthApi);
                const response = await healthApi.healthHealthGet();
                setHealthInfo(response.data as any);
            } catch (error) {
                console.error('Health check failed:', error);
                setHealthInfo({
                    status: 'Error connecting to backend',
                    ping: 0,
                    uptime_formatted: 'N/A',
                    database_stats: {
                        total_cards: 0,
                        total_users: 0,
                        cards_with_stats: 0,
                        cards_stats_today: 0
                    }
                });
            }
        };
        
        checkHealth();
    }, []);

    // Fetch new GIF
    const fetchNewGif = async () => {
        setLoading(true);
        try {
            const reactions = await fetchAllReactions(token || undefined);
            const randomReaction = reactions[Math.floor(Math.random() * reactions.length)];
            const gifUrl = await fetchGif(randomReaction, token || undefined);
            
            setGif(gifUrl);
            setCurrentReaction(randomReaction);
            saveGifToHistory(gifUrl, randomReaction);
        } catch (error) {
            console.error('Failed to fetch gif:', error);
        } finally {
            setLoading(false);
        }
    };

    // Initial GIF fetch
    useEffect(() => {
        fetchNewGif();
    }, []);

    // Load GIF from history
    const loadFromHistory = (historyItem: GifHistoryItem) => {
        setGif(historyItem.url);
        setCurrentReaction(historyItem.reaction);
        setLoading(false);
    };

    if (loading && !gif) {
        return <div className="loading-container">Loading...</div>;
    }

    return (
        <div className="random-gif-page">
            <div className="gif-main-content">
                <div className="gif-controls">
                    <button onClick={fetchNewGif} disabled={loading} className="btn btn-primary refresh-btn">
                        {loading ? 'Loading...' : 'New GIF'}
                    </button>
                    <button 
                        onClick={() => setShowHistory(!showHistory)} 
                        className="btn btn-secondary history-btn"
                    >
                        {showHistory ? 'Hide History' : 'Show History'} ({gifHistory.length})
                    </button>
                </div>

                <div className="gif-display">
                    {gif && (
                        <div className="gif-container">
                            <img src={gif} alt="Random Anime Gif" className="anime-gif" />
                            <div className="gif-info">
                                <span className="reaction-tag">Reaction: {currentReaction}</span>
                            </div>
                        </div>
                    )}
                    {!gif && !loading && <div className="error-message">Failed to load GIF</div>}
                </div>

                {showHistory && (
                    <div className="gif-history">
                        <h3>GIF History</h3>
                        <div className="history-grid">
                            {gifHistory.map((item) => (
                                <div key={item.id} className="history-item" onClick={() => loadFromHistory(item)}>
                                    <img src={item.url} alt={item.reaction} />
                                    <span className="history-reaction">{item.reaction}</span>
                                    <span className="history-time">
                                        {new Date(item.timestamp).toLocaleTimeString()}
                                    </span>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>

            <div className="status-panel">
                <h3>System Status</h3>
                {healthInfo && (
                    <div className="status-info">
                        <div className="status-item">
                            <span className="status-label">Status:</span>
                            <span className={`status-value ${healthInfo.status === 'healthy' ? 'status-healthy' : 'status-error'}`}>
                                {healthInfo.status}
                            </span>
                        </div>

                        <div className="status-item">
                            <span className="status-label">Response Time:</span>
                            <span className="status-value">{healthInfo.ping} ms</span>
                        </div>

                        <div className="status-item">
                            <span className="status-label">Uptime:</span>
                            <span className="status-value">{healthInfo.uptime_formatted}</span>
                        </div>

                        <div className="status-section">
                            <h4>Database Stats</h4>
                            <div className="status-item">
                                <span className="status-label">Total Cards:</span>
                                <span className="status-value">{healthInfo.database_stats.total_cards.toLocaleString()}</span>
                            </div>
                            <div className="status-item">
                                <span className="status-label">Total Users:</span>
                                <span className="status-value">{healthInfo.database_stats.total_users.toLocaleString()}</span>
                            </div>
                            <div className="status-item">
                                <span className="status-label">Cards with Stats:</span>
                                <span className="status-value">{healthInfo.database_stats.cards_with_stats.toLocaleString()}</span>
                            </div>
                            <div className="status-item">
                                <span className="status-label">Stats Today:</span>
                                <span className="status-value">{healthInfo.database_stats.cards_stats_today.toLocaleString()}</span>
                            </div>
                        </div>

                        <div className="status-item timestamp">
                            <span className="status-label">Last Updated:</span>
                            <span className="status-value">
                                {new Date().toLocaleTimeString()}
                            </span>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default RandomAnimeGifPage;
