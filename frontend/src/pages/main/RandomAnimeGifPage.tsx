import { useEffect, useState } from "react";
import { useAuth } from "../../context/AuthContext";
import { createAuthenticatedClient } from "../../utils/apiClient";
import { HealthApi } from "../../client";

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
    const [loading, setLoading] = useState<boolean>(true);
    const [status, setStatus] = useState<string>('');
    const { token } = useAuth();

    // Check backend health status using our generated client
    useEffect(() => {
        const checkHealth = async () => {
            try {
                const healthApi = createAuthenticatedClient(HealthApi);
                const response = await healthApi.healthHealthGet();
                setStatus(response.data.status);
            } catch (error) {
                console.error('Health check failed:', error);
                setStatus('Error connecting to backend');
            }
        };
        
        checkHealth();
    }, []);

    // Fetch the GIF using the external API
    useEffect(() => {
        const initialize = async () => {
            setLoading(true);
            try {
                const reactions = await fetchAllReactions(token || undefined);
                const randomReaction = reactions[Math.floor(Math.random() * reactions.length)];
                const gif = await fetchGif(randomReaction, token || undefined);
                setGif(gif);
            } catch (error) {
                console.error('Failed to fetch gif:', error);
            } finally {
                setLoading(false);
            }
        };
        initialize();
    }, [token]);

    if (loading) {
        return <div>Loading...</div>;
    }

    return (
        <div className="random-gif-container">
            <div className="status-indicator">Backend status: {status}</div>
            {gif && <img src={gif} alt="Random Anime Gif" className="anime-gif" />}
            {!gif && <div className="error-message">Failed to load GIF</div>}
        </div>
    );
};

export default RandomAnimeGifPage;
