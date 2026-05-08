import { type ChangeEvent, useEffect, useState } from "react";
import { createAuthenticatedClient } from "../../utils/apiClient";
import { HealthApi } from "../../client";
import { useTranslation } from 'react-i18next';
import { formatCurrentTime } from "../../utils/dateUtils";
import { useDomain } from "../../context/DomainContext";
import GifMainContent, { type GifHistoryItem } from "../../components/GifMainContent";

interface HealthInfo {
    status: string;
    ping: number;
    uptime_formatted: string;
}

const fetchAllReactions = async () => {
    const response = await fetch('https://api.otakugifs.xyz/gif/allreactions');
    const data = await response.json();
    return data.reactions;
}

const fetchGif = async (reaction: string) => {
    const response = await fetch(`https://api.otakugifs.xyz/gif?reaction=${reaction}`, {
    });
    const data = await response.json();
    return data.url;
};

const RandomAnimeGifPage = () => {
    const { t } = useTranslation();
    const { currentDomain, setCurrentDomain, availableDomains } = useDomain();
    const [gif, setGif] = useState<string>('');
    const [currentReaction, setCurrentReaction] = useState<string>('');
    const [loading, setLoading] = useState<boolean>(true);
    const [healthInfo, setHealthInfo] = useState<HealthInfo | null>(null);
    const [gifHistory, setGifHistory] = useState<GifHistoryItem[]>([]);
    const [showHistory, setShowHistory] = useState<boolean>(false);
    const [domainUpdatedMessage, setDomainUpdatedMessage] = useState<string>('');

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
                    status: t('randomGif.errorConnectingBackend'),
                    ping: 0,
                    uptime_formatted: 'N/A',
                });
            }
        };

        checkHealth();
    }, []);

    // Fetch new GIF
    const fetchNewGif = async () => {
        setLoading(true);
        try {
            const reactions = await fetchAllReactions();
            const randomReaction = reactions[Math.floor(Math.random() * reactions.length)];
            const gifUrl = await fetchGif(randomReaction);

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

    const handleDomainChange = (e: ChangeEvent<HTMLSelectElement>) => {
        setCurrentDomain(e.target.value);
        setDomainUpdatedMessage(t('settings.domainSettingsUpdated'));

        setTimeout(() => {
            setDomainUpdatedMessage('');
        }, 3000);
    };

    if (loading && !gif) {
        return <div className="loading-container">{t('randomGif.loading')}</div>;
    }

    return (
        <div className="random-gif-page">
            <GifMainContent
                loading={loading}
                gif={gif}
                currentReaction={currentReaction}
                showHistory={showHistory}
                gifHistory={gifHistory}
                onFetchNewGif={fetchNewGif}
                onToggleHistory={() => setShowHistory(!showHistory)}
                onLoadFromHistory={loadFromHistory}
            />

            <div className="status-panel">
                <h3>{t('randomGif.systemStatus')}</h3>
                {healthInfo && (
                    <div className="status-info">
                        <div className="status-item">
                            <span className="status-label">{t('randomGif.status')}:</span>
                            <span className={`status-value ${healthInfo.status === 'healthy' ? 'status-healthy' : 'status-error'}`}>
                                {healthInfo.status}
                            </span>
                        </div>

                        <div className="status-item">
                            <span className="status-label">{t('randomGif.responseTime')}:</span>
                            <span className="status-value">{healthInfo.ping} ms</span>
                        </div>

                        <div className="status-item">
                            <span className="status-label">{t('randomGif.uptime')}:</span>
                            <span className="status-value">{healthInfo.uptime_formatted}</span>
                        </div>

                        <div className="status-item timestamp">
                            <span className="status-label">{t('randomGif.lastUpdated')}:</span>
                            <span className="status-value">
                                {formatCurrentTime()}
                            </span>
                        </div>

                        <div className="status-item card-domain-settings">
                            <label htmlFor="card-domain-setting">{t('settings.cardDomain')}</label>
                            <select
                                id="card-domain-setting"
                                value={currentDomain}
                                onChange={handleDomainChange}
                            >
                                {availableDomains.map((domain) => (
                                    <option key={domain} value={domain}>
                                        {domain}
                                    </option>
                                ))}
                            </select>
                            {domainUpdatedMessage && (
                                <div className="card-domain-success-message">{domainUpdatedMessage}</div>
                            )}
                        </div>


                        <div className="status-bottom-section">
                            <div className="status-download-links">
                                <a
                                    href="https://chromewebstore.google.com/detail/animestar-extension/ocpbplnohadkjdindnodcmpmjboifjae"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="status-download-button chrome-store-button"
                                >
                                    <img src="/icons/chrome.svg" alt="Chrome" className="download-icon" />
                                    <span>{t('settings.chromeWebStore')}</span>
                                </a>
                                <a
                                    href="https://addons.mozilla.org/firefox/addon/animestar-extension/"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="status-download-button firefox-store-button"
                                >
                                    <img src="/icons/firefox.svg" alt="Firefox" className="download-icon" />
                                    <span>{t('settings.firefoxAddons')}</span>
                                </a>
                                <a
                                    href="https://github.com/Teri-anric/AnimeStarsExtensions/releases/latest"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="status-download-button github-button"
                                >
                                    <img src="/github-mark/github-mark-white.svg" alt="GitHub" className="download-icon" />
                                    <span>{t('settings.githubReleases')}</span>
                                </a>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default RandomAnimeGifPage;
