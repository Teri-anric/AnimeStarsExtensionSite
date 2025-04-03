import { useEffect, useState } from "react"
import './App.css'
import { HealthApi, HealthResponse } from './client/api'
import RandomAnimeGif from "./components/RandomAnimeGif";

function App() {
  const [health, setHealth] = useState<HealthResponse | null>(null)

  useEffect(() => {
    const healthApi = new HealthApi({
      basePath: 'http://localhost:8000',
      isJsonMime: () => true
    })
    healthApi.healthHealthGet().then((res) => {
      setHealth(res.data)
    })
  }, [])


  return (
    <>
      <p>{health?.status}</p>
      <RandomAnimeGif />
    </>
  )
}

export default App;
