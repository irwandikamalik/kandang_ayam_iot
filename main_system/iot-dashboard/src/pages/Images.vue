<template>

  <div class="images-page">

    <!-- HEADER -->
    <div class="page-header">

      <h1>Detection Images</h1>

      <button
        class="refresh-btn"
        @click="loadImages"
      >
        🔄 Refresh
      </button>

    </div>

    <!-- EMPTY -->
    <div
      v-if="images.length === 0"
      class="empty-box"
    >

      <h2>No Detection Images</h2>

      <p>
        YOLO screenshots will appear here
      </p>

    </div>

    <!-- GALLERY -->
    <div
      v-else
      class="gallery-grid"
    >

      <div
        v-for="item in images"
        :key="item.id"
        class="image-card"
      >

        <!-- IMAGE -->
        <a
        :href="getImageUrl(item.image_name)"
        target="_blank"
        >

        <img
            :src="getImageUrl(item.image_name)"
            class="detect-image"
        />

        </a>

        <!-- INFO -->
        <div class="image-info">

          <h3>
            {{ item.detected_class }}
          </h3>

          <p>
            Confidence:
            {{
              (
                Number(item.confidence)
                * 100
              ).toFixed(1)
            }}%
          </p>

          <span>
            {{
              formatDate(item.created_at)
            }}
          </span>

            <button
                class="delete-btn"
                @click="deleteImage(item.id)"
                >
                🗑 Delete
            </button>

        </div>

      </div>

    </div>

  </div>

</template>

<script setup>

import { ref, onMounted } from 'vue'
import axios from 'axios'

const API = window.location.origin

const images = ref([])

const loadImages = async () => {

  try {

    const res = await axios.get(
      `${API}/api/images`
    )

    images.value = res.data

  } catch (err) {

    console.error(
      'Load images error:',
      err
    )
  }
}

const getImageUrl = (filename) => {

  return `${API}/log_images/${filename}`
}

const formatDate = (date) => {

  const parts = date.split(' ')

  return `${parts[1]} ${parts[2]} ${parts[3]} ${parts[4]}`
}
const deleteImage = async (id) => {

  const confirmDelete =
    confirm(
      'Delete this image?'
    )

  if (!confirmDelete) return

  try {

    await axios.delete(
      `${API}/delete-image/${id}`
    )

    loadImages()

  } catch (err) {

    console.error(
      'Delete error:',
      err
    )
  }
}

onMounted(() => {

  loadImages()

  setInterval(loadImages, 5000)
})

</script>

<style scoped>

.images-page {

  min-height: 100vh;

  padding: 24px;

  box-sizing: border-box;
}


/* HEADER */
.page-header {

  display: flex;

  justify-content: space-between;

  align-items: center;

  margin-bottom: 24px;

  gap: 16px;

  flex-wrap: wrap;
}

.page-header h1 {

  margin: 0;

  font-size: clamp(28px, 5vw, 48px);

  font-weight: 800;

  background: linear-gradient(
    90deg,
    #38bdf8,
    #a78bfa
  );

  -webkit-background-clip: text;

  color: transparent;
}


/* BUTTON */
.refresh-btn {

  border: none;

  padding: 12px 20px;

  border-radius: 14px;

  cursor: pointer;

  font-weight: 700;

  color: white;

  background: linear-gradient(
    135deg,
    #38bdf8,
    #a78bfa
  );

  transition: 0.2s;
}

.refresh-btn:hover {

  transform: translateY(-2px);
}

.refresh-btn:active {

  transform: scale(0.96);
}


/* EMPTY */
.empty-box {

  width: 100%;

  padding: 60px 20px;

  border-radius: 24px;

  text-align: center;

  background: rgba(255,255,255,0.04);

  border: 1px solid rgba(255,255,255,0.08);

  backdrop-filter: blur(12px);
}

.empty-box h2 {

  margin-bottom: 8px;
}


/* GRID */
.gallery-grid {

  display: grid;

  grid-template-columns:
    repeat(
      auto-fit,
      minmax(280px, 1fr)
    );

  gap: 24px;
}


/* CARD */
.image-card {

  overflow: hidden;

  border-radius: 24px;

  background: rgba(255,255,255,0.04);

  border: 1px solid rgba(255,255,255,0.08);

  backdrop-filter: blur(12px);

  box-shadow:
    0 10px 30px rgba(0,0,0,0.35);

  transition:
    transform 0.25s ease,
    box-shadow 0.25s ease;
}

.image-card:hover {

  transform: translateY(-6px);

  box-shadow:
    0 16px 40px rgba(0,0,0,0.45),
    0 0 24px rgba(56,189,248,0.15);
}


/* IMAGE */
.detect-image {

  transition:
    transform 0.3s ease;

  width: 100%;

  height: 220px;

  object-fit: cover;

  background: #0f172a;

  cursor: pointer;

}

.detect-image:hover {

  transform: scale(1.05);
}

/* INFO */
.image-info {

  padding: 18px;
}

.image-info h3 {

  margin: 0 0 10px 0;

  font-size: 20px;

  font-weight: 700;
}

.image-info p {

  margin: 0 0 8px 0;

  font-size: 15px;
}

.image-info span {

  font-size: 13px;

  opacity: 0.7;
}


/* LIGHT MODE */
body.light-mode .image-card,
body.light-mode .empty-box {

  background: rgba(255,255,255,0.85);

  border: 1px solid rgba(0,0,0,0.08);

  box-shadow:
    0 8px 24px rgba(0,0,0,0.08);
}


/* MOBILE */
@media (max-width: 768px) {

  .images-page {

    padding: 14px;
  }

  .detect-image {

    height: 200px;
  }
}

.delete-btn {

  margin-top: 12px;

  width: 100%;

  border: none;

  padding: 10px;

  border-radius: 12px;

  cursor: pointer;

  font-weight: 700;

  color: white;

  background:
    linear-gradient(
      135deg,
      #ef4444,
      #dc2626
    );

  transition: 0.2s;
}

.delete-btn:hover {

  transform: translateY(-2px);

  background:
    linear-gradient(
      135deg,
      #f87171,
      #ef4444
    );
}

.delete-btn:active {

  transform: scale(0.96);
}

</style>