import { useEffect, useState } from "react";


const fetchAllReactions = async () => {
    const response = await fetch('https://api.otakugifs.xyz/gif/allreactions');
    const data = await response.json();
    return data.reactions;
}

const fetchGif = async (reaction: string) => {
    const response = await fetch(`https://api.otakugifs.xyz/gif?reaction=${reaction}`);
    const data = await response.json();
    return data.url;
};

const RandomAnimeGif = () => {
    const [gif, setGif] = useState<string>('');

    useEffect(() => {
        const initialize = async () => {
            const reactions = await fetchAllReactions();
            const randomReaction = reactions[Math.floor(Math.random() * reactions.length)];
            const gif = await fetchGif(randomReaction);
            setGif(gif);
        };
        initialize();
    }, []);

    return <>
        {gif && <img src={gif} alt="Random Anime Gif" />}
    </>;
};

export default RandomAnimeGif;