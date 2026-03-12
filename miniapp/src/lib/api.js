const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

export async function getPlaces(params = {}) {
  const url = new URL(`${API_BASE_URL}/api/places`)

  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      url.searchParams.set(key, value)
    }
  })

  const response = await fetch(url)
  if (!response.ok) throw new Error('Не удалось загрузить заведения')
  return response.json()
}

export async function getPlace(id) {
  const response = await fetch(`${API_BASE_URL}/api/places/${id}`)
  if (!response.ok) throw new Error('Не удалось загрузить карточку')
  return response.json()
}
