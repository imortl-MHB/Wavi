import { useEffect, useMemo, useState } from 'react'
import { getPlaces } from './lib/api'

const quickFilters = [
  { label: 'Кофе', q: 'кофе' },
  { label: 'Завтрак', q: 'завтрак' },
  { label: 'Свидание', q: 'свидание' },
  { label: 'До 1000 ₽', max_price: 1000 },
]

function openYandexMaps(place) {
  const url = `https://yandex.ru/maps/?text=${encodeURIComponent(place.address)}`
  window.open(url, '_blank')
}

export default function App() {
  const [places, setPlaces] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [search, setSearch] = useState('')
  const [district, setDistrict] = useState('')
  const [maxPrice, setMaxPrice] = useState('')

  useEffect(() => {
    const tg = window.Telegram?.WebApp
    if (tg) {
      tg.ready()
      tg.expand()
    }
  }, [])

  async function loadPlaces(params = {}) {
    setLoading(true)
    setError('')
    try {
      const data = await getPlaces(params)
      setPlaces(data.items)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadPlaces()
  }, [])

  const title = useMemo(() => 'Wavi — где поесть в Воронеже', [])

  return (
    <div className="min-h-screen bg-neutral-950 text-white">
      <div className="mx-auto max-w-md px-4 py-5">
        <h1 className="text-2xl font-bold">{title}</h1>
        <p className="mt-2 text-sm text-neutral-300">
          Быстрый выбор мест по настроению, бюджету и району.
        </p>

        <div className="mt-4 flex flex-wrap gap-2">
          {quickFilters.map((item) => (
            <button
              key={item.label}
              onClick={() => {
                setSearch(item.q || '')
                setMaxPrice(item.max_price || '')
                loadPlaces(item)
              }}
              className="rounded-full bg-neutral-800 px-3 py-2 text-sm"
            >
              {item.label}
            </button>
          ))}
        </div>

        <div className="mt-5 space-y-3 rounded-2xl bg-neutral-900 p-4">
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Например: кофе, свидание, бар"
            className="w-full rounded-xl border border-neutral-700 bg-neutral-950 px-3 py-3 text-sm outline-none"
          />

          <select
            value={district}
            onChange={(e) => setDistrict(e.target.value)}
            className="w-full rounded-xl border border-neutral-700 bg-neutral-950 px-3 py-3 text-sm outline-none"
          >
            <option value="">Все районы</option>
            <option value="Центр">Центр</option>
            <option value="Северный">Северный</option>
            <option value="Левый берег">Левый берег</option>
          </select>

          <input
            value={maxPrice}
            onChange={(e) => setMaxPrice(e.target.value)}
            placeholder="Макс. чек, например 1000"
            className="w-full rounded-xl border border-neutral-700 bg-neutral-950 px-3 py-3 text-sm outline-none"
          />

          <button
            onClick={() => loadPlaces({ q: search, district, max_price: maxPrice || undefined })}
            className="w-full rounded-xl bg-white px-4 py-3 font-medium text-black"
          >
            Подобрать
          </button>
        </div>

        {loading && <p className="mt-4 text-sm text-neutral-400">Загружаю места…</p>}
        {error && <p className="mt-4 text-sm text-red-400">{error}</p>}

        <div className="mt-5 space-y-3">
          {places.map((place) => (
            <div key={place.id} className="rounded-2xl bg-neutral-900 p-4 shadow-lg">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <h2 className="text-lg font-semibold">{place.name}</h2>
                  <p className="mt-1 text-sm text-neutral-300">{place.description}</p>
                </div>
                <span className="rounded-full bg-neutral-800 px-2 py-1 text-xs">
                  {place.avg_check} ₽
                </span>
              </div>

              <p className="mt-3 text-sm text-neutral-400">📍 {place.district}, {place.address}</p>

              <div className="mt-3 flex flex-wrap gap-2">
                {place.tags.map((tag) => (
                  <span key={tag} className="rounded-full bg-neutral-800 px-2 py-1 text-xs text-neutral-200">
                    {tag}
                  </span>
                ))}
              </div>

              <div className="mt-4 flex gap-2">
                <button
                  onClick={() => openYandexMaps(place)}
                  className="flex-1 rounded-xl bg-white px-4 py-3 text-sm font-medium text-black"
                >
                  Открыть маршрут
                </button>
                <button
                  onClick={() => alert('Избранное добавим на следующем шаге')}
                  className="rounded-xl border border-neutral-700 px-4 py-3 text-sm"
                >
                  ♥
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
