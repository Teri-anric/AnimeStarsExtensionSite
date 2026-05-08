import { useTranslation } from "react-i18next";
import { formatTime } from "../utils/dateUtils";

export interface GifHistoryItem {
    id: string;
    url: string;
    reaction: string;
    timestamp: number;
}

interface GifMainContentProps {
    loading: boolean;
    gif: string;
    currentReaction: string;
    showHistory: boolean;
    gifHistory: GifHistoryItem[];
    onFetchNewGif: () => void;
    onToggleHistory: () => void;
    onLoadFromHistory: (historyItem: GifHistoryItem) => void;
}

const GifMainContent = ({
    loading,
    gif,
    currentReaction,
    showHistory,
    gifHistory,
    onFetchNewGif,
    onToggleHistory,
    onLoadFromHistory,
}: GifMainContentProps) => {
    const { t } = useTranslation();

    return (
        <div className="gif-main-content">
            <div className="gif-controls">
                <button onClick={onFetchNewGif} disabled={loading} className="btn btn-primary refresh-btn">
                    {loading ? t("randomGif.loadingGif") : t("randomGif.newGif")}
                </button>
                <button onClick={onToggleHistory} className="btn btn-secondary history-btn">
                    {showHistory ? t("randomGif.hideHistory") : t("randomGif.showHistory")} ({gifHistory.length})
                </button>
            </div>

            <div className="gif-display">
                {gif && (
                    <div className="gif-container">
                        <img src={gif} alt="Random Anime Gif" className="anime-gif" />
                        <div className="gif-info">
                            <span className="reaction-tag">{t("randomGif.reaction")}: {currentReaction}</span>
                        </div>
                    </div>
                )}
                {!gif && !loading && <div className="error-message">{t("randomGif.failedToLoadGif")}</div>}
            </div>

            {showHistory && (
                <div className="gif-history">
                    <h3>{t("randomGif.gifHistory")}</h3>
                    <div className="history-grid">
                        {gifHistory.map((item) => (
                            <div key={item.id} className="history-item" onClick={() => onLoadFromHistory(item)}>
                                <img src={item.url} alt={item.reaction} />
                                <span className="history-reaction">{item.reaction}</span>
                                <span className="history-time">{formatTime(item.timestamp)}</span>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};

export default GifMainContent;
