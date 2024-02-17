<script setup>
import { ref, watch } from 'vue'
import { useGeolocation } from '@vueuse/core'

const baseUrl = 'http://localhost:8000'

const query = ref('')

const location = ref(null)

const locationResults = ref([])

const searchGeo = () => {
  const { coords, pause } = useGeolocation()

  watch(coords, () => {
    location.value = [coords.value.longitude, coords.value.latitude]
    pause()
  })
}

const searchQuery = async () => {
  const response = await fetch(
    `${baseUrl}/search-address?` +
      new URLSearchParams({
        query: query.value
      })
  )

  const results = await response.json()

  if (results.length > 0) {
    const { lat, lng } = results[0].geometry.location
    location.value = [lng, lat]
  }
}

watch(location, async () => {
  const response = await fetch(
    `${baseUrl}/nearest-antennas?` +
      new URLSearchParams({
        lng: location.value[0],
        lat: location.value[1]
      })
  )

  const results = await response.json()

  locationResults.value = results.map((item) => ({ ...item, info: JSON.parse(item.info) }))
})
</script>

<template>
  <div class="flex justify-center h-screen">
    <div>
      <div class="my-4">
        <img src="./assets/logo.svg" class="h-[180px] m-auto" />
      </div>
      <div class="mb-4">
        <h1
          class="text-3xl font-extrabold text-center bg-gradient-to-r from-red-500 to-orange-500 bg-clip-text text-transparent"
        >
          חפש אנטנות סלולר באזורך
        </h1>
      </div>
      <div class="mb-4 flex w-[600px]">
        <div class="flex-1">
          <div class="flex">
            <input
              v-model="query"
              placeholder="כתובת"
              type="text"
              class="w-full rounded-s-3xl border-red-500 border-l-0 focus:ring-0 px-6 focus:border-red-600"
            />
            <button
              @click="searchQuery()"
              class="border py-2 px-6 rounded-e-3xl border-red-500 bg-gradient-to-r from-red-500 to-orange-500 text-white"
            >
              חפש
            </button>
          </div>
        </div>
        <div class="mr-1">
          <button
            @click="searchGeo()"
            class="border py-2 px-6 rounded-3xl bg-gradient-to-r from-red-500 to-orange-500 text-white"
          >
            המיקום שלי
          </button>
        </div>
      </div>
      <div class="flex justify-center text-center" v-if="locationResults.length > 0">
        <table>
          <thead class="bg-slate-200">
            <tr>
              <th class="p-1">חברה</th>
              <th class="p-1">כתובת</th>
              <th class="p-1">טכנולוגיית שידור</th>
              <th class="p-1">מרחק בק״מ</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="result in locationResults" class="border-b">
              <td class="p-1">{{ result.info['חברה'] }}</td>
              <td class="p-1">{{ result.info['כתובת האתר'] }}</td>
              <td class="p-1">{{ result.info['טכנולוגיית שידור'] }}</td>
              <td class="p-1">{{ (result.distance / 1000).toFixed(3) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
